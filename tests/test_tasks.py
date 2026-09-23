import pytest
from datetime import datetime

from taskcli import storage
from taskcli.models import Task, TaskStatus
from taskcli.tasks import (
    find_task,
    add_task,
    mark_status,
    update_task,
    delete_task,
    list_tasks
)


@pytest.fixture
def tasks_file(tmp_path, monkeypatch):
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(storage, "TASKS_FILE", tasks_file)
    return tasks_file


@pytest.fixture
def tasks() -> list[Task]:
    current_time = datetime.now().isoformat()

    return [
        Task(
            id=1,
            name="Task 1",
            description="Task 1",
            created_at=current_time,
            updated_at=current_time,
        ),
        Task(
            id=2,
            name="Task 2",
            description="Task 2",
            created_at=current_time,
            updated_at=current_time,
        )
    ]


@pytest.fixture
def prepared_tasks(tasks_file, tasks):
    for task in tasks:
        add_task(task.name, task.description)


def test_find_existing_task(tasks):
    result = find_task(tasks, 2)

    assert result is not None
    assert result.id == 2
    assert result.name == "Task 2"


def test_find_missing_task(tasks):
    result = find_task(tasks, 1234)

    assert result is None


def test_add_task(tasks_file):
    add_task("New task", "New description")

    result = storage.load_tasks()

    assert len(result) == 1
    assert result[0].name == "New task"
    assert result[0].description == "New description"
    assert result[0].status == TaskStatus.TODO


def test_mark_status(prepared_tasks):
    mark_status(1, TaskStatus.DONE)
    mark_status(2, TaskStatus.IN_PROGRESS)

    result = storage.load_tasks()

    assert len(result) == 2
    assert result[0].status == TaskStatus.DONE
    assert result[1].status == TaskStatus.IN_PROGRESS


def test_mark_status_on_missing_task(prepared_tasks):
    mark_status(1234, TaskStatus.DONE)
    result = storage.load_tasks()
    assert len(result) == 2
    assert result[0].status == TaskStatus.TODO
    assert result[1].status == TaskStatus.TODO


def test_update_task(prepared_tasks):
    update_task(1, "updated name", "updated description")
    update_task(2, "updated name", None)

    result = storage.load_tasks()

    assert len(result) == 2
    assert result[0].name == "updated name"
    assert result[0].description == "updated description"
    assert result[1].name == "updated name"
    assert result[1].description == "Task 2"


def test_update_missing_task(prepared_tasks):
    update_task(1234, "updated name", "updated description")

    result = storage.load_tasks()

    assert len(result) == 2
    assert result[0].name == "Task 1"
    assert result[0].description == "Task 1"
    assert result[1].name == "Task 2"
    assert result[1].description == "Task 2"


def test_delete_task(prepared_tasks):
    delete_task(2)

    result = storage.load_tasks()

    assert len(result) == 1
    assert result[0].name == "Task 1"
    assert result[0].description == "Task 1"


def test_delete_missing_task(prepared_tasks):
    delete_task(1234)

    result = storage.load_tasks()

    assert len(result) == 2
    assert result[0].name == "Task 1"
    assert result[1].name == "Task 2"


def test_list_tasks(prepared_tasks, capsys):
    list_tasks(None)

    captured = capsys.readouterr()
    assert "1: Task 1" in captured.out
    assert "2: Task 2" in captured.out

    mark_status(1, TaskStatus.DONE)

    list_tasks(TaskStatus.DONE)

    captured = capsys.readouterr()
    assert "1: Task 1" in captured.out
    assert "2: Task 2" not in captured.out
