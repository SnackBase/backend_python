from uuid import uuid4
from sqlmodel import Session

from app.data.models.product import Product, ProductCreate, ProductPublic
from app.data.access.product import (
    delete_product_data_by_id,
    get_product_data_by_id,
    get_products_data,
    save_image,
    save_product,
)
from app.settings import Settings


async def create_product(
    product: ProductCreate, session: Session, settings: Settings
) -> ProductPublic:
    image_id = str(uuid4())
    db_product = Product(
        name=product.name,
        price=product.price,
        type=product.type,
        currency=product.currency,
        image_id=image_id,
    )
    await save_image(image=product.image, path=db_product.image_path)
    db_product = await save_product(product=db_product, session=session)
    public_product = ProductPublic.model_validate(db_product)
    return public_product


async def get_products(
    limit: int | None = None, *, session: Session
) -> list[ProductPublic]:
    products = await get_products_data(limit=limit, session=session)
    return [ProductPublic.model_validate(p) for p in products]


async def get_product_by_id(id: int, session: Session) -> Product | None:
    return await get_product_data_by_id(id=id, session=session)


async def get_public_product_by_id(id: int, session: Session) -> ProductPublic | None:
    product = await get_product_by_id(id=id, session=session)
    if product is None:
        return None
    return ProductPublic.model_validate(product)


async def delete_product_by_id(id: int, session: Session) -> ProductPublic | None:
    product = await get_product_data_by_id(id=id, session=session)
    if product is None:
        return None
    product = await delete_product_data_by_id(product=product, session=session)
    return ProductPublic.model_validate(product)
