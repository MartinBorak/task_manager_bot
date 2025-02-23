from enum import Enum
from typing import Self


class TaskStatus(Enum):
    TO_DO = 1
    DOING = 2
    DONE = 3

    @classmethod
    def all(cls) -> list[Self]:
        return [
            TaskStatus.TO_DO,
            TaskStatus.DOING,
            TaskStatus.DONE,
        ]

    @classmethod
    def from_string(cls, value: str) -> Self | None:
        match value.lower():
            case "to_do" | "to do":
                return TaskStatus.TO_DO
            case "doing":
                return TaskStatus.DOING
            case "done":
                return TaskStatus.DONE
            case _:
                return None

    def to_string(self) -> str | None:
        match self:
            case TaskStatus.TO_DO:
                return "To do"
            case TaskStatus.DOING:
                return "Doing"
            case TaskStatus.DONE:
                return "Done"
            case _:
                return None
