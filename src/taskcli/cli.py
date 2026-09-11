import argparse
import json
from datetime import datetime, date, time
from pathlib import Path

TASKS_FILE = Path.home() / "taskcli.json"
if not TASKS_FILE.exists():
    TASKS_FILE.write_text("[]")


def load_tasks():
    with TASKS_FILE.open("r") as file:
        return json.load(file)


def save_tasks(tasks):
    with TASKS_FILE.open("w") as file:
        json.dump(tasks, file, indent=4)


def add_task(args):
    description = args.description if args.description else ""
    tasks = load_tasks()
    new_id = len(tasks) + 1
    new_task = {
        "id": new_id,
        "name": args.name,
        "description": description,
        "status": "todo",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
    }
    tasks.append(new_task)

    save_tasks(tasks)

    print(f"Task added successfully (ID: {new_id})")


def update_task(args):
    task_id = args.id

    tasks = load_tasks()
    index = next(
        (i for i, task in enumerate(tasks) if task["id"] == args.id),
        None
    )

    if not index is None:
        if args.name:
            tasks[index]["name"] = args.name
        if args.description:
            tasks[index]["description"] = args.description
        tasks[index]["updatedAt"] = datetime.now().isoformat()
        save_tasks(tasks)
        print(f"Task updated successfully (ID: {task_id})")
        return

    print(f"Task not found (ID: {task_id})")
    return


def delete_task(args):
    task_id = args.id
    tasks = load_tasks()

    tasks = [task for task in tasks if task["id"] != task_id]
    save_tasks(tasks)
    print(f"Task deleted successfully (ID: {task_id})")


def list_tasks(args):
    status = args.filter.lower() if args.filter else None
    tasks = load_tasks()
    print("-------TASKS--------")
    if status:
        print(f"Filter: {status}\n")
        tasks = [
            task for task in tasks
            if task["status"].lower() == status
        ]
    print()
    for task in tasks:
        updated_at = datetime.fromisoformat(task["updatedAt"])
        print("--------------------")
        print(f"{task['id']}: {task['name']}")
        print(f"Decsription: {task['description']}")
        print(f"Status: {task['status']}")
        print(f"Last change: {updated_at.strftime("%d %B %Y, %H:%M")}")

    print("--------------------")


def mark_done(args):
    task_id = args.id

    tasks = load_tasks()
    index = next(
        (i for i, task in enumerate(tasks) if task["id"] == args.id),
        None
    )

    if not index is None:
        tasks[index]["status"] = "done"
        tasks[index]["updatedAt"] = datetime.now().isoformat()
        save_tasks(tasks)
        print(f"Task updated successfully (ID: {task_id})")
        return

    print(f"Task not found (ID: {task_id})")
    return


def mark_in_progress(args):
    task_id = args.id

    tasks = load_tasks()
    index = next(
        (i for i, task in enumerate(tasks) if task["id"] == args.id),
        None
    )

    if not index is None:
        tasks[index]["status"] = "in-progress"
        tasks[index]["updatedAt"] = datetime.now().isoformat()
        save_tasks(tasks)
        print(f"Task updated successfully (ID: {task_id})")
        return

    print(f"Task not found (ID: {task_id})")
    return


def main():
    parser = argparse.ArgumentParser(
        prog="taskcli",
        usage="%(prog)s [options]",
        description="A simple task tracker tool",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_task_parser = subparsers.add_parser("add", description="Add a new task")
    add_task_parser.add_argument("name", type=str, help="Name of the task")
    add_task_parser.add_argument("-d", "--description", type=str, help="Description of the task")
    add_task_parser.set_defaults(func=add_task)

    update_task_parser = subparsers.add_parser("update", description="Update a task")
    update_task_parser.add_argument("id", type=int, help="ID of the task")
    update_task_parser.add_argument("-n", "--name", type=str, help="Name of the task")
    update_task_parser.add_argument("-d", "--description", type=str, help="Description of the task")
    update_task_parser.set_defaults(func=update_task)

    delete_task_parser = subparsers.add_parser("delete", description="Delete a task")
    delete_task_parser.add_argument("id", type=int, help="ID of the task")
    delete_task_parser.set_defaults(func=delete_task)

    list_tasks_parser = subparsers.add_parser("list", description="List all tasks")
    list_tasks_parser.add_argument("-f", "--filter", type=str, help="Filter tasks",
                                   choices=["done", "in-progress", "todo"])
    list_tasks_parser.set_defaults(func=list_tasks)

    mark_done_parser = subparsers.add_parser("mark-done", description="Mark task as done")
    mark_done_parser.add_argument("id", type=int, help="ID of the task")
    mark_done_parser.set_defaults(func=mark_done)

    mark_in_progress_parser = subparsers.add_parser("mark-in-progress", description="Mark task as in-progress")
    mark_in_progress_parser.add_argument("id", type=int, help="ID of the task")
    mark_in_progress_parser.set_defaults(func=mark_in_progress)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
