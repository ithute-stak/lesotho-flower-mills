"""Connection-pinned HTTPS JWKS transport.

Resolve public IPs, connect directly to one selected address, retain hostname
as TLS SNI and verify the certificate against the original trusted hostname.
"""
import http.client
import ipaddress
import json
import socket
import ssl
from urllib.parse import urlsplit
from .ithute_jwks_cache import validate_public_dns

class _PinnedHTTPSConnection(http.client.HTTPSConnection):
 def __init__(self, hostname, pinned_ip, timeout=5):
  super().__init__(hostname,port=443,timeout=timeout,context=ssl.create_default_context())
  self.pinned_ip=pinned_ip

 def connect(self):
  raw=socket.create_connection((self.pinned_ip,443),self.timeout)
  try:
   self.sock=self._context.wrap_socket(raw,server_hostname=self.host)
  except BaseException:
   raw.close()
   raise

def fetch_pinned_jwks(url:str,*,resolver=None,connection_factory=None):
 parsed=urlsplit(url)
 if parsed.scheme!="https" or not parsed.hostname or parsed.port not in (None,443) or parsed.username or parsed.password or parsed.fragment or parsed.query:
  raise ValueError("Untrusted JWKS endpoint")
 addresses=validate_public_dns(parsed.hostname,resolver=resolver)
 address=addresses[0]
 if not ipaddress.ip_address(address).is_global:
  raise ValueError("Unsafe JWKS destination")
 conn=(connection_factory or _PinnedHTTPSConnection)(parsed.hostname,address)
 try:
  conn.request("GET",parsed.path or "/",headers={"Accept":"application/json","Host":parsed.hostname})
  response=conn.getresponse()
  if response.status!=200 or response.getheader("Content-Type","").split(";")[0].strip().lower()!="application/json":
   raise ValueError("Untrusted JWKS response")
  length=response.getheader("Content-Length")
  if length is not None and int(length)>65536:
   raise ValueError("Oversized JWKS")
  body=response.read(65537)
  if len(body)>65536:
   raise ValueError("Oversized JWKS")
  value=json.loads(body)
  if not isinstance(value,dict) or not isinstance(value.get("keys"),list):
   raise ValueError("Invalid JWKS document")
  return value
 finally:
  conn.close()
