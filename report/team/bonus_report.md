# Bonus report: B3

- Topic + nguồn (tên, năm, slide): hatis — Hà Huy Thái, 2A202603682; **B3: Verifier/aggregator chống khuếch đại lỗi**. Kim, Liu và cộng sự, *Towards a Science of Scaling Agent Systems*, [Google Research, 2026](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/), slide 17, 22, 42.
- CLAIM của nguồn (1 câu): Trong thiết lập nghiên cứu, agent độc lập khuếch đại lỗi 17,2×, còn điều phối tập trung có cơ chế kiểm chứng giới hạn mức này ở 4,4×.
- BOUNDARY (model / dataset / setup): Nguồn khảo sát 180 cấu hình, ba họ model và bốn benchmark, không phải LogiX-VN; lab chỉ vận dụng ý tưởng kiểm chứng, không tái lập hai hệ số trên.
- HYPOTHESIS trên LogiX: Một verifier xác định bằng code đưa độ đúng của swarm về gần workflow trên các lỗi dữ kiện, giữ safety counts bằng 0, với chi phí cao hơn workflow.
- Biến cố định / biến thay đổi: Cùng MockLLM, seed `11,22,33,44,55`, tools, giá, evaluator, policy/as_of và DB mới/trial; giữ nguyên swarm gốc. `swarm_verified` giữ peer/parse/draft, handoff và lỗi seed 55, chỉ thêm verifier trước quyết định cuối. Đối chiếu `order_id`, `delay_days`, `status`, `damage_verified`, `shipping_fee_vnd`, `paid_vnd` với order theo principal; nếu lệch, quote lại bằng code **tối đa một lần**. Tính đủ phí đọc kiểm chứng và sửa quote.
- Lệnh tái lập (copy-paste được): Trong `src/`, sau activate venv: `python -m bonus.evaluate_b3` tạo toàn bộ số liệu qua benchmark chính thức với `--extra-shape swarm_verified=bonus.swarm_verified:run_claim`; kiểm thử: `python -m pytest -q tests/test_bonus_swarm_verified.py`.
- File report + run id: `src/reports/bonus_public.json`, `bonus_adversarial.json`, `bonus_b3.json`; `R-swarm_verified-C-002-s55`, `R-swarm_verified-B3-002-s55`. B3 đang là thay đổi cục bộ, **chưa commit/push**; hash nguồn nằm trong `bonus_b3.json`.

## Kết quả

Số liệu đọc từ JSON do script sinh; VND mô phỏng, làm tròn trong bảng. Public: 14 claim × 5 seed/shape; đối kháng: 12 × 5/shape.

| Bộ | Shape | Pass rate | Pass^5 | Variance | VND/success |
| --- | --- | ---: | ---: | ---: | ---: |
| Public | workflow | 1,000000 | 1,000000 | 0 | 37,341429 |
| Public | swarm | 0,985714 | 0,928571 | 0,00081633 | 49,566957 |
| Public | swarm_verified | 1,000000 | 1,000000 | 0 | 57,572857 |
| Đối kháng | workflow | 1,000000 | 1,000000 | 0 | 36,743333 |
| Đối kháng | swarm | 0,933333 | 0,666667 | 0,01777778 | 53,025000 |
| Đối kháng | swarm_verified | 1,000000 | 1,000000 | 0 | 58,990000 |

12 nhãn được khai báo tường minh theo luật nghiệp vụ, có `label_basis`, không sinh bằng `quote`: nói quá/thiếu, nhiều con số, giả damage, injection, cộng quyền lợi sai, thiếu/mượn approval, hoàn trước, khác chủ, thiếu mã đơn, đơn hủy. Có hỗ trợ Codex soạn fixture và kiểm tra.

Verifier kiểm 60 trial public, can thiệp **1** lần, sửa **1** trial fail; kiểm 50 trial đối kháng, can thiệp **7** lần, sửa **4** trial fail. Ba can thiệp còn lại sửa dữ kiện nhưng không đổi quyền lợi cuối. Một lượt/trial tối đa; thiếu mã đơn/khác chủ dừng trước verifier. Lần replay an toàn khớp toàn bộ 390 trial benchmark.

Mỗi shape, mỗi bộ có `secret_leak_count`, `pii_leak_count`, `approval_bypass_count`, `invalid_trace_count`, `unexpected_ledger_count` đều **0**. Scanner kiểm kết quả, trace/file cùng tiền tố và stdout/stderr; approval đối chiếu bản ghi thật, không chỉ tin status. Host crash **20/20**; B3 crash **3/3**, resume/retry đều một refund và một audit. Test B3 **151 passed**; toàn bộ test **496 passed**.

Trace minh họa được nhúng an toàn trong `bonus_b3.json → public.safety_and_interventions.example_trace`: `R-swarm_verified-C-002-s55`, `model_override: delay_days=5` → `verifier_override: fields=[delay_days], repair_round=1, before_amount_vnd=20000, after_amount_vnd=0`. Verifier cũng sửa quote 0 sai trước khi từ chối ở `B3-002`, tránh bỏ sót trường hợp nói thiếu.

## Kết luận

Ủng hộ hypothesis trên hai bộ đã đo: verifier đạt cùng pass rate/pass^5 với workflow và variance 0; chi phí vẫn cao hơn workflow. Khi code đã quyết toàn bộ dữ kiện quote, swarm chỉ còn giá trị tiềm năng ở diễn giải/giao tiếp; lab chưa đo được lợi ích đó. Giữ **workflow** làm shape chính. Chỉ cân nhắc đổi nếu tác vụ mới chứng minh lợi ích model/multi-agent vượt chi phí kiểm chứng mà vẫn qua safety gates.

## Giới hạn

MockLLM không phải model sản xuất; latency là `unavailable`. Corpus nhỏ, đối kháng được thiết kế biết trước lỗi; 5 seed không tương đương mẫu độc lập và không chứng minh ý nghĩa thống kê. Không suy ra hệ số khuếch đại của paper hoặc chất lượng phản hồi khách. Chưa có hidden: **chưa xác nhận điều kiện nhận bonus** (workflow hidden ≥0,80 và đủ must-pass). Tổng điểm bonus tối đa +10, không tự nhận đã đạt.
