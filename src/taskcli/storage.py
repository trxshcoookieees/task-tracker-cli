import json
from dataclasses import asdict
from pathlib import Path
from taskcli.models import Task

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
