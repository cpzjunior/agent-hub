from agent_hub.bootstrap import build_agent_registry
from agent_hub.integrations.langchain.openai import OpenAIInterpreter
from agent_hub.mcp.server import create_mcp_server


def main() -> None:
    interpreters = {
        "git-agent": OpenAIInterpreter(),
        "agent-builder": OpenAIInterpreter(),
        "bookmark-agent": OpenAIInterpreter(),
        "project-ideas-agent": OpenAIInterpreter(),
    }

    registry = build_agent_registry(interpreters)
    server = create_mcp_server(registry)

    server.run()


if __name__ == "__main__":
    main()
