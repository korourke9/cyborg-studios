from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GeneratedImage:
    data: bytes
    content_type: str = "image/png"


class ImageGenerator(Protocol):
    """Generate raster images from text prompts (separate from chat LlmModel)."""

    def generate(self, prompt: str, *, size: str = "512x512") -> GeneratedImage: ...
