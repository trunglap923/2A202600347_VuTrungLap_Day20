"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


import time
from multi_agent_research_lab.services.llm_client import LLMClient


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a real single-agent baseline using LLMClient."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    client = LLMClient()
    start_time = time.time()
    
    # Minimal single-agent prompt
    system_prompt = "You are a helpful research assistant. Provide a comprehensive summary based on the user's query."
    response = client.complete(system_prompt, query)
    
    latency = time.time() - start_time
    state.final_answer = response.content
    
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))
    console.print(f"[bold blue]Latency:[/bold blue] {latency:.2f}s")
    console.print(f"[bold green]Estimated Cost:[/bold green] ${response.cost_usd if response.cost_usd else 0.0:.6f}")
    console.print(f"[bold yellow]Tokens:[/bold yellow] In: {response.input_tokens}, Out: {response.output_tokens}")


from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    start_time = time.time()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    
    latency = time.time() - start_time
    
    # Calculate total cost from agent_results if available
    total_cost = sum(r.metadata.get("cost_usd", 0.0) for r in result.agent_results)
    
    console.print(Panel.fit(result.final_answer or "No final answer generated.", title="Multi-Agent Workflow"))
    console.print(f"[bold blue]Latency:[/bold blue] {latency:.2f}s")
    console.print(f"[bold green]Estimated Cost:[/bold green] ${total_cost:.6f}")
    console.print(f"[bold yellow]Iterations:[/bold yellow] {result.iteration}")
    
    # Optional: print trace summary
    trace_names = " -> ".join(t["name"] for t in result.trace if t["name"] != "supervisor_decision")
    console.print(f"[bold cyan]Trace:[/bold cyan] {trace_names}")
    
    # User requested to see the detailed logs (trace) again
    console.print("\n[bold magenta]Detailed Trace Logs:[/bold magenta]")
    import json
    console.print(json.dumps(result.trace, indent=2, ensure_ascii=False))

    # Print sources researched
    console.print("\n[bold green]Sources Researched:[/bold green]")
    if result.sources:
        for i, source in enumerate(result.sources, 1):
            console.print(f"  {i}. {source.title} ({source.url})")
    else:
        console.print("  [italic red]No sources found.[/italic red]")


@app.command()
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Compare baseline vs multi-agent and save report."""

    _init()
    metrics_list = []

    # 1. Baseline
    console.print("[bold]Running Baseline...[/bold]")
    def baseline_runner(q: str) -> ResearchState:
        client = LLMClient()
        state = ResearchState(request=ResearchQuery(query=q))
        resp = client.complete("You are a research assistant.", q)
        state.final_answer = resp.content
        return state

    _, b_metrics = run_benchmark("Baseline", query, baseline_runner)
    metrics_list.append(b_metrics)

    # 2. Multi-Agent
    console.print("[bold]Running Multi-Agent...[/bold]")
    def multi_agent_runner(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        return workflow.run(state)

    _, ma_metrics = run_benchmark("Multi-Agent", query, multi_agent_runner)
    metrics_list.append(ma_metrics)

    # Render and save report
    report_md = render_markdown_report(metrics_list)
    report_path = "reports/benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    
    console.print(Panel.fit(f"Report saved to {report_path}", title="Benchmark Complete"))
    console.print(report_md)


if __name__ == "__main__":
    app()
