from datetime import datetime
from taskcli.storage import load_tasks, save_tasks
from taskcli.models import Task, TaskStatus


def add_task(name: str, description: str | None) -> None:
    tasks = load_tasks()
    new_id = max((task.id for task in tasks), default=0) + 1
    date_now = datetime.now().isoformat()
    new_task = Task(
        id=new_id,
        name=name,
        description=description,
        created_at=date_now,
        updated_at=date_now
    )
    tasks.append(new_task)
    save_tasks(tasks)

    print(f"Task added successfully (ID: {new_id})")


def update_task(task_id: int, name: str | None, description: str | None) -> None:
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Task not found (ID: {task_id})")
        return

    if name is not None:
        task.name = name
    if description is not None:
        task.description = description
    task.updated_at = datetime.now().isoformat()
    save_tasks(tasks)
    print(f"Task updated successfully (ID: {task_id})")


def delete_task(task_id: int) -> None:
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Task not found (ID: {task_id})")
        return

    tasks.remove(task)
    save_tasks(tasks)
    print(f"Task deleted successfully (ID: {task_id})")


def list_tasks(status: TaskStatus | None) -> None:
    tasks = load_tasks()
    print("-------TASKS--------")
    if status:
        print(f"Filter: {status}\n")
        tasks = [
            task for task in tasks
            if task.status == status
        ]
    for task in tasks:
        updated_at = datetime.fromisoformat(task.updated_at)
        print("--------------------")
        print(f"{task.id}: {task.name}")
        print(f"Description: {task.description}")
        print(f"Status: {task.status.value}")
        print(f"Last change: {updated_at.strftime("%d %B %Y, %H:%M")}")

    print("--------------------")


def mark_status(task_id: int, status: TaskStatus) -> None:
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Task not found (ID: {task_id})")
        return

    update_status(task, status)
    save_tasks(tasks)
    print(f"Task updated successfully (ID: {task_id})")


def update_status(task: Task, status: TaskStatus) -> None:
    task.status = status
    task.updated_at = datetime.now().isoformat()


def find_task(tasks: list[Task], task_id: int) -> Task | None:
    return next(
        (task for task in tasks if task.id == task_id),
        None
    )
