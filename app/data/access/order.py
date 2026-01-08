from sqlmodel import Session, select
from app.data.models.order import Order
from app.data.models.user import User


def create_order_data(order: Order, session: Session) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def get_orders_data(include_deleted: bool = False, *, session: Session) -> list[Order]:
    statement = select(Order)
    if not include_deleted:
        statement = statement.where(Order.deleted_at == None)  # noqa: E711  # noqa necessary for the condition handling via sqlmodel
    return list(session.exec(statement=statement).all())


def get_user_orders_data(user: User) -> list[Order] | None:
    return user.orders


def get_order_by_id_data(id: int, session: Session) -> Order | None:
    return session.get(Order, id)
