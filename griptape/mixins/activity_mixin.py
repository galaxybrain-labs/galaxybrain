from __future__ import annotations

import inspect
from copy import deepcopy
from typing import Callable, Optional

import jsonschema
from attrs import Attribute, define, field
from jinja2 import Template
from schema import Schema


@define(slots=False)
class ActivityMixin:
    """Provides Tool Activity management functionality to Tools.

    Attributes:
        allowlist: List of Tool Activities to include in the Tool schema.
        denylist: List of Tool Activities to remove from the Tool schema.
        extra_schema_properties: Mapping of Activity name and extra properties to include in the activity's schema.
    """

    allowlist: Optional[list[str]] = field(default=None, kw_only=True)
    denylist: Optional[list[str]] = field(default=None, kw_only=True)
    extra_schema_properties: Optional[dict[str, dict]] = field(default=None, kw_only=True)

    @allowlist.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_allowlist(self, _: Attribute, allowlist: Optional[list[str]]) -> None:
        if allowlist is None:
            return

        if self.denylist is not None:
            raise ValueError("can't have both allowlist and denylist specified")

        for activity_name in allowlist:
            self._validate_tool_activity(activity_name)

    @denylist.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_denylist(self, _: Attribute, denylist: Optional[list[str]]) -> None:
        if denylist is None:
            return

        if self.allowlist is not None:
            raise ValueError("can't have both allowlist and denylist specified")

        for activity_name in denylist:
            self._validate_tool_activity(activity_name)

    def enable_activities(self) -> None:
        self.allowlist = None
        self.denylist = None

    def disable_activities(self) -> None:
        self.allowlist = []
        self.denylist = None

    # This method has to remain a method and can't be decorated with @property because
    # of the max depth recursion issue in `inspect.getmembers`.
    def activities(self) -> list[Callable]:
        methods = []

        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            allowlist_condition = self.allowlist is None or name in self.allowlist
            denylist_condition = self.denylist is None or name not in self.denylist

            if getattr(method, "is_activity", False) and allowlist_condition and denylist_condition:
                methods.append(method)

        return methods

    def find_activity(self, name: str) -> Optional[Callable]:
        for activity in self.activities():
            if getattr(activity, "is_activity", False) and getattr(activity, "name") == name:
                return activity

        return None

    def activity_name(self, activity: Callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not an activity.")
        return getattr(activity, "name")

    def activity_description(self, activity: Callable) -> str:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not an activity.")
        return Template(getattr(activity, "config")["description"]).render({"_self": self})

    def activity_schema(self, activity: Callable) -> Optional[Schema | dict]:
        if activity is None or not getattr(activity, "is_activity", False):
            raise Exception("This method is not an activity.")
        if getattr(activity, "config")["schema"] is not None:
            config_schema = getattr(activity, "config")["schema"]
            if isinstance(config_schema, Callable):
                config_schema = config_schema(self)
            else:
                # Need to deepcopy to avoid modifying the original schema
                config_schema = deepcopy(getattr(activity, "config")["schema"])
            activity_name = self.activity_name(activity)

            if self.extra_schema_properties is not None and activity_name in self.extra_schema_properties:
                config_schema.schema.update(self.extra_schema_properties[activity_name])

            return Schema({"values": config_schema})
        else:
            return None

    def validate_schema(self, activity: Callable, schema: dict) -> None:
        activity_schema = self.activity_schema(activity)

        if activity_schema is None:
            return

        json_schema = schema.json_schema("Schema") if isinstance(schema, Schema) else schema

        jsonschema.validate(schema, json_schema)

    def _validate_tool_activity(self, activity_name: str) -> None:
        tool = self.__class__

        activity = getattr(tool, activity_name, None)

        if not activity or not getattr(activity, "is_activity", False):
            raise ValueError(f"activity {activity_name} is not a valid activity for {tool}")
