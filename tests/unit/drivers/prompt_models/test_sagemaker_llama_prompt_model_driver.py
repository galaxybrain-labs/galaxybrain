import boto3
import pytest
from griptape.utils import PromptStack
from griptape.drivers import AmazonSageMakerPromptDriver, SageMakerLlamaPromptModelDriver


class TestSageMakerLlamaPromptModelDriver:
    @pytest.fixture(autouse=True)
    def tokenizer(self, mocker):
        from_pretrained = tokenizer = mocker.patch("transformers.AutoTokenizer").from_pretrained
        from_pretrained.return_value.apply_chat_template.return_value = [1, 2, 3]
        from_pretrained.return_value.decode.return_value = "model-output"
        from_pretrained.return_value.model_max_length = 8000

        return tokenizer

    @pytest.fixture
    def driver(self):
        return AmazonSageMakerPromptDriver(
            endpoint="endpoint-name",
            model="inference-component-name",
            session=boto3.Session(region_name="us-east-1"),
            prompt_model_driver=SageMakerLlamaPromptModelDriver(),
            temperature=0.12345,
            max_tokens=7991,
        ).prompt_model_driver

    @pytest.fixture
    def stack(self):
        stack = PromptStack()

        stack.add_system_input("foo")
        stack.add_user_input("bar")

        return stack

    def test_init(self, driver):
        assert driver.prompt_driver is not None

    def test_prompt_stack_to_model_input(self, driver, stack):
        result = driver.prompt_stack_to_model_input(stack)

        driver.tokenizer.tokenizer.apply_chat_template.assert_called_once_with(
            [{"role": "system", "content": "foo"}, {"role": "user", "content": "bar"}],
            tokenize=True,
            add_generation_prompt=True,
        )

        assert result == "model-output"

    def test_prompt_stack_to_model_params(self, driver, stack):
        assert driver.prompt_stack_to_model_params(stack)["max_new_tokens"] == 7991
        assert driver.prompt_stack_to_model_params(stack)["temperature"] == 0.12345

    def test_process_output(self, driver, stack):
        assert driver.process_output({"generated_text": "foobar"}).value == "foobar"

    def test_process_output_invalid_format(self, driver, stack):
        with pytest.raises(ValueError):
            assert driver.process_output([{"generated_text": "foobar"}])

    def test_tokenizer_max_model_length(self, driver):
        assert driver.tokenizer.tokenizer.model_max_length == 8000
