"""K4mi SSO tokens and the admin tier.

K4mi grants document access through the Django groups named in the token's
`groups` claim. A Gnos3 admin in no group used to get an empty claim and saw
no document in K4mi; the token now also names every group granting
k4mi.documents.admin. Also checks that the Groups page's defaults read is open
to admins while the defaults save stays superadmin-only.

No app import: routers are checked from their source (importing them opens
the database).
"""

import ast
from pathlib import Path
from types import SimpleNamespace

from open_webui.utils.k4mi_groups import grants_k4mi_documents_admin, k4mi_token_group_names

ROUTERS = Path(__file__).resolve().parents[2] / 'routers'


def group(name, k4mi_admin=None, **extra):
    permissions = dict(extra)
    if k4mi_admin is not None:
        permissions['k4mi'] = {'documents': {'read': True, 'write': True, 'admin': k4mi_admin}}
    return SimpleNamespace(name=name, permissions=permissions)


ADMINS = group('Admins', k4mi_admin=True)
VIEWERS = group('Viewers', k4mi_admin=False)
ACCOUNTANTS = group('Accountants')
ALL = [ADMINS, VIEWERS, ACCOUNTANTS]


def test_grants_k4mi_documents_admin():
    assert grants_k4mi_documents_admin(ADMINS.permissions)
    assert not grants_k4mi_documents_admin(VIEWERS.permissions)
    assert not grants_k4mi_documents_admin(ACCOUNTANTS.permissions)
    assert not grants_k4mi_documents_admin(None)
    assert not grants_k4mi_documents_admin({'k4mi': True})
    assert not grants_k4mi_documents_admin({'k4mi': {'documents': 'admin'}})


def test_admin_in_no_group_gets_the_k4mi_admin_groups():
    assert k4mi_token_group_names('admin', [], ALL) == ['Admins']


def test_superadmin_too():
    assert k4mi_token_group_names('superadmin', [], ALL) == ['Admins']


def test_admin_keeps_own_groups_without_duplicates():
    assert k4mi_token_group_names('admin', [VIEWERS, ADMINS], ALL) == ['Viewers', 'Admins']


def test_follows_the_permission_not_the_name():
    renamed = group('Direction', k4mi_admin=True)
    assert k4mi_token_group_names('admin', [], [renamed, VIEWERS]) == ['Direction']


def test_user_gets_only_own_groups():
    assert k4mi_token_group_names('user', [VIEWERS], ALL) == ['Viewers']
    assert k4mi_token_group_names('user', [], ALL) == []


def test_no_group_grants_k4mi_admin():
    assert k4mi_token_group_names('admin', [], [VIEWERS, ACCOUNTANTS]) == []


def test_unnamed_groups_are_skipped():
    assert k4mi_token_group_names('admin', [group('')], [group('', k4mi_admin=True)]) == []


def _route_gate(source: Path, method: str, path: str) -> str:
    """Name of the dependency the endpoint's `user` parameter is gated by."""
    tree = ast.parse(source.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for dec in node.decorator_list:
            if (
                isinstance(dec, ast.Call)
                and isinstance(dec.func, ast.Attribute)
                and dec.func.attr == method
                and dec.args
                and isinstance(dec.args[0], ast.Constant)
                and dec.args[0].value == path
            ):
                args = node.args.args + node.args.kwonlyargs
                defaults = dict(zip([a.arg for a in args][-len(node.args.defaults) :], node.args.defaults))
                defaults.update({a.arg: d for a, d in zip(node.args.kwonlyargs, node.args.kw_defaults) if d})
                dep = defaults['user']
                return dep.args[0].id
    raise AssertionError(f'{method.upper()} {path} not found in {source.name}')


def _calls(source: Path, function: str) -> set[str]:
    tree = ast.parse(source.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == function:
            return {
                n.func.id
                for n in ast.walk(node)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            }
    raise AssertionError(f'{function} not found in {source.name}')


def test_default_permissions_read_by_admins_saved_by_superadmin_only():
    users = ROUTERS / 'users.py'
    assert _route_gate(users, 'get', '/default/permissions') == 'get_admin_or_above_user'
    assert _route_gate(users, 'post', '/default/permissions') == 'get_admin_user'


def test_both_k4mi_endpoints_build_groups_with_the_admin_rule():
    auths = ROUTERS / 'auths.py'
    for endpoint in ('k4mi_exchange_token', 'k4mi_open'):
        assert '_k4mi_token_groups' in _calls(auths, endpoint), endpoint
