"""Verify the mandatory production Compose overlay does not enable risky features."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def test_production_overlay_enforces_fail_closed_runtime():
 s=(ROOT/"compose.production.yaml").read_text()
 assert "LFM_ENV: production" in s
 for key in ("LFM_SANDBOX_PAYMENTS_ENABLED","LFM_ITHUTE_PAY_CHECKOUT_ENABLED","LFM_E2E_SEED"):
  assert key+': "false"' in s
 assert s.count("no-new-privileges:true")==5
 assert s.count("- ALL")==5

def test_base_compose_only_exposes_loopback_ports():
 s=(ROOT/"compose.yaml").read_text()
 for port in (8000,3000,3001,3002,3003):
  assert f'127.0.0.1:{port}:{port}' in s
