"""B3: preserve the reference swarm, then verify its facts before writing.

The peer/parse/draft calls, read-only handoff, seeded ticket-delay weakness,
and host writer follow lab8.shapes.swarm_reference. Only the final verifier
is added. The provided reference file is left unchanged.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "swarm_verified"
# Every structured input used by compensation.quote, plus order identity.
VERIFIED_FIELDS = (
    "order_id", "delay_days", "status", "damage_verified", "shipping_fee_vnd", "paid_vnd",
)


def verify_quote(
    conn: sqlite3.Connection,
    budget: Budget,
    trace: Trace,
    *,
    claim: dict[str, Any],
    proposed_order: dict[str, Any],
    proposed_quote: dict[str, Any],
) -> dict[str, Any]:
    """One trusted scoped read, at most one deterministic repair, no writes.

    Re-read by the original claim's order/principal, never by the agent's
    proposed identity. Do not put ticket text or arbitrary proposed values
    into the trace. Code compensation and current policy remain trusted.
    """
    budget.add_tool(tool_cost())
    canonical = lookup_order(conn, claim["order_id"], claim["principal_id"])
    if not canonical["visible"]:
        trace.add("verifier_check", {"visible": False, "reason": canonical["reason"]})
        return {"ok": False, "reason": canonical["reason"]}
    order = canonical["order"]
    mismatched = [field for field in VERIFIED_FIELDS if proposed_order.get(field) != order[field]]
    trace.add("verifier_check", {"visible": True, "matched": not mismatched})
    if not mismatched:
        return {"ok": True, "quote": proposed_quote}
    budget.add_tool(tool_cost())
    repaired = compute_compensation(conn, order)
    trace.add("verifier_override", {
        "fields": mismatched,
        "repair_round": 1,
        "before_amount_vnd": int(proposed_quote["amount_vnd"]),
        "after_amount_vnd": int(repaired["amount_vnd"]),
    })
    return {"ok": True, "quote": repaired}


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status, proposal=0, reason=None):
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed,
            status=status, proposal_amount=proposal, budget=budget,
            trace=trace, error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", reason="unknown_claim")

    ticket = claim["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)
    if not claim["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return done("needs_info", reason="missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}", claim_id=claim_id,
        task="check_applicable_policy", facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    tools = investigated["tools"]
    view = tools.get("lookup_order", {})
    trace.add("investigator", {
        "lookup_order": view,
        "policy_count": len((tools.get("lookup_policy") or {}).get("policies") or []),
    })
    if not view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", reason=view.get("reason"))

    order = dict(view["order"])
    # Deliberately keep the reference mistake: the verifier must catch it.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})
    proposed_quote = tools["compute_compensation"]
    if order["delay_days"] != view["order"]["delay_days"]:
        budget.add_tool(tool_cost())
        proposed_quote = compute_compensation(conn, order)

    # Added B3 boundary: runs before BOTH zero-quote denial and money write.
    # Otherwise a false negative (ticket understating delay) would evade repair.
    verified = verify_quote(
        conn, budget, trace, claim=claim,
        proposed_order=order, proposed_quote=proposed_quote,
    )
    if not verified["ok"]:
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", reason=verified["reason"])
    quoted = verified["quote"]
    proposal = int(quoted["amount_vnd"])
    trace.add("quote", quoted)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
    if proposal <= 0:
        return done("denied", reason=quoted.get("reason"))

    trace.write()
    # Full quote; approval, per-order cap, ledger and audit remain host-owned.
    # InjectedCrash propagates. The connection is closed in run_claim.finally.
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal)
