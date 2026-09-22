from enum import Enum
from dataclasses import dataclass


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


@dataclass
class Task:
    id: int
    name: str
    created_at: str
    updated_at: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
