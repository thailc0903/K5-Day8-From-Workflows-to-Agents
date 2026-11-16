# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders. Chênh lệch cost có thể đến từ lời gọi draft ngoài phần quyết định; ablation loại bỏ duy nhất thành phần đó. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang và cộng sự, EMNLP 2026, [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/). Bằng chứng: benchmark kiểm soát về phương pháp tối ưu cấu trúc MAS; không phải báo cáo production. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Trong thiết lập nghiên cứu, hiệu quả báo cáo có thể phụ thuộc prompt và topology khởi đầu; so sánh cần giữ cố định backbone, registry và runtime để quy kết đúng thay đổi cấu trúc. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn đánh giá các phương pháp tái cấu trúc MAS trong benchmark riêng, không phải LogiX-VN. Lab này dùng MockLLM, 14 public claim, host SQLite và evaluator không chấm câu trả lời khách; chỉ vận dụng nguyên tắc kiểm soát, không tái lập kết quả của paper. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Bỏ lời gọi MockLLM `draft` cuối workflow giữ pass rate/pass^5 ở 1.0, variance 0; giảm khoảng 0.9 VND/success và một model call/trial. Đây là kiểm tra phụ thuộc dữ liệu của code: draft không tham gia quote/host, không phải giả thuyết về năng lực model thật. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ workflow `_run`, MockLLM, mọi tool đọc, host, corpus C-001…C-014, seed 11/22/33/44/55, as_of 2026-11-15, pricing, evaluator và DB mới mỗi trial. Biến duy nhất: `draft_reply=True/False`; `bonus/workflow_no_draft.py` gọi cùng `_run` với False. Tên shape/run_id khác chỉ để tách artifact. Không thay quyết định, prompt của lời gọi được giữ, hay số tool. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Nếu draft vô tình ảnh hưởng quyết định thì status/proposal/ledger sẽ lệch giữa cặp; test so sánh trực tiếp 5 nhánh và benchmark toàn bộ corpus. Đo pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps, model/tool calls. Kiểm tra trace/chuỗi cấm bằng evaluator; approval và crash kiểm riêng trong test, không tạo safety counts hidden giả. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `& .\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.workflow_no_draft:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json` (PowerShell, thư mục `src/`; sau khi activate venv có thể dùng `python` thay đường dẫn interpreter).
- Run id / file report: `R-workflow-C-001-s11` và `R-workflow_no_draft-C-001-s11`, cùng các cặp claim/seed còn lại trong `src/reports/research_ablation.json`; commit kỹ thuật `95ac60e`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Ủng hộ trong public. Hai biến thể đều 70/70, pass rate=1.0, pass^5=1.0, seed min–max=1.0–1.0, variance=0. Cost/success 37.34142857142857 → 36.42857142857143 VND, giảm 0.91285714285714 (~2.44%); tổng cost 2613.9 → 2550.0. Mean model calls 1 → 0; mean tool calls cùng 3.642857142857143. Mean/p95 steps 6.928571/8 → 5.928571/7, do bỏ một event draft, không phải đo thời gian. Test cặp xác nhận status, proposal, effect, audit và tool_calls không đổi.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Evaluator không chấm chất lượng câu trả lời khách. Ablation chứng minh tính độc lập của bước draft trong implementation này; chưa đủ quy chênh lệch bốn shape hoàn toàn cho topology hoặc kết luận về lợi ích MAS nói chung. Không có dữ liệu hidden. Đây là ablation bắt buộc của research card, không đăng ký điểm bonus B1–B7.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
