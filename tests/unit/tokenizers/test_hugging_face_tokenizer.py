from os import environ

environ["TRANSFORMERS_VERBOSITY"] = "error"

import pytest  # noqa: E402
from griptape.utils import PromptStack  # noqa: E402
from transformers import GPT2Tokenizer  # noqa: E402
from griptape.tokenizers import HuggingFaceTokenizer  # noqa: E402


class TestHuggingFaceTokenizer:
    @pytest.fixture
    def tokenizer(self):
        return HuggingFaceTokenizer(tokenizer=GPT2Tokenizer.from_pretrained("gpt2"), max_output_tokens=1024)

    def test_token_count(self, tokenizer):
        assert (
            tokenizer.count_tokens(PromptStack(inputs=[PromptStack.Input(content="foo bar huzzah", role="user")])) == 6
        )
        assert tokenizer.count_tokens("foo bar huzzah") == 5

    def test_input_tokens_left(self, tokenizer):
        assert tokenizer.count_input_tokens_left("foo bar huzzah") == 1019

    def test_output_tokens_left(self, tokenizer):
        assert tokenizer.count_output_tokens_left("foo bar huzzah") == 1019
