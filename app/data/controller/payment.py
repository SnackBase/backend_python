from datetime import UTC, datetime
from sqlmodel import Session
from app.auth.models.user import UserPublic
from app.data.access.payment import (
    get_payment_by_id_data,
    upsert_payment_data,
    get_all_payments_admin_data,
)
from app.data.access.user import get_user_data_from_authserver_by_id
from app.data.models.payment import Payment, PaymentCreate, PaymentPublic
from app.data.models.user import User


def convert_to_public(payment: Payment, user: UserPublic) -> PaymentPublic:
    return PaymentPublic(**(payment.model_dump() | {"user": user}))


def convert_one_to_public(payment: Payment) -> PaymentPublic:
    public_user = get_user_data_from_authserver_by_id(id=payment.user.sub)
    return convert_to_public(payment=payment, user=public_user)


def convert_many_to_public(payments: list[Payment]):
    user_set = set(x.user.sub for x in payments)
    user_dict = {sub: get_user_data_from_authserver_by_id(id=sub) for sub in user_set}
    return [convert_to_public(payment=p, user=user_dict[p.user.sub]) for p in payments]


def create_payment(
    payment: PaymentCreate, user: User, session: Session
) -> PaymentPublic:
    assert user.id is not None
    payment_db = Payment(
        id=None,
        user_id=user.id,
        amount=payment.amount,
        processed_at=None,
        confirmed=False,
        note=None,
        user=user,
    )

    payment_db = upsert_payment_data(payment=payment_db, session=session)

    return convert_one_to_public(payment=payment_db)


def get_all_payments_of_user(user: User) -> list[PaymentPublic]:
    if user.payments is None or len(user.payments) < 1:
        return []
    return sorted(
        convert_many_to_public(payments=user.payments),
        key=lambda x: x.created_at,
        reverse=True,
    )


def get_all_payments_admin(session: Session) -> list[PaymentPublic]:
    payments = get_all_payments_admin_data(session=session)
    return convert_many_to_public(payments=payments)


def update_payment_by_id(
    id: int, confirmed: bool, note: str | None, session: Session
) -> PaymentPublic:
    payment = get_payment_by_id_data(id=id, session=session)
    if payment is None:
        raise KeyError
    if payment.processed_at is not None:
        raise ValueError
    payment.confirmed = confirmed
    payment.note = note
    payment.processed_at = datetime.now(tz=UTC)
    payment = upsert_payment_data(payment=payment, session=session)
    return convert_one_to_public(payment=payment)
