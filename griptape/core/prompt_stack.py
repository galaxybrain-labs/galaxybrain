from dataclasses import dataclass
from typing import Optional
from attr import define, field, Factory


@define
class PromptStack:
    USER_ROLE = "user"
    ASSISTANT_ROLE = "assistant"
    SYSTEM_ROLE = "system"

    @dataclass
    class Input:
        content: str
        role: str

        def is_system(self) -> bool:
            return self.role == PromptStack.SYSTEM_ROLE

        def is_user(self) -> bool:
            return self.role == PromptStack.USER_ROLE

        def is_assistant(self) -> bool:
            return self.role == PromptStack.ASSISTANT_ROLE

    initial_input: Optional[Input] = field(default=None)
    inputs: list[Input] = field(
        default=Factory(lambda self: [self.initial_input] if self.initial_input else []),
        kw_only=True
    )

    def add_input(self, content: str, role: str) -> Input:
        self.inputs.append(
            self.Input(
                content=content,
                role=role
            )
        )

        return self.inputs[-1]

    def add_system_input(self, content: str) -> Input:
        return self.add_input(content, self.SYSTEM_ROLE)

    def add_user_input(self, content: str) -> Input:
        return self.add_input(content, self.USER_ROLE)

    def add_assistant_input(self, content: str) -> Input:
        return self.add_input(content, self.ASSISTANT_ROLE)
