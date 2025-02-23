import json
import os
from typing import Any

from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1 import (
    CollectionReference,
    DocumentReference,
    DocumentSnapshot,
)
from google.cloud.firestore_v1.stream_generator import StreamGenerator
from google.cloud.firestore_v1.types import WriteResult

from models import Task

COLLECTION_NAME = "tasks"

firebase_credentials = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(firebase_credentials)
initialize_app(cred)

db = firestore.client()


def db_get_collection() -> CollectionReference:
    return db.collection(COLLECTION_NAME)


def db_get_stream() -> StreamGenerator[DocumentSnapshot]:
    return db_get_collection().stream()


def db_get_document(document_id: str) -> DocumentReference:
    return db_get_collection().document(document_id)


async def db_add_document(document_id: str, data: dict) -> WriteResult:
    return db_get_document(document_id).set(data)


async def db_update_document(document_id: str, update_data: dict) -> WriteResult:
    return db_get_document(document_id).update(update_data)


async def db_delete_document(document_id: str) -> Any:
    return db_get_document(document_id).delete()


def get_all_tasks() -> list[Task]:
    return [Task.from_document(document) for document in db_get_stream()]


def get_task(task_id: str) -> Task | None:
    document = db_get_document(task_id).get()
    return Task.from_document(document) if document.exists else None
