"""Conservative, read-only deployment readiness review."""
from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class DeploymentGate:
 code:str
 evidence:str

GATES=(
 DeploymentGate("production_compose_validated","Resolved three-file Docker Compose validation in clean CI"),
 DeploymentGate("health_checks_verified","FastAPI and four portals respond after restart"),
 DeploymentGate("tls_certificate_verified","Certificate chain and renewal verified for authorised domains"),
 DeploymentGate("internal_portal_access_restricted","VPN or identity-aware access to administration and warehouse"),
 DeploymentGate("secrets_rotation_verified","Secrets provisioning and emergency rotation demonstration"),
 DeploymentGate("backup_restore_verified","Restoration drill with consistent order and inventory state"),
 DeploymentGate("release_rollback_verified","Rollback drill against versioned images and schema policy"),
 DeploymentGate("independent_security_review","Signed independent security and operational approval"),
)

def deployment_readiness():
 return {"deployment_approved":False,"external_pilot_approved":False,
  "gates":[{**asdict(g),"status":"unverified","evidence_reference":None} for g in GATES]}
