import inspect

from agent_hub.core import Agent


def test_agent_is_abstract() -> None:
    assert inspect.isabstract(Agent)