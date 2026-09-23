from pydantic_ai import Agent
from pydantic_ai_harness import SubAgent, SubAgents, ToolOutputLimits
from pydantic_ai.toolsets.abstract import AbstractToolset
from pydantic_ai.durable_exec.prefect import PrefectDurability, TaskConfig
from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.output import ToolOutput
from pydantic_ai.toolsets.function import FunctionToolset
from utils.get_prompt_instruction import get_prompt_instruction
from tools.tavily_web_tools import web_fetch, web_search
from schemas.agents import AgentConfig
from typing import Callable, Any
from loguru import logger

class IdentifiedToolOutputLimits(ToolOutputLimits):
    """ToolOutputLimits, but stamps `id` onto its internal `read_tool_result` toolset.

    Upstream bug: `ToolOutputLimits.get_toolset()` always returns a bare
    `FunctionToolset([read_tool_result])` with no id, ignoring `self.id`.
    A leaf toolset without an id breaks Prefect/Temporal durable execution.
    """

    def get_toolset(self) -> AbstractToolset[Any] | None:
        toolset = super().get_toolset()
        if toolset is not None and toolset.id is None:
            toolset._id = self.id  # type: ignore[attr-defined]
        return toolset # type: ignore


class IdentifiedSubAgents(SubAgents):
    """SubAgents, but stamps `id` onto its internal `delegate_task` toolset.

    Same upstream bug as `ToolOutputLimits`: `SubAgents.get_toolset()` never
    forwards `self.id` to the `SubAgentToolset` it builds.
    """

    def get_toolset(self) -> AbstractToolset[Any] | None:
        toolset = super().get_toolset()
        if toolset is not None and toolset.id is None:
            toolset._id = self.id  # type: ignore[attr-defined]
        return toolset # type: ignore


class AgentFactory:
    def __init__(self, openrouter_api_key: str | None, subagent_configs: dict[str, AgentConfig] | None = None):
        self.openrouter_api_key: str | None = openrouter_api_key
        # Provide a lookup map for subagent configs so we can recursively build them
        self.subagent_configs: dict[str, AgentConfig] = subagent_configs or {}
        
        # Tool registry mapping config strings to actual Python functions
        self.tool_registry: dict[str, Callable] = {
            "web_fetch": web_fetch,
            "web_search": web_search,
        }

    def create_subagent(self, config: AgentConfig) -> SubAgent:
        return SubAgent(self.create_agent(config=config))
    
    def create_agent(self, config: AgentConfig) -> Agent:
        settings = OpenRouterModelSettings(
            openrouter_cache_instructions=True,
            openrouter_provider={
                "order": config.settings_openrouter_provider_list, # TODO: Add to accept None as value
                "allow_fallbacks": False
            }
        )
        model = OpenRouterModel(
            config.model_name,
            provider=OpenRouterProvider(api_key=self.openrouter_api_key),
        )

        # 3. Build base kwargs for the Agent
        agent_kwargs = {
            "model": model,
            "name": config.agent_name,
            "model_settings": settings,
            "instructions": get_prompt_instruction(config.instructions_path),
            "description": get_prompt_instruction(config.sub_descriptions_path),
            "retries": {'output': config.retries_output},
            "max_concurrency": config.max_concurrency,
        }

        # 4. Conditionally add Output Type and Dependencies Type
        if config.output_schema:
            agent_kwargs["output_type"] = ToolOutput(config.output_schema)
        if config.deps_type:
            agent_kwargs["deps_type"] = config.deps_type

        # 5. Conditionally add Capabilities (Subagents)
        capabilities: list[Any] = [
            IdentifiedToolOutputLimits(id=f"{config.agent_name}_tool_output_limits"),
            PrefectDurability(
                model_task_config=TaskConfig(
                    retries=3,
                    retry_delay_seconds=[1.0, 2.0, 5.0],  # Exponential backoff
                    timeout_seconds=600.0,
                    log_prints=True
                )
            ),
        ]
        if config.subagents_list:
            subagents_pool = self._get_subagents_pool(config.subagents_list)
            if subagents_pool:
                capabilities.append(
                    IdentifiedSubAgents(
                        agents=subagents_pool,
                        agent_folders=None,
                        tool_retries=3,
                        id=f"{config.agent_name}_subagents",
                    )
                )
        agent_kwargs["capabilities"] = capabilities

        # 6. Conditionally add Tools
        if config.tools_list:
            agent_kwargs["toolsets"] = [
                FunctionToolset(self._get_tools_pool(config.tools_list), id=f"{config.agent_name}_tools")
            ]

        # 7. Unpack kwargs into the Agent
        return Agent(**agent_kwargs) # type: ignore[call-overload]

    def _get_tools_pool(self, tools_list: list[str]) -> list[Callable]:
        """Maps list of string names to actual tool functions."""
        tool_seq = []
        for tool_name in tools_list:
            tool_fn = self.tool_registry.get(tool_name)
            if tool_fn:
                tool_seq.append(tool_fn)
            else:
                logger.warning(f"Tool '{tool_name}' not found in registry.")
        return tool_seq

    def _get_subagents_pool(self, subagents_list: list[str]) -> list[SubAgent]:
        """Maps list of string names to actual SubAgent instances recursively."""
        subagent_seq = []
        for subagent_name in subagents_list:
            sub_config = self.subagent_configs.get(subagent_name)
            if sub_config:
                # Recursively create the subagent using the mapped config
                subagent_seq.append(self.create_subagent(sub_config))
            else:
                logger.warning(f"Subagent config for '{subagent_name}' not found in registry.")
        return subagent_seq