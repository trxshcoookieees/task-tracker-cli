# Task Tracker CLI

A simple command-line task tracker built with Python.

## Usage

### Add a task

```bash
task-cli add "Task name" -d "Task description"
```

### List all tasks

```bash
task-cli list
```

Filter by status:

```bash
task-cli list -f todo
task-cli list -f in-progress
task-cli list -f done
```

### Update a task

```bash
task-cli update <id> -n "New name" -d "New description"
```

### Change status

```bash
task-cli mark-in-progress <id>
task-cli mark-done <id>
```

### Delete a task

```bash
task-cli delete <id>
```

## Data Storage

Tasks are stored in `~/taskcli.json`.

---

This project is based on the [Task Tracker](https://roadmap.sh/projects/task-tracker) from the roadmap.sh
