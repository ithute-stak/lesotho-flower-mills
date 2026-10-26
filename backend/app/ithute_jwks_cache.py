"""Operator-pinned JWKS HTTPS retrieval with finite cache and fail-closed outages.

Never derive the URL from a JWT header or claims. Inject a tested HTTP client.
"""
import ipaddress
import socket
import time
from urllib.parse import urlsplit
import httpx

def validate_public_dns(hostname:str,resolver=None)->tuple[str,...]:
 # Preflight only: DNS may change before TLS connection.
 lookup=resolver or socket.getaddrinfo
 try:
  entries=lookup(hostname,443,type=socket.SOCK_STREAM)
  addresses=tuple(sorted({item[4][0] for item in entries}))
  if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
   raise ValueError("JWKS DNS contains non-global address")
  return addresses
 except (OSError,ValueError,TypeError,IndexError) as exc:
  raise ValueError("Unsafe JWKS DNS resolution") from exc

class TrustedJWKSCache:
 def __init__(self,url:str,*,ttl_seconds:int=300,client=None,clock=None):
  parsed=urlsplit(url)
  if (parsed.scheme!="https" or not parsed.hostname or parsed.username or
      parsed.password or parsed.fragment or parsed.query or parsed.port not in (None,443)):
   raise ValueError("Pinned HTTPS JWKS URL required")
  try:
   address=ipaddress.ip_address(parsed.hostname)
  except ValueError:
   address=None
  if address is not None and not address.is_global:
   raise ValueError("Nonpublic JWKS endpoint forbidden")
  if ttl_seconds<1 or ttl_seconds>900:
   raise ValueError("JWKS cache TTL must be 1–900 seconds")
  self.url=url
  self.ttl=ttl_seconds
  self.client=client
  self.clock=clock or time.monotonic
  self._keys=None
  self._expires=0.0

 def get(self):
  now=self.clock()
  if self._keys is not None and now<self._expires:
   return self._keys
  try:
   if self.client is None:
    # Unpinned DNS-to-TLS connections are forbidden pending audited transport.
    raise ValueError("Production JWKS transport not approved")
   response=self.client.get(self.url)
   if response.status_code!=200 or len(response.content)>65536:
    raise ValueError("JWKS fetch rejected")
   if response.headers.get("content-type","").split(";")[0].strip().lower()!="application/json":
    raise ValueError("Unexpected JWKS content type")
   data=response.json()
   if not isinstance(data,dict) or not isinstance(data.get("keys"),list) or not 1<=len(data["keys"])<=20:
    raise ValueError("Invalid JWKS keys")
   if not all(isinstance(k,dict) and k.get("kty")=="RSA" and isinstance(k.get("kid"),str)
              and k["kid"] and "n" in k and "e" in k for k in data["keys"]):
    raise ValueError("Invalid RSA signing key")
   if len({k["kid"] for k in data["keys"]})!=len(data["keys"]):
    raise ValueError("Duplicate key identifier")
  except (httpx.HTTPError,ValueError,TypeError,KeyError) as exc:
   self._keys=None
   self._expires=0.0
   raise ValueError("Trusted JWKS retrieval failed") from exc
  self._keys=data
  self._expires=self.clock()+self.ttl
  return data
