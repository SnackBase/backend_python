from datetime import UTC, datetime
from sqlmodel import Field, Relationship, SQLModel

from app.auth.models.user import UserPublic
from app.data.models.user import User


class PaymentUpdate(SQLModel):
    note: str | None = None


class PaymentCreate(SQLModel):
    amount: float = Field(gt=0)


class PaymentPublic(SQLModel):
    id: int
    amount: float
    created_at: datetime
    processed_at: datetime | None
    confirmed: bool
    note: str | None

    user: UserPublic


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float = Field(gt=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    processed_at: datetime | None = None
    confirmed: bool = False
    note: str | None = None

    # Relationship
    user: User = Relationship(back_populates="payments")
