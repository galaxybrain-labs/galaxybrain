import base64
import pytest
from griptape.artifacts import BlobArtifact, BaseArtifact
from griptape.schemas import BlobArtifactSchema


class TestBlobArtifact:
    def test_value_type_conversion(self):
        assert BlobArtifact(1).value == b"1"

    def test_to_text(self):
        assert BlobArtifact(b"foobar", name="foobar.txt", dir_name="foo").to_text() == "foo/foobar.txt"

    def test_to_dict(self):
        assert BlobArtifact(b"foobar", name="foobar.txt", dir_name="foo").to_dict()["name"] == "foobar.txt"

    def test_full_path_with_path(self):
        assert BlobArtifact(b"foobar", name="foobar.txt", dir_name="foo").full_path == "foo/foobar.txt"

    def test_full_path_without_path(self):
        assert BlobArtifact(b"foobar", name="foobar.txt").full_path == "foobar.txt"

    def test_serialization(self):
        artifact = BlobArtifact(b"foobar", name="foobar.txt", dir_name="foo")
        artifact_dict = BlobArtifactSchema().dump(artifact)

        assert artifact_dict["name"] == "foobar.txt"
        assert artifact_dict["dir_name"] == "foo"
        assert base64.b64decode(artifact_dict["value"]) == b"foobar"

    def test_deserialization(self):
        artifact = BlobArtifact(b"foobar", name="foobar.txt", dir_name="foo")
        artifact_dict = BlobArtifactSchema().dump(artifact)
        deserialized_artifact: BlobArtifact = BaseArtifact.from_dict(artifact_dict)

        assert deserialized_artifact.name == "foobar.txt"
        assert deserialized_artifact.dir_name == "foo"
        assert deserialized_artifact.value == b"foobar"

    def test_name(self):
        assert BlobArtifact(b"foo", name="bar").name == "bar"
