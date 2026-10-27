"""Group names a K4mi exchange token carries (K4mi SSO bridge).

K4mi knows nothing about Gnos3 permissions. paperless.gnos_jwt_auth adds the
signed-in user to the Django group of the same name as each entry of the
token's ``groups`` claim (additive, never removed), and what a K4mi user can
see comes from those Django groups: their model permissions plus the
per-document grants K4mi workflows give each group. ``k4mi.documents.*`` on a
Gnos3 group therefore only reaches K4mi through that group's name.

A user's own groups are always sent. A Gnos3 ``admin`` (or ``superadmin``)
bypasses every per-module data check, but belongs to no group by default, so
K4mi gave them nothing to see. For them the token also carries every group
that grants ``k4mi.documents.admin``: in K4mi they join the groups a member
of the Gnos3 "Admins" group joins and see the same documents. They do not
become K4mi superusers; that, with K4mi's platform settings (mail, workflows,
application configuration), stays with the superadmin tier.

No imports from the app on purpose: the tests load this module on its own.
"""

from typing import Any, Iterable

# Same set as open_webui.utils.auth.ADMIN_TIER_ROLES.
ADMIN_TIER_ROLES = frozenset({'admin', 'superadmin'})


def grants_k4mi_documents_admin(permissions: Any) -> bool:
    """True when a group's permissions dict sets k4mi.documents.admin."""
    if not isinstance(permissions, dict):
        return False
    k4mi = permissions.get('k4mi')
    documents = k4mi.get('documents') if isinstance(k4mi, dict) else None
    return isinstance(documents, dict) and bool(documents.get('admin'))


def k4mi_token_group_names(
    role: str,
    member_groups: Iterable[Any],
    all_groups: Iterable[Any] = (),
) -> list[str]:
    """Names for the token's ``groups`` claim, in order, without duplicates.

    ``member_groups`` are the user's own groups; ``all_groups`` every group on
    the server (only read for admin-tier roles). Items need ``name`` and
    ``permissions`` attributes (GroupModel).
    """
    names = [g.name for g in member_groups if getattr(g, 'name', None)]
    if role in ADMIN_TIER_ROLES:
        names += [
            g.name
            for g in all_groups
            if getattr(g, 'name', None) and grants_k4mi_documents_admin(getattr(g, 'permissions', None))
        ]
    return list(dict.fromkeys(names))
