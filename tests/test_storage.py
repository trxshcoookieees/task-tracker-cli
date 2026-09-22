import json
from datetime import datetime

from taskcli import storage
from taskcli.models import Task, TaskStatus

current_time = datetime.now().isoformat()
data = [
    Task(
        id=1,
        name="Task 1",
        description="Task 1",
        status=TaskStatus.TODO,
        created_at=current_time,
        updated_at=current_time,
    ),
    Task(
        id=2,
        name="Task 2",
        description="Task 2",
        status=TaskStatus.DONE,
        created_at=current_time,
        updated_at=current_time,
    )
]


def test_save_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    storage.save_tasks(data)
    assert storage.TASKS_FILE.exists()
    assert storage.load_tasks() == data


def test_load_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = [
        {
            "id": 1,
            "name": "Task 1",
            "description": "Task 1",
            "status": "todo",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "id": 2,
            "name": "Task 2",
            "description": "Task 2",
            "status": "done",
            "created_at": current_time,
            "updated_at": current_time,
        }
    ]

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    assert len(tasks) == 2
    assert isinstance(tasks[0], Task)
    assert isinstance(tasks[0].status, TaskStatus)
    assert tasks[0].status == TaskStatus.TODO
    assert tasks[1].status == TaskStatus.DONE
