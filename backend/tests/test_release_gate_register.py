from app.release_gate_register import GATES,release_gate_register

def test_release_gates_have_unique_codes_and_evidence_requirements():
 assert len({gate.code for gate in GATES})==len(GATES)
 assert all(gate.owner and gate.evidence and gate.target in {"demo","pilot"} for gate in GATES)

def test_no_gate_can_self_approve():
 rows=release_gate_register()
 assert rows
 assert all(row["status"]=="unverified" and row["evidence_reference"] is None for row in rows)
 assert {row["code"] for row in rows} >= {"customer_web_e2e","admin_web_e2e","warehouse_web_e2e","driver_web_e2e"}
