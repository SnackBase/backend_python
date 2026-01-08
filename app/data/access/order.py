from sqlmodel import Session
from app.data.models.order import Order


def create_order_data(order: Order, session: Session) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
