from __future__ import annotations
from typing import Any
from attrs import define, field
from griptape.artifacts import BaseArtifact


@define
class BooleanArtifact(BaseArtifact):
    value: bool = field(converter=bool, metadata={"serializable": True})
    meta: dict[str, Any] = field(factory=dict, kw_only=True, metadata={"serializable": True})

    @classmethod
    def parse_bool(cls, value: str) -> BooleanArtifact:
        """
        Convert a string literal to a BooleanArtifact. The string must be either "true" or "false" with any casing.
        """
        if value is not None:
            if value.lower() == "true":
                return BooleanArtifact(True)
            elif value.lower() == "false":
                return BooleanArtifact(False)
        raise ValueError(f"Cannot convert string literal '{value}' to BooleanArtifact")

    def __add__(self, other: BaseArtifact) -> BooleanArtifact:
        raise ValueError("Cannot add BooleanArtifact with other artifacts")
