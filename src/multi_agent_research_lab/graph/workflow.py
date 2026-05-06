"""LangGraph workflow skeleton."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from langgraph.graph import StateGraph, END
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent


from multi_agent_research_lab.agents.critic import CriticAgent


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()

    def build(self) -> StateGraph:
        """Create a LangGraph graph."""

        workflow = StateGraph(ResearchState)

        # Define nodes
        workflow.add_node("supervisor", self.supervisor.run)
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("analyst", self.analyst.run)
        workflow.add_node("writer", self.writer.run)
        workflow.add_node("critic", self.critic.run)

        # Define edges
        workflow.set_entry_point("supervisor")

        # Conditional routing from supervisor
        def router(state: ResearchState) -> str:
            if not state.route_history:
                return "supervisor"
            next_agent = state.route_history[-1]
            if next_agent == "done":
                return END
            return next_agent

        workflow.add_conditional_edges(
            "supervisor",
            router,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                END: END,
            },
        )

        # Worker agents always go back to supervisor
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")

        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""

        app = self.build()
        # LangGraph invoke returns the final state (as a dict or pydantic model depending on how it's defined)
        # Since we used ResearchState (BaseModel) as the state type, it should work fine.
        result = app.invoke(state)
        
        # Ensure result is ResearchState
        if isinstance(result, dict):
            return ResearchState(**result)
        return result
