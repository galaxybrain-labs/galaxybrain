from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import (
    BaseDeltaMessageContent,
    DeltaMessage,
    TextDeltaMessageContent,
    MessageStack,
    Message,
    TextMessageContent,
)
from griptape.events import CompletionChunkEvent, FinishPromptEvent, StartPromptEvent
from griptape.mixins import ExponentialBackoffMixin, SerializableMixin
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class BasePromptDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    """Base class for Prompt Drivers.

    Attributes:
        temperature: The temperature to use for the completion.
        max_tokens: The maximum number of tokens to generate. If not specified, the value will be automatically generated based by the tokenizer.
        structure: An optional `Structure` to publish events to.
        message_stack_to_string: A function that converts a `MessageStack` to a string.
        ignored_exception_types: A tuple of exception types to ignore.
        model: The model name.
        tokenizer: An instance of `BaseTokenizer` to when calculating tokens.
        stream: Whether to stream the completion or not. `CompletionChunkEvent`s will be published to the `Structure` if one is provided.
    """

    temperature: float = field(default=0.1, kw_only=True, metadata={"serializable": True})
    max_tokens: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    structure: Optional[Structure] = field(default=None, kw_only=True)
    ignored_exception_types: tuple[type[Exception], ...] = field(
        default=Factory(lambda: (ImportError, ValueError)), kw_only=True
    )
    model: str = field(metadata={"serializable": True})
    tokenizer: BaseTokenizer
    stream: bool = field(default=False, kw_only=True, metadata={"serializable": True})

    def before_run(self, message_stack: MessageStack) -> None:
        if self.structure:
            self.structure.publish_event(StartPromptEvent(model=self.model, message_stack=message_stack))

    def after_run(self, result: Message) -> None:
        if self.structure:
            self.structure.publish_event(
                FinishPromptEvent(
                    model=self.model,
                    result=result.value,
                    input_token_count=result.usage.input_tokens,
                    output_token_count=result.usage.output_tokens,
                )
            )

    def run(self, message_stack: MessageStack) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(message_stack)

                if self.stream:
                    result = self.__process_stream(message_stack)
                else:
                    result = self.__process_run(message_stack)

                self.after_run(result)

                return result.to_text_artifact()
        else:
            raise Exception("prompt driver failed after all retry attempts")

    def message_stack_to_string(self, message_stack: MessageStack) -> str:
        """Converts a Message Stack to a string for token counting or model input.
        This base implementation is only a rough approximation, and should be overridden by subclasses with model-specific tokens.

        Args:
            message_stack: The Message Stack to convert to a string.

        Returns:
            A single string representation of the Message Stack.
        """
        prompt_lines = []

        for i in message_stack.messages:
            content = i.to_text_artifact().to_text()
            if i.is_user():
                prompt_lines.append(f"User: {content}")
            elif i.is_assistant():
                prompt_lines.append(f"Assistant: {content}")
            else:
                prompt_lines.append(content)

        prompt_lines.append("Assistant:")

        return "\n\n".join(prompt_lines)

    @abstractmethod
    def try_run(self, message_stack: MessageStack) -> Message: ...

    @abstractmethod
    def try_stream(self, message_stack: MessageStack) -> Iterator[DeltaMessage]: ...

    def __process_run(self, message_stack: MessageStack) -> Message:
        result = self.try_run(message_stack)

        return result

    def __process_stream(self, message_stack: MessageStack) -> Message:
        delta_contents: dict[int, list[BaseDeltaMessageContent]] = {}
        usage = DeltaMessage.Usage()

        # Aggregate all content deltas from the stream
        deltas = self.try_stream(message_stack)
        for delta in deltas:
            usage += delta.usage

            if delta.content is not None:
                if delta.content.index in delta_contents:
                    delta_contents[delta.content.index].append(delta.content)
                else:
                    delta_contents[delta.content.index] = [delta.content]

            if isinstance(delta.content, TextDeltaMessageContent):
                self.structure.publish_event(CompletionChunkEvent(token=delta.content.text))

        # Build a complete content from the content deltas
        content = []
        for index, deltas in delta_contents.items():
            text_deltas = [delta for delta in deltas if isinstance(delta, TextDeltaMessageContent)]
            if text_deltas:
                content.append(TextMessageContent.from_deltas(text_deltas))

        result = Message(
            content=content,
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

        return result
