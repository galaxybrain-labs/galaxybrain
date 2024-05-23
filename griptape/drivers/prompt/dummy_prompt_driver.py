from collections.abc import Iterator
from typing import Optional
from attrs import field, Factory, define
from griptape.tokenizers import DummyTokenizer
from griptape.drivers import BasePromptDriver
from griptape.artifacts import TextArtifact
from griptape.exceptions import DummyException
from griptape.utils.prompt_stack import PromptStack


@define
class DummyPromptDriver(BasePromptDriver):
    model: Optional[str] = field(init=False)
    tokenizer: DummyTokenizer = field(default=Factory(lambda: DummyTokenizer()), kw_only=True)

    def __attrs_post_init__(self):
        self.model = None

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        raise DummyException(__class__.__name__, "try_run")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        raise DummyException(__class__.__name__, "try_stream")
