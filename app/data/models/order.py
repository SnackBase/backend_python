from datetime import datetime, UTC
from typing import TYPE_CHECKING
from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel


from app.auth.models.user import UserPublic
from app.data.models.serialization import model_config
from app.data.models.product import ProductPublic


if TYPE_CHECKING:
    from app.data.models.user import User
    from app.data.models.product import Product


class OrderItemBase(SQLModel):
    count: int = Field(gt=0)
    model_config = model_config  # type: ignore[assignment]


class OrderBase(SQLModel):
    model_config = model_config  # type: ignore[assignment]


class OrderCreate(OrderBase):
    items: list["OrderItemCreate"] = Field(min_items=1)


class OrderItemCreate(OrderItemBase):
    product_id: int


class OrderPublic(OrderBase):
    id: int
    created_at: datetime
    deleted_at: datetime | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_per_order(self) -> float:
        return sum(item.total_per_order_item for item in self.items)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    user: UserPublic
    items: list["OrderItemPublic"] = Field(min_items=1)


class OrderItemPublic(OrderItemBase, ProductPublic):
    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_per_order_item(self) -> float:
        return self.price * self.count


class Order(OrderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    deleted_at: datetime | None = Field(default=None)

    # relationships
    user: "User" = Relationship(back_populates="orders")
    items: list["OrderItem"] = Relationship(back_populates="order")


class OrderItem(OrderItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int | None = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")

    # relationships
    order: Order | None = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="items")
