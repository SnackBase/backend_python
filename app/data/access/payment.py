from sqlmodel import Session, desc, select
from app.data.models.payment import Payment


def upsert_payment_data(payment: Payment, session: Session) -> Payment:
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


def get_all_payments_admin_data(session: Session) -> list[Payment]:
    statement = select(Payment).order_by(desc(Payment.created_at))
    return list(session.exec(statement=statement))


def get_payment_by_id_data(id: int, session: Session) -> Payment | None:
    return session.get(Payment, id)
