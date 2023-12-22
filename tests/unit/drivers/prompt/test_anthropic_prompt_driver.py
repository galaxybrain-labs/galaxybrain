from griptape.drivers import AnthropicPromptDriver
from griptape.utils import PromptStack
from griptape.tokenizers import AnthropicTokenizer
from unittest.mock import ANY, Mock
import pytest


class TestAnthropicPromptDriver:
    @pytest.fixture
    def mock_completion_create(self, mocker):
        mock_completion_create = mocker.patch("anthropic.Anthropic").return_value.completions.create
        mock_completion_create.return_value.completion = "model-output"
        return mock_completion_create

    @pytest.fixture
    def mock_completion_stream_create(self, mocker):
        mock_completion_create = mocker.patch("anthropic.Anthropic").return_value.completions.create
        mock_chunk = Mock()
        mock_chunk.completion = "model-output"
        mock_completion_create.return_value = iter([mock_chunk])
        return mock_completion_create

    @pytest.mark.parametrize("model", [("claude-2.1"), ("claude-2.0")])
    def test_init(self, model):
        assert AnthropicPromptDriver(model=model, api_key="1234")

    @pytest.mark.parametrize(
        "model,expected_prompt",
        [
            (
                "claude-2.1",
                [
                    "\n\nHuman: generic-input",
                    "system-input",
                    "\n\nHuman: user-input",
                    "\n\nAssistant: assistant-input",
                    "\n\nAssistant:",
                ],
            ),
            (
                "claude-2.0",
                [
                    "\n\nHuman: generic-input",
                    "\n\nHuman: system-input",
                    "\n\nAssistant:",
                    "\n\nHuman: user-input",
                    "\n\nAssistant: assistant-input",
                    "\n\nAssistant:",
                ],
            ),
        ],
    )
    def test_try_run(self, mock_completion_create, model, expected_prompt):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=model, api_key="api-key")

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_completion_create.assert_called_once_with(
            prompt="".join(expected_prompt),
            stop_sequences=ANY,
            model=driver.model,
            max_tokens_to_sample=ANY,
            temperature=ANY,
        )
        assert text_artifact.value == "model-output"

    @pytest.mark.parametrize(
        "model,expected_prompt",
        [
            (
                "claude-2.1",
                [
                    "\n\nHuman: generic-input",
                    "system-input",
                    "\n\nHuman: user-input",
                    "\n\nAssistant: assistant-input",
                    "\n\nAssistant:",
                ],
            ),
            (
                "claude-2.0",
                [
                    "\n\nHuman: generic-input",
                    "\n\nHuman: system-input",
                    "\n\nAssistant:",
                    "\n\nHuman: user-input",
                    "\n\nAssistant: assistant-input",
                    "\n\nAssistant:",
                ],
            ),
        ],
    )
    def test_try_stream_run(self, mock_completion_stream_create, model, expected_prompt):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=model, api_key="api-key", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_completion_stream_create.assert_called_once_with(
            prompt="".join(expected_prompt),
            stop_sequences=ANY,
            model=driver.model,
            max_tokens_to_sample=ANY,
            temperature=ANY,
            stream=driver.stream,
        )
        assert text_artifact.value == "model-output"

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        prompt_stack = "prompt-stack"
        driver = AnthropicPromptDriver(model=AnthropicTokenizer.DEFAULT_MODEL, api_key="api-key")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"
