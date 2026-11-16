"""Research-card ablation: change only the workflow's draft call."""

from lab8.db import connect
from lab8.schemas import RunResult
from lab8.shapes.workflow import _run


def run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(
            conn, claim_id, seed=seed, crash_at=crash_at,
            draft_reply=False, shape="workflow_no_draft",
        )
    finally:
        conn.close()
