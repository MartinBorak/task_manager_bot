from dataclasses import dataclass
from typing import Self

from google.cloud.firestore_v1 import DocumentSnapshot

from enums import TaskStatus


@dataclass
class Task:
    name: str
    deadline: str
    member: int
    status: TaskStatus

    def to_dict(self) -> dict:
        return {
            "deadline": self.deadline,
            "member": self.member,
            "status": self.status.value,
        }

    @classmethod
    def from_document(cls, document: DocumentSnapshot) -> Self:
        document_data = document.to_dict()

        return Task(
            name=document.id,
            deadline=document_data["deadline"],
            member=document_data["member"],
            status=document_data["status"],
        )
