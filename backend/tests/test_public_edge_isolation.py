from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_public_edge_has_dedicated_network_without_internal_apps():
 text=(ROOT/"compose.https.yaml").read_text()
 edge=text.split("  edge:",1)[1].split("\n  customer-web:",1)[0]
 assert "    networks:\n      - public_edge" in edge
 assert "      - default" not in edge
 assert "  admin-web:" not in text and "  warehouse-web:" not in text
 assert "  public_edge:" in text

def test_internal_hosts_remain_unrouted_at_public_edge():
 text=(ROOT/"deploy/Caddyfile").read_text()
 assert "reverse_proxy admin-web" not in text
 assert "reverse_proxy warehouse-web" not in text
 for domain in ("ADMIN","WAREHOUSE"):
  block=text.split("{$LFM_"+domain+"_DOMAIN} {",1)[1].split("\n}",1)[0]
  assert 'respond "Internal portal access is not activated" 403' in block
