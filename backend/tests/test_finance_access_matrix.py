"""Contract tests: every declared sensitive route retains finance dependency."""
import importlib
import inspect
from fastapi.params import Depends
from app import finance_permissions
from app.finance_access_matrix import FINANCE_ROUTES

def test_finance_matrix_has_no_duplicate_routes():
 pairs=[(entry.module,entry.function) for entry in FINANCE_ROUTES]
 assert len(pairs)==len(set(pairs))
 assert len(pairs)>=20

def test_financial_routes_have_exact_declared_dependency():
 for entry in FINANCE_ROUTES:
  module=importlib.import_module("app."+entry.module)
  handler=getattr(module,entry.function)
  params=inspect.signature(handler).parameters
  assert "identity" in params, entry
  dependency=params["identity"].default
  assert isinstance(dependency,Depends),entry
  assert dependency.dependency is getattr(finance_permissions,entry.permission),entry

def test_finance_role_hierarchy_is_explicit():
 assert finance_permissions.finance_read is not finance_permissions.finance_review
 assert finance_permissions.finance_review is not finance_permissions.finance_admin
