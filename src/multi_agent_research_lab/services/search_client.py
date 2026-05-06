"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import SourceDocument


from duckduckgo_search import DDGS


from multi_agent_research_lab.core.errors import SearchClientError


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query using DuckDuckGo."""

        results = []
        try:
            with DDGS() as ddgs:
                ddgs_gen = ddgs.text(query, max_results=max_results)
                for r in ddgs_gen:
                    results.append(
                        SourceDocument(
                            title=r.get("title", "No Title"),
                            url=r.get("href", ""),
                            snippet=r.get("body", ""),
                            metadata={"source": "duckduckgo"},
                        )
                    )
        except Exception as e:
            raise SearchClientError(f"DuckDuckGo search failed: {e}") from e

        return results
