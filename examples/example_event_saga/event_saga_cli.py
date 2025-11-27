"""Saga Pattern CLI.

Demonstrates saga pattern for distributed workflow coordination.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class SagaState(Enum):
    """Saga execution state."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    COMPENSATING = auto()
    COMPENSATED = auto()
    FAILED = auto()


@dataclass
class StepResult:
    """Result of a saga step."""

    success: bool
    data: Any = None
    error: str | None = None


@dataclass
class SagaStep:
    """A single step in a saga."""

    name: str
    action: Callable[[], StepResult]
    compensate: Callable[[], StepResult]
    state: SagaState = SagaState.PENDING
    result: StepResult | None = None


class Saga:
    """Saga coordinator for distributed transactions."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: list[SagaStep] = []
        self._state = SagaState.PENDING
        self._completed_steps: list[SagaStep] = []

    def add_step(
        self,
        name: str,
        action: Callable[[], StepResult],
        compensate: Callable[[], StepResult],
    ) -> "Saga":
        """Add a step to the saga."""
        self._steps.append(SagaStep(name, action, compensate))
        return self

    def execute(self) -> bool:
        """Execute the saga. Returns True if successful."""
        self._state = SagaState.RUNNING
        self._completed_steps.clear()

        for step in self._steps:
            step.state = SagaState.RUNNING
            step.result = step.action()

            if step.result.success:
                step.state = SagaState.COMPLETED
                self._completed_steps.append(step)
            else:
                step.state = SagaState.FAILED
                self._compensate()
                return False

        self._state = SagaState.COMPLETED
        return True

    def _compensate(self) -> None:
        """Compensate completed steps in reverse order."""
        self._state = SagaState.COMPENSATING

        for step in reversed(self._completed_steps):
            step.state = SagaState.COMPENSATING
            step.compensate()
            step.state = SagaState.COMPENSATED

        self._state = SagaState.COMPENSATED

    @property
    def state(self) -> SagaState:
        return self._state

    def step_states(self) -> dict[str, SagaState]:
        """Get state of all steps."""
        return {step.name: step.state for step in self._steps}


class SagaBuilder:
    """Builder for creating sagas."""

    def __init__(self, name: str) -> None:
        self._saga = Saga(name)

    def step(
        self,
        name: str,
        action: Callable[[], StepResult],
        compensate: Callable[[], StepResult] | None = None,
    ) -> "SagaBuilder":
        """Add a step."""
        comp = compensate or (lambda: StepResult(True))
        self._saga.add_step(name, action, comp)
        return self

    def build(self) -> Saga:
        """Build the saga."""
        return self._saga


# Example: Order processing saga
@dataclass
class OrderContext:
    """Context for order saga."""

    order_id: str
    amount: float
    inventory_reserved: bool = False
    payment_charged: bool = False
    shipping_scheduled: bool = False


def create_order_saga(ctx: OrderContext) -> Saga:
    """Create an order processing saga."""

    def reserve_inventory() -> StepResult:
        ctx.inventory_reserved = True
        return StepResult(True, data="Inventory reserved")

    def release_inventory() -> StepResult:
        ctx.inventory_reserved = False
        return StepResult(True, data="Inventory released")

    def charge_payment() -> StepResult:
        if ctx.amount > 1000:  # Simulate failure for large orders
            return StepResult(False, error="Payment declined")
        ctx.payment_charged = True
        return StepResult(True, data="Payment charged")

    def refund_payment() -> StepResult:
        ctx.payment_charged = False
        return StepResult(True, data="Payment refunded")

    def schedule_shipping() -> StepResult:
        ctx.shipping_scheduled = True
        return StepResult(True, data="Shipping scheduled")

    def cancel_shipping() -> StepResult:
        ctx.shipping_scheduled = False
        return StepResult(True, data="Shipping cancelled")

    return (
        SagaBuilder(f"order-{ctx.order_id}")
        .step("reserve_inventory", reserve_inventory, release_inventory)
        .step("charge_payment", charge_payment, refund_payment)
        .step("schedule_shipping", schedule_shipping, cancel_shipping)
        .build()
    )


# Choreography-based saga (event-driven)
@dataclass
class SagaEvent:
    """Event in a choreography saga."""

    saga_id: str
    step_name: str
    event_type: str
    data: Any = None


class ChoreographySaga:
    """Event-driven saga coordinator."""

    def __init__(self, saga_id: str) -> None:
        self.saga_id = saga_id
        self._handlers: dict[str, Callable[[SagaEvent], SagaEvent | None]] = {}
        self._events: list[SagaEvent] = []
        self._compensations: list[Callable[[], None]] = []

    def on(
        self,
        event_type: str,
        handler: Callable[[SagaEvent], SagaEvent | None],
        compensation: Callable[[], None] | None = None,
    ) -> "ChoreographySaga":
        """Register event handler."""
        self._handlers[event_type] = handler
        if compensation:
            self._compensations.append(compensation)
        return self

    def emit(self, event: SagaEvent) -> None:
        """Emit an event."""
        self._events.append(event)
        if event.event_type in self._handlers:
            next_event = self._handlers[event.event_type](event)
            if next_event:
                self.emit(next_event)

    def compensate(self) -> None:
        """Run compensations in reverse."""
        for comp in reversed(self._compensations):
            comp()

    def events(self) -> list[SagaEvent]:
        """Get all emitted events."""
        return list(self._events)


def simulate_saga(operations: list[str]) -> list[str]:
    """Simulate saga operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "order_success":
            ctx = OrderContext(order_id="1", amount=100.0)
            saga = create_order_saga(ctx)
            success = saga.execute()
            results.append(f"success={success} state={saga.state.name}")
        elif cmd == "order_fail":
            ctx = OrderContext(order_id="2", amount=2000.0)  # Will fail
            saga = create_order_saga(ctx)
            success = saga.execute()
            results.append(
                f"success={success} state={saga.state.name} "
                f"inventory={ctx.inventory_reserved} payment={ctx.payment_charged}"
            )
        elif cmd == "builder":
            saga = (
                SagaBuilder("test")
                .step("step1", lambda: StepResult(True))
                .step("step2", lambda: StepResult(True))
                .build()
            )
            saga.execute()
            results.append(f"state={saga.state.name}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: event_saga_cli.py <command>")
        return 1

    cmd = sys.argv[1]

    if cmd == "demo":
        # Successful order
        ctx1 = OrderContext(order_id="ORD-001", amount=99.99)
        saga1 = create_order_saga(ctx1)
        print("Order 1 (amount=$99.99):")
        success = saga1.execute()
        print(f"  Success: {success}")
        print(f"  State: {saga1.state.name}")
        print(f"  Context: inventory={ctx1.inventory_reserved}, payment={ctx1.payment_charged}")
        print()

        # Failed order (triggers compensation)
        ctx2 = OrderContext(order_id="ORD-002", amount=1500.00)
        saga2 = create_order_saga(ctx2)
        print("Order 2 (amount=$1500, will fail):")
        success = saga2.execute()
        print(f"  Success: {success}")
        print(f"  State: {saga2.state.name}")
        print(f"  Context: inventory={ctx2.inventory_reserved}, payment={ctx2.payment_charged}")
        print(f"  Step states: {saga2.step_states()}")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
