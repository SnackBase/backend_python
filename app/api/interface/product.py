from typing import Annotated
from fastapi import Query
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.data.enums.product import ProductTypes


class ProductFilterModel(BaseModel):
    age_restrict: bool | None = False
    product_type: ProductTypes | None = None
    offset: int | None = None
    limit: int | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        serialize_by_alias=True,
    )


ProductFilter = Annotated[ProductFilterModel, Query()]
