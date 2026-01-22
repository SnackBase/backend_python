from typing import TYPE_CHECKING
import uuid
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.data.models.order import Order
    from app.data.models.payment import Payment


class User(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Used to link other data to the user",
    )
    # sub could be used to fuse the databse user with the user from keycloak, e.g. to show additoinal information about the user in an overview
    sub: uuid.UUID = Field(
        description="Unique ID (UUID) from the auth server (keycloak). sub=subject."
    )
    age_restrict: bool = Field(
        default=False,
        description="True to restrict the user from buying items for them a certain age is required",
    )
    allowed_overdraw: float = Field(
        default=30,
        ge=0,
        description="Maximum amount/hard limit the user is allowed to overspent on orders before any further order are blocked until the account balance is above this threshold. Users are able to perform deposits/paymentss to resolve this.",
    )

    # relationships
    orders: list["Order"] | None = Relationship(back_populates="user")
    payments: list["Payment"] | None = Relationship(back_populates="user")
