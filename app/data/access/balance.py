from sqlmodel import Session, select, func
from app.data.models.order import Order, OrderItem
from app.data.models.payment import Payment
from app.data.models.product import Product
from app.data.models.user import User


def get_expenses_by_user_data(user: User, session: Session) -> float:
    assert user.id is not None
    statement = (
        select(OrderItem.count, Product.price)
        .where(Order.user_id == user.id)
        .where(Order.id == OrderItem.order_id)
        .where(OrderItem.product_id == Product.id)
    )
    result = session.exec(statement=statement).all()
    return sum(c * p for c, p in result)


def get_payments_by_user_data(
    user: User, session: Session, include_pending: bool = False
) -> float:
    assert user.id is not None
    statement = select(func.sum(Payment.amount)).where(Payment.user_id == user.id)
    if not include_pending:
        statement = statement.where(Payment.processed_at != None)  # noqa: E711
    result = session.exec(statement=statement).one()
    if result is None:
        return 0.0
    return result
