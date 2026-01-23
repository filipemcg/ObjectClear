from PIL import Image
from io import BytesIO
import requests

class ImageHelper:
    def __init__(self, content: bytes) -> None:
        """
        Initialize with raw image content (e.g., from requests.get(url).content).
        """
        self._original_content: bytes = content
        self.image: Image.Image = self._load_image(content)

    def _load_image(self, content: bytes) -> Image.Image:
        """
        Converts raw byte content to a PIL Image.
        """
        return Image.open(BytesIO(content)).convert("RGB")

    def get_bytes(self, format: str = "JPEG", quality: int = 100) -> bytes:
        """
        Get the current image as bytes, suitable for upload.
        """
        buffer = BytesIO()
        self.image.save(buffer, format=format, quality=quality)
        buffer.seek(0)
        return buffer.read()

    def resize(self, width: int = 600) -> Image.Image:
        """
        Resize the image to the given width and height.
        """
        original_width, original_height = self.image.size
        if width <= original_width:
            return self.image

        new_height = int((width / original_width) * original_height)
        self.image = self.image.resize((width, new_height), Image.LANCZOS)
        return self.image

    @classmethod
    def from_url(cls, url: str):
        """
        Create an ImageHelper instance from a URL.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data = requests.get(url, headers=headers).content

        return cls(data)
