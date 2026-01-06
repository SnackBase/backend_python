from app.data.access.user import get_users_data
from app.auth.models.user import UserPublic


def get_users() -> UserPublic:
    users = get_users_data()
    return [UserPublic.model_validate(u) for u in users]
