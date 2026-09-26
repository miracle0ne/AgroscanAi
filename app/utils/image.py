import os
import tempfile

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()


def prepare_image(file):
    """
    Read uploaded image and convert HEIC/HEIF to JPEG.

    Returns:
        image_bytes, mime_type
    """

    image_bytes = file.read()

    if not image_bytes:
        raise ValueError("Uploaded image is empty.")

    mime_type = file.mimetype or "image/jpeg"

    extension = os.path.splitext(
        file.filename or ""
    )[1].lower()

    if extension in {".heic", ".heif"}:
        with tempfile.TemporaryDirectory() as temp:
            input_file = os.path.join(
                temp,
                "plant" + extension
            )

            output_file = os.path.join(
                temp,
                "plant.jpg"
            )

            with open(input_file, "wb") as image:
                image.write(image_bytes)

            with Image.open(input_file) as image:
                image = image.convert("RGB")
                image.save(
                    output_file,
                    format="JPEG",
                    quality=90
                )

            with open(output_file, "rb") as image:
                image_bytes = image.read()

            mime_type = "image/jpeg"

    return image_bytes, mime_type
