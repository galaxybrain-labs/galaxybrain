from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver
    from griptape.tokenizers import BaseTokenizer


def value_to_str(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(f"{key}: {val}" for key, val in value.items())
    else:
        return str(value)


@define
class TextArtifact(BaseArtifact):
    value: str = field(converter=value_to_str, metadata={"serializable": True})
    encoding: str = field(default="utf-8", kw_only=True)
    encoding_error_handler: str = field(default="strict", kw_only=True)
    embedding: Optional[list[float]] = field(default=None, kw_only=True)

    def __add__(self, other: BaseArtifact) -> TextArtifact:
        return TextArtifact(self.value + other.value)

    def __bool__(self) -> bool:
        return bool(self.value.strip())

    def to_text(self) -> str:
        return self.value

    def to_bytes(self) -> bytes:
        return str(self.value).encode(encoding=self.encoding, errors=self.encoding_error_handler)

    def generate_embedding(self, driver: BaseEmbeddingDriver) -> list[float]:
        if self.embedding is None:
            self.embedding = []

        self.embedding.clear()
        self.embedding.extend(driver.embed_string(str(self.value)))

        return self.embedding

    def token_count(self, tokenizer: BaseTokenizer) -> int:
        return tokenizer.count_tokens(str(self.value))
