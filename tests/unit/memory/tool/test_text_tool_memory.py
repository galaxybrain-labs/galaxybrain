from griptape.artifacts import TextArtifact, ListArtifact
from griptape.drivers import MemoryTextToolMemoryDriver
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_tool.tool import MockTool


class TestTextToolMemory:
    def test_init(self):
        memory = TextToolMemory(
            name="MyMemory",
            driver=MemoryTextToolMemoryDriver()
        )

        assert memory.name == "MyMemory"

    def test_allowlist(self):
        assert len(TextToolMemory().activities()) == 1
        assert TextToolMemory().activities()[0].__name__ == "save"

    def test_process_output(self):
        memory = TextToolMemory(
            name="MyMemory",
            driver=MemoryTextToolMemoryDriver()
        )

        assert memory.process_output(MockTool().test, TextArtifact("foo")).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names'
        )

    def test_process_output_with_many_artifacts(self):
        memory = TextToolMemory(
            name="MyMemory",
            driver=MemoryTextToolMemoryDriver()
        )

        assert memory.process_output(MockTool().test, ListArtifact([TextArtifact("foo")])).to_text().startswith(
            'Output of "MockTool.test" was stored in memory "MyMemory" with the following artifact names'
        )

    def test_save_and_load_value(self):
        memory = TextToolMemory()
        output = memory.save({"values": {"artifact_value": "foobar"}})
        name = output.value.split(":")[-1].strip()

        assert memory.load({"values": {"artifact_name": name}}).value == "foobar"

