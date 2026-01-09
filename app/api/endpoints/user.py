from fastapi import APIRouter

from app.api.interface.tags import Tags
from app.auth.service import AuthorizedDep, AuthorizedKioskDep
from app.data.controller.user import get_users
from app.auth.models.user import UserFull, UserPublic


router = APIRouter(prefix="/users", tags=[Tags.USERS])


@router.get("")
async def get_users_endpoint(
    *, _: AuthorizedKioskDep
) -> list[UserPublic]:  # ? Necessary Scopes might be changes in a future revision
    return get_users()


@router.get("/me")
async def get_me(user: AuthorizedDep) -> UserFull:
    return user
