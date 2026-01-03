import asyncio
from pathlib import Path
import io
import aiofiles
from fastapi import UploadFile
from PIL import Image
from sqlmodel import Sequence, Session, select

from app.data.models.product import Product


async def save_image(image: UploadFile, path: Path, *, quality: int = 85) -> None:
    """
    Convert an uploaded image (jpeg/png/etc.) to WEBP and save it asynchronously.
    """

    # Read uploaded file asynchronously
    data = await image.read()

    def convert_to_webp_bytes() -> bytes:
        with Image.open(io.BytesIO(data)) as img:
            img = img.convert("RGBA") if img.mode in ("P", "LA") else img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="WEBP", quality=quality, method=6)
            return buf.getvalue()

    # Offload CPU-bound Pillow work
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
