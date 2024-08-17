import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.unit.drivers.vector.test_base_local_vector_store_driver import BaseLocalVectorStoreDriver


class TestLocalVectorStoreDriver(BaseLocalVectorStoreDriver):
    @pytest.fixture()
    def driver(self):
        return LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver())

    def test_upsert_text_artifacts_dict(self, driver):
        driver.upsert_text_artifacts({"foo": [TextArtifact("bar"), TextArtifact("baz")], "bar": [TextArtifact("bar")]})

        assert len(driver.load_artifacts(namespace="foo")) == 2
        assert len(driver.load_artifacts(namespace="bar")) == 1

    def test_upsert_text_artifacts_list(self, driver):
        driver.upsert_text_artifacts([TextArtifact("bar"), TextArtifact("baz")])

        assert len(driver.load_artifacts(namespace="foo")) == 0
        assert len(driver.load_artifacts()) == 2

    def test_upsert_text_artifacts_stress_test(self, driver):
        driver.upsert_text_artifacts(
            {
                "test1": [TextArtifact(f"foo-{i}") for i in range(0, 1000)],
                "test2": [TextArtifact(f"foo-{i}") for i in range(0, 1000)],
                "test3": [TextArtifact(f"foo-{i}") for i in range(0, 1000)]
            }
        )

        assert len(driver.query("foo", namespace="test1")) == 1000
        assert len(driver.query("foo", namespace="test2")) == 1000
        assert len(driver.query("foo", namespace="test3")) == 1000
