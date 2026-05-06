# Design Template

## Problem
Hệ thống cần xử lý các câu hỏi nghiên cứu phức tạp từ người dùng (ví dụ: "Research GraphRAG state-of-the-art and write a 500-word summary"). Yêu cầu hệ thống có khả năng tự động tạo từ khoá, tìm kiếm tài liệu từ Internet, phân tích, tổng hợp thông tin và viết ra một báo cáo chuyên nghiệp theo định dạng Markdown.

## Why multi-agent?
Một Single-agent (Baseline) chỉ có thể dựa vào kiến thức tĩnh (pre-trained knowledge), dễ sinh ra ảo giác (hallucination) khi gặp chủ đề mới. Việc sử dụng Multi-agent giúp mỗi Agent chuyên biệt hoá vai trò của mình (tìm kiếm, phân tích, viết bài, phản biện), cho phép truy xuất dữ liệu real-time từ Internet và kiểm định chéo để tăng chất lượng báo cáo, giảm quá tải ngữ cảnh.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối luồng chạy, quyết định Agent tiếp theo hoặc kết thúc. | Trạng thái hiện tại (route_history) | Tên Agent tiếp theo / END | Bị kẹt trong vòng lặp vô hạn (infinite loop). |
| Researcher | Tạo từ khóa tìm kiếm, thu thập dữ liệu từ Internet và tóm tắt nhanh. | User Query | Danh sách URLs, Research Notes | Không tìm thấy kết quả do từ khóa bị LLM sinh sai định dạng. |
| Analyst | Phân tích Research Notes, trích xuất claim và insight chính. | Research Notes | Analysis Notes | Bỏ sót thông tin quan trọng hoặc tóm tắt sai ý. |
| Writer | Tổng hợp mọi thứ thành bài báo cáo Markdown hoàn chỉnh. | Research Notes, Analysis Notes | Final Answer | Sinh nội dung lan man, sai format hoặc ảo giác. |
| Critic | Phản biện, kiểm tra chất lượng và độ chính xác của Final Answer. | Final Answer | Feedback (Trace) | Đưa ra feedback quá khắt khe hoặc không cần thiết. |

## Shared state
- `request`: Chứa câu hỏi ban đầu (query) và đối tượng người đọc (audience).
- `sources`: Lưu danh sách các nguồn tài liệu đã tìm được từ Internet để tiện truy xuất.
- `research_notes`: Ghi chú nghiên cứu sơ bộ của Researcher.
- `analysis_notes`: Insight và phân tích chi tiết của Analyst.
- `final_answer`: Báo cáo cuối cùng do Writer viết.
- `route_history`: Lịch sử các Node đã đi qua để Supervisor biết bước tiếp theo.
- `iteration`: Đếm số bước đã chạy để ngắt vòng lặp (Guardrail).
- `agent_results`: Lưu trữ output chi tiết (content, cost, tokens) của từng Agent để phục vụ Benchmark.

## Routing policy
Luồng chạy tuần tự (Sequential Workflow) được quản lý tập trung qua Supervisor:
`Supervisor -> Researcher -> Supervisor -> Analyst -> Supervisor -> Writer -> Supervisor -> Critic -> Supervisor -> END`
*Graph:* Cấu trúc LangGraph StateGraph. Mọi Worker Agents sau khi chạy xong đều phải quay về báo cáo cho Supervisor. Supervisor dùng `conditional_edges` để điều phối dựa vào `route_history`.

## Guardrails
- **Max iterations:** 6 (Cấu hình qua `.env` `MAX_ITERATIONS` để chống vòng lặp vô hạn).
- **Timeout:** 60s (Cấu hình qua `.env` `TIMEOUT_SECONDS`).
- **Retry:** Tích hợp cơ chế retry nếu gọi LLM API bị fail do network.
- **Fallback:** Trả về "No sources found" nếu Researcher thất bại, giúp các Agent sau không bị crash.
- **Validation:** Áp dụng Pydantic BaseModels (`ResearchState`, `AgentResult`) để ràng buộc chặt chẽ kiểu dữ liệu đầu vào/ra.

## Benchmark plan
- **Query mẫu:** "Research GraphRAG state-of-the-art and write a 500-word summary"
- **Metrics (Tiêu chí đo lường):** Latency (giây), Cost (USD), Tokens Usage, Số tài liệu thực tế, Chất lượng (0-10).
- **Expected outcome (Kỳ vọng):** Multi-Agent sẽ có Latency cao hơn và Cost tốn kém hơn Baseline, nhưng đem lại chất lượng (Quality) vượt trội, có dẫn chứng rõ ràng, dữ liệu cập nhật mới nhất và không bị ảo giác.
