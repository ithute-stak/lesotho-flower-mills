from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_edge_requires_domains_and_uses_tls_ports():
 compose=(ROOT/"compose.https.yaml").read_text()
 caddy=(ROOT/"deploy/Caddyfile").read_text()
 assert '"80:80"' in compose and '"443:443"' in compose
 for name in ("CUSTOMER","ADMIN","WAREHOUSE","DRIVER"):
  assert "LFM_"+name+"_DOMAIN" in compose
  assert "{$LFM_"+name+"_DOMAIN}" in caddy
 assert "reverse_proxy customer-web:3000" in caddy
 assert "reverse_proxy admin-web:3001" in caddy
 assert "reverse_proxy warehouse-web:3002" in caddy
 assert "reverse_proxy driver-web:3003" in caddy

def test_api_health_check_remains_internal():
 production=(ROOT/"compose.production.yaml").read_text()
 assert "127.0.0.1:8000/health" in production
 assert "LFM_ENV: production" in production

def test_internal_portals_have_default_network_denial():
 caddy=(ROOT/"deploy/Caddyfile").read_text()
 for domain,matcher in (("ADMIN","outside_admin"),("WAREHOUSE","outside_warehouse")):
  block=caddy.split("{$LFM_"+domain+"_DOMAIN} {",1)[1].split("\n}",1)[0]
  assert "@"+matcher+" not remote_ip private_ranges" in block
  assert 'respond @'+matcher+' "Internal portal requires private network access" 403' in block
