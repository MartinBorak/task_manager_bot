import uuid
from dataclasses import dataclass
from typing import Self

from google.cloud.firestore_v1 import DocumentSnapshot

from enums import TaskStatus


@dataclass
class Task:
    id: str
    name: str
    deadline: str
    member: int
    status: TaskStatus

    def __init__(
        self,
        name: str,
        deadline: str,
        member: int,
        status: TaskStatus,
        id: str = None,
    ) -> None:
        self.id = id or str(uuid.uuid4())[:8]
        self.name = name
        self.deadline = deadline
        self.member = member
        self.status = status

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "deadline": self.deadline,
            "member": self.member,
            "status": self.status.value,
        }

    @classmethod
    def from_document(cls, document: DocumentSnapshot) -> Self:
        document_data = document.to_dict()

        return Task(
            id=document.id,
            name=document_data["name"],
            deadline=document_data["deadline"],
            member=document_data["member"],
            status=document_data["status"],
        )
