from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.auth.service import AuthenticatedUserDep
from app.data.access.user import add_user_to_db, get_user_from_db, get_users_data
from app.auth.models.user import UserPublic
from app.data.connector import SessionDep
from app.data.models.user import User


def get_users() -> list[UserPublic]:
    users = get_users_data()
    return [UserPublic.model_validate(u) for u in users]


def check_if_user_in_db(user: AuthenticatedUserDep, session: SessionDep) -> User:
    try:
        user_db = get_user_from_db(user=user, session=session)
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
