from sqlmodel import Session
from app.data.access.order import create_order_data, get_my_orders_data
from app.data.access.product import get_product_data_by_id
from app.data.models.order import (
    Order,
    OrderCreate,
    OrderItem,
    OrderItemPublic,
    OrderPublic,
)
from app.data.models.product import Product
from app.data.models.user import User


def create_order(order: OrderCreate, user: User, session: Session) -> OrderPublic:
    # retrieve products per order item from the database
    products: list[Product] = []
    for item in order.items:
        product = get_product_data_by_id(id=item.product_id, session=session)
        if product is None:
            msg = f"Order declined. Product with id {item.product_id} not found in database."
            raise ValueError(msg)
        if product.age_restrict and user.age_restrict:
            msg = "Order declined due to age restriction"
            raise ValueError(msg)
        products.append(product)
    # strict in zip may lead to a ValueError, that should be handled in the endpoints
    order_items: list[OrderItem] = []
    for product, item in zip(products, order.items, strict=True):
        assert product.id is not None
        order_items.append(OrderItem(id=None, product_id=product.id, count=item.count))
    order_db = Order(id=None, user_id=user.id, items=order_items)
    order_db = create_order_data(order=order_db, session=session)
    return convert_order_to_public(order=order_db)


def convert_order_to_public(order: Order) -> OrderPublic:
    public_items = [
        OrderItemPublic(
            product_id=item.product_id,
            count=item.count,
            price_per_item=item.product.price,
        )
        for item in order.items
    ]
    return OrderPublic(**(order.model_dump() | {"items": public_items}))


def get_my_orders(user: User) -> list[OrderPublic]:
    orders = get_my_orders_data(user=user)
    if orders is None:
        return []
    return [convert_order_to_public(order=order) for order in orders]
