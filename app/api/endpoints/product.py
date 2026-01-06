from typing import Annotated
from fastapi import Form, HTTPException, Path, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter

from app.api.interface.product import ProductFilter, ProductFilterModel
from app.data.models.product import ProductCreate, ProductPublic
from app.data.controller.product import (
    create_product,
    delete_product_by_id,
    get_product_by_id,
    get_products,
    get_public_product_by_id,
)
from app.data.connector import SessionDep
from app.settings import SettingsDep
from app.constants.product import (
    ENDPOINT_PREFIX,
    ALLOWED_MIME_TYPES,
)
from app.auth.service import AuthorizedAnyDep, AuthorizedAdminDep

router = APIRouter(prefix=ENDPOINT_PREFIX, tags=["Product"])

IDType = Annotated[int, Path(description="Unique ID of the product", ge=0)]


def _product_not_found_error(id: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"no product found with given ID: {id}",
    )


@router.post("")
async def create_product_endpoint(
    product: Annotated[ProductCreate, Form(media_type="multipart/form-data")],
    session: SessionDep,
    settings: SettingsDep,
    *,
    _: AuthorizedAdminDep,
) -> ProductPublic:
    """
    Create a new product with image upload.

    Accepts product data and an image file via multipart/form-data. The image
    is automatically converted to WebP format, resized if needed, and stored
    with a unique UUID filename.

    Parameters
    ----------
    product : ProductCreate
        Product data (name, price, type, currency) and image file
    session : SessionDep
        Injected database session
    settings : SettingsDep
        Injected application settings
    _ : AuthorizedAdminDep
        Authorization check (admin role required)

    Returns
    -------
    ProductPublic
        The created product with ID and image URL

    Raises
    ------
    HTTPException
        - 400 BAD_REQUEST: Invalid image MIME type or file too large (>5MB)
        - 401 UNAUTHORIZED: Missing or invalid authentication token
        - 403 FORBIDDEN: User lacks admin scope
        - 500 INTERNAL_SERVER_ERROR: Image processing or database error

    Examples
    --------
    POST /products
    Content-Type: multipart/form-data

    name=Cola&price=2.5&type=drink&currency=EUR&image=<file>

    Response:
    {
        "id": 1,
        "name": "Cola",
        "price": 2.5,
        "type": "drink",
        "currency": "EUR",
        "image": "http://localhost:8000/api/v1/products/1/image"
    }
    """

    # Validate image MIME type (fast check, no file read)
    if product.image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {product.image.content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    return await create_product(product=product, session=session, settings=settings)


@router.get("")
async def get_products_endpoint(
    filter: ProductFilter, session: SessionDep, _: AuthorizedAnyDep
) -> list[ProductPublic]:
    """
    Retrieve all products.

    Returns a list of all products with their computed image URLs.
    Requires any valid authentication scope.

    Parameters
    ----------
    session : SessionDep
        Injected database session
    _ : AuthorizedAnyDep
        Authorization check (any authenticated user)

    Returns
    -------
    list[ProductPublic]
        List of all products with image URLs

    Raises
    ------
    HTTPException
        - 401 UNAUTHORIZED: Missing or invalid authentication token
        - 403 FORBIDDEN: User has no valid scopes
    """
    return await get_products(filter=filter, session=session)


@router.get("/{id}")
async def get_product_by_id_endpoint(
    id: IDType, *, session: SessionDep, _: AuthorizedAnyDep
):
    """
    Retrieve a single product by ID.

    Parameters
    ----------
    id : int
        Product ID (must be >= 0)
    session : SessionDep
        Injected database session
    _ : AuthorizedAnyDep
        Authorization check (any authenticated user)

    Returns
    -------
    ProductPublic
        The requested product with image URL

    Raises
    ------
    HTTPException
        - 401 UNAUTHORIZED: Missing or invalid authentication token
        - 403 FORBIDDEN: User has no valid scopes
        - 404 NOT_FOUND: Product with given ID doesn't exist
    """
    product = await get_public_product_by_id(id=id, session=session)
    if product is None:
        _product_not_found_error(id=id)
    return product


@router.get("/{id}/image")
async def get_product_image_by_id_endpoint(
    id: IDType, *, session: SessionDep, _: AuthorizedAnyDep
) -> FileResponse:
    """
    Retrieve the image file for a product.

    Returns the actual WebP image file for the specified product.

    Parameters
    ----------
    id : int
        Product ID (must be >= 0)
    session : SessionDep
        Injected database session
    _ : AuthorizedAnyDep
        Authorization check (any authenticated user)

    Returns
    -------
    FileResponse
        The product's WebP image file

    Raises
    ------
    HTTPException
        - 401 UNAUTHORIZED: Missing or invalid authentication token
        - 403 FORBIDDEN: User has no valid scopes
        - 404 NOT_FOUND: Product doesn't exist or image file not found
    """
    product = await get_product_by_id(id=id, session=session)
    if product is None:
        _product_not_found_error(id=id)
    if not product.image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No image found for product with ID {id}",
        )
    return FileResponse(path=product.image_path)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id_endpoint(
    id: IDType,
    *,
    session: SessionDep,
    _: AuthorizedAdminDep,
) -> None:
    """
    Delete a product and its image.

    Removes both the database record and the physical image file from disk.
    Requires admin authorization.

    Parameters
    ----------
    id : int
        Product ID to delete (must be >= 0)
    session : SessionDep
        Injected database session
    _ : AuthorizedAdminDep
        Authorization check (admin role required)

    Returns
    -------
    None
        Returns 204 No Content on success

    Raises
    ------
    HTTPException
        - 401 UNAUTHORIZED: Missing or invalid authentication token
        - 403 FORBIDDEN: User lacks admin scope
        - 404 NOT_FOUND: Product with given ID doesn't exist
    """
    product = await delete_product_by_id(id=id, session=session)
    if product is None:
        _product_not_found_error(id=id)
    return None
