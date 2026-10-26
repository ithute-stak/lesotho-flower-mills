import json
import socket
import pytest
from app.ithute_pinned_https import fetch_pinned_jwks

def resolver(ips):
 return lambda host,port,**kw:[(socket.AF_INET,socket.SOCK_STREAM,6,"",(ip,port)) for ip in ips]

class FakeResponse:
 status=200
 def getheader(self,name,default=""):
  return "application/json" if name=="Content-Type" else default
 def read(self,n):
  return json.dumps({"keys":[{"kid":"test"}]}).encode()
class FakeConnection:
 def __init__(self,host,ip):
  self.host=host
  self.ip=ip
  self.headers=None
 def request(self,method,path,headers):
  self.headers=headers
 def getresponse(self):return FakeResponse()
 def close(self):pass

def test_pins_public_destination_but_preserves_original_hostname():
 captured=[]
 def factory(host,ip):
  captured.append((host,ip))
  return FakeConnection(host,ip)
 assert fetch_pinned_jwks("https://auth.example/jwks",resolver=resolver(["8.8.8.8"]),connection_factory=factory)["keys"][0]["kid"]=="test"
 assert captured==[("auth.example","8.8.8.8")]

@pytest.mark.parametrize("ips",[[],["127.0.0.1"],["8.8.8.8","10.10.10.10"],["169.254.169.254"]])
def test_blocks_unsafe_dns_before_connection(ips):
 with pytest.raises(ValueError):
  fetch_pinned_jwks("https://auth.example/jwks",resolver=resolver(ips),connection_factory=lambda *args:pytest.fail("unsafe connection"))

def test_rejects_redirect_or_other_bad_status():
 class Redirect(FakeResponse):
  status=302
 class Conn(FakeConnection):
  def getresponse(self):return Redirect()
 with pytest.raises(ValueError):
  fetch_pinned_jwks("https://auth.example/jwks",resolver=resolver(["8.8.8.8"]),connection_factory=Conn)
