from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union, cast

from attrs import Factory, define, field

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.common import ImageMessageContent, Message, PromptStack, TextMessageContent
from griptape.configs.defaults_config import Defaults
from griptape.tasks import BaseTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.drivers import BasePromptDriver


@define
class ImageQueryTask(BaseTask):
    """A task that executes a natural language query on one or more input images.

    Accepts a text prompt and a list of
    images as input in one of the following formats:
    - tuple of (template string, list[ImageArtifact])
    - tuple of (TextArtifact, list[ImageArtifact])
    - Callable that returns a tuple of (TextArtifact, list[ImageArtifact]).

    Attributes:
        prompt_driver: The driver used to execute the query.
    """

    prompt_driver: BasePromptDriver = field(
        default=Factory(lambda: Defaults.drivers_config.prompt_driver), kw_only=True
    )
    _input: Union[
        tuple[str, list[ImageArtifact]],
        tuple[TextArtifact, list[ImageArtifact]],
        Callable[[BaseTask], ListArtifact],
        ListArtifact,
    ] = field(default=None, alias="input")

    @property
    def input(self) -> ListArtifact:
        if isinstance(self._input, ListArtifact):
            return self._input
        elif isinstance(self._input, tuple):
            if isinstance(self._input[0], TextArtifact):
                query_text = self._input[0]
            else:
                query_text = TextArtifact(J2().render_from_string(self._input[0], **self.full_context))

            return ListArtifact([query_text, *self._input[1]])
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError(
                "Input must be a tuple of a TextArtifact and a list of ImageArtifacts or a callable that "
                "returns a tuple of a TextArtifact and a list of ImageArtifacts.",
            )

    @input.setter
    def input(
        self,
        value: (
            Union[
                tuple[str, list[ImageArtifact]],
                tuple[TextArtifact, list[ImageArtifact]],
                Callable[[BaseTask], ListArtifact],
            ]
        ),
    ) -> None:
        self._input = value

    def try_run(self) -> TextArtifact:
        query = self.input.value[0]

        if all(isinstance(artifact, ImageArtifact) for artifact in self.input.value[1:]):
            image_artifacts = [
                image_artifact for image_artifact in self.input.value[1:] if isinstance(image_artifact, ImageArtifact)
            ]
        else:
            raise ValueError("All inputs after the query must be ImageArtifacts.")

        self.output = cast(
            TextArtifact,
            self.prompt_driver.run(
                PromptStack(
                    messages=[
                        Message(
                            role=Message.USER_ROLE,
                            content=[
                                TextMessageContent(TextArtifact(query)),
                                *[ImageMessageContent(image_artifact) for image_artifact in image_artifacts],
                            ],
                        ),
                    ]
                )
            ).to_artifact(),
        )

        return self.output
