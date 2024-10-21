from attrs import define, field

from griptape.events.base_chunk_event import BaseChunkEvent


@define
class MockChunkEvent(BaseChunkEvent):
    token: str = field(kw_only=True, metadata={"serializable": True})

    def __str__(self) -> str:
        return "mock " + self.token
