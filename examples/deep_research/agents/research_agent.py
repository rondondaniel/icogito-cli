from loguru import logger
import os
from examples.deep_research.schemas.datamodel import TopicNewsBatch
from icogito_lib.agents.factory import AgentFactory
from icogito_lib.schemas.agents import AgentConfig, ResearchState
from icogito_lib.utils.load_agent_config import load_agent_config

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.error("OPENROUTER_API_KEY is missing!")
    raise ValueError("OPENROUTER_API_KEY is missing! Check your .env file.")

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "deep_research_agent_agent.yaml")
    researcher_config: AgentConfig = load_agent_config(config_path)
    researcher_config.output_schema = TopicNewsBatch
    researcher_config.deps_type = ResearchState
    factory = AgentFactory(
        openrouter_api_key=OPENROUTER_API_KEY,
        subagent_configs={}
    )

    researcher_agent = factory.create_agent(config=researcher_config)
    final_answer = researcher_agent.run_sync(
                user_prompt="research news about sovereign AI for this week",
                deps=ResearchState()
    )
    # Safely handle the logging depending on if the output is a Pydantic model or a string
    if hasattr(final_answer.output, "model_dump_json"):
        print(f"Agent {researcher_agent.name} Answer:\n{final_answer.output.model_dump_json(indent=2)}")
    else:
        print(f"Agent {researcher_agent.name} Answer:\n{final_answer.output}")