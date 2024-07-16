import pytest

from griptape.artifacts import BooleanArtifact


class TestBooleanArtifact:
    def test_parse_bool(self):
        assert BooleanArtifact.parse_bool("true").value is True
        assert BooleanArtifact.parse_bool("false").value is False
        assert BooleanArtifact.parse_bool("True").value is True
        assert BooleanArtifact.parse_bool("False").value is False

        with pytest.raises(ValueError):
            BooleanArtifact.parse_bool("foo")

        with pytest.raises(ValueError):
            BooleanArtifact.parse_bool(None)

        assert BooleanArtifact.parse_bool(True).value is True
        assert BooleanArtifact.parse_bool(False).value is False

    def test_add(self):
        with pytest.raises(ValueError):
            BooleanArtifact(True) + BooleanArtifact(True)

    def test_value_type_conversion(self):
        assert BooleanArtifact(1).value is True
        assert BooleanArtifact(0).value is False
        assert BooleanArtifact(True).value is True
        assert BooleanArtifact(False).value is False
        assert BooleanArtifact("true").value is True
        assert BooleanArtifact("false").value is True
        assert BooleanArtifact([1]).value is True
        assert BooleanArtifact([]).value is False
        assert BooleanArtifact(False).value is False
        assert BooleanArtifact(True).value is True
