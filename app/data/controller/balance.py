from sqlmodel import Session
from app.data.access.balance import get_expenses_by_user_data, get_payments_by_user_data
from app.data.models.user import User


def get_balance_by_user(user: User, session: Session) -> float:
    payment_total = get_payments_by_user_data(user=user, session=session)
    expenses_total = get_expenses_by_user_data(user=user, session=session)
    return payment_total - expenses_total
