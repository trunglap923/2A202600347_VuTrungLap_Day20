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
    total_cost = 0.0
    # In my implementation, I didn't store cost in the state directly yet, 
    # but the trace has info. Let's assume we want to sum costs.
    # For now, I'll just use the latency and add a note.
    
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=None, # Will implement if we track cost in state
        notes=f"Iteration count: {state.iteration}"
    )
    return state, metrics
