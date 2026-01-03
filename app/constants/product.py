IMAGE_SIZE = 5 * 1024**2
ENDPOINT_PREFIX = "/products"
IMAGE_ROUTE = "/image"

# Allowed image MIME types for upload validation
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

MAX_SIZE = (800, 800)  # Good for web product images
