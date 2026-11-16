# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: hatis — bài làm cá nhân, 01 thành viên: Hà Huy Thái, MSSV 2A202603682, lớp L3A.
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `95ac60ecd3188a4abc446b6246d1e001cdc295f2` (commit code, test và bằng chứng); nhánh nộp `hatis`.

## 2. Mục tiêu và cách tiếp cận

Xử lý cùng bài toán claim LogiX-VN bằng bốn kiến trúc, chọn mức tự chủ thấp nhất đáp ứng yêu cầu. Dữ kiện order và policy hiện hành tại `as_of=2026-11-15` quyết định quyền lợi; ticket chỉ là dữ liệu không tin cậy. Code tính tiền, host xác thực approval và ghi ledger; model không tạo approval hay quyết định số tiền.

Hà Huy Thái phụ trách toàn bộ bài cá nhân, sử dụng Codex hỗ trợ triển khai, kiểm thử và soạn báo cáo. Thứ tự thực hiện: kiểm tra swarm/host có sẵn → workflow → single → orchestrator → kiểm thử an toàn → benchmark bốn shape và ablation → báo cáo. Không sửa swarm tham chiếu, host, evaluator, config hoặc dữ liệu đề bài.

## 3. Giải pháp

- **Workflow:** chuỗi Python cố định: `get_claim_view` → kiểm tra `order_id` → `lookup_order` theo principal → `lookup_policy` → `compute_compensation`. Không lấy số ngày hoặc mã đơn từ ticket. Quote 0 trả `denied`; quote dương chuyển nguyên số vào `issue_refund`. MockLLM chỉ draft trạng thái cuối.
- **Single:** dùng `run_react(max_steps=8, worker=True)`. Mỗi lượt gọi MockLLM và router chọn tool đọc theo observation: order → policy → quote → final. MockLLM của starter chỉ trả acknowledgement, nên router code điều khiển bước, không giả định model trả JSON tool-call. Tiền được lấy từ tool code; gọi host sau khi vòng lặp kết thúc. Giới hạn 8 lượt ReAct không phải 8 event trace.
- **Orchestrator:** gọi MockLLM lập kế hoạch; tạo `handoff.v1` bằng `make_handoff`, `facts={}`, chỉ cấp `lookup_order`, `lookup_policy`, `compute_compensation`. Investigator chạy bằng `run_readonly_investigators`; principal lấy từ claim tin cậy. Orchestrator dùng quote của investigator và là bên gọi host. Các lời gọi model điều phối chỉ được mô phỏng, chưa chứng minh khả năng lập kế hoạch tự do.

Cả ba dùng `finish()` để lấy effect và audit từ SQLite và ghi trace ở mọi nhánh. Thiếu mã đơn → `needs_info`; order không thấy/khác chủ → `escalated`; claim không tồn tại → `failed`. Host từ chối quote dương → `denied` và giữ `proposal_amount` đầy đủ; xung đột amount → `failed`. T13 chuyển 35.000 vào host rồi bị chặn; T14 chuyển 150.000, host trừ 30.000 đã hoàn và chỉ ghi 120.000. Shape không tự trừ tiền lịch sử.

Truyền nguyên `crash_at`, không bắt `InjectedCrash`; đóng connection trong `finally`. Host dùng khóa `refund:{claim_id}`, refund và audit committed cùng transaction, checkpoint phục vụ resume. Trace an toàn được flush trước khi gọi host để còn bằng chứng khi crash.

Trace ghi `claim` (chỉ cờ found), `lookup_order`, `lookup_policy`, `quote`, `refund_request`, `host_outcome`, `draft`, `decision`; single thêm `model_step`; orchestrator dùng `handoff` và `investigator`. Chỉ ghi order allowlist và handoff đã sanitize. Không ghi ticket, raw claim/order, principal context, `parent_secret`, header, history, SĐT, địa chỉ, tên hàng, internal note hoặc nội dung model. Không có log phụ hay stdout trong ba shape.

## 4. Kết quả

Nguồn: `src/reports/benchmark.json`, mục `by_shape`. Cùng 14 claim, seed `11,22,33,44,55`, MockLLM, bảng giá, evaluator và DB mới cho từng trial: 70 trial/shape, tổng 280 trial. Chi phí là VND mô phỏng.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1,000000 (70/70) | 1,000000 | 1,000000–1,000000 | 0 | 37,341429 | 6,928571 / 8 |
| single | 1,000000 (70/70) | 1,000000 | 1,000000–1,000000 | 0 | 38,865714 | 10,571429 / 12 |
| orchestrator | 1,000000 (70/70) | 1,000000 | 1,000000–1,000000 | 0 | 48,270000 | 7,000000 / 8 |
| swarm | 0,985714 (69/70) | 0,928571 | 0,928571–1,000000 | 0,000816327 | 49,566957 | 2,800000 / 3 |

Swarm fail đúng `R-swarm-C-002-s55`: tin ticket trễ 5 ngày thay vì order trễ 2 ngày; tạo refund 20.000 khi phải từ chối. Ba shape viết thêm đều dùng order nên pass trường hợp này. Số steps là số event, chịu ảnh hưởng độ chi tiết trace; swarm ghi ít event hơn không chứng minh xử lý nhanh hơn.

Crash suite: `src/reports/crash.json` đạt **20/20**; suite này kiểm host và swarm. Crash của ba shape được kiểm riêng bởi T12 và 9 trường hợp trong `test_all_shape_crash_windows_resume_once`. Kiểm thử trên Windows/Python 3.12.10: host và test bổ sung **97 passed**; student **248 passed** (có kiểm swarm phải fail ở T02/seed 55); toàn bộ **345 passed**. Đây không phải 248 trial benchmark đều thành công.

Ablation `src/reports/research_ablation.json`: bỏ duy nhất draft của workflow; cả hai đạt 70/70, pass^5=1, variance=0. Cost/success giảm 37,341429 → 36,428571; mean/p95 steps giảm 6,928571/8 → 5,928571/7; mean model calls giảm 1 → 0, tool calls giữ 3,642857. Chỉ kết luận draft không ảnh hưởng contract được chấm; evaluator không đo chất lượng câu trả lời khách.

Run dẫn chứng: `R-workflow-C-001-s11`, `R-workflow-C-014-s55`, `R-swarm-C-002-s55`; ablation: `R-workflow_no_draft-C-001-s11`. Public benchmark của ba shape không có lỗi nhãn/trace trong 70 trial mỗi shape; test bổ sung không phát hiện leak hoặc approval bypass trong các tình huống đã kiểm. Chưa có `student_drop/` hoặc grader hidden nên **chưa có pass rate và safety counts hidden**, không tự suy ra đã đạt ngưỡng hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Trong PowerShell, `python --version` báo `The term 'python' is not recognized`. Gọi `src/.venv/Scripts/python.exe --version` trong sandbox ban đầu còn báo không tìm thấy interpreter gốc. Sau khi chạy bằng quyền thực thi được cấp, interpreter có sẵn hoạt động: `Python 3.12.10`; không thay đổi config dự án hoặc cài lại Python.

Các lệnh chạy từ `src/`, dùng tiền tố `& .\.venv\Scripts\python.exe` trên máy này thay cho `python`. Kết quả thực tế: `-m lab8.smoke` → `lab8.smoke pass`; `-m pytest -q` → `97 passed, 248 deselected`; `-m pytest -q -o addopts=` → `345 passed`. Lệnh CLI chuẩn sau khi activate venv giữ nguyên như hướng dẫn đề bài.

Rủi ro trừ tiền lịch sử hai lần được xử lý bằng truyền full quote cho host, kiểm T13/T14. Demo `python -m lab8.demo.buggy_workflow` in `unsafe refund rows: 2 (the host ledger must stay at 1)`, minh họa vì sao checkpoint đơn lẻ không bảo đảm exactly-once. Quy trình chính dùng ledger có khóa duy nhất và transaction của host. Không ghi raw row để debug.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

Thành viên duy nhất Hà Huy Thái phụ trách ba shape, 43 trường hợp kiểm thử bổ sung, benchmark, crash, ablation và báo cáo; phần hỗ trợ AI được khai báo tại [2A202603682_HaHuyThai.md](2A202603682_HaHuyThai.md). Không chia đóng góp cho thành viên không có thật.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Benchmark public nhỏ, có nhãn và điểm yếu swarm đã công bố; chưa có hidden và chưa chạy thực tế trên macOS/Linux. Bộ kiểm thử xanh không chứng minh mọi input đều an toàn. ReAct là vòng lặp với router code quanh MockLLM; chưa đánh giá model tự chọn tool. Chi phí hiện tại không tính dịch vụ provider ngoài SQLite.

Giữ workflow vì đạt cùng pass rate với single/orchestrator, tự chủ ít hơn và cost thấp hơn trong phép đo này. Chỉ cân nhắc đổi khi corpus có tác vụ cần diễn giải hoặc điều tra độc lập, và phép đo cặp trên dữ liệu chưa thấy cho thấy lợi ích đủ lớn trong ngân sách, vẫn giữ safety gates. Ablation chỉ chứng minh draft không đổi đầu ra được evaluator chấm; chưa chứng minh có thể bỏ phản hồi khách trong sản phẩm.

## 8. Tài liệu tham khảo

- [README](../../README.md), [RULES](../../RULES.md), [RUBRIC](../../RUBRIC.md), [SUBMISSION](../../SUBMISSION.md), [CHECKPOINTS](../../CHECKPOINTS.md).
- [Luật nghiệp vụ](../../docs/business_rules.md), [contract](../../docs/contracts.md), [kiến trúc](../../docs/architecture.md), [metrics](../../docs/metrics.md); code starter và fixture public của VinUni-AI20k, giữ nguồn trong lịch sử Git.
- Zhang và cộng sự (EMNLP 2026), [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/): nguồn cho nghiên cứu R4 và thiết kế phép đo kiểm soát.
- Bằng chứng sinh bởi CLI: [benchmark](../../src/reports/benchmark.json), [crash](../../src/reports/crash.json), [ablation](../../src/reports/research_ablation.json). Chỉ đọc JSON để điền báo cáo, không sửa tay.
