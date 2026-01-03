from pathlib import Path
from sqlmodel import SQLModel, Field
from pydantic import computed_field, HttpUrl
from pydantic_extra_types.currency_code import Currency
from enum import Enum
from urllib.parse import urljoin
from fastapi import UploadFile

from app.constants.product import IMAGE_ROUTE, ENDPOINT_PREFIX
from app.settings import get_settings


settings = get_settings()


class ProductTypes(Enum):
    DRINK = "drink"
    SNACK = "snack"
    FOOD = "food"


class ProductBase(SQLModel):
    name: str
    price: float = Field(ge=0)
    type: ProductTypes
    currency: Currency = Field(default=Currency("EUR"))


class ProductCreate(ProductBase):
    image: UploadFile


class ProductPublic(ProductBase):
    id: int

    @computed_field
    @property
    def image(self) -> HttpUrl:
        return HttpUrl(
            urljoin(
                str(settings.host),
                settings.api_prefix + ENDPOINT_PREFIX + f"/{self.id}" + IMAGE_ROUTE,
            )
        )


class Product(ProductBase, table=True):
    id: int | None = Field(primary_key=True)
    image_id: str

    @property
    def image_path(self) -> Path:
        return settings.product_image_root_dir / (self.image_id + ".webp")
