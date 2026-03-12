import base64
from pathlib import Path


SUPPORTED_IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def detect_image_mime_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    mime_type = SUPPORTED_IMAGE_MIME_TYPES.get(suffix)
    if mime_type is None:
        supported = ", ".join(sorted(SUPPORTED_IMAGE_MIME_TYPES))
        raise ValueError(f"Unsupported image extension {suffix!r}. Supported extensions: {supported}")
    return mime_type


def image_to_base64(path: str) -> str:
    image_path = Path(path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {path}")
    if not image_path.is_file():
        raise ValueError(f"Image path is not a file: {path}")

    data = image_path.read_bytes()
    if not data:
        raise ValueError(f"Image file is empty: {path}")

    return base64.b64encode(data).decode("utf-8")
