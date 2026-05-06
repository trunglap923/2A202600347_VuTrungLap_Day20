"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self) -> None:
        self.llm = LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        if not state.final_answer:
            state.add_trace_event("critic_skipped", {"reason": "No final answer yet"})
            return state

        system_prompt = (
            "You are a critical reviewer. Your task is to review the final report for accuracy, "
            "completeness, and citation coverage. Identify any hallucinations or weak evidence. "
            "Provide constructive feedback."
        )
        user_prompt = (
            f"User Query: {state.request.query}\n"
            f"Research Notes: {state.research_notes}\n"
            f"Final Answer: {state.final_answer}"
        )

        response = self.llm.complete(system_prompt, user_prompt)
        
        # We can store feedback in a new field or reuse errors/trace
        # Let's add it to trace for now and maybe add a field to state if needed
        state.add_trace_event("critic_review", {"feedback": response.content})
        
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=response.content,
                metadata={
                    "cost_usd": response.cost_usd or 0.0,
                    "input_tokens": response.input_tokens or 0,
                    "output_tokens": response.output_tokens or 0
                }
            )
        )
        
        return state
