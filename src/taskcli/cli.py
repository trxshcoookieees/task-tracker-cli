import argparse
import json
from datetime import datetime
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
    new_id = max((task["id"] for task in tasks), default=0) + 1
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
        print(f"Description: {task['description']}")
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
    mark_done_parser.set_defaults(func=mark_done)

    # Mark in-progress command
    mark_in_progress_parser = subparsers.add_parser(
        "mark-in-progress",
        help="Mark a task as in progress",
        description="Change task status to 'in-progress'.",
        epilog="Example: task-cli mark-in-progress 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mark_in_progress_parser.add_argument("id", type=int, help="task ID to mark as in progress")
    mark_in_progress_parser.set_defaults(func=mark_in_progress)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
