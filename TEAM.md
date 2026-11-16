# Team

## Thông tin nhóm

- Tên nhóm: hatis (làm cá nhân, 01 thành viên)
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-hatis-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: URL hiện tại https://github.com/thailc0903/K5-Day8-From-Workflows-to-Agents; nhánh `hatis`; commit kỹ thuật `95ac60ecd3188a4abc446b6246d1e001cdc295f2`. Tên repo cần đổi theo dòng trên trước khi nộp LMS.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Hà Huy Thái | 2A202603682 | thailc0903@gmail.com | [thailc0903](https://github.com/thailc0903) | Phụ trách toàn bộ bài cá nhân: ba shape, tích hợp, test, benchmark, ablation và báo cáo; có hỗ trợ AI được khai báo trong báo cáo cá nhân |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Hà Huy Thái | Workflow, single, orchestrator, an toàn, đánh giá và báo cáo | [95ac60e](https://github.com/thailc0903/K5-Day8-From-Workflows-to-Agents/commit/95ac60ecd3188a4abc446b6246d1e001cdc295f2): triển khai ba shape, ablation và bằng chứng; commit tạo với hỗ trợ Codex | `src/tests/test_hatis_shapes.py`: 43 trường hợp, gồm approval sai claim/bị thu hồi/thiếu/0, policy tương lai, xung đột số tiền, 9 cửa sổ crash, handoff, giới hạn ReAct, injection và ablation |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603682_HaHuyThai

### Phần việc phụ trách

- Phụ trách toàn bộ bài cá nhân của nhóm hatis: ba shape A/B/C, kiểm tra host, durability, policy, handoff, benchmark và báo cáo.

### Đóng góp cụ thể

- Hoàn thiện ba shape đúng contract; bổ sung 43 trường hợp kiểm thử; chạy benchmark 14 claim × 5 seed × 4 shape; thực hiện ablation bỏ duy nhất bước draft của workflow. Chi tiết hỗ trợ AI ghi trong báo cáo cá nhân.

### Bằng chứng

- Commit kỹ thuật `95ac60e`; `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/research_ablation.json`; [báo cáo cá nhân](report/team/2A202603682_HaHuyThai.md).
