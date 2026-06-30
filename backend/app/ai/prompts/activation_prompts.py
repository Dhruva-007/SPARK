"""
SPARK — Activation Agent Prompts
Prompts for generating starter materials that eliminate blank page paralysis.
"""


def build_activation_prompt(
    task_title: str,
    task_description: str,
    category: str,
    complexity: str,
    milestones: list[dict],
    genome_context: str,
) -> str:
    """
    Builds the prompt for the Activation Agent to generate starter materials.

    Returns a prompt that produces:
    - Document outline structure
    - Concrete first-action checklist
    - The single smallest first step
    - Implicit requirements extraction
    """
    milestones_str = "\n".join(
        f"{i+1}. {m['title']}" for i, m in enumerate(milestones[:5])
    )

    return f"""Generate activation materials for this task to eliminate blank-page paralysis.

TASK:
Title: {task_title}
Description: {task_description}
Category: {category}
Complexity: {complexity}

PLANNED MILESTONES:
{milestones_str}

USER CONTEXT:
{genome_context}

Generate:
1. A document outline (headers and sub-headers only, no content)
2. A checklist of the first 5 concrete actions to take RIGHT NOW
3. The single smallest possible first action (must take less than 5 minutes)
4. Any implicit requirements or assumptions that need clarification

The first action must be so small that there is zero reason not to do it immediately.
"""


def build_document_outline_prompt(
    task_title: str,
    task_description: str,
    category: str,
) -> str:
    """
    Builds a prompt specifically for generating a Google Doc outline.
    """
    return f"""Create a structured document outline for: {task_title}

Description: {task_description}
Type: {category}

Generate a hierarchical outline with:
- Main sections (H1)
- Sub-sections (H2)
- Key points to address in each section (H3)

The outline should guide the user to fill in content without thinking about structure.
Format as a clean hierarchical list.
"""