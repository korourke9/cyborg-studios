"""Image generator adapters (local A1111/Forge + optional OpenAI)."""

from __future__ import annotations

import base64
import logging
from urllib.parse import urljoin

import httpx
from openai import OpenAI

from gamebuilder.orchestration.application.port.image_generator import (
    GeneratedImage,
    ImageGenerator,
)
from gamebuilder.orchestration.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)

_DEFAULT_A1111_BASE = "http://host.docker.internal:7860"


class NoopImageGenerator:
    def generate(self, prompt: str, *, size: str = "512x512") -> GeneratedImage:
        raise RuntimeError("Image generation is disabled (IMAGE_PROVIDER=none)")


class Automatic1111ImageGenerator:
    """Stable Diffusion WebUI / Forge txt2img API."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str = "",
        timeout_seconds: float = 180.0,
    ) -> None:
        self._base_url = base_url.rstrip("/") + "/"
        self._model = model
        self._timeout = timeout_seconds

    def generate(self, prompt: str, *, size: str = "512x512") -> GeneratedImage:
        width, height = _parse_size(size)
        payload: dict = {
            "prompt": prompt,
            "steps": 20,
            "width": width,
            "height": height,
        }
        if self._model:
            payload["override_settings"] = {"sd_model_checkpoint": self._model}

        url = urljoin(self._base_url, "sdapi/v1/txt2img")
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            body = response.json()

        images = body.get("images") or []
        if not images:
            raise RuntimeError("A1111 returned no images")
        raw = base64.b64decode(images[0])
        return GeneratedImage(data=raw, content_type="image/png")


class OpenAIImageGenerator:
    def __init__(self, *, api_key: str, model: str = "dall-e-3") -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, *, size: str = "512x512") -> GeneratedImage:
        # dall-e-3 requires specific sizes; map local default upward.
        openai_size = "1024x1024" if size in {"512x512", "768x768"} else size
        result = self._client.images.generate(
            model=self._model,
            prompt=prompt,
            size=openai_size,  # type: ignore[arg-type]
            response_format="b64_json",
            n=1,
        )
        b64 = result.data[0].b64_json
        if not b64:
            raise RuntimeError("OpenAI image response missing b64_json")
        return GeneratedImage(data=base64.b64decode(b64), content_type="image/png")


def create_image_generator(settings: Settings) -> ImageGenerator | None:
    if not settings.image_is_configured():
        return None

    provider = settings.normalized_image_provider()
    if provider in {"automatic1111", "a1111", "forge"}:
        base = settings.image_base_url or _DEFAULT_A1111_BASE
        return Automatic1111ImageGenerator(
            base_url=base,
            model=settings.image_model.strip(),
        )

    if provider == "openai":
        api_key = settings.image_api_key or settings.llm_api_key
        if not api_key:
            raise ValueError("IMAGE_PROVIDER=openai requires IMAGE_API_KEY or LLM_API_KEY")
        model = settings.image_model.strip() or "dall-e-3"
        return OpenAIImageGenerator(api_key=api_key, model=model)

    raise ValueError(
        f"Unsupported IMAGE_PROVIDER={settings.image_provider!r}; "
        "supported: none, automatic1111, a1111, forge, openai"
    )


def _parse_size(size: str) -> tuple[int, int]:
    try:
        width_s, height_s = size.lower().split("x", 1)
        return int(width_s), int(height_s)
    except ValueError as exc:
        raise ValueError(f"Invalid image size {size!r}; expected WxH") from exc
