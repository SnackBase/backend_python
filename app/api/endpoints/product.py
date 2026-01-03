from typing import Annotated
from fastapi import Form, HTTPException, Path, Response, status
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter

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
    IMAGE_SIZE,
    ALLOWED_MIME_TYPES,
)

router = APIRouter(prefix=ENDPOINT_PREFIX, tags=["Product"])

IDType = Annotated[int, Path(description="Unique ID of the product", ge=0)]


def _product_not_found_error(id: int) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"no product found with given ID: {id}",
    )


@router.post("")
async def create_product_endpoint(
    product: Annotated[ProductCreate, Form()],
    session: SessionDep,
    settings: SettingsDep,
) -> ProductPublic:
    """Create a new product with image upload."""

    # Validate image MIME type
    if product.image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {product.image.content_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # Validate image size
    contents = await product.image.read()
    if len(contents) > IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {IMAGE_SIZE / (1024 * 1024):.1f} MB",
        )
    # Reset file pointer after reading
    await product.image.seek(0)

    return await create_product(product=product, session=session, settings=settings)


@router.get("")
async def get_products_endpoint(session: SessionDep) -> list[ProductPublic]:
    return await get_products(session=session)


@router.get("/{id}")
async def get_product_by_id_endpoint(
    id: IDType,
    *,
    session: SessionDep,
):
    product = await get_public_product_by_id(id=id, session=session)
    if product is None:
        _product_not_found_error(id=id)
    return product


@router.get("/{id}/image")
async def get_product_image_by_id_endpoint(
    id: IDType,
    *,
    session: SessionDep,
) -> FileResponse:
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
) -> None:
    product = await delete_product_by_id(id=id, session=session)
    if product is None:
        _product_not_found_error(id=id)
    return None
