from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from .drivers.base_driver_config import BaseDriverConfig
    from .logging.logging_config import LoggingConfig


@define(kw_only=True)
class BaseConfig(SerializableMixin, ABC):
    _logging: Optional[LoggingConfig] = field(alias="logging")
    _drivers: Optional[BaseDriverConfig] = field(alias="drivers")

    def reset(self) -> None:
        self._logging = None
        self._drivers = None
