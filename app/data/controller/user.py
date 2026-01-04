from app.data.access.user import get_users_data
from app.data.models.user import UserPublic


async def get_users() -> UserPublic:
    users = await get_users_data()
    return [UserPublic.model_validate(u) for u in users]
