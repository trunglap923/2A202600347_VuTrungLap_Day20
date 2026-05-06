"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and cost, and return metrics."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    # Calculate total cost from trace or agent_results if available
    # For simplicity, we can extract it from the state if we added it there,
    # but here we'll just sum up what we can find.
    total_cost = sum(r.metadata.get("cost_usd", 0.0) for r in state.agent_results)
    total_in = sum(r.metadata.get("input_tokens", 0) for r in state.agent_results)
    total_out = sum(r.metadata.get("output_tokens", 0) for r in state.agent_results)
    
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        input_tokens=total_in,
        output_tokens=total_out,
        sources_count=len(state.sources),
        final_answer=state.final_answer,
        notes=f"Iterations: {state.iteration}"
    )
    return state, metrics
