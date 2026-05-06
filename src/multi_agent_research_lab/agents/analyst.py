"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        if not state.research_notes:
            state.analysis_notes = "No research notes available to analyze."
            return state

        system_prompt = (
            "You are a strategic analyst. Your task is to analyze research notes, "
            "extract key claims, identify contradictions or gaps, and provide a structured "
            "set of insights. Be critical and objective."
        )
        user_prompt = (
            f"User Query: {state.request.query}\n\n"
            f"Research Notes:\n{state.research_notes}"
        )

        response = self.llm.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content
        state.add_trace_event("analysis_completed", {"notes_length": len(response.content)})
        
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=response.content,
                metadata={
                    "cost_usd": response.cost_usd or 0.0,
                    "input_tokens": response.input_tokens or 0,
                    "output_tokens": response.output_tokens or 0
                }
            )
        )
        
        return state
