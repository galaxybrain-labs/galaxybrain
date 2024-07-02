import pytest
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import PromptGenerationRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestPromptGenerationRagModule:
    @pytest.fixture
    def module(self):
        return PromptGenerationRagModule(prompt_driver=MockPromptDriver())

    def test_run(self, module):
        assert module.run(RagContext(initial_query="test")).output.value == "mock output"

    def test_prompt(self, module):
        system_message = module.default_system_template_generator(
            text_chunks=["*TEXT SEGMENT 1*", "*TEXT SEGMENT 2*"],
            before_system_prompt=["*RULESET*", "*META*"],
            after_system_prompt=[],
        )

        assert "*RULESET*" in system_message
        assert "*META*" in system_message
        assert "*TEXT SEGMENT 1*" in system_message
        assert "*TEXT SEGMENT 2*" in system_message
