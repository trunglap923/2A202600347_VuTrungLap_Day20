# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. **Case nào nên dùng multi-agent? Vì sao?**
   - *Nên dùng:* Cho các tác vụ phức tạp, cần nhiều bước suy luận, nghiên cứu tài liệu từ internet, hoặc cần kiểm định chéo (ví dụ: tổng hợp báo cáo tài chính, nghiên cứu khoa học).
   - *Vì sao:* Giúp phân tách rõ ràng trách nhiệm, mỗi Agent chuyên một việc (phân tích, tổng hợp, phản biện) với prompt cụ thể, giảm tình trạng LLM bị "quá tải ngữ cảnh" (hallucination).

2. **Case nào không nên dùng multi-agent? Vì sao?**
   - *Không nên dùng:* Cho các tác vụ tra cứu đơn giản, hỏi đáp thông thường (FAQ), dịch thuật ngắn hoặc các ứng dụng cần thời gian phản hồi (latency) cực thấp theo thời gian thực.
   - *Vì sao:* Multi-Agent tiêu thụ rất nhiều tài nguyên (token) và mất nhiều thời gian do phải qua nhiều bước phối hợp, gây chậm trễ và lãng phí chi phí API không cần thiết.
