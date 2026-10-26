import json
import httpx
import pytest
from app.ithute_jwks_cache import TrustedJWKSCache

URL="https://auth.ithute.example/.well-known/jwks.json"
KEY={"kty":"RSA","kid":"v1","n":"AQAB","e":"AQAB"}

def client(handler):
 return httpx.Client(transport=httpx.MockTransport(handler),follow_redirects=False)

def response(keys=None,status=200):
 return httpx.Response(status,headers={"content-type":"application/json"},content=json.dumps({"keys":keys if keys is not None else [KEY]}).encode())

def test_cache_reuses_keys_and_rotates_after_expiry():
 now=[0.]
 calls=[]
 def handler(request):
  calls.append(1)
  return response([{**KEY,"kid":"v"+str(len(calls))}])
 with client(handler) as http:
  cache=TrustedJWKSCache(URL,ttl_seconds=10,client=http,clock=lambda:now[0])
  assert cache.get()["keys"][0]["kid"]=="v1"
  assert cache.get()["keys"][0]["kid"]=="v1"
  assert len(calls)==1
  now[0]=11.
  assert cache.get()["keys"][0]["kid"]=="v2"

def test_outage_expires_old_keys_and_denies():
 now=[0.]
 calls=[0]
 def handler(request):
  calls[0]+=1
  return response() if calls[0]==1 else httpx.Response(503)
 with client(handler) as http:
  cache=TrustedJWKSCache(URL,ttl_seconds=2,client=http,clock=lambda:now[0])
  cache.get()
  now[0]=3.
  with pytest.raises(ValueError):
   cache.get()
  with pytest.raises(ValueError):
   cache.get()

@pytest.mark.parametrize("url",["http://auth.example/jwks","https://127.0.0.1/jwks","https://user:pass@auth.example/jwks","https://auth.example:8080/jwks","https://auth.example/jwks?token=bad"])
def test_rejects_untrusted_urls(url):
 with pytest.raises(ValueError):
  TrustedJWKSCache(url)

def test_rejects_redirect_and_duplicate_keys():
 with client(lambda req:httpx.Response(302,headers={"location":"https://attacker.example"})) as http:
  with pytest.raises(ValueError):
   TrustedJWKSCache(URL,client=http).get()
 with client(lambda req:response([KEY,KEY])) as http:
  with pytest.raises(ValueError):
   TrustedJWKSCache(URL,client=http).get()
