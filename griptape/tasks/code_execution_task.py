from __future__ import annotations

from typing import Callable, TypeVar, Union

from attrs import define, field

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tasks.base_task import BaseTask
from griptape.utils import J2, deprecation_warn

T = TypeVar("T", bound=BaseArtifact)  # Return type of task


@define
class CodeExecutionTask(BaseTask[T]):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"
    _input: Union[str, TextArtifact, Callable[[BaseTask], TextArtifact]] = field(
        default=DEFAULT_INPUT_TEMPLATE,
        alias="input",
    )
    on_run: Callable[[CodeExecutionTask[T]], T] = field(kw_only=True)

    @property
    def input(self) -> TextArtifact:
        deprecation_warn("CodeExecutionTask.input is deprecated and will be removed in a future release.")
        if isinstance(self._input, TextArtifact):
            return self._input
        elif callable(self._input):
            return self._input(self)
        else:
            return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    def try_run(self) -> T:
        return self.on_run(self)
