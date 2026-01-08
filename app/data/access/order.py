from sqlmodel import Session
from app.data.models.order import Order
from app.data.models.user import User


def create_order_data(order: Order, session: Session) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def get_my_orders_data(user: User) -> list[Order] | None:
    return user.orders
