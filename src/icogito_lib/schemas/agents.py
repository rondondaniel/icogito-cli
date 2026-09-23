from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from typing import Type, Any
from dataclasses import dataclass, field

@dataclass
class ResearchState:
    visited_urls: set[str] = field(default_factory=set)
    searched_queries: set[str] = field(default_factory=set)

class AgentConfig(BaseModel):
    model_name: str
    agent_name: str
    instructions_path: str
    settings_openrouter_provider_list: list[str] # TODO: Add to accept None as value
    sub_instructions_path: str | None = None
    sub_descriptions_path: str | None = None
    sub_agent_description: str | None = None
    agent_instruction: str | None = None
    subagents_list: list[str] | None = None
    tools_list: list[str] | None = None
    output_schema: Type[BaseModel] | None = None
    deps_type: Type[Any] | None = None
    retries_output: int = 3
    max_concurrency: int = 1

class UsageLimitErrorResponse(BaseModel):
    error_code: str = Field(
        default="UsageLimitExceeded",
        description="The standard error code identifier for routing."
    )
    message: str = Field(
        ...,
        description="The raw error message explaining the usage limit violation."
    )
    limit_type: Optional[str] = Field(
        default=None,
        description="The type of quota exceeded (e.g., 'requests_per_minute', 'tokens_per_day', 'budget')."
    )
    current_usage: Optional[int | float] = Field(
        default=None,
        description="The recorded usage at the time the exception was raised."
    )
    max_limit: Optional[int | float] = Field(
        default=None,
        description="The maximum allowed threshold for the specified limit_type."
    )
    retry_after_seconds: Optional[int] = Field(
        default=None,
        description="The suggested backoff time in seconds extracted from the API response headers."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The exact UTC timestamp when the error occurred."
    )