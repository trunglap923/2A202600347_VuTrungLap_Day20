"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.errors import StudentTodoError


from multi_agent_research_lab.core.config import get_settings
from openai import OpenAI


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


from multi_agent_research_lab.core.errors import LLMClientError


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise LLMClientError("OPENAI_API_KEY is not set in settings")
        from langsmith import wrappers
        self.client = wrappers.wrap_openai(OpenAI(api_key=self.settings.openai_api_key))

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Connected to OpenAI provider.
        Includes retry logic via tenacity (implied by typical production needs, 
        though for lab we keep it simple or use OpenAI's built-in retries).
        """

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )
        except Exception as e:
            raise LLMClientError(f"OpenAI completion failed: {e}") from e

        content = response.choices[0].message.content or ""
        usage = response.usage

        # Basic cost calculation for gpt-4o-mini if possible, else None
        # Input: $0.150 / 1M tokens, Output: $0.600 / 1M tokens
        cost = None
        if usage and self.settings.openai_model == "gpt-4o-mini":
            cost = (usage.prompt_tokens * 0.150 / 1_000_000) + (
                usage.completion_tokens * 0.600 / 1_000_000
            )

        return LLMResponse(
            content=content,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            cost_usd=cost,
        )
