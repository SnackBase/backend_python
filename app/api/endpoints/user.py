from fastapi import APIRouter, HTTPException, Path, status

from app.api.interface.tags import Tags
from app.auth.service import AuthorizedAdminDep, AuthorizedDep, AuthorizedKioskDep
from app.data.connector import SessionDep
from app.data.controller.user import get_users, get_user_from_authserver_by_id
from app.auth.models.user import UserDetailView, UserPublic


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
async def get_me(user: AuthorizedDep) -> UserDetailView:
    return UserDetailView.model_validate(user)


@admin_router.get("/{id}")
def get_user_from_authserver_by_id_endpoint(
    id: int = Path(gt=0), *, session: SessionDep, _: AuthorizedAdminDep
) -> UserDetailView:
    user = get_user_from_authserver_by_id(id=id, session=session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with given id {id}",
        )
    return user


router.include_router(general_router)
router.include_router(admin_router)
