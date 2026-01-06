from app.auth.service import keycloak_admin

from app.data.models.user import User


async def get_users_data() -> list[User]:
    # First get the group
    groups: list[dict] = keycloak_admin.get_groups({"search": "customer"})
    if not groups or len(groups) < 1:
        return []
    group_id = groups[0].get("id", None)
    if group_id is None:
        return []

    # Get all members of the group
    users = keycloak_admin.get_group_members(group_id=group_id)

    return [User(**u) for u in users]
