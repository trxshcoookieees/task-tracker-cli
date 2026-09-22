import argparse
import json
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path


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


TASKS_FILE = Path.home() / "taskcli.json"


def load_tasks() -> list[Task]:
    if not TASKS_FILE.exists():
        return []
    try:
        with TASKS_FILE.open("r") as file:
            data = json.load(file)
            return [Task(**task) for task in data]
    except json.JSONDecodeError:
        print("Error: task file contains invalid JSON")
        return []


def save_tasks(tasks: list[Task]) -> None:
    with TASKS_FILE.open("w") as file:
        json.dump(
            [asdict(task) for task in tasks],
            file,
            indent=4
        )


def add_task(args) -> None:
    description = args.description
    tasks = load_tasks()
    new_id = max((task.id for task in tasks), default=0) + 1
    date_now = datetime.now().isoformat()
    new_task = Task(
        id=new_id,
        name=args.name,
        description=description,
        created_at=date_now,
        updated_at=date_now
    )
    tasks.append(new_task)
    save_tasks(tasks)

    print(f"Task added successfully (ID: {new_id})")


def update_task(args) -> None:
    task_id = args.id

    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Task not found (ID: {task_id})")
        return

    if args.name is not None:
        task.name = args.name
    if args.description is not None:
        task.description = args.description
    task.updated_at = datetime.now().isoformat()
    save_tasks(tasks)
    print(f"Task updated successfully (ID: {task_id})")


def delete_task(args) -> None:
    task_id = args.id
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Task not found (ID: {task_id})")
        return

    tasks.remove(task)
    save_tasks(tasks)
    print(f"Task deleted successfully (ID: {task_id})")


def list_tasks(args) -> None:
    status = args.filter
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
        print(f"Status: {task.status}")
        print(f"Last change: {updated_at.strftime("%d %B %Y, %H:%M")}")

    print("--------------------")


def mark_status(args) -> None:
    task_id = args.id

    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Task not found (ID: {task_id})")
        return

    update_status(task, args.status)
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


def main():
    parser = argparse.ArgumentParser(
        prog="task-cli",
        description="A simple command-line task tracker to manage your tasks efficiently.",
        epilog="Examples:\n"
               "  task-cli add \"Buy groceries\" -d \"Milk, eggs, bread\"\n"
               "  task-cli list -f todo\n"
               "  task-cli mark-in-progress 1\n"
               "  task-cli mark-done 1\n"
               "  task-cli update 1 -n \"Buy groceries and fruits\"\n"
               "  task-cli delete 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands to manage your tasks",
        help="Use 'task-cli <command> --help' for more information"
    )

    # Add task command
    add_task_parser = subparsers.add_parser(
        "add",
        help="Create a new task",
        description="Add a new task to your task list.",
        epilog="Example: task-cli add \"Buy groceries\" -d \"Milk, eggs, bread\"",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    add_task_parser.add_argument("name", type=str, help="task name (required)")
    add_task_parser.add_argument("-d", "--description", type=str,
                                 help="detailed description of the task (optional)")
    add_task_parser.set_defaults(func=add_task)

    # Update task command
    update_task_parser = subparsers.add_parser(
        "update",
        help="Modify an existing task",
        description="Update the name or description of an existing task.",
        epilog="Example: task-cli update 1 -n \"New task name\" -d \"Updated description\"",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    update_task_parser.add_argument("id", type=int, help="task ID to update")
    update_task_parser.add_argument("-n", "--name", type=str,
                                    help="new name for the task")
    update_task_parser.add_argument("-d", "--description", type=str,
                                    help="new description for the task")
    update_task_parser.set_defaults(func=update_task)

    # Delete task command
    delete_task_parser = subparsers.add_parser(
        "delete",
        help="Remove a task permanently",
        description="Delete a task from your task list. This action cannot be undone.",
        epilog="Example: task-cli delete 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    delete_task_parser.add_argument("id", type=int, help="task ID to delete")
    delete_task_parser.set_defaults(func=delete_task)

    # List tasks command
    list_tasks_parser = subparsers.add_parser(
        "list",
        help="Display all tasks",
        description="Show all tasks or filter them by status.",
        epilog="Examples:\n"
               "  task-cli list              # Show all tasks\n"
               "  task-cli list -f todo      # Show only pending tasks\n"
               "  task-cli list -f in-progress\n"
               "  task-cli list -f done",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    list_tasks_parser.add_argument("-f", "--filter", type=str,
                                   help="filter tasks by status",
                                   choices=["done", "in-progress", "todo"],
                                   metavar="STATUS")
    list_tasks_parser.set_defaults(func=list_tasks)

    # Mark done command
    mark_done_parser = subparsers.add_parser(
        "mark-done",
        help="Mark a task as completed",
        description="Change task status to 'done'.",
        epilog="Example: task-cli mark-done 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mark_done_parser.add_argument("id", type=int, help="task ID to mark as done")
    mark_done_parser.set_defaults(
        func=mark_status,
        status=TaskStatus.DONE
    )

    # Mark in-progress command
    mark_in_progress_parser = subparsers.add_parser(
        "mark-in-progress",
        help="Mark a task as in progress",
        description="Change task status to 'in-progress'.",
        epilog="Example: task-cli mark-in-progress 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mark_in_progress_parser.add_argument("id", type=int, help="task ID to mark as in progress")
    mark_in_progress_parser.set_defaults(
        func=mark_status,
        status=TaskStatus.IN_PROGRESS
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
