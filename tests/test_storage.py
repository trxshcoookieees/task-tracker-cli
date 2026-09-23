import json
import pytest
from datetime import datetime

from taskcli import storage
from taskcli.models import Task, TaskStatus

current_time = datetime.now().isoformat()


@pytest.fixture
def tasks_file(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(storage, "TASKS_FILE", tasks_file)
    return tasks_file


@pytest.fixture
def write_json(tasks_file):
    def _write_json(data):
        with tasks_file.open("w") as file:
            json.dump(data, file)

    return _write_json


def test_save_tasks(tasks_file):
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

    storage.save_tasks(data)

    assert tasks_file.exists()
    assert storage.load_tasks() == data


def test_load_tasks(write_json):
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

    write_json(json_data)

    tasks = storage.load_tasks()
    assert len(tasks) == 2
    assert isinstance(tasks[0], Task)
    assert isinstance(tasks[0].status, TaskStatus)
    assert tasks[0].status == TaskStatus.TODO
    assert tasks[1].status == TaskStatus.DONE


def test_load_tasks_with_invalid_json_structure(write_json, capsys):
    json_data = {
        "hello": "world"
    }

    write_json(json_data)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Error: task file has invalid structure" in captured.out


def test_load_tasks_with_invalid_task_element(write_json, capsys):
    json_data = [
        "hello"
    ]

    write_json(json_data)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


def test_load_tasks_with_incomplete_task(write_json, capsys):
    json_data = [
        {
            "id": 1,
            "name": "Task 1"
        }
    ]

    write_json(json_data)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


@pytest.mark.parametrize(
    "json_data",
    [
        [
            {
                "id": 1,
                "status": "done",
                "created_at": current_time,
                "updated_at": current_time
            }
        ],
        [
            {
                "id": 1,
                "name": "Task 1",
                "created_at": current_time,
                "updated_at": current_time
            }
        ],
    ]
)
def test_load_tasks_with_missing_required_field(json_data, write_json, capsys):
    write_json(json_data)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


def test_load_tasks_with_invalid_task_status(write_json, capsys):
    json_data = [
        {
            "id": 1,
            "status": "bullshit",
            "created_at": current_time,
            "updated_at": current_time
        }
    ]

    write_json(json_data)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert tasks == []
    assert "Warning: Invalid task at index 0, skipped" in captured.out


def test_load_tasks_skips_invalid_task_and_loads_valid_tasks(write_json, capsys):
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

    write_json(json_data)

    tasks = storage.load_tasks()
    captured = capsys.readouterr()

    assert len(tasks) == 2
    assert tasks[0].id == 1
    assert tasks[1].id == 3
    assert "Warning: Invalid task at index 1, skipped" in captured.out
