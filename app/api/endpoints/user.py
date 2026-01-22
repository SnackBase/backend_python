from fastapi import APIRouter, HTTPException, Path, status

from app.api.interface.tags import Tags
from app.auth.service import AuthorizedAdminDep, AuthorizedDep, AuthorizedKioskDep
from app.data.connector import SessionDep
from app.data.controller.user import (
    get_me,
    get_users,
    get_user_details_by_id,
    get_users_detail_view,
)
from app.auth.models.user import UserPublic
from app.data.models.user import UserDetailView


router = APIRouter(tags=[Tags.USERS])
general_router = APIRouter(prefix=f"/{Tags.USERS.value.lower()}")
admin_router = APIRouter(
    prefix=f"/{Tags.ADMIN.value.lower()}/{Tags.USERS.value.lower()}", tags=[Tags.ADMIN]
)


@general_router.get("")
async def get_users_endpoint(
    *, _: AuthorizedKioskDep
) -> list[UserPublic]:  # ? Necessary Scopes might be changes in a future revision
    return get_users()


@general_router.get("/me")
async def get_me_endpoint(user: AuthorizedDep, session: SessionDep) -> UserDetailView:
    return get_me(user_auth_server=user, session=session)


@admin_router.get("/{id}")
def get_user_detail_view_by_id_endpoint(
    id: int = Path(gt=0), *, session: SessionDep, _: AuthorizedAdminDep
) -> UserDetailView:
    user = get_user_details_by_id(id=id, session=session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with given id {id}",
        )
    return user


@admin_router.get("")
def get_users_detail_view_endpoint(
    session: SessionDep, _: AuthorizedAdminDep
) -> list[UserDetailView]:
    return get_users_detail_view(session=session)


router.include_router(general_router)
router.include_router(admin_router)
