from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_internal_gateway_overlay_never_exposes_external_interfaces():
 s=(ROOT/"compose.internal-gateway.yaml").read_text()
 assert '127.0.0.1:3001:3001' in s
 assert '127.0.0.1:3002:3002' in s
 assert '"0.0.0.0:3001' not in s
 assert '"0.0.0.0:3002' not in s

def test_public_edge_never_proxies_internal_apps():
 s=(ROOT/"deploy/Caddyfile").read_text()
 assert "reverse_proxy admin-web" not in s
 assert "reverse_proxy warehouse-web" not in s
 for name in ("ADMIN","WAREHOUSE"):
  block=s.split("{$LFM_"+name+"_DOMAIN} {",1)[1].split("\n}",1)[0]
  assert 'respond "Internal portal access is not activated" 403' in block
