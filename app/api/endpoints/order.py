from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, status
from sqlmodel import Session

from app.api.interface.tags import Tags
from app.auth.service import AuthorizedAdminDep
from app.data.connector import SessionDep
from app.data.controller.order import (
    create_order,
    delete_order_by_id,
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


DBID = Annotated[int, Path(gt=0)]


router = APIRouter(tags=[Tags.ORDERS])
consumer_router = APIRouter(
    prefix=f"/{Tags.ORDERS.value.lower()}", tags=[Tags.CONSUMERS]
)
admin_router = APIRouter(
    prefix=f"/{Tags.ADMIN.value.lower()}/{Tags.ORDERS.value.lower()}", tags=[Tags.ADMIN]
)


@consumer_router.post("")
def create_new_order_endpoint(
    order: OrderCreate, *, user: UserDBDep, session: SessionDep
) -> OrderPublic:
    try:
        return create_order(order=order, user=user, session=session)
    except ValueError as e:
        # TODO: change status code
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@consumer_router.get("")
def get_user_orders_endpoint(user: UserDBDep, session: SessionDep) -> list[OrderPublic]:
    return get_user_orders(user=user, session=session)


def _get_order_by_id(
    id: DBID, user: User | None, session: Session, admin_access: bool = False
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


@consumer_router.get("/{id}")
def get_order_by_id_endpoint(
    id: DBID, *, user: UserDBDep, session: SessionDep
) -> OrderPublic:
    return _get_order_by_id(id=id, user=user, session=session, admin_access=False)


@admin_router.get("")
def get_orders_admin_endpoint(
    include_deleted: bool = False, *, session: SessionDep, _: AuthorizedAdminDep
) -> list[OrderPublic]:
    return get_orders(include_deleted=include_deleted, session=session)


@admin_router.get("/{id}")
def get_order_by_id_admin_endpoint(
    id: DBID, *, _: AuthorizedAdminDep, session: SessionDep
) -> OrderPublic:
    return _get_order_by_id(id=id, user=None, session=session, admin_access=True)


@admin_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_by_id_admin_endpoint(
    id: DBID, *, _: AuthorizedAdminDep, session: SessionDep
) -> None:
    try:
        delete_order_by_id(id=id, session=session)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No order found with given id {id}",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED, detail="Order already deleted"
        )


router.include_router(admin_router)
router.include_router(consumer_router)
