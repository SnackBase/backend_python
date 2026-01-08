from sqlmodel import Session, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound


from app.auth.service import keycloak_admin
from app.auth.models.user import UserFull
from app.data.models.user import User


def get_users_data() -> list[UserFull]:
    # First get the group
    groups: list[dict] = keycloak_admin.get_groups({"search": "customer"})
    if not groups or len(groups) < 1:
        return []
    group_id = groups[0].get("id", None)
    if group_id is None:
        return []

    # Get all members of the group
    users = keycloak_admin.get_group_members(group_id=group_id)

    return [UserFull(**u) for u in users]


def get_user_from_db(user: UserFull, session: Session) -> User | None:
    statement = select(User).where(User.sub == user.sub)
    try:
        return session.exec(statement).one()
    except MultipleResultsFound as e:
        raise ValueError(
            f"Multiple users found in database with sub: {user.sub} - Error: {e}"
        )
    except NoResultFound:
        # raise ValueError(f"No user found in database with sub: {user.sub} - Error: {e}")
        return None


def add_user_to_db(user: User, session: Session) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
