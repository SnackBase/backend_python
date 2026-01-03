import asyncio
from pathlib import Path
import io
import aiofiles
from fastapi import UploadFile, HTTPException, status
from PIL import Image
from sqlmodel import Sequence, Session, select

from app.data.models.product import Product
from app.constants.product import IMAGE_SIZE, MAX_SIZE


async def save_image(image: UploadFile, path: Path, *, quality: int = 85) -> None:
    """
    Convert an uploaded image (jpeg/png/etc.) to WEBP and save it asynchronously.

    Args:
        image: The uploaded file (may already be read)
        path: Destination path for the WebP file
        quality: WebP quality (1-100, default 85 is a good balance)

    Raises:
        HTTPException: If file is too large or cannot be processed
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


async def save_product(product: Product, session: Session) -> Product:
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


async def get_products_data(
    limit: int | None = None, *, session: Session
) -> Sequence[Product]:
    statement = select(Product)
    if limit is not None:
        statement = statement.limit(limit=limit)
    return session.exec(statement=statement).all()


async def get_product_data_by_id(id: int, session: Session) -> Product:
    return session.get(Product, id)


async def delete_product_data_by_id(
    product: Product,
    session: Session,
) -> Product | None:
    product.image_path.unlink(missing_ok=True)
    session.delete(product)
    session.commit()
    return product
