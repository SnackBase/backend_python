from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.auth.service import AuthenticatedUserDep
from app.data.access.user import (
    add_user_to_db,
    get_user_data_from_authserver_by_sub,
    get_user_from_db_by_sub,
    get_user_from_db_by_numeric_id,
    get_users_data,
)
from app.auth.models.user import UserFull, UserPublic, UserWithEmail
from app.data.connector import SessionDep
from app.data.models.user import User, UserDetailView


def get_users() -> list[UserPublic]:
    users = get_users_data()
    return [UserPublic.model_validate(u) for u in users]


def convert_auth_server_user_to_detail_view(
    user_auth_server: UserFull | UserWithEmail, user_db: User
) -> UserDetailView:
    return UserDetailView(**(user_db.model_dump() | user_auth_server.model_dump()))


def get_users_detail_view(session: Session) -> list[UserDetailView]:
    users_auth_server = get_users_data()
    users: list[UserDetailView] = []
    for user_auth_server in users_auth_server:
        user_db = check_if_user_in_db(user=user_auth_server, session=session)
        if user_auth_server is None:
            continue
        users.append(
            convert_auth_server_user_to_detail_view(
                user_auth_server=user_auth_server, user_db=user_db
            )
        )
    return users


def get_user_details_by_id(id: int, session: Session) -> UserDetailView | None:
    user_db = get_user_from_db_by_numeric_id(id=id, session=session)
    if user_db is None:
        return None
    user_auth_server = get_user_data_from_authserver_by_sub(sub=user_db.sub)
    return convert_auth_server_user_to_detail_view(
        user_auth_server=user_auth_server, user_db=user_db
    )


def check_if_user_in_db(user: AuthenticatedUserDep, session: SessionDep) -> User:
    try:
        user_db = get_user_from_db_by_sub(user_sub=user.sub, session=session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    if user_db is None:
        user_db = User(
            id=None, sub=user.sub, age_restrict=False
        )  # age_restrict defaults to False, has to be changed via another function
        user_db = add_user_to_db(user=user_db, session=session)
    return user_db


UserDBDep = Annotated[User, Depends(check_if_user_in_db)]


def get_me(user_auth_server: UserFull, session: Session) -> UserDetailView:
    user_db = check_if_user_in_db(user=user_auth_server, session=session)
    return convert_auth_server_user_to_detail_view(
        user_auth_server=user_auth_server, user_db=user_db
    )
