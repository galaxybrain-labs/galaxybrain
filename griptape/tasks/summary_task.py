from __future__ import annotations
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.engines import BaseSummaryEngine, PromptSummaryEngine
from griptape.structures import Structure
from griptape.tasks import BaseTextInputTask


@define
class SummaryTask(BaseTextInputTask):
    summary_engine: BaseSummaryEngine = field(
        kw_only=True,
        default=Factory(lambda: PromptSummaryEngine())
    )

    def run(self) -> TextArtifact:
        return TextArtifact(
            self.summary_engine.summarize_text(self.input.to_text())
        )
