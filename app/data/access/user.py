from app.auth.service import keycloak_admin

from app.data.models.user import User


async def get_users_data() -> list[User]:
    users: list[dict] = keycloak_admin.get_users({})
    return [User(**u) for u in users]
