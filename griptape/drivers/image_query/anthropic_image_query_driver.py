from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field, Factory
from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers import BaseImageQueryDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from anthropic import Anthropic


@define
class AnthropicImageQueryDriver(BaseImageQueryDriver):
    """
    Attributes:
        api_key: Anthropic API key.
        model: Anthropic model name.
        client: Custom `Anthropic` client.
        max_output_tokens: Max output tokens to return.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Anthropic = field(
        default=Factory(
            lambda self: import_optional_dependency("anthropic").Anthropic(api_key=self.api_key), takes_self=True
        ),
        kw_only=True,
    )
    max_output_tokens: Optional[int] = field(default=4096, kw_only=True, metadata={"serializable": True})

    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        response = self.client.messages.create(**self._base_params(query, images))
        content_blocks = response.content

        if len(content_blocks) < 1:
            raise ValueError("Response content is empty")

        text_content = content_blocks[0].text

        return TextArtifact(text_content)

    def _base_params(self, text_query: str, images: list[ImageArtifact]):
        content = [self._construct_image_message(image) for image in images]
        content.append(self._construct_text_message(text_query))
        messages = self._construct_messages(content)
        params = {"model": self.model, "messages": messages}

        if self.max_output_tokens is not None:
            params["max_tokens"] = self.max_output_tokens

        return params

    def _construct_image_message(self, image_data: ImageArtifact) -> dict:
        data = image_data.base64
        type = image_data.mime_type

        return {"source": {"data": data, "media_type": type, "type": "base64"}, "type": "image"}

    def _construct_text_message(self, query: str) -> dict:
        return {"text": query, "type": "text"}

    def _construct_messages(self, content: list) -> list:
        return [{"content": content, "role": "user"}]
