from datetime import datetime,timedelta,timezone
import json
import jwt
import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from app.ithute_jwks_cache import TrustedJWKSCache
from app.ithute_token_service import IthuteTokenService

ISSUER="https://auth.ithute.example"
AUDIENCE="lfm-staff"
URL=ISSUER+"/jwks"

def fixture_key(kid):
 private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
 jwk=json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
 jwk.update({"kid":kid,"use":"sig","alg":"RS256"})
 return private,jwk

def sign(private,kid,audience=AUDIENCE):
 now=datetime.now(timezone.utc)
 return jwt.encode({"sub":"staff-1","iss":ISSUER,"aud":audience,"iat":now,"nbf":now,
                    "exp":now+timedelta(minutes=5)},private,algorithm="RS256",headers={"kid":kid})

def test_trusted_token_service_verifies_and_rejects_key_rotation():
 private,public=fixture_key("first")
 new_private,new_public=fixture_key("next")
 keys=[public]
 now=[0.]
 def serve(req):
  return httpx.Response(200,headers={"content-type":"application/json"},json={"keys":keys})
 with httpx.Client(transport=httpx.MockTransport(serve)) as client:
  cache=TrustedJWKSCache(URL,client=client,ttl_seconds=5,clock=lambda:now[0])
  service=IthuteTokenService(ISSUER,AUDIENCE,cache)
  assert service.verify(sign(private,"first"))["sub"]=="staff-1"
  with pytest.raises(ValueError):
   service.verify(sign(private,"first",audience="wrong"))
  keys[:]=[new_public]
  now[0]=6.
  assert service.verify(sign(new_private,"next"))["sub"]=="staff-1"
  with pytest.raises(ValueError):
   service.verify(sign(private,"first"))

def test_failed_jwks_refresh_rejects_token():
 private,jwk=fixture_key("first")
 now=[0.]
 calls=[0]
 def serve(req):
  calls[0]+=1
  if calls[0]>1:
   return httpx.Response(503)
  return httpx.Response(200,headers={"content-type":"application/json"},json={"keys":[jwk]})
 with httpx.Client(transport=httpx.MockTransport(serve)) as client:
  service=IthuteTokenService(ISSUER,AUDIENCE,
   TrustedJWKSCache(URL,client=client,ttl_seconds=2,clock=lambda:now[0]))
  assert service.verify(sign(private,"first"))["sub"]=="staff-1"
  now[0]=3.
  with pytest.raises(ValueError):
   service.verify(sign(private,"first"))
