from unittest.mock import Mock
from uuid import uuid4
import pytest
from fastapi import HTTPException
from app.staff_link_admin import verify_link

def test_review_rejects_unattested_subject():
 db=Mock()
 db.execute.return_value.mappings.return_value.first.return_value={
 "requested_by":"maker","active":False,"revoked_at":None,
 "local_user_id":uuid4(),"issuer":"https://auth.example.invalid",
 "central_subject":"central-subject","attested_issuer":None,
 "attested_subject":None,"attested_at":None,"attestation_reference":None}
 with pytest.raises(HTTPException) as exc:
  verify_link(uuid4(),{"sub":"different-admin"},db)
 assert exc.value.status_code==409
 db.commit.assert_not_called()

def test_review_rejects_mismatched_subject_attestation():
 from datetime import datetime,timezone
 db=Mock()
 db.execute.return_value.mappings.return_value.first.return_value={
 "requested_by":"maker","active":False,"revoked_at":None,
 "local_user_id":uuid4(),"issuer":"https://auth.example.invalid",
 "central_subject":"correct-subject","attested_issuer":"https://auth.example.invalid",
 "attested_subject":"other-subject","attested_at":datetime.now(timezone.utc),
 "attestation_reference":"test-only"}
 with pytest.raises(HTTPException) as exc:
  verify_link(uuid4(),{"sub":"different-admin"},db)
 assert exc.value.status_code==409
