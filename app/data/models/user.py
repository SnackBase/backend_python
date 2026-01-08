from typing import TYPE_CHECKING
import uuid
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.data.models.order import Order


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

    # relationships
    orders: list["Order"] | None = Relationship(back_populates="user")
