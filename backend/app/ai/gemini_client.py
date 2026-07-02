"""
SPARK — Gemini 2.5 Flash Client
The single interface all agents use to communicate with Gemini.
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

TOKEN_BUDGETS: dict[str, int] = {
    "planner": 8192,
    "activation": 8192,
    "momentum": 4096,
    "risk": 4096,
    "context": 2048,
    "simulation": 8192,
    "intervention": 4096,
    "recovery": 8192,
    "reflection": 4096,
    "memory": 2048,
    "default": 4096,
}


class GeminiClient:
    """Production Gemini 2.5 Flash client for SPARK agents."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._model_name = self._settings.VERTEX_AI_MODEL
        self._model: Optional[GenerativeModel] = None

    def _get_model(self) -> GenerativeModel:
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
        Retries parse failures with a correction prompt.
        Generation errors (billing, auth) propagate immediately.
        """
        schema_description = _build_schema_description(response_model)
        full_prompt = f"{prompt}\n\n{schema_description}"

        max_parse_attempts = 3
        raw_text: str = ""
        last_parse_error: Optional[Exception] = None

        for attempt in range(1, max_parse_attempts + 1):
            try:
                current_prompt = (
                    full_prompt
                    if attempt == 1
                    else _build_correction_prompt(
                        original_prompt=full_prompt,
                        bad_response=raw_text,
                        error=str(last_parse_error),
                    )
                )

                raw_text = await self._generate_with_retry(
                    prompt=current_prompt,
                    system_instruction=system_instruction,
                    agent_role=agent_role,
                    temperature=temperature,
                    json_mode=True,
                )

                # Log raw response in debug mode for troubleshooting
                logger.debug(
                    "Raw Gemini response",
                    agent_role=agent_role,
                    attempt=attempt,
                    preview=raw_text[:300],
                )

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
                raise

            except Exception as exc:
                last_parse_error = exc
                logger.warning(
                    "Structured output parse attempt failed",
                    agent_role=agent_role,
                    attempt=attempt,
                    error=str(exc),
                    raw_preview=raw_text[:500] if raw_text else "(no response)",
                )

                if attempt == max_parse_attempts:
                    logger.error(
                        "All parse attempts exhausted",
                        agent_role=agent_role,
                        full_raw_response=raw_text,
                    )
                    raise GeminiResponseParseError(raw_text) from exc

        raise GeminiError("Unexpected structured generation failure")

    async def stream(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        agent_role: str = "intervention",
        temperature: float = 0.8,
    ) -> AsyncGenerator[str, None]:
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


_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client


def _extract_json(text: str) -> Any:
    """
    Extract JSON from model response.
    Handles markdown code blocks and outer wrapper objects.
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
    Generates a concise field-list description from a Pydantic model.
    Avoids dumping the full JSON schema which wastes tokens and confuses the model.
    Instead describes required fields clearly in plain language.
    """
    try:
        schema = model.model_json_schema()
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        field_lines = []
        for field_name, field_info in properties.items():
            field_type = field_info.get("type", "any")
            description = field_info.get("description", "")
            is_required = field_name in required
            req_marker = " (required)" if is_required else " (optional)"
            field_lines.append(f'  "{field_name}": {field_type}{req_marker} — {description}')

        fields_str = "\n".join(field_lines)

        return (
            f"Respond with a single valid JSON object with these fields:\n"
            f"{fields_str}\n\n"
            f"Rules:\n"
            f"- Output ONLY the JSON object\n"
            f"- No markdown, no code blocks, no explanation\n"
            f"- No text before or after the JSON\n"
            f"- All string values must be properly escaped\n"
            f"- Ensure the JSON is complete and valid"
        )
    except Exception:
        return (
            "Respond with a single valid JSON object matching the required structure. "
            "Output ONLY the JSON. No markdown. No explanation."
        )


def _build_correction_prompt(
    original_prompt: str,
    bad_response: str,
    error: str,
) -> str:
    return (
        f"{original_prompt}\n\n"
        f"Your previous response could not be parsed as valid JSON.\n"
        f"Error: {error}\n"
        f"Previous response (invalid):\n{bad_response[:1000]}\n\n"
        f"Please respond with ONLY valid JSON matching the schema above. "
        f"No text, no markdown, no explanation."
    )