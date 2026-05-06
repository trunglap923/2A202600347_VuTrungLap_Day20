"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        system_prompt = (
            "You are a professional technical writer. Your goal is to synthesize research notes "
            "and analysis insights into a high-quality, clear, and comprehensive final report "
            "tailored for the intended audience."
        )
        user_prompt = (
            f"User Query: {state.request.query}\n"
            f"Audience: {state.request.audience}\n\n"
            f"Research Notes:\n{state.research_notes if state.research_notes else 'None'}\n\n"
            f"Analysis Notes:\n{state.analysis_notes if state.analysis_notes else 'None'}\n\n"
            "Please write the final answer. Use Markdown formatting. Include references if possible."
        )

        response = self.llm.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        state.add_trace_event("writing_completed", {"answer_length": len(response.content)})
        
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=response.content,
                metadata={"cost_usd": response.cost_usd or 0.0}
            )
        )
        
        return state
