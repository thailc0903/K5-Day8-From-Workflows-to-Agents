# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: f8e24fbd33e3cabd4ba8f68fe9c4e8690aeb0224 (commit chứa code, test, báo cáo và bonus B3; nhánh nộp main)
- Run id dẫn chứng: R-workflow-C-001-s11; R-workflow-C-014-s55; đối chứng R-swarm-C-002-s55 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0, public 14 claim × 5 seed, 70/70 trial (src/reports/benchmark.json → by_shape.workflow); hidden chưa có kết quả
- Cost per success (mô phỏng, VND): 37.34142857142857 (src/reports/benchmark.json → by_shape.workflow.cost_per_success_vnd)
- Crash safety: 20/20 (src/reports/crash.json: host và swarm); ba shape viết thêm qua T12 và 9 trường hợp crash trong src/tests/test_hatis_shapes.py
- Secret leak / approval bypass: Không phát hiện trong các tình huống public/test bổ sung đã chạy; 70/70 trial workflow pass kiểm tra nhãn và trace. Test approval thiếu, thu hồi, 0, mượn claim khác đều không ghi refund. Chưa có secret_leak_count / approval_bypass_count hidden; không tự khai số chấm chính thức.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm hatis chọn workflow vì luồng claims chủ yếu tuần tự, luật tiền và approval đã rõ. Trên cùng 14 claim, 5 seed, MockLLM, bảng giá và evaluator, workflow, single và orchestrator đều đạt pass rate/pass^5 = 1.0/1.0, variance = 0. Workflow có cost/success 37.341429 VND, thấp hơn single 38.865714 và orchestrator 48.27. Swarm đạt 69/70 trial, pass^5=13/14, variance=0.000816327, cost/success=49.566957. Workflow ít tự chủ nhất trong các shape đạt đủ public; quyết định này còn chờ hidden để xác nhận cổng ≥0.75, không lấy public thay cho hidden.

## Có đáng đổi lấy multi-agent không

Chưa có lợi ích pass rate để đổi sang multi-agent trong phép đo hiện tại. Nếu pass chỉ nhỉnh hơn nhưng cost và variance tăng, giữ workflow cho đến khi cải thiện trên claim khó có ý nghĩa thực tế, đủ dữ liệu lặp và không vi phạm safety. Đổi quyết định khi dữ liệu chưa thấy có nhánh cần điều tra độc lập hoặc xử lý ngôn ngữ mà workflow không làm được, và so sánh cặp cùng điều kiện cho thấy kiến trúc khác đáp ứng yêu cầu tốt hơn trong ngân sách chấp nhận được. Không suy rộng rằng multi-agent luôn kém.

## Trace và bằng chứng

Workflow ghi `claim` (cờ found), `lookup_order` allowlist, số policy hiện hành và as_of, `quote`, `refund_request`, `host_outcome`, `draft` (chỉ status), `decision`. Single thêm `model_step`; orchestrator ghi `handoff` sanitize và `investigator`. Không ghi ticket, raw claim/order, parent context, `parent_secret`, header, history, SĐT, địa chỉ, internal note, tên hàng hoặc nội dung model. Dữ liệu ticket có thể lặp lại bí mật, nên ngay cả ticket trong claim view cũng không được log.

Mỗi lần return dùng `finish()` ghi trace JSON mới tại `src/traces/<run_id>.json` khi chạy từ `src/`. `run_id=make_run_id(shape, claim_id, seed)` khớp kết quả; mọi event nằm trong file scanner đọc, không có debug dump ở thư mục khác và không in stdout. Flush trace trước host để crash vẫn có tiền tố an toàn, không bắt `InjectedCrash`. Không commit traces/SQLite. Bằng chứng: ma trận student, `test_ticket_cannot_supply_order_or_leak_context`, `test_orchestrator_forwards_only_sanitized_handoff` và test crash bổ sung. Không dùng việc scanner không thấy log ở ngoài phạm vi để khẳng định an toàn.

Lệnh tái lập (chạy trong `src/`, sau khi activate venv):

```text
python -m lab8.smoke
python -m pytest -q
python -m pytest -q -m student -o addopts=
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.workflow_no_draft:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
python -m lab8.check_submission
```

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

Chỉ 14 public claim, 5 seed; chưa có student_drop hoặc điểm hidden, chưa chứng minh chạy nhiều hệ điều hành. Steps đếm event trace, mức log giữa shape khác nhau nên không thể dùng số đó làm latency hoặc số lượt ReAct. Benchmark bốn shape còn khác prompt và cơ chế phối hợp, vì vậy không quy mọi chênh lệch cho topology. Ablation R4 chỉ thay bước draft: giữ nguyên quyền lợi, giảm 0.912857 VND/success; không đo chất lượng phản hồi khách.
