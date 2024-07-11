from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from attrs import define, field, Factory
from griptape.utils import import_optional_dependency
from griptape.drivers import BaseEmbeddingDriver

if TYPE_CHECKING:
    from ollama import Client


@define
class OllamaEmbeddingDriver(BaseEmbeddingDriver):
    """
    Attributes:
        model: Ollama embedding model name.
        host: Optional Ollama host.
        client: Ollama `Client`.
    """

    model: str = field(kw_only=True, metadata={"serializable": True})
    host: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("ollama").Client(host=self.host), takes_self=True),
        kw_only=True,
    )

    def try_embed_chunk(self, chunk: str) -> list[float]:
        return list(self.client.embeddings(model=self.model, prompt=chunk)["embedding"])
