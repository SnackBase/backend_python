from app.auth.service import keycloak_admin

from app.auth.models.user import UserFull


def get_users_data() -> list[UserFull]:
    # First get the group
    groups: list[dict] = keycloak_admin.get_groups({"search": "customer"})
    if not groups or len(groups) < 1:
        return []
    group_id = groups[0].get("id", None)
    if group_id is None:
        return []

    # Get all members of the group
    users = keycloak_admin.get_group_members(group_id=group_id)

    return [UserFull(**u) for u in users]
