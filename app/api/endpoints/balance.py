from fastapi import APIRouter

from app.api.interface.tags import Tags
from app.data.connector import SessionDep
from app.data.controller.balance import get_balance_by_user
from app.data.controller.user import UserDBDep


router = APIRouter(tags=[Tags.BALANCE], prefix=f"/{Tags.BALANCE}")


@router.get("")
def get_user_balance_endpoint(user: UserDBDep, *, session: SessionDep) -> float:
    return get_balance_by_user(user=user, session=session)
