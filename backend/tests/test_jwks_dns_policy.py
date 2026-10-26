import socket
import pytest
from app.ithute_jwks_cache import TrustedJWKSCache,validate_public_dns

def fake_dns(addresses):
 return lambda host,port,**kw:[(socket.AF_INET,socket.SOCK_STREAM,6,"",(ip,port)) for ip in addresses]

def test_dns_all_global_addresses():
 assert validate_public_dns("auth.example",fake_dns(["8.8.8.8","1.1.1.1"]))==("1.1.1.1","8.8.8.8")

@pytest.mark.parametrize("addresses",[[],["127.0.0.1"],["10.0.0.1"],["8.8.8.8","192.168.1.2"],["169.254.169.254"]])
def test_dns_rejects_private_and_mixed_addresses(addresses):
 with pytest.raises(ValueError):
  validate_public_dns("auth.example",fake_dns(addresses))

def test_cache_uses_pinned_transport_when_no_http_client(monkeypatch):
 from app import ithute_pinned_https
 calls=[]
 def stub(url):
  calls.append(url)
  return {"keys":[{"kty":"RSA","kid":"ci-key","n":"AQAB","e":"AQAB"}]}
 monkeypatch.setattr(ithute_pinned_https,"fetch_pinned_jwks",stub)
 value=TrustedJWKSCache("https://auth.example/jwks").get()
 assert value["keys"][0]["kid"]=="ci-key"
 assert calls==["https://auth.example/jwks"]
