from datetime import datetime,timedelta,timezone
import json
import pytest
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from app.ithute_jwks import JWKSConfig,verify_token_with_jwks

TRUST=JWKSConfig("https://auth.ithute.example","lfm-staff")

def keypair(kid):
 private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
 jwk=json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
 jwk.update({"kid":kid,"use":"sig","alg":"RS256"})
 return private,jwk

def signed(private,kid):
 now=datetime.now(timezone.utc)
 return jwt.encode({"sub":"staff-123","iss":TRUST.issuer,"aud":TRUST.audience,
                    "iat":now,"nbf":now,"exp":now+timedelta(minutes=5)},
                   private,algorithm="RS256",headers={"kid":kid})

def test_jwks_rotation_old_and_new_kids():
 old,old_jwk=keypair("old")
 new,new_jwk=keypair("new")
 rotated={"keys":[old_jwk,new_jwk]}
 assert verify_token_with_jwks(signed(old,"old"),rotated,TRUST)["sub"]=="staff-123"
 assert verify_token_with_jwks(signed(new,"new"),rotated,TRUST)["sub"]=="staff-123"
 with pytest.raises(ValueError):
  verify_token_with_jwks(signed(old,"old"),{"keys":[new_jwk]},TRUST)

def test_unknown_duplicate_wrong_signature_and_algorithm():
 good,jwk=keypair("key")
 other,_=keypair("other")
 valid=signed(good,"key")
 with pytest.raises(ValueError):
  verify_token_with_jwks(valid,{"keys":[]},TRUST)
 with pytest.raises(ValueError):
  verify_token_with_jwks(valid,{"keys":[jwk,jwk]},TRUST)
 with pytest.raises(ValueError):
  verify_token_with_jwks(signed(other,"key"),{"keys":[jwk]},TRUST)
 with pytest.raises(ValueError):
  verify_token_with_jwks(jwt.encode({"sub":"x"},"fake-secret",algorithm="HS256",headers={"kid":"key"}),{"keys":[jwk]},TRUST)
