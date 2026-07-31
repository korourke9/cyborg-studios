from openai import OpenAI

from gamebuilder.orchestration.application.port.llm import LlmModel


class OpenAICompatibleLlmModel:
    """Adapter for OpenAI Chat Completions API and compatible local servers (Ollama, vLLM, LM Studio)."""

    def __init__(
        self,
        client: OpenAI,
        model: str,
        *,
        json_mode: bool = True,
    ) -> None:
        self._client = client
        self._model = model
        self._json_mode = json_mode

    def complete(self, *, system: str, user: str) -> str:
        kwargs: dict = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        # JSON response_format is OpenAI-cloud-specific; many local servers reject it.
        if self._json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError(f"Empty completion from model {self._model}")
        return content
