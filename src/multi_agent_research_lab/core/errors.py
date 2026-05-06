"""Domain-specific errors for the lab skeleton."""


class LabError(Exception):
    """Base error for the lab package."""


class StudentTodoError(LabError):
    """Raised where learners are expected to implement core logic."""


class AgentExecutionError(LabError):
    """Raised when an agent fails after retries/fallbacks."""


class ValidationError(LabError):
    """Raised when state or output validation fails."""


class LLMClientError(LabError):
    """Raised when LLM provider returns an error (rate limit, auth, etc.)."""


class SearchClientError(LabError):
    """Raised when search provider fails."""
