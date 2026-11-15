
from pathlib import Path

import pytest

from agent_hub.agents.decision_architect import DecisionArchitect
from agent_hub.agents.decision_architect.models import (
    Decision,
    DecisionSession,
    DecisionStatus,
    EventType,
)
from agent_hub.core.interpreter import (
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
)


class FakeInterpreter(Interpreter):
    """Interpreter mock returning predefined results."""

    def __init__(
        self,
        results: list[InterpretationResult],
    ) -> None:
        self.results = results
        self.requests: list[InterpretationRequest] = []

    async def interpret(
        self,
        request: InterpretationRequest,
    ) -> InterpretationResult:
        self.requests.append(request)

        if not self.results:
            raise RuntimeError(
                "No more interpretation results available."
            )

        return self.results.pop(0)


@pytest.fixture
def agent_path(tmp_path: Path) -> Path:
    """Create a minimal Decision Architect directory structure."""

    skills_path = tmp_path / "skills"
    skills_path.mkdir()

    skill_names = [
        "decision-domain",
        "initial-context",
        "decision-objectives",
        "risks-and-uncertainties",
        "decision-consequences",
        "decision-evolution",
    ]

    for skill_name in skill_names:
        skill_dir = skills_path / skill_name
        skill_dir.mkdir()

        (skill_dir / "SKILL.md").write_text(
            f"---\n"
            f"name: {skill_name}\n"
            f"description: Test skill for {skill_name}.\n"
            f"---\n"
            f"# {skill_name}\n\n"
            f"Test instructions.\n",
            encoding="utf-8",
        )

    workflow_dir = (
        tmp_path
        / "workflows"
        / "decision-architecture"
    )
    workflow_dir.mkdir(parents=True)

    (workflow_dir / "WORKFLOW.md").write_text(
        "# Decision Architecture Workflow\n\nTest workflow.",
        encoding="utf-8",
    )

    return tmp_path


def make_interpreter(
    *results: InterpretationResult,
) -> FakeInterpreter:
    return FakeInterpreter(list(results))


@pytest.fixture
def successful_interpreter() -> FakeInterpreter:
    return make_interpreter(
        InterpretationResult(
            skill_name="decision-domain",
        ),
        InterpretationResult(
            skill_name="decision-domain",
            parameters={
                "decision_updates": {
                    "name": "Legacy system replacement",
                    "description": "Evaluate system replacement.",
                },
                "event_type": "updated",
                "event_target": "name",
                "event_description": "Decision identified.",
                "event_rationale": "Initial decision analysis.",
                "event_source": "user",
            },
            message="Decision model updated.",
        ),
    )


def test_loads_all_skills_and_workflow(
    agent_path: Path,
) -> None:
    agent = DecisionArchitect(agent_path=agent_path)

    assert len(agent.skills) == 6
    assert agent._workflow == (
        "# Decision Architecture Workflow\n\nTest workflow."
    )


@pytest.mark.asyncio
async def test_executes_selected_skill(
    agent_path: Path,
    successful_interpreter: FakeInterpreter,
) -> None:
    agent = DecisionArchitect(
        interpreter=successful_interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "I need to evaluate replacing a legacy system."}
    )

    assert result.status == "completed"
    assert result.skill_name == "decision-domain"
    assert result.session.decision.name == "Legacy system replacement"
    assert len(successful_interpreter.requests) == 2

    selection_request = successful_interpreter.requests[0]
    execution_request = successful_interpreter.requests[1]

    assert len(selection_request.skills) == 6
    assert len(execution_request.skills) == 1
    assert execution_request.skills[0].name == "decision-domain"


@pytest.mark.asyncio
async def test_preserves_existing_session(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            skill_name="initial-context",
        ),
        InterpretationResult(
            skill_name="initial-context",
            parameters={
                "decision_updates": {
                    "context": "Legacy system has integration constraints."
                },
            },
            message="Context updated.",
        ),
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    session = DecisionSession(
        decision=Decision(
            name="Legacy system replacement",
        )
    )

    result = await agent.run(
        {
            "instruction": "The legacy system has integration constraints.",
            "session": session,
        }
    )

    assert result.status == "completed"
    assert result.session.id == session.id
    assert result.session.decision.name == "Legacy system replacement"
    assert (
        result.session.decision.context
        == "Legacy system has integration constraints."
    )


@pytest.mark.asyncio
async def test_returns_needs_input_when_selection_requires_information(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            missing_inputs=["decision_subject"],
            message="Please clarify which decision should be analyzed.",
        )
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Help me make a decision."}
    )

    assert result.status == "needs_input"
    assert result.required_input == ["decision_subject"]
    assert len(interpreter.requests) == 1


@pytest.mark.asyncio
async def test_returns_needs_input_when_skill_requires_information(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            skill_name="decision-objectives",
        ),
        InterpretationResult(
            skill_name="decision-objectives",
            missing_inputs=["desired_outcome"],
            message="The desired outcome is unclear.",
        ),
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Help define the objectives."}
    )

    assert result.status == "needs_input"
    assert result.skill_name == "decision-objectives"
    assert result.required_input == ["desired_outcome"]


@pytest.mark.asyncio
async def test_returns_unsupported_when_no_skill_is_selected(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            message="No suitable skill found.",
        )
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Perform an unrelated task."}
    )

    assert result.status == "unsupported"
    assert result.skill_name is None


@pytest.mark.asyncio
async def test_records_decision_event(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            skill_name="decision-domain",
        ),
        InterpretationResult(
            skill_name="decision-domain",
            parameters={
                "decision_updates": {
                    "name": "New decision",
                },
                "event_type": "created",
                "event_target": "decision",
                "event_description": "Decision created.",
                "event_source": "user",
            },
        ),
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Analyze a new decision."}
    )

    assert result.status == "completed"
    assert len(result.session.events) == 1
    assert result.session.events[0].event_type == EventType.CREATED
    assert result.session.events[0].target == "decision"
    assert result.session.events[0].description == "Decision created."


@pytest.mark.asyncio
async def test_updates_decision_status(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            skill_name="decision-evolution",
        ),
        InterpretationResult(
            skill_name="decision-evolution",
            parameters={
                "decision_updates": {
                    "status": DecisionStatus.DECIDED.value,
                },
                "event_type": "status_changed",
                "event_target": "status",
                "event_description": "Decision marked as decided.",
            },
        ),
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "The decision has been made."}
    )

    assert result.status == "completed"
    assert result.session.decision.status == DecisionStatus.DECIDED


@pytest.mark.asyncio
async def test_rejects_invalid_decision_update(
    agent_path: Path,
) -> None:
    interpreter = make_interpreter(
        InterpretationResult(
            skill_name="decision-domain",
        ),
        InterpretationResult(
            skill_name="decision-domain",
            parameters={
                "decision_updates": {
                    "unknown_field": "invalid",
                },
            },
        ),
    )

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Update the decision."}
    )

    assert result.status == "failed"
    assert "unknown_field" in result.message


@pytest.mark.asyncio
async def test_handles_interpreter_error(
    agent_path: Path,
) -> None:
    interpreter = FakeInterpreter([])

    agent = DecisionArchitect(
        interpreter=interpreter,
        agent_path=agent_path,
    )

    result = await agent.run(
        {"instruction": "Analyze a decision."}
    )

    assert result.status == "failed"
    assert "No more interpretation results" in result.message


@pytest.mark.asyncio
async def test_rejects_empty_instruction(
    agent_path: Path,
) -> None:
    agent = DecisionArchitect(agent_path=agent_path)

    result = await agent.run({"instruction": "   "})

    assert result.status == "failed"
    assert "Instruction cannot be empty" in result.message
