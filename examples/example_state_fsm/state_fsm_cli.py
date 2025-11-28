"""Finite State Machine CLI.

Demonstrates FSM patterns for state management and transitions.
"""

import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

S = TypeVar("S")
E = TypeVar("E")


@dataclass
class Transition(Generic[S, E]):
    """State transition definition."""

    from_state: S
    event: E
    to_state: S
    action: Callable[[], None] | None = None
    guard: Callable[[], bool] | None = None


@dataclass
class FSM(Generic[S, E]):
    """Finite State Machine."""

    initial_state: S
    current_state: S = field(init=False)
    transitions: list[Transition[S, E]] = field(default_factory=list)
    on_enter: dict[S, Callable[[], None]] = field(default_factory=dict)
    on_exit: dict[S, Callable[[], None]] = field(default_factory=dict)
    history: list[S] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.current_state = self.initial_state
        self.history.append(self.initial_state)

    def add_transition(
        self,
        from_state: S,
        event: E,
        to_state: S,
        action: Callable[[], None] | None = None,
        guard: Callable[[], bool] | None = None,
    ) -> None:
        """Add a state transition."""
        self.transitions.append(Transition(from_state, event, to_state, action, guard))

    def set_on_enter(self, state: S, callback: Callable[[], None]) -> None:
        """Set callback for entering a state."""
        self.on_enter[state] = callback

    def set_on_exit(self, state: S, callback: Callable[[], None]) -> None:
        """Set callback for exiting a state."""
        self.on_exit[state] = callback

    def process(self, event: E) -> bool:
        """Process an event and transition if possible."""
        for trans in self.transitions:
            if trans.from_state == self.current_state and trans.event == event:
                if trans.guard and not trans.guard():
                    continue

                if self.current_state in self.on_exit:
                    self.on_exit[self.current_state]()

                if trans.action:
                    trans.action()

                self.current_state = trans.to_state
                self.history.append(trans.to_state)

                if trans.to_state in self.on_enter:
                    self.on_enter[trans.to_state]()

                return True

        return False

    def can_process(self, event: E) -> bool:
        """Check if event can be processed from current state."""
        for trans in self.transitions:
            if trans.from_state == self.current_state and trans.event == event:
                if trans.guard is None or trans.guard():
                    return True
        return False

    def available_events(self) -> list[E]:
        """Get list of events that can be processed from current state."""
        events = []
        for trans in self.transitions:
            if trans.from_state == self.current_state:
                if trans.guard is None or trans.guard():
                    events.append(trans.event)
        return events

    def reset(self) -> None:
        """Reset to initial state."""
        self.current_state = self.initial_state
        self.history = [self.initial_state]


class TrafficLight:
    """Traffic light state machine example."""

    def __init__(self) -> None:
        self.fsm: FSM[str, str] = FSM("red")
        self.fsm.add_transition("red", "timer", "green")
        self.fsm.add_transition("green", "timer", "yellow")
        self.fsm.add_transition("yellow", "timer", "red")

    def tick(self) -> str:
        """Advance to next state."""
        self.fsm.process("timer")
        return self.fsm.current_state

    @property
    def state(self) -> str:
        return self.fsm.current_state


class Turnstile:
    """Turnstile state machine example."""

    def __init__(self) -> None:
        self.fsm: FSM[str, str] = FSM("locked")
        self.coins_inserted = 0

        self.fsm.add_transition("locked", "coin", "unlocked", action=self._accept_coin)
        self.fsm.add_transition("unlocked", "push", "locked", action=self._pass_through)
        self.fsm.add_transition("locked", "push", "locked")
        self.fsm.add_transition("unlocked", "coin", "unlocked", action=self._accept_coin)

    def _accept_coin(self) -> None:
        self.coins_inserted += 1

    def _pass_through(self) -> None:
        pass

    def insert_coin(self) -> bool:
        return self.fsm.process("coin")

    def push(self) -> bool:
        return self.fsm.process("push")

    @property
    def state(self) -> str:
        return self.fsm.current_state


class Connection:
    """TCP-like connection state machine."""

    def __init__(self) -> None:
        self.fsm: FSM[str, str] = FSM("closed")
        self._setup_transitions()

    def _setup_transitions(self) -> None:
        self.fsm.add_transition("closed", "open", "opening")
        self.fsm.add_transition("opening", "connected", "open")
        self.fsm.add_transition("opening", "error", "closed")
        self.fsm.add_transition("open", "close", "closing")
        self.fsm.add_transition("open", "error", "closed")
        self.fsm.add_transition("closing", "closed", "closed")
        self.fsm.add_transition("closing", "error", "closed")

    def open(self) -> bool:
        return self.fsm.process("open")

    def connected(self) -> bool:
        return self.fsm.process("connected")

    def close(self) -> bool:
        return self.fsm.process("close")

    def error(self) -> bool:
        return self.fsm.process("error")

    def closed(self) -> bool:
        return self.fsm.process("closed")

    @property
    def state(self) -> str:
        return self.fsm.current_state


class Order:
    """Order processing state machine."""

    STATES = ["created", "confirmed", "processing", "shipped", "delivered", "cancelled"]

    def __init__(self) -> None:
        self.fsm: FSM[str, str] = FSM("created")
        self._paid = False
        self._setup_transitions()

    def _setup_transitions(self) -> None:
        self.fsm.add_transition("created", "confirm", "confirmed")
        self.fsm.add_transition("created", "cancel", "cancelled")
        self.fsm.add_transition("confirmed", "pay", "processing", guard=lambda: True)
        self.fsm.add_transition("confirmed", "cancel", "cancelled")
        self.fsm.add_transition("processing", "ship", "shipped")
        self.fsm.add_transition("processing", "cancel", "cancelled")
        self.fsm.add_transition("shipped", "deliver", "delivered")

    def confirm(self) -> bool:
        return self.fsm.process("confirm")

    def pay(self) -> bool:
        result = self.fsm.process("pay")
        if result:
            self._paid = True
        return result

    def ship(self) -> bool:
        return self.fsm.process("ship")

    def deliver(self) -> bool:
        return self.fsm.process("deliver")

    def cancel(self) -> bool:
        return self.fsm.process("cancel")

    @property
    def state(self) -> str:
        return self.fsm.current_state


@dataclass
class StateBuilder(Generic[S, E]):
    """Builder for FSM."""

    initial: S
    transitions: list[tuple[S, E, S]] = field(default_factory=list)

    def add(self, from_state: S, event: E, to_state: S) -> "StateBuilder[S, E]":
        self.transitions.append((from_state, event, to_state))
        return self

    def build(self) -> FSM[S, E]:
        fsm: FSM[S, E] = FSM(self.initial)
        for from_s, event, to_s in self.transitions:
            fsm.add_transition(from_s, event, to_s)
        return fsm


def validate_fsm(fsm: FSM[Any, Any], states: list[Any]) -> list[str]:
    """Validate FSM for common issues."""
    errors = []

    # Check if all transition states are valid
    for trans in fsm.transitions:
        if trans.from_state not in states:
            errors.append(f"Invalid from_state: {trans.from_state}")
        if trans.to_state not in states:
            errors.append(f"Invalid to_state: {trans.to_state}")

    # Check if initial state is valid
    if fsm.initial_state not in states:
        errors.append(f"Invalid initial_state: {fsm.initial_state}")

    return errors


def simulate_fsm(transitions: list[str], events: list[str]) -> list[str]:
    """Simulate FSM from transition definitions."""
    fsm: FSM[str, str] = FSM(transitions[0].split("-")[0] if transitions else "start")

    for trans in transitions:
        parts = trans.split("-")
        if len(parts) == 3:
            from_s, event, to_s = parts
            fsm.add_transition(from_s, event, to_s)

    results = []
    for event in events:
        if event == "state":
            results.append(fsm.current_state)
        elif event == "history":
            results.append(",".join(fsm.history))
        elif event == "available":
            results.append(",".join(fsm.available_events()))
        else:
            success = fsm.process(event)
            results.append("ok" if success else "fail")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: state_fsm_cli.py <command> [args...]")
        print("Commands: traffic, turnstile, order, simulate")
        return 1

    cmd = sys.argv[1]

    if cmd == "traffic":
        light = TrafficLight()
        print(f"Initial: {light.state}")
        for _ in range(6):
            light.tick()
            print(f"After tick: {light.state}")

    elif cmd == "turnstile":
        turnstile = Turnstile()
        print(f"Initial: {turnstile.state}")
        print(f"Push (should fail): {turnstile.push()} -> {turnstile.state}")
        print(f"Insert coin: {turnstile.insert_coin()} -> {turnstile.state}")
        print(f"Push (should pass): {turnstile.push()} -> {turnstile.state}")

    elif cmd == "order":
        order = Order()
        print(f"Initial: {order.state}")
        order.confirm()
        print(f"After confirm: {order.state}")
        order.pay()
        print(f"After pay: {order.state}")
        order.ship()
        print(f"After ship: {order.state}")
        order.deliver()
        print(f"After deliver: {order.state}")

    elif cmd == "simulate":
        if len(sys.argv) < 4:
            print("Usage: simulate <transitions> <events>", file=sys.stderr)
            return 1
        transitions = sys.argv[2].split(",")
        events = sys.argv[3].split(",")
        results = simulate_fsm(transitions, events)
        for result in results:
            print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
