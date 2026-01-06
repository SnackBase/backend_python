import asyncio
from pathlib import Path
import io
import aiofiles
from fastapi import UploadFile, HTTPException, status
from PIL import Image
from sqlmodel import Sequence, Session, select
from datetime import datetime, UTC

from app.api.interface.product import ProductFilterModel
from app.data.models.product import Product
from app.constants.product import IMAGE_SIZE, MAX_SIZE


async def save_image(image: UploadFile, path: Path, *, quality: int = 85) -> None:
    """
    Convert an uploaded image to WebP format and save asynchronously.

    Reads the uploaded file, validates size, converts to WebP (with automatic
    resizing if needed), and saves to disk using async I/O. CPU-intensive image
    processing is offloaded to a thread pool.

    Parameters
    ----------
    image : UploadFile
        The uploaded image file (may already be read by validation)
    path : Path
        Destination filesystem path for the WebP file
    quality : int, default=85
        WebP compression quality (1-100, higher = better quality/larger file)

    Raises
    ------
    HTTPException
        - 400 BAD_REQUEST: If file exceeds maximum size (5 MB)
        - 500 INTERNAL_SERVER_ERROR: If image processing or file write fails

    Notes
    -----
    - Automatically resizes images larger than 800x800 pixels
    - Preserves transparency for RGBA/PNG images
    - Uses method=4 for balanced compression speed
    - Ensures parent directories exist before writing
    """

    # Read uploaded file asynchronously (handles both read and unread files)
    data = await image.read()

    # Validate file size
    if len(data) > IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {IMAGE_SIZE / (1024 * 1024):.1f} MB",
        )

    def convert_to_webp_bytes() -> bytes:
        with Image.open(io.BytesIO(data)) as img:
            # Resize large images for faster processing and smaller files
            if img.width > MAX_SIZE[0] or img.height > MAX_SIZE[1]:
                img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)

            # Preserve transparency for images that have it
            if img.mode in ("RGBA", "LA"):
                # Already has alpha channel, keep it
                img = img.convert("RGBA")
            elif img.mode == "P":
                # Palette mode - check if it has transparency
                if "transparency" in img.info:
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
            elif img.mode == "RGB":
                # Already RGB, no transparency
                pass
            else:
                # Other modes (L, CMYK, etc.) - convert to RGB
                img = img.convert("RGB")

            buf = io.BytesIO()
            # Use method=1 for faster encoding (good speed/quality balance)
            img.save(buf, format="WEBP", quality=quality, method=4)
            return buf.getvalue()

    # Offload CPU-bound Pillow work to thread pool
    webp_bytes = await asyncio.to_thread(convert_to_webp_bytes)

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write file asynchronously
    async with aiofiles.open(path, "wb") as f:
        await f.write(webp_bytes)


def save_product(product: Product, session: Session) -> Product:
    """
    Persist a new product to the database.

    Adds the product to the session, commits the transaction, and refreshes
    to get the auto-generated ID and any default values.

    Parameters
    ----------
    product : Product
        The product instance to save (without ID)
    session : Session
        Active SQLModel database session

    Returns
    -------
    Product
        The saved product with generated ID and refreshed fields

    Examples
    --------
    >>> product = Product(name="Cola", price=2.5, type=ProductTypes.DRINK, image_id="abc123")
    >>> saved = save_product(product, session)
    >>> saved.id
    1
    """
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def save_products(products: list[Product], session: Session) -> list[Product]:
    for product in products:
        session.add(product)
    session.commit()
    for product in products:
        session.refresh(product)
    return products


def get_products_data(
    filter: ProductFilterModel,
    *,
    session: Session,
) -> Sequence[Product]:
    """
    Retrieve products from the database with optional limit.

    Parameters
    ----------
    limit : int | None, default=None
        Maximum number of products to return. If None, returns all products.
    session : Session
        Active SQLModel database session

    Returns
    -------
    Sequence[Product]
        List of product instances from the database

    Examples
    --------
    >>> # Get all products
    >>> products = get_products_data(session=session)
    >>> len(products)
    50
    >>> # Get first 10 products
    >>> products = get_products_data(limit=10, session=session)
    >>> len(products)
    10
    """
    statement = select(Product).where(Product.deleted_at == None)  # noqa: E711  # noqa necessary for the condition handling via sqlmodel
    if filter.age_restrict is not None and filter.age_restrict:
        statement = statement.where(Product.age_restrict != True)  # noqa: E712  # noqa necessary for the condition handling via sqlmodel
    if filter.product_type is not None:
        statement = statement.where(Product.type == filter.product_type)
    if filter.offset is not None:
        statement = statement.offset(offset=filter.offset)
    if filter.limit is not None:
        statement = statement.limit(limit=filter.limit)
    return session.exec(statement=statement).all()


def get_product_data_by_id(
    id: int, include_deleted: bool = False, *, session: Session
) -> Product:
    """
    Retrieve a single product by its ID.

    Parameters
    ----------
    id : int
        The unique product identifier
    session : Session
        Active SQLModel database session

    Returns
    -------
    Product | None
        The product instance if found, None otherwise

    Examples
    --------
    >>> product = get_product_data_by_id(id=1, session=session)
    >>> product.name if product else "Not found"
    'Cola 0.33L'
    """
    product = session.get(Product, id)
    if not include_deleted and product.deleted_at is not None:
        return None
    return product


def delete_product_data_by_id(
    product: Product,
    session: Session,
) -> Product | None:
    """
    Delete a product and its associated image file from the system.

    Removes both the database record and the physical image file from disk.
    The image file deletion is graceful (won't raise error if file doesn't exist).

    Parameters
    ----------
    product : Product
        The product instance to delete
    session : Session
        Active SQLModel database session

    Returns
    -------
    Product | None
        The deleted product instance (for reference/logging)

    Notes
    -----
    Deletes the image file first (if it exists), then removes the database record.
    Uses missing_ok=True to avoid errors if the image file was already deleted.

    Examples
    --------
    >>> product = get_product_data_by_id(id=1, session=session)
    >>> deleted = delete_product_data_by_id(product, session)
    >>> deleted.name
    'Cola 0.33L'
    """
    if product.deleted_at is not None:
        return product
    product.image_path.unlink(
        missing_ok=True
    )  # ? TODO: might be removed to be able to show a product image for historic data
    product.deleted_at = datetime.now(tz=datetime.UTC)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
