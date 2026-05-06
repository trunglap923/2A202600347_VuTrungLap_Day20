"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to a professional markdown report."""

    lines = [
        "# 📊 Báo cáo So sánh Hiệu suất (Benchmark Report)",
        "",
        "Báo cáo này so sánh hiệu suất giữa phương pháp Single-Agent (Baseline) và Multi-Agent Workflow.",
        "",
        "| Tên lượt chạy | Độ trễ (s) | Chi phí (USD) | Tokens (In/Out) | Sources | Chất lượng (0-10) | Ghi chú |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    
    for item in metrics:
        cost = "N/A" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.6f}"
        quality = "N/A" if item.quality_score is None else f"{item.quality_score}/10"
        tokens = f"{item.input_tokens or 0}/{item.output_tokens or 0}"
        sources = f"{item.sources_count or 0}"
        lines.append(f"| **{item.run_name}** | {item.latency_seconds:.2f}s | {cost} | {tokens} | {sources} | {quality} | {item.notes} |")
    
    lines.extend([
        "",
        "## 🔍 Nhận xét nhanh",
        "- **Single-Agent (Baseline):** Thường có độ trễ thấp hơn nhưng phụ thuộc hoàn toàn vào kiến thức tĩnh của mô hình.",
        "- **Multi-Agent:** Độ trễ cao hơn do quy trình nhiều bước (Nghiên cứu -> Phân tích -> Phản biện), nhưng dữ liệu được cập nhật mới nhất từ Internet và có sự kiểm định chéo giữa các agent.",
        "",
        "## 📝 Chi tiết Câu trả lời (Final Answers)"
    ])
    
    for item in metrics:
        lines.extend([
            "",
            f"### {item.run_name}",
            item.final_answer or "No answer provided."
        ])
    
    return "\n".join(lines) + "\n"
