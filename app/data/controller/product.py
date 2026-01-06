from uuid import uuid4
from sqlmodel import Session

from app.api.interface.product import ProductFilterModel
from app.data.models.product import Product, ProductCreate, ProductPublic, ProductTypes
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
    """
    Create a new product with image upload.

    Generates a unique UUID for the image, saves the uploaded file as WebP,
    persists the product to the database, and returns the public representation.

    Parameters
    ----------
    product : ProductCreate
        Product data including name, price, type, currency, and image file
    session : Session
        Active database session for persistence
    settings : Settings
        Application settings (unused, kept for future extensibility)

    Returns
    -------
    ProductPublic
        The created product with ID and image URL

    Raises
    ------
    HTTPException
        - 400 BAD_REQUEST: If image validation fails (size/type)
        - 500 INTERNAL_SERVER_ERROR: If image processing or DB save fails

    Examples
    --------
    >>> product_data = ProductCreate(name="Cola", price=2.5, type=ProductTypes.DRINK, image=file)
    >>> created = await create_product(product_data, session, settings)
    >>> created.id
    1
    """
    image_id = str(uuid4())
    db_product = Product(
        name=product.name,
        price=product.price,
        type=product.type,
        currency=product.currency,
        image_id=image_id,
        age_restrict=product.age_restrict,
    )
    await save_image(image=product.image, path=db_product.image_path)
    db_product = save_product(product=db_product, session=session)
    public_product = ProductPublic.model_validate(db_product)
    return public_product


def get_products(
    filter: ProductFilterModel,
    *,
    session: Session,
) -> list[ProductPublic]:
    """
    Retrieve all products as public API models.

    Parameters
    ----------
    limit : int | None, default=None
        Maximum number of products to return
    session : Session
        Active database session

    Returns
    -------
    list[ProductPublic]
        List of products with computed image URLs
    """
    products = get_products_data(filter=filter, session=session)
    return [ProductPublic.model_validate(p) for p in products]


def get_product_by_id(id: int, session: Session) -> Product | None:
    """
    Retrieve a product database model by ID.

    Parameters
    ----------
    id : int
        Product identifier
    session : Session
        Active database session

    Returns
    -------
    Product | None
        Product database model or None if not found
    """
    return get_product_data_by_id(id=id, session=session)


def get_public_product_by_id(id: int, session: Session) -> ProductPublic | None:
    """
    Retrieve a product as public API model by ID.

    Parameters
    ----------
    id : int
        Product identifier
    session : Session
        Active database session

    Returns
    -------
    ProductPublic | None
        Product with computed image URL or None if not found
    """
    product = get_product_by_id(id=id, session=session)
    if product is None:
        return None
    return ProductPublic.model_validate(product)


def delete_product_by_id(id: int, session: Session) -> ProductPublic | None:
    """
    Delete a product and its image by ID.

    Parameters
    ----------
    id : int
        Product identifier to delete
    session : Session
        Active database session

    Returns
    -------
    ProductPublic | None
        The deleted product as public model or None if not found
    """
    product = get_product_data_by_id(id=id, session=session)
    if product is None:
        return None
    product = delete_product_data_by_id(product=product, session=session)
    return ProductPublic.model_validate(product)
