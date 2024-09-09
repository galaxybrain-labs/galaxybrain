from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.common import Reference


@define
class BaseArtifact(SerializableMixin, ABC):
    """Serves as the base class for all Artifacts.

    Artifacts are used to store data that can be provided as input to, or received as output from, a language model (LLM).

    Attributes:
        id: The unique identifier of the Artifact. Defaults to a random UUID.
        reference: The optional Reference to the Artifact.
        meta: The metadata associated with the Artifact. Defaults to an empty dictionary.
        name: The name of the Artifact. Defaults to the id.
        value: The value of the Artifact.
        encoding: The encoding of the Artifact when converting to bytes.
    """

    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True, metadata={"serializable": True})
    reference: Optional[Reference] = field(default=None, kw_only=True, metadata={"serializable": True})
    meta: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})
    name: str = field(
        default=Factory(lambda self: self.id, takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
    value: Any = field()
    encoding: str = field(default="utf-8", kw_only=True)

    def __str__(self) -> str:
        return self.to_text()

    def __bool__(self) -> bool:
        return bool(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def to_bytes(self) -> bytes:
        return self.to_text().encode(self.encoding)

    @abstractmethod
    def to_text(self) -> str: ...
