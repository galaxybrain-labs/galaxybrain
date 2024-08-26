from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.drivers import BaseConversationMemoryDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    import boto3

    from griptape.memory.structure import Run


@define
class AmazonDynamoDbConversationMemoryDriver(BaseConversationMemoryDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    table_name: str = field(kw_only=True, metadata={"serializable": True})
    partition_key: str = field(kw_only=True, metadata={"serializable": True})
    value_attribute_key: str = field(kw_only=True, metadata={"serializable": True})
    partition_key_value: str = field(kw_only=True, metadata={"serializable": True})
    sort_key: Optional[str] = field(default=None, metadata={"serializable": True})
    sort_key_value: Optional[str | int] = field(default=None, metadata={"serializable": True})

    table: Any = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.table = self.session.resource("dynamodb").Table(self.table_name)

    def store(self, runs: list[Run], metadata: dict) -> None:
        self.table.update_item(
            Key=self._get_key(),
            UpdateExpression="set #attr = :value",
            ExpressionAttributeNames={"#attr": self.value_attribute_key},
            ExpressionAttributeValues={
                ":value": json.dumps(self._to_params_dict(runs, metadata)),
            },
        )

    def load(self) -> tuple[list[Run], dict[str, Any]]:
        response = self.table.get_item(Key=self._get_key())

        if "Item" in response and self.value_attribute_key in response["Item"]:
            memory_dict = json.loads(response["Item"][self.value_attribute_key])
            return self._from_params_dict(memory_dict)
        else:
            return [], {}

    def _get_key(self) -> dict[str, str | int]:
        key: dict[str, str | int] = {self.partition_key: self.partition_key_value}

        if self.sort_key is not None and self.sort_key_value is not None:
            key[self.sort_key] = self.sort_key_value

        return key
