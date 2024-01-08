from unittest.mock import Mock

import pytest

from griptape.artifacts import TextArtifact
from griptape.engines.image.image_generation_engine import ImageGenerationEngine

from griptape.rules import Rule, Ruleset
from tests.mocks.mock_image_generation_task import MockImageGenerationTask


class TestBaseImageGenerationTask:
    @pytest.fixture
    def engine(self):
        return Mock()

    def test_validate_negative_rulesets(self, engine: ImageGenerationEngine):
        with pytest.raises(ValueError):
            MockImageGenerationTask(
                TextArtifact("some input"),
                image_generation_engine=engine,
                negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
                negative_rules=[Rule(value="Negative Rule")],
                output_dir="some/dir",
            )

        assert MockImageGenerationTask(
            TextArtifact("some input"),
            image_generation_engine=engine,
            negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
            output_dir="some/dir",
        )

    def test_validate_negative_rules(self, engine: ImageGenerationEngine):
        with pytest.raises(ValueError):
            MockImageGenerationTask(
                TextArtifact("some input"),
                image_generation_engine=engine,
                negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
                negative_rules=[Rule(value="Negative Rule")],
                output_dir="some/dir",
            )

        assert MockImageGenerationTask(
            TextArtifact("some input"),
            image_generation_engine=engine,
            negative_rules=[Rule(value="Negative Rule")],
            output_dir="some/dir",
        )

    def test_all_negative_rulesets_from_rulesets(self, engine: ImageGenerationEngine):
        ruleset = Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])

        task = MockImageGenerationTask(
            TextArtifact("some input"),
            image_generation_engine=engine,
            negative_rulesets=[ruleset],
            output_dir="some/dir",
        )

        assert task.all_negative_rulesets[0] == ruleset

    def test_all_negative_rulesets_from_rules(self, engine: ImageGenerationEngine):
        rule = Rule(value="Negative Rule")

        task = MockImageGenerationTask(
            TextArtifact("some input"), image_generation_engine=engine, negative_rules=[rule], output_dir="some/dir"
        )

        assert task.all_negative_rulesets[0].name == task.NEGATIVE_RULESET_NAME
        assert task.all_negative_rulesets[0].rules[0] == rule

    def test_validate_output_dir(self, engine: ImageGenerationEngine):
        with pytest.raises(ValueError):
            MockImageGenerationTask(
                TextArtifact("some input"),
                image_generation_engine=engine,
                output_dir="some/dir",
                output_file="some/file",
            )
