from __future__ import annotations
from typing import Optional
from attr import define, field, Factory
from griptape.drivers import BaseEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer
import openai


@define
class OpenAiEmbeddingDriver(BaseEmbeddingDriver):
    """
    Attributes:
        model: OpenAI embedding model name. Defaults to `text-embedding-ada-002`.
        dimensions: Vector dimensions. Defaults to `1536`.
        base_url: API URL. Defaults to OpenAI's v1 API URL.
        api_key: API key to pass directly. Defaults to `OPENAI_API_KEY` environment variable.
        organization: OpenAI organization. Defaults to 'OPENAI_ORGANIZATION' environment variable.
        tokenizer: Optionally provide custom `OpenAiTokenizer`.
    """

    DEFAULT_MODEL = "text-embedding-ada-002"
    DEFAULT_DIMENSIONS = 1536

    model: str = field(default=DEFAULT_MODEL, kw_only=True)
    dimensions: int = field(default=DEFAULT_DIMENSIONS, kw_only=True)
    base_url: str = field(default=None, kw_only=True)
    api_key: Optional[str] = field(default=None, kw_only=True)
    organization: Optional[str] = field(default=None, kw_only=True)
    client: openai.OpenAI = field(
        init=False,
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        ),
    )
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )

    def try_embed_chunk(self, chunk: str) -> list[float]:
        # Address a performance issue in older ada models
        # https://github.com/openai/openai-python/issues/418#issuecomment-1525939500
        if self.model.endswith("001"):
            chunk = chunk.replace("\n", " ")
        return self.client.embeddings.create(**self._params(chunk)).data[0].embedding

    def _params(self, chunk: str) -> dict:
        return {"input": chunk, "model": self.model}
