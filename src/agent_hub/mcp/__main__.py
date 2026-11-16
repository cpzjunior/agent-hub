from agent_hub.bootstrap import build_agent_registry
from agent_hub.integrations.langchain.openai import OpenAIInterpreter
from agent_hub.mcp.server import create_mcp_server


def main() -> None:
    interpreters = {
        "git-agent": OpenAIInterpreter(),
        "agent-builder": OpenAIInterpreter(),
        "archmage-scribe": OpenAIInterpreter(),
        "bookmark-agent": OpenAIInterpreter(),
        "decision-architect": OpenAIInterpreter(),
        "project-ideas-agent": OpenAIInterpreter(),
        "writing-assistant": OpenAIInterpreter(),
    }

    registry = build_agent_registry(interpreters)
    server = create_mcp_server(registry)

    server.run()


if __name__ == "__main__":
    main()
