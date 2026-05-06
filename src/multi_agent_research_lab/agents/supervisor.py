"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.config import get_settings


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.settings = get_settings()

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""

        # Enforce max iterations
        if state.iteration >= self.settings.max_iterations:
            state.record_route("done")
            return state

        # Determine next step based on state
        system_prompt = (
            "You are a research supervisor. Based on the current state, decide the next agent to call. "
            "Options: 'researcher', 'analyst', 'writer', 'critic', 'done'.\n\n"
            "Rules:\n"
            "1. If research_notes are empty, go to 'researcher'.\n"
            "2. If research_notes exist but haven't been analyzed, go to 'analyst'.\n"
            "3. If analysis is done but no final answer, go to 'writer'.\n"
            "4. If writer has produced a final answer but it hasn't been reviewed, go to 'critic'.\n"
            "5. If critic review is complete and the answer is satisfactory, go to 'done'.\n"
            "Respond with ONLY the name of the agent or 'done'."
        )

        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Research Notes: {state.research_notes[:500] if state.research_notes else 'None'}\n"
            f"Analysis Notes: {state.analysis_notes[:500] if state.analysis_notes else 'None'}\n"
            f"Final Answer: {'Exists' if state.final_answer else 'None'}\n"
            f"Has been reviewed: {'Yes' if any(t['name'] == 'critic_review' for t in state.trace) else 'No'}\n"
            f"Iteration: {state.iteration}"
        )

        response = self.llm.complete(system_prompt, user_prompt)
        next_step = response.content.strip().lower()

        # Validation of next_step
        allowed = ["researcher", "analyst", "writer", "critic", "done"]
        if next_step not in allowed:
            next_step = "done"  # Fallback

        state.record_route(next_step)
        state.add_trace_event("supervisor_decision", {"next": next_step, "iteration": state.iteration})
        
        return state
