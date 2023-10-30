import pytest
from griptape.api import ApiGenerator
from griptape.artifacts import BaseArtifact
from tests.mocks.mock_tool.tool import MockTool


class TestApiGenerator:
    @pytest.fixture
    def generator(self):
        return ApiGenerator("localhost:3000", tool=MockTool())

    def test_full_host_path(self):
        assert ApiGenerator("localhost:3000", tool=MockTool()).full_host_path == "localhost:3000"
        assert ApiGenerator(
            "localhost:3000",
            tool=MockTool(),
            path_prefix="foobar"
        ).full_host_path == "localhost:3000/foobar"

    def test_generate_yaml_api_spec(self, generator):
        spec = generator.generate_yaml_api_spec()

        assert spec.startswith("components:\n  schemas:\n    HTTPValidationError")
        assert "test" in spec
        assert "test_error" in spec
        assert "test_str_output" in spec
        assert spec.endswith("description: Validation Error\n      summary: Partial\n")

    def test_generate_json_api_spec(self, generator):
        spec = generator.generate_json_api_spec()

        assert spec.startswith('{"openapi": "3.1.0", "info": {"title": "MockTool API"')
        assert "test" in spec
        assert "test_error" in spec
        assert "test_str_output" in spec
        assert spec.endswith('"required": ["loc", "msg", "type"], "title": "ValidationError"}}}}')

    def test_generate_api(self, generator):
        api = generator.generate_api()

        assert api.title == "MockTool API"
        assert len(api.routes) == 10

    def test_execute_activity(self, generator):
        activity = generator.tool.test

        assert BaseArtifact.from_dict(
            generator.execute_activity(activity, {"values": {"test": "foobar"}})
        ).value == "ack foobar"
