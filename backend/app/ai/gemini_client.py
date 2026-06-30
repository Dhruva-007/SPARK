"""
SPARK — Gemini 2.5 Flash Client
The single interface all agents use to communicate with Gemini.

Responsibilities:
- Generate text responses (direct completion)
- Generate structured JSON responses (with validation + retry)
- Stream responses (for real-time intervention chat)
- Manage token budgets per agent
- Retry with exponential backoff on transient failures
- Correct malformed JSON responses with a repair prompt

All agents import this client. Never call Vertex AI SDK directly
from an agent — always go through GeminiClient.
"""

import asyncio
import json
import re
from typing import Any, AsyncGenerator, Optional, Type, TypeVar

from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    SafetySetting,
)

from app.core.config import get_settings
from app.core.exceptions import GeminiError, GeminiResponseParseError
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

# ── Safety settings ───────────────────────────────────────────
_SAFETY_SETTINGS = [
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]

# ── Token budgets per agent role ──────────────────────────────
TOKEN_BUDGETS: dict[str, int] = {
    "planner": 4096,
    "activation": 8192,
    "momentum": 2048,
    "risk": 2048,
    "context": 1024,
    "simulation": 4096,
    "intervention": 4096,
    "recovery": 8192,
    "reflection": 4096,
    "memory": 1024,
    "default": 2048,
}


class GeminiClient:
    """
    Production Gemini 2.5 Flash client for SPARK agents.

    Usage:
        client = GeminiClient()

        # Text response
        text = await client.generate("Summarize this task: ...")

        # Structured JSON response (validated against Pydantic model)
        plan = await client.generate_structured(
            prompt="Generate a plan for...",
            response_model=ExecutionPlan,
            agent_role="planner",
        )

        # Streaming response
        async for chunk in client.stream("Help me with..."):
            print(chunk, end="")
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model_name = self._settings.VERTEX_AI_MODEL
        self._model: Optional[GenerativeModel] = None

    def _get_model(self) -> GenerativeModel:
        """
        Returns the GenerativeModel instance.
        Lazy initialization — creates model on first use.
        """
        if self._model is None:
            from app.ai.vertex_client import get_generative_model
            self._model = get_generative_model(self._model_name)
        return self._model

    def _build_generation_config(
        self,
        agent_role: str = "default",
        temperature: float = 0.7,
        top_p: float = 0.95,
        json_mode: bool = False,
    ) -> GenerationConfig:
        """
        Build generation configuration for a specific agent role.
        JSON mode requests structured output from the model.
        """
        max_tokens = TOKEN_BUDGETS.get(agent_role, TOKEN_BUDGETS["default"])

        config_kwargs: dict[str, Any] = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"

        return GenerationConfig(**config_kwargs)

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        agent_role: str = "default",
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a text response from Gemini.

        Args:
            prompt: The user prompt
            system_instruction: System-level instruction for the model
            agent_role: Used to select token budget
            temperature: Creativity level (0=deterministic, 1=creative)

        Returns:
            Generated text string

        Raises:
            GeminiError: If generation fails after retries
        """
        return await self._generate_with_retry(
            prompt=prompt,
            system_instruction=system_instruction,
            agent_role=agent_role,
            temperature=temperature,
            json_mode=False,
        )

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        agent_role: str = "default",
        temperature: float = 0.3,
    ) -> T:
        """
        Generate a structured JSON response validated against a Pydantic model.

        Retry strategy:
        - Attempt 1: Full prompt with schema description
        - Attempt 2: Correction prompt if parse failed (not if generation failed)
        - Attempt 3: Final correction attempt
        - Raises GeminiResponseParseError if all attempts fail

        Args:
            prompt: The user prompt
            response_model: Pydantic model class to validate against
            system_instruction: System-level instruction
            agent_role: Used to select token budget
            temperature: Lower = more deterministic JSON output

        Returns:
            Validated Pydantic model instance

        Raises:
            GeminiError: If generation itself fails (billing, auth, network)
            GeminiResponseParseError: If JSON cannot be parsed after all retries
        """
        schema_description = _build_schema_description(response_model)
        full_prompt = f"{prompt}\n\n{schema_description}"

        # Generation errors (billing, auth, network) are not retried here —
        # they propagate immediately. Only JSON parse failures trigger retries.
        max_parse_attempts = 3
        raw_text: str = ""

        for attempt in range(1, max_parse_attempts + 1):
            try:
                # Build the prompt for this attempt
                if attempt == 1:
                    current_prompt = full_prompt
                else:
                    # Correction prompt — include the bad response for the model to fix
                    current_prompt = _build_correction_prompt(
                        original_prompt=full_prompt,
                        bad_response=raw_text,
                        error=str(last_parse_error),  # type: ignore[possibly-undefined]
                    )

                # Generation — let any GeminiError propagate immediately
                # (billing, auth, and network errors should not be retried here)
                raw_text = await self._generate_with_retry(
                    prompt=current_prompt,
                    system_instruction=system_instruction,
                    agent_role=agent_role,
                    temperature=temperature,
                    json_mode=True,
                )

                # Parse and validate the JSON response
                parsed_json = _extract_json(raw_text)
                validated = response_model.model_validate(parsed_json)

                if attempt > 1:
                    logger.info(
                        "Structured output parsed after correction",
                        agent_role=agent_role,
                        attempt=attempt,
                    )

                return validated

            except GeminiError:
                # Generation-level failure — re-raise immediately, do not retry
                # These are not parse errors: billing, auth, quota, network
                raise

            except Exception as exc:
                # Parse or validation failure — record and retry
                last_parse_error = exc
                logger.warning(
                    "Structured output parse attempt failed",
                    agent_role=agent_role,
                    attempt=attempt,
                    error=str(exc),
                    raw_preview=raw_text[:200] if raw_text else "(no response)",
                )

                if attempt == max_parse_attempts:
                    raise GeminiResponseParseError(raw_text) from exc

        # Unreachable — loop always returns or raises
        raise GeminiError("Unexpected structured generation failure")

    async def stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        agent_role: str = "intervention",
        temperature: float = 0.8,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from Gemini token by token.
        Used by the Intervention Agent for real-time collaboration.

        Args:
            prompt: The user prompt
            system_instruction: System-level instruction
            agent_role: Used to select token budget
            temperature: Higher = more conversational

        Yields:
            Text chunks as they arrive from the model
        """
        try:
            generation_config = self._build_generation_config(
                agent_role=agent_role,
                temperature=temperature,
                json_mode=False,
            )

            if system_instruction:
                active_model = GenerativeModel(
                    self._model_name,
                    system_instruction=system_instruction,
                )
            else:
                active_model = self._get_model()

            loop = asyncio.get_event_loop()
            responses = await loop.run_in_executor(
                None,
                lambda: active_model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=_SAFETY_SETTINGS,
                    stream=True,
                ),
            )

            for response in responses:
                if response.text:
                    yield response.text

        except Exception as exc:
            logger.error("Gemini streaming failed", error=str(exc))
            raise GeminiError(f"Streaming generation failed: {exc}") from exc

    async def _generate_with_retry(
        self,
        prompt: str,
        system_instruction: Optional[str],
        agent_role: str,
        temperature: float,
        json_mode: bool,
    ) -> str:
        """
        Internal generation method with retry logic.
        Only retries on transient network/connection errors.
        Does NOT retry on billing, auth, or quota errors.
        """

        @retry(
            retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            reraise=True,
        )
        def _sync_generate() -> str:
            if system_instruction:
                active_model = GenerativeModel(
                    self._model_name,
                    system_instruction=system_instruction,
                )
            else:
                active_model = self._get_model()

            generation_config = self._build_generation_config(
                agent_role=agent_role,
                temperature=temperature,
                json_mode=json_mode,
            )

            response = active_model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=_SAFETY_SETTINGS,
            )

            if not response.text:
                raise GeminiError(
                    "Empty response from Gemini",
                    details={"agent_role": agent_role},
                )

            return response.text

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, _sync_generate)

            logger.debug(
                "Gemini generation complete",
                agent_role=agent_role,
                json_mode=json_mode,
                chars=len(result),
            )

            return result

        except GeminiError:
            raise
        except Exception as exc:
            logger.error(
                "Gemini generation failed",
                agent_role=agent_role,
                error=str(exc),
            )
            raise GeminiError(f"Generation failed: {exc}") from exc


# ── Module-level singleton ────────────────────────────────────

_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """
    Returns the shared GeminiClient singleton.
    Creates it on first call (lazy initialization).
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


# ── Helper functions ──────────────────────────────────────────

def _extract_json(text: str) -> Any:
    """
    Extract JSON from a model response.
    Handles cases where the model wraps JSON in markdown code blocks.

    Tries in order:
    1. Direct JSON parse
    2. Extract from ```json ... ``` code block
    3. Extract first {...} or [...] block found
    """
    stripped = text.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown code block
    code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(code_block_pattern, stripped)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find first JSON object or array
    json_pattern = r"(\{[\s\S]*\}|\[[\s\S]*\])"
    match = re.search(json_pattern, stripped)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    raise GeminiResponseParseError(text)


def _build_schema_description(model: Type[BaseModel]) -> str:
    """
    Generates a JSON schema description from a Pydantic model.
    Injected into prompts so Gemini knows exactly what to produce.
    """
    schema = model.model_json_schema()
    schema_str = json.dumps(schema, indent=2)
    return (
        f"You MUST respond with valid JSON that exactly matches this schema:\n"
        f"```json\n{schema_str}\n```\n"
        f"Respond with ONLY the JSON object. No explanation. No markdown. "
        f"No text before or after the JSON."
    )


def _build_correction_prompt(
    original_prompt: str,
    bad_response: str,
    error: str,
) -> str:
    """
    Builds a correction prompt when JSON parsing fails.
    """
    return (
        f"{original_prompt}\n\n"
        f"Your previous response could not be parsed as valid JSON.\n"
        f"Error: {error}\n"
        f"Previous response (invalid):\n{bad_response[:1000]}\n\n"
        f"Please respond with ONLY valid JSON matching the schema above. "
        f"No text, no markdown, no explanation."
    )