from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import Session

from app.auth.service import AuthorizedAdminDep
from app.data.connector import SessionDep
from app.data.controller.order import (
    create_order,
    get_orders,
    get_user_orders,
    get_order_by_id,
)
from app.data.controller.user import UserDBDep
from app.data.models.order import OrderCreate, OrderPublic
from app.data.models.user import User


def _order_not_found_exception(id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No order found with given id {id}",
    )


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


@router.get("")
def get_orders_endpoint(
    include_deleted: bool = False, *, session: SessionDep, _: AuthorizedAdminDep
) -> list[OrderPublic]:
    return get_orders(include_deleted=include_deleted, session=session)


@router.get("/me")
def get_user_orders_endpoint(user: UserDBDep) -> list[OrderPublic]:
    return get_user_orders(user=user)


def _get_order_by_id(
    id: int, user: User, session: Session, admin_access: bool = False
) -> OrderPublic:
    try:
        order = get_order_by_id(
            id=id, user=user, session=session, admin_access=admin_access
        )
    except KeyError:
        raise _order_not_found_exception(id=id)
    if order is None:
        raise _order_not_found_exception(id=id)
    return order


@router.get("/{id}")
def get_order_by_id_endpoint(
    id: int, *, user: UserDBDep, session: SessionDep
) -> OrderPublic:
    return _get_order_by_id(id=id, user=user, session=session, admin_access=False)


@router.get("/admin/{id}")
def get_order_by_id_admin_endpoint(
    id: int, *, user: UserDBDep, _: AuthorizedAdminDep, session: SessionDep
) -> OrderPublic:
    return _get_order_by_id(id=id, user=user, session=session, admin_access=True)
