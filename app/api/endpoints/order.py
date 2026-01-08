from fastapi import APIRouter, HTTPException, status

from app.data.connector import SessionDep
from app.data.controller.order import create_order
from app.data.controller.user import UserDBDep
from app.data.models.order import OrderCreate, OrderPublic


# TODO: regroup tags as enum for all routers
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("")
def create_new_order_endpoint(
    order: OrderCreate, *, user: UserDBDep, session: SessionDep
) -> OrderPublic:
    try:
        return create_order(order=order, user=user, session=session)
    except ValueError as e:
        # TODO: change status code
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
