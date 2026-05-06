# Peer Review Rubric

Mỗi nhóm review repo/trace của một nhóm khác trong 8 phút.

| Tiêu chí | Câu hỏi | Điểm |
|---|---|---:|
| Role clarity | Mỗi agent có nhiệm vụ rõ, không overlap quá nhiều không? | 0-2 |
| State design | Shared state có đủ thông tin để handoff mà không mất context không? | 0-2 |
| Failure guard | Có max iterations, timeout, retry/fallback, validation không? | 0-2 |
| Benchmark | Có so sánh single vs multi-agent bằng metric cụ thể không? | 0-2 |
| Trace explanation | Nhóm giải thích được trace: ai làm gì, tốn bao nhiêu, sai ở đâu không? | 0-2 |

## Feedback format

```text
Strength:
- Nhóm đã phân chia rõ ràng các roles: Researcher tìm kiếm, Analyst phân tích thông tin, Writer tổng hợp thành Markdown, và Critic phản biện kỹ lưỡng.
- Áp dụng LangSmith tracing thành công, giao diện hiển thị Trace cực kỳ trực quan và chuyên nghiệp.
- Code thiết kế chuẩn, có đủ schemas, config từ env, và lưu log chi tiết từng Agent.
- Benchmark sinh ra báo cáo Markdown rất đầy đủ về latency, token usage và cost.

Risk / failure mode:
- Ở phiên bản đầu, Researcher gặp lỗi lấy sai từ khoá khiến DuckDuckGo (ddgs) không trả về kết quả, dẫn tới toàn bộ các Agent phía sau bị "ảo giác" (nhưng đã fix thành công).
- Thời gian chạy (Latency) của quy trình Multi-Agent khá lâu (> 60s), dễ bị timeout nếu kết nối API không ổn định.

One concrete improvement:
- Nên tích hợp thêm cơ chế fallback hoặc retry tự động ngay trong code nếu SearchClient trả về mảng rỗng `[]`, ép buộc ResearcherAgent phải generate lại từ khoá khác tốt hơn.

Score: 10/10
```
