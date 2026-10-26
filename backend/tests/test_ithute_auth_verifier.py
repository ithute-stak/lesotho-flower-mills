from datetime import datetime,timedelta,timezone
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from app.ithute_auth_verifier import IthuteAuthTrust,verify_ithute_token

@pytest.fixture
def keys():
 private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
 public=private.public_key().public_bytes(
  serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
 return private,public

def token(private,**changes):
 now=datetime.now(timezone.utc)
 claims={"iss":"https://auth.ithute.example","aud":"lfm-staff","sub":"staff-123",
         "iat":now,"nbf":now,"exp":now+timedelta(minutes=5)}
 claims.update(changes)
 return jwt.encode(claims,private,algorithm="RS256")

def test_valid_signed_issuer_and_audience(keys):
 private,public=keys
 trust=IthuteAuthTrust("https://auth.ithute.example","lfm-staff",public)
 assert verify_ithute_token(token(private),trust)["sub"]=="staff-123"

@pytest.mark.parametrize("change",[
 {"iss":"https://attacker.example"},{"aud":"wrong-audience"},
 {"exp":datetime(2020,1,1,tzinfo=timezone.utc)},{"sub":""},
 {"iat":datetime.now(timezone.utc)+timedelta(minutes=10)},
])
def test_rejects_invalid_claims(keys,change):
 private,public=keys
 trust=IthuteAuthTrust("https://auth.ithute.example","lfm-staff",public)
 with pytest.raises(ValueError):
  verify_ithute_token(token(private,**change),trust)

def test_rejects_wrong_signing_key(keys):
 private,public=keys
 different=rsa.generate_private_key(public_exponent=65537,key_size=2048)
 with pytest.raises(ValueError):
  verify_ithute_token(token(different),IthuteAuthTrust("https://auth.ithute.example","lfm-staff",public))

def test_rejects_hs256_algorithm_confusion(keys):
 _,public=keys
 unsafe=jwt.encode({"sub":"staff-123"},"attacker-secret",algorithm="HS256")
 with pytest.raises(ValueError):
  verify_ithute_token(unsafe,IthuteAuthTrust("https://auth.ithute.example","lfm-staff",public))
