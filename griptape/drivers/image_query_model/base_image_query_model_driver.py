from __future__ import annotations
from abc import ABC, abstractmethod
from attr import define
from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.mixins import SerializableMixin


@define
class BaseImageQueryModelDriver(SerializableMixin, ABC):
    @abstractmethod
    def construct_image_query_request_parameters(self, query: str, images: list[ImageArtifact]) -> dict:
        ...

    @abstractmethod
    def process_output(self, output: dict) -> TextArtifact:
        ...
