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


def test_load_tasks_with_invalid_json_structure(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = {
        "hello": "world"
    }

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Error: task file has invalid structure" in captured.out


def test_load_tasks_with_invalid_task_element(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = [
        "hello"
    ]

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


def test_load_tasks_with_incomplete_task(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = [
        {
            "id": 1,
            "name": "Task 1"
        }
    ]

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


def test_load_tasks_with_missing_required_field(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = [
        {
            "id": 1,
            "status": "done",
            "created_at": current_time,
            "updated_at": current_time
        }
    ]

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out

def test_load_tasks_with_invalid_task_status(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = [
        {
            "id": 1,
            "status": "bullshit",
            "created_at": current_time,
            "updated_at": current_time
        }
    ]

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


def test_load_tasks_skips_invalid_task_and_loads_valid_tasks(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "TASKS_FILE", tmp_path / "tasks.json")

    json_data = [
        {
            "id": 1,
            "name": "Valid task",
            "status": "todo",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "id": 2,
            "name": "Broken task",
            "status": "banana",
            "created_at": current_time,
            "updated_at": current_time,
        },
        {
            "id": 3,
            "name": "Another valid task",
            "status": "done",
            "created_at": current_time,
            "updated_at": current_time,
        },
    ]

    with storage.TASKS_FILE.open("w") as file:
        json.dump(json_data, file)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert len(tasks) == 2
    assert tasks[0].id == 1
    assert tasks[1].id == 3
    assert "Warning: Invalid task at index 1, skipped" in captured.out