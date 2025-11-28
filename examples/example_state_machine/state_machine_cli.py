"""Generic State Machine Pattern CLI.

Demonstrates state pattern for modeling complex state transitions.
"""

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, TypeVar

S = TypeVar("S")
C = TypeVar("C")


class State(ABC, Generic[C]):
    """Abstract state interface."""

    @abstractmethod
    def name(self) -> str:
        """Get state name."""
        ...

    def on_enter(self, context: C) -> None:
        """Called when entering this state."""
        pass

    def on_exit(self, context: C) -> None:
        """Called when exiting this state."""
        pass

    @abstractmethod
    def handle(self, context: C, event: str) -> "State[C] | None":
        """Handle event and return next state."""
        ...


@dataclass
class StateMachine(Generic[C]):
    """Generic state machine."""

    context: C
    initial_state: State[C]
    current_state: State[C] = field(init=False)
    history: list[str] = field(default_factory=list)
    listeners: list[Callable[[str, str], None]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.current_state = self.initial_state
        self.history.append(self.initial_state.name())
        self.initial_state.on_enter(self.context)

    def process(self, event: str) -> bool:
        """Process event through current state."""
        next_state = self.current_state.handle(self.context, event)

        if next_state is not None:
            old_name = self.current_state.name()
            self.current_state.on_exit(self.context)

            self.current_state = next_state
            self.history.append(next_state.name())

            next_state.on_enter(self.context)

            for listener in self.listeners:
                listener(old_name, next_state.name())

            return True

        return False

    def add_listener(self, listener: Callable[[str, str], None]) -> None:
        """Add state change listener."""
        self.listeners.append(listener)

    @property
    def state_name(self) -> str:
        return self.current_state.name()


# Vending Machine Example


@dataclass
class VendingContext:
    """Vending machine context."""

    balance: int = 0
    selected_item: str = ""
    item_prices: dict[str, int] = field(
        default_factory=lambda: {"cola": 100, "chips": 75, "candy": 50}
    )
    inventory: dict[str, int] = field(default_factory=lambda: {"cola": 5, "chips": 3, "candy": 10})
    dispensed: str = ""


class IdleState(State[VendingContext]):
    """Idle state - waiting for coins."""

    def name(self) -> str:
        return "idle"

    def on_enter(self, context: VendingContext) -> None:
        context.balance = 0
        context.selected_item = ""
        context.dispensed = ""

    def handle(self, context: VendingContext, event: str) -> State[VendingContext] | None:
        if event.startswith("insert:"):
            amount = int(event.split(":")[1])
            context.balance += amount
            return SelectingState()
        return None


class SelectingState(State[VendingContext]):
    """Selecting state - has coins, selecting item."""

    def name(self) -> str:
        return "selecting"

    def handle(self, context: VendingContext, event: str) -> State[VendingContext] | None:
        if event.startswith("insert:"):
            amount = int(event.split(":")[1])
            context.balance += amount
            return None

        if event.startswith("select:"):
            item = event.split(":")[1]
            if item in context.item_prices:
                context.selected_item = item
                price = context.item_prices[item]
                if context.balance >= price and context.inventory.get(item, 0) > 0:
                    return DispensingState()
                return InsufficientState()
            return None

        if event == "cancel":
            return IdleState()

        return None


class InsufficientState(State[VendingContext]):
    """Insufficient funds or no stock."""

    def name(self) -> str:
        return "insufficient"

    def handle(self, context: VendingContext, event: str) -> State[VendingContext] | None:
        if event.startswith("insert:"):
            amount = int(event.split(":")[1])
            context.balance += amount
            price = context.item_prices.get(context.selected_item, 0)
            if context.balance >= price:
                return DispensingState()
            return None

        if event == "cancel":
            return IdleState()

        return None


class DispensingState(State[VendingContext]):
    """Dispensing item."""

    def name(self) -> str:
        return "dispensing"

    def on_enter(self, context: VendingContext) -> None:
        item = context.selected_item
        price = context.item_prices.get(item, 0)
        context.balance -= price
        context.inventory[item] -= 1
        context.dispensed = item

    def handle(self, context: VendingContext, event: str) -> State[VendingContext] | None:
        if event == "take":
            if context.balance > 0:
                return ChangeState()
            return IdleState()
        return None


class ChangeState(State[VendingContext]):
    """Returning change."""

    def name(self) -> str:
        return "change"

    def on_enter(self, context: VendingContext) -> None:
        pass  # Change is available

    def handle(self, context: VendingContext, event: str) -> State[VendingContext] | None:
        if event == "take_change":
            context.balance = 0
            return IdleState()
        return None


class VendingMachine:
    """Vending machine facade."""

    def __init__(self) -> None:
        self.context = VendingContext()
        self.machine = StateMachine(self.context, IdleState())

    def insert_coin(self, amount: int) -> bool:
        return self.machine.process(f"insert:{amount}")

    def select_item(self, item: str) -> bool:
        return self.machine.process(f"select:{item}")

    def cancel(self) -> bool:
        return self.machine.process("cancel")

    def take_item(self) -> bool:
        return self.machine.process("take")

    def take_change(self) -> bool:
        return self.machine.process("take_change")

    @property
    def state(self) -> str:
        return self.machine.state_name

    @property
    def balance(self) -> int:
        return self.context.balance

    @property
    def dispensed(self) -> str:
        return self.context.dispensed


# Document Workflow Example


@dataclass
class DocumentContext:
    """Document workflow context."""

    title: str = ""
    content: str = ""
    author: str = ""
    reviewer: str = ""
    comments: list[str] = field(default_factory=list)


class DraftState(State[DocumentContext]):
    def name(self) -> str:
        return "draft"

    def handle(self, context: DocumentContext, event: str) -> State[DocumentContext] | None:
        if event == "submit":
            if context.content:
                return ReviewState()
        return None


class ReviewState(State[DocumentContext]):
    def name(self) -> str:
        return "review"

    def handle(self, context: DocumentContext, event: str) -> State[DocumentContext] | None:
        if event == "approve":
            return ApprovedState()
        if event == "reject":
            return DraftState()
        if event.startswith("comment:"):
            context.comments.append(event.split(":", 1)[1])
        return None


class ApprovedState(State[DocumentContext]):
    def name(self) -> str:
        return "approved"

    def handle(self, context: DocumentContext, event: str) -> State[DocumentContext] | None:
        if event == "publish":
            return PublishedState()
        if event == "archive":
            return ArchivedState()
        return None


class PublishedState(State[DocumentContext]):
    def name(self) -> str:
        return "published"

    def handle(self, context: DocumentContext, event: str) -> State[DocumentContext] | None:
        if event == "unpublish":
            return ApprovedState()
        if event == "archive":
            return ArchivedState()
        return None


class ArchivedState(State[DocumentContext]):
    def name(self) -> str:
        return "archived"

    def handle(self, context: DocumentContext, event: str) -> State[DocumentContext] | None:
        if event == "restore":
            return DraftState()
        return None


class DocumentWorkflow:
    """Document workflow facade."""

    def __init__(self, title: str, author: str) -> None:
        self.context = DocumentContext(title=title, author=author)
        self.machine = StateMachine(self.context, DraftState())

    def edit(self, content: str) -> None:
        self.context.content = content

    def submit(self) -> bool:
        return self.machine.process("submit")

    def approve(self) -> bool:
        return self.machine.process("approve")

    def reject(self) -> bool:
        return self.machine.process("reject")

    def publish(self) -> bool:
        return self.machine.process("publish")

    def archive(self) -> bool:
        return self.machine.process("archive")

    @property
    def state(self) -> str:
        return self.machine.state_name


def simulate_machine(machine_type: str, events: list[str]) -> list[str]:
    """Simulate state machine operations."""
    results = []

    if machine_type == "vending":
        vm = VendingMachine()
        for event in events:
            if event == "state":
                results.append(vm.state)
            elif event == "balance":
                results.append(str(vm.balance))
            elif event == "dispensed":
                results.append(vm.dispensed or "none")
            elif event.startswith("insert:"):
                vm.insert_coin(int(event.split(":")[1]))
                results.append("ok")
            elif event.startswith("select:"):
                vm.select_item(event.split(":")[1])
                results.append("ok")
            elif event == "take":
                vm.take_item()
                results.append("ok")
            elif event == "take_change":
                vm.take_change()
                results.append("ok")
            elif event == "cancel":
                vm.cancel()
                results.append("ok")

    elif machine_type == "document":
        doc = DocumentWorkflow("Test", "Author")
        for event in events:
            if event == "state":
                results.append(doc.state)
            elif event.startswith("edit:"):
                doc.edit(event.split(":", 1)[1])
                results.append("ok")
            elif event == "submit":
                results.append("ok" if doc.submit() else "fail")
            elif event == "approve":
                results.append("ok" if doc.approve() else "fail")
            elif event == "reject":
                results.append("ok" if doc.reject() else "fail")
            elif event == "publish":
                results.append("ok" if doc.publish() else "fail")
            elif event == "archive":
                results.append("ok" if doc.archive() else "fail")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: state_machine_cli.py <command> [args...]")
        print("Commands: vending, document")
        return 1

    cmd = sys.argv[1]

    if cmd == "vending":
        vm = VendingMachine()
        print(f"Initial state: {vm.state}")

        vm.insert_coin(50)
        print(f"After insert 50: state={vm.state}, balance={vm.balance}")

        vm.insert_coin(50)
        print(f"After insert 50: state={vm.state}, balance={vm.balance}")

        vm.select_item("cola")
        print(f"After select cola: state={vm.state}, dispensed={vm.dispensed}")

        vm.take_item()
        print(f"After take: state={vm.state}")

    elif cmd == "document":
        doc = DocumentWorkflow("My Document", "Alice")
        print(f"Initial state: {doc.state}")

        doc.edit("Hello World")
        doc.submit()
        print(f"After submit: {doc.state}")

        doc.approve()
        print(f"After approve: {doc.state}")

        doc.publish()
        print(f"After publish: {doc.state}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
