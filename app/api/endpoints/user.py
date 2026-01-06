from fastapi import APIRouter

from app.auth.service import AuthorizedDep, AuthorizedKioskDep
from app.data.controller.user import get_users
from app.data.models.user import UserFull, UserPublic


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_users_endpoint(
    *, _: AuthorizedKioskDep
) -> list[UserPublic]:  # ? Necessary Scopes might be changes in a future revision
    return await get_users()


@router.get("/me")
async def get_me(user: AuthorizedDep) -> UserFull:
    return user
