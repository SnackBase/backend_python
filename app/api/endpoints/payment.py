from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, status
from sqlmodel import Session

from app.api.interface.tags import Tags
from app.auth.service import AuthorizedAdminDep, AuthorizedCustomerDep
from app.data.connector import SessionDep
from app.data.controller.payment import (
    create_payment,
    get_all_payments_admin,
    get_all_payments_of_user,
    update_payment_by_id,
)
from app.data.controller.user import UserDBDep
from app.data.models.payment import PaymentCreate, PaymentPublic, PaymentUpdate


router = APIRouter(tags=[Tags.PAYMENTS])
consumer_router = APIRouter(prefix=f"/{Tags.PAYMENTS.value.lower()}")
admin_router = APIRouter(
    prefix=f"/{Tags.ADMIN.value.lower()}/{Tags.PAYMENTS.value.lower()}",
    tags=[Tags.ADMIN],
)


@consumer_router.post("")
def create_payment_endpoint(
    payment: PaymentCreate,
    *,
    user: UserDBDep,
    session: SessionDep,
    _: AuthorizedCustomerDep,
) -> PaymentPublic:
    return create_payment(payment=payment, user=user, session=session)


@consumer_router.get("")
def get_all_payments_of_user_endpoint(user: UserDBDep) -> list[PaymentPublic]:
    return get_all_payments_of_user(user=user)


@admin_router.get("")
def get_all_payments_admin_endpoint(
    session: SessionDep, _: AuthorizedAdminDep
) -> list[PaymentPublic]:
    return get_all_payments_admin(session=session)


def _update_payment_by_id_util(
    id: int, confirmed: bool, note: str | None, session: Session
) -> PaymentPublic:
    try:
        payment = update_payment_by_id(
            id=id, confirmed=confirmed, note=note, session=session
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payment found for given id {id}",
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    return payment


@admin_router.put("/{id}/confirm")
def confirm_payment_admin_endpoint(
    id: Annotated[int, Path(gt=0)],
    payment_data: PaymentUpdate,
    *,
    session: SessionDep,
    _: AuthorizedAdminDep,
) -> PaymentPublic:
    return _update_payment_by_id_util(
        id=id, confirmed=True, note=payment_data.note, session=session
    )


@admin_router.put("/{id}/decline")
def decline_payment_admin_endpoint(
    id: Annotated[int, Path(gt=0)],
    payment_data: PaymentUpdate,
    *,
    session: SessionDep,
    _: AuthorizedAdminDep,
) -> PaymentPublic:
    return _update_payment_by_id_util(
        id=id, confirmed=False, note=payment_data.note, session=session
    )


router.include_router(consumer_router)
router.include_router(admin_router)
