from __future__ import annotations
from collections.abc import Iterator
from attrs import define

from griptape.artifacts import TextArtifact
from griptape.common import PromptStack, Message, TextPromptStackContent, DeltaMessage, TextDeltaPromptStackContent
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer


@define
class MockFailingPromptDriver(BasePromptDriver):
    max_failures: int
    current_attempt: int = 0
    model: str = "test-model"
    tokenizer: BaseTokenizer = OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)

    def try_run(self, prompt_stack: PromptStack) -> Message:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception("failed attempt")
        else:
            return Message(
                content=[TextPromptStackContent(TextArtifact("success"))],
                role=Message.ASSISTANT_ROLE,
                usage=Message.Usage(input_tokens=100, output_tokens=100),
            )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception("failed attempt")
        else:
            yield DeltaMessage(
                content=TextDeltaPromptStackContent("success"),
                usage=DeltaMessage.Usage(input_tokens=100, output_tokens=100),
            )
