#!/usr/bin/env python3
"""Task queue CLI.

Simple task queue with priority and status tracking.
"""

import argparse
import json
import sys
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Represents a task in the queue."""

    def __init__(
        self,
        task_id: str,
        name: str,
        priority: int = 0,
        data: dict | None = None,
    ):
        self.task_id = task_id
        self.name = name
        self.priority = priority
        self.data = data or {}
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.result: str | None = None
        self.error: str | None = None

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "priority": self.priority,
            "data": self.data,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task from dictionary."""
        task = cls(
            task_id=data["task_id"],
            name=data["name"],
            priority=data.get("priority", 0),
            data=data.get("data", {}),
        )
        task.status = TaskStatus(data.get("status", "pending"))
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        task.result = data.get("result")
        task.error = data.get("error")
        return task


class TaskQueue:
    """Priority task queue."""

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.next_id = 1

    def add(self, name: str, priority: int = 0, data: dict | None = None) -> Task:
        """Add a task to the queue."""
        task_id = f"task_{self.next_id}"
        self.next_id += 1

        task = Task(task_id, name, priority, data)
        self.tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def next_pending(self) -> Task | None:
        """Get next pending task by priority."""
        pending = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]

        if not pending:
            return None

        # Sort by priority (higher first), then by creation time
        pending.sort(key=lambda t: (-t.priority, t.created_at))
        return pending[0]

    def start(self, task_id: str) -> bool:
        """Mark task as running."""
        task = self.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        return True

    def complete(self, task_id: str, result: str | None = None) -> bool:
        """Mark task as completed."""
        task = self.get(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return False

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.result = result
        return True

    def fail(self, task_id: str, error: str) -> bool:
        """Mark task as failed."""
        task = self.get(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return False

        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        task.error = error
        return True

    def list_by_status(self, status: TaskStatus | None = None) -> list[Task]:
        """List tasks, optionally filtered by status."""
        if status is None:
            return list(self.tasks.values())
        return [t for t in self.tasks.values() if t.status == status]

    def count_by_status(self) -> dict[str, int]:
        """Count tasks by status."""
        counts = {s.value: 0 for s in TaskStatus}
        for task in self.tasks.values():
            counts[task.status.value] += 1
        return counts

    def clear_completed(self) -> int:
        """Remove completed and failed tasks."""
        to_remove = [
            t.task_id
            for t in self.tasks.values()
            if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
        ]
        for task_id in to_remove:
            del self.tasks[task_id]
        return len(to_remove)

    def to_dict(self) -> dict:
        """Export queue to dictionary."""
        return {
            "next_id": self.next_id,
            "tasks": [t.to_dict() for t in self.tasks.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskQueue":
        """Import queue from dictionary."""
        queue = cls()
        queue.next_id = data.get("next_id", 1)
        for task_data in data.get("tasks", []):
            task = Task.from_dict(task_data)
            queue.tasks[task.task_id] = task
        return queue


def main() -> int:
    parser = argparse.ArgumentParser(description="Task queue management")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("name", help="Task name")
    add_parser.add_argument(
        "-p", "--priority", type=int, default=0, help="Task priority (higher = more urgent)"
    )
    add_parser.add_argument("-d", "--data", help="Task data (JSON)")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--status", choices=["pending", "running", "completed", "failed"], help="Filter by status"
    )

    # Next command
    subparsers.add_parser("next", help="Get next pending task")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start a task")
    start_parser.add_argument("task_id", help="Task ID")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Complete a task")
    complete_parser.add_argument("task_id", help="Task ID")
    complete_parser.add_argument("--result", help="Task result")

    # Fail command
    fail_parser = subparsers.add_parser("fail", help="Fail a task")
    fail_parser.add_argument("task_id", help="Task ID")
    fail_parser.add_argument("error", help="Error message")

    # Status command
    subparsers.add_parser("status", help="Show queue status")

    # Clear command
    subparsers.add_parser("clear", help="Clear completed tasks")

    parser.add_argument("-f", "--file", default="queue.json", help="Queue file")

    args = parser.parse_args()

    # Load queue
    try:
        with open(args.file) as f:
            queue = TaskQueue.from_dict(json.load(f))
    except FileNotFoundError:
        queue = TaskQueue()

    def save_queue():
        with open(args.file, "w") as f:
            json.dump(queue.to_dict(), f, indent=2)

    # Execute command
    if args.command == "add":
        data = json.loads(args.data) if args.data else None
        task = queue.add(args.name, args.priority, data)
        save_queue()
        print(f"Created {task.task_id}: {task.name}")

    elif args.command == "list":
        status = TaskStatus(args.status) if args.status else None
        tasks = queue.list_by_status(status)
        if not tasks:
            print("No tasks")
        else:
            for task in tasks:
                print(
                    f"{task.task_id}: {task.name} [{task.status.value}] (priority: {task.priority})"
                )

    elif args.command == "next":
        task = queue.next_pending()
        if task:
            print(f"{task.task_id}: {task.name}")
            print(json.dumps(task.to_dict(), indent=2))
        else:
            print("No pending tasks")

    elif args.command == "start":
        if queue.start(args.task_id):
            save_queue()
            print(f"Started {args.task_id}")
        else:
            print(f"Cannot start {args.task_id}", file=sys.stderr)
            return 1

    elif args.command == "complete":
        if queue.complete(args.task_id, args.result):
            save_queue()
            print(f"Completed {args.task_id}")
        else:
            print(f"Cannot complete {args.task_id}", file=sys.stderr)
            return 1

    elif args.command == "fail":
        if queue.fail(args.task_id, args.error):
            save_queue()
            print(f"Failed {args.task_id}: {args.error}")
        else:
            print(f"Cannot fail {args.task_id}", file=sys.stderr)
            return 1

    elif args.command == "status":
        counts = queue.count_by_status()
        total = sum(counts.values())
        print(f"Total: {total} tasks")
        for status, count in counts.items():
            print(f"  {status}: {count}")

    elif args.command == "clear":
        removed = queue.clear_completed()
        save_queue()
        print(f"Removed {removed} tasks")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
