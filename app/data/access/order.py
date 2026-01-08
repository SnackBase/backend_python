from sqlmodel import Session
from app.data.models.order import Order
from app.data.models.user import User


def create_order_data(order: Order, session: Session) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def get_user_orders_data(user: User) -> list[Order] | None:
    return user.orders


def get_order_by_id_data(id: int, session: Session) -> Order | None:
    return session.get(Order, id)
