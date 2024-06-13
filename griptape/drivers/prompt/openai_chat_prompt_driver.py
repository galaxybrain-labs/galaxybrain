from __future__ import annotations

from collections.abc import Iterator
from typing import Literal, Optional, TYPE_CHECKING

import openai
from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    BasePromptStackContent,
    DeltaPromptStackElement,
    DeltaTextPromptStackContent,
    ImagePromptStackContent,
    PromptStack,
    PromptStackElement,
    TextPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer


if TYPE_CHECKING:
    from openai.types.chat.chat_completion_message import ChatCompletionMessage
    from openai.types.chat.chat_completion_chunk import ChoiceDelta


@define
class OpenAiChatPromptDriver(BasePromptDriver):
    """
    Attributes:
        base_url: An optional OpenAi API URL.
        api_key: An optional OpenAi API key. If not provided, the `OPENAI_API_KEY` environment variable will be used.
        organization: An optional OpenAI organization. If not provided, the `OPENAI_ORG_ID` environment variable will be used.
        client: An `openai.OpenAI` client.
        model: An OpenAI model name.
        tokenizer: An `OpenAiTokenizer`.
        user: A user id. Can be used to track requests by user.
        response_format: An optional OpenAi Chat Completion response format. Currently only supports `json_object` which will enable OpenAi's JSON mode.
        seed: An optional OpenAi Chat Completion seed.
        ignored_exception_types: An optional tuple of exception types to ignore. Defaults to OpenAI's known exception types.
    """

    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    organization: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        )
    )
    model: str = field(kw_only=True, metadata={"serializable": True})
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    user: str = field(default="", kw_only=True, metadata={"serializable": True})
    response_format: Optional[Literal["json_object"]] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    seed: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    ignored_exception_types: tuple[type[Exception], ...] = field(
        default=Factory(
            lambda: (
                openai.BadRequestError,
                openai.AuthenticationError,
                openai.PermissionDeniedError,
                openai.NotFoundError,
                openai.ConflictError,
                openai.UnprocessableEntityError,
            )
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            message = result.choices[0].message

            return PromptStackElement(
                content=[self.__message_to_prompt_stack_content(message)],
                role=message.role,
                usage=PromptStackElement.Usage(
                    input_tokens=result.usage.prompt_tokens, output_tokens=result.usage.completion_tokens
                ),
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        result = self.client.chat.completions.create(
            **self._base_params(prompt_stack), stream=True, stream_options={"include_usage": True}
        )

        for chunk in result:
            if chunk.usage is not None:
                yield DeltaPromptStackElement(
                    delta_usage=DeltaPromptStackElement.DeltaUsage(
                        input_tokens=chunk.usage.prompt_tokens, output_tokens=chunk.usage.completion_tokens
                    )
                )
            elif chunk.choices is not None:
                if len(chunk.choices) == 1:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    yield self.__message_delta_to_prompt_stack_content_delta(delta)
                else:
                    raise Exception("Completion with more than one choice is not supported yet.")

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        return [{"role": self.__to_role(input), "content": self.__to_content(input)} for input in prompt_stack.inputs]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "user": self.user,
            "seed": self.seed,
            **({"stop": self.tokenizer.stop_sequences} if self.tokenizer.stop_sequences else {}),
            **({"max_tokens": self.max_tokens} if self.max_tokens is not None else {}),
        }

        if self.response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
            # JSON mode still requires a system input instructing the LLM to output JSON.
            prompt_stack.add_system_input("Provide your response as a valid JSON object.")

        messages = self._prompt_stack_to_messages(prompt_stack)

        params["messages"] = messages

        return params

    def __to_role(self, input: PromptStackElement) -> str:
        if input.is_system():
            return "system"
        elif input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_content(self, input: PromptStackElement) -> str | list[dict]:
        if all(isinstance(content, TextPromptStackContent) for content in input.content):
            return input.to_text_artifact().to_text()
        else:
            return [self.__prompt_stack_content_message_content(content) for content in input.content]

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"type": "text", "text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{content.artifact.mime_type};base64,{content.artifact.base64}"},
            }
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __message_to_prompt_stack_content(self, message: ChatCompletionMessage) -> BasePromptStackContent:
        if message.content is not None:
            return TextPromptStackContent(TextArtifact(message.content))
        else:
            raise ValueError(f"Unsupported message type: {message}")

    def __message_delta_to_prompt_stack_content_delta(self, content_delta: ChoiceDelta) -> BaseDeltaPromptStackContent:
        if content_delta.content is not None:
            delta_content = content_delta.content

            return DeltaTextPromptStackContent(delta_content, role=content_delta.role)
        else:
            return DeltaTextPromptStackContent("", role=content_delta.role)
