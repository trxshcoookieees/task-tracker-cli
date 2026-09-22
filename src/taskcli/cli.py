import argparse

from taskcli.models import TaskStatus
from taskcli.tasks import (
    add_task,
    update_task,
    list_tasks,
    delete_task,
    mark_status
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
    add_task_parser.set_defaults(
        func=lambda params: add_task(params.name, params.description)
    )

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
    update_task_parser.set_defaults(
        func=lambda params: update_task(params.id, params.name, params.description)
    )

    # Delete task command
    delete_task_parser = subparsers.add_parser(
        "delete",
        help="Remove a task permanently",
        description="Delete a task from your task list. This action cannot be undone.",
        epilog="Example: task-cli delete 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    delete_task_parser.add_argument("id", type=int, help="task ID to delete")
    delete_task_parser.set_defaults(
        func=lambda params: delete_task(params.id)
    )

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
    list_tasks_parser.add_argument("-f", "--filter", type=TaskStatus,
                                   choices=list(TaskStatus),
                                   help="filter tasks by status",
                                   metavar="STATUS")
    list_tasks_parser.set_defaults(
        func=lambda params: list_tasks(params.filter)
    )

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
        func=lambda params: mark_status(params.id, TaskStatus.DONE),
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
        func=lambda params: mark_status(params.id, TaskStatus.IN_PROGRESS)
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
