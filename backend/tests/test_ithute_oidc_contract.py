from app.ithute_oidc_contract import validate_oidc_discovery

ISSUER="https://auth.example.invalid"
VALID={
 "issuer":ISSUER,
 "authorization_endpoint":ISSUER+"/oauth/authorize",
 "token_endpoint":ISSUER+"/oauth/token",
 "jwks_uri":ISSUER+"/.well-known/jwks.json",
 "id_token_signing_alg_values_supported":["RS256"],
}

def test_valid_document():
 assert validate_oidc_discovery(VALID,ISSUER)==[]

def test_rejects_wrong_issuer_and_key_host():
 doc={**VALID,"issuer":"https://wrong.example.invalid",
      "jwks_uri":"https://evil.example.invalid/.well-known/jwks.json"}
 assert set(validate_oidc_discovery(doc,ISSUER))=={"issuer_mismatch","invalid_jwks_uri"}

def test_rejects_downgrade_and_missing_alg():
 doc={**VALID,"token_endpoint":"http://auth.example.invalid/oauth/token",
      "id_token_signing_alg_values_supported":[]}
 assert "invalid_token_endpoint" in validate_oidc_discovery(doc,ISSUER)
 assert "rs256_support_not_confirmed" in validate_oidc_discovery(doc,ISSUER)
