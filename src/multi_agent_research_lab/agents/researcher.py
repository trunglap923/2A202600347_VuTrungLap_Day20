"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.state import ResearchState


from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.search_client = SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        # 1. Generate search queries based on the main query
        search_query_prompt = (
            "Given the user query, generate 3 effective search queries to gather comprehensive information. "
            "Respond with only the queries, one per line, with no bullet points or numbering."
        )
        search_queries_resp = self.llm.complete(
            search_query_prompt, f"User Query: {state.request.query}"
        )
        search_queries = [q.strip().lstrip('1234567890.-* ') for q in search_queries_resp.content.split("\n") if q.strip()][:3]

        # 2. Execute search
        all_sources = []
        for q in search_queries[:3]:
            sources = self.search_client.search(q, max_results=state.request.max_sources)
            all_sources.extend(sources)

        state.sources = all_sources

        # 3. Summarize sources into research notes
        sources_text = "\n\n".join(
            [f"Source: {s.title} ({s.url})\nContent: {s.snippet}" for s in all_sources]
        )
        summary_prompt = (
            "Summarize the following search results into concise research notes. "
            "Focus on facts, key entities, and data relevant to the user query. "
            "Use bullet points."
        )
        summary_resp = self.llm.complete(summary_prompt, f"Query: {state.request.query}\n\nSources:\n{sources_text}")
        
        state.research_notes = summary_resp.content
        state.add_trace_event("research_completed", {"sources_count": len(all_sources)})
        
        from multi_agent_research_lab.core.schemas import AgentName, AgentResult
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=summary_resp.content,
                metadata={
                    "cost_usd": (search_queries_resp.cost_usd or 0.0) + (summary_resp.cost_usd or 0.0),
                    "input_tokens": (search_queries_resp.input_tokens or 0) + (summary_resp.input_tokens or 0),
                    "output_tokens": (search_queries_resp.output_tokens or 0) + (summary_resp.output_tokens or 0)
                }
            )
        )
        
        return state
