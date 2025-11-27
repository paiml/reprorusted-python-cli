"""Tests for event_saga_cli.py"""


from event_saga_cli import (
    ChoreographySaga,
    OrderContext,
    Saga,
    SagaBuilder,
    SagaEvent,
    SagaState,
    SagaStep,
    StepResult,
    create_order_saga,
    simulate_saga,
)


class TestStepResult:
    def test_success(self):
        result = StepResult(True, data="done")
        assert result.success
        assert result.data == "done"

    def test_failure(self):
        result = StepResult(False, error="oops")
        assert not result.success
        assert result.error == "oops"


class TestSagaState:
    def test_states_exist(self):
        assert SagaState.PENDING
        assert SagaState.RUNNING
        assert SagaState.COMPLETED
        assert SagaState.COMPENSATING
        assert SagaState.COMPENSATED
        assert SagaState.FAILED


class TestSagaStep:
    def test_create(self):
        step = SagaStep(
            name="test",
            action=lambda: StepResult(True),
            compensate=lambda: StepResult(True),
        )
        assert step.name == "test"
        assert step.state == SagaState.PENDING


class TestSaga:
    def test_create(self):
        saga = Saga("test")
        assert saga.name == "test"
        assert saga.state == SagaState.PENDING

    def test_add_step(self):
        saga = Saga("test")
        saga.add_step("step1", lambda: StepResult(True), lambda: StepResult(True))
        assert len(saga._steps) == 1

    def test_execute_success(self):
        saga = Saga("test")
        saga.add_step("step1", lambda: StepResult(True), lambda: StepResult(True))
        saga.add_step("step2", lambda: StepResult(True), lambda: StepResult(True))
        success = saga.execute()
        assert success
        assert saga.state == SagaState.COMPLETED

    def test_execute_failure_compensates(self):
        compensated = []

        saga = Saga("test")
        saga.add_step(
            "step1",
            lambda: StepResult(True),
            lambda: (compensated.append("step1"), StepResult(True))[1],
        )
        saga.add_step(
            "step2",
            lambda: StepResult(False, error="fail"),
            lambda: StepResult(True),
        )

        success = saga.execute()
        assert not success
        assert saga.state == SagaState.COMPENSATED
        assert "step1" in compensated

    def test_step_states(self):
        saga = Saga("test")
        saga.add_step("s1", lambda: StepResult(True), lambda: StepResult(True))
        saga.add_step("s2", lambda: StepResult(True), lambda: StepResult(True))
        saga.execute()
        states = saga.step_states()
        assert states["s1"] == SagaState.COMPLETED
        assert states["s2"] == SagaState.COMPLETED


class TestSagaBuilder:
    def test_build(self):
        saga = SagaBuilder("test").step(
            "s1", lambda: StepResult(True)
        ).build()
        assert saga.name == "test"

    def test_chain_steps(self):
        saga = (
            SagaBuilder("test")
            .step("s1", lambda: StepResult(True))
            .step("s2", lambda: StepResult(True))
            .step("s3", lambda: StepResult(True))
            .build()
        )
        assert len(saga._steps) == 3


class TestOrderContext:
    def test_create(self):
        ctx = OrderContext(order_id="1", amount=100.0)
        assert ctx.order_id == "1"
        assert not ctx.inventory_reserved


class TestCreateOrderSaga:
    def test_success(self):
        ctx = OrderContext(order_id="1", amount=100.0)
        saga = create_order_saga(ctx)
        success = saga.execute()
        assert success
        assert ctx.inventory_reserved
        assert ctx.payment_charged
        assert ctx.shipping_scheduled

    def test_failure_compensates(self):
        ctx = OrderContext(order_id="2", amount=2000.0)  # Will fail
        saga = create_order_saga(ctx)
        success = saga.execute()
        assert not success
        assert not ctx.inventory_reserved  # Compensated
        assert not ctx.payment_charged


class TestChoreographySaga:
    def test_emit(self):
        saga = ChoreographySaga("test")
        events = []
        saga.on("start", lambda e: events.append(e) or None)
        saga.emit(SagaEvent("test", "step1", "start"))
        assert len(events) == 1

    def test_chain_events(self):
        saga = ChoreographySaga("test")
        saga.on("a", lambda e: SagaEvent(e.saga_id, "step2", "b"))
        saga.on("b", lambda e: SagaEvent(e.saga_id, "step3", "c"))
        saga.on("c", lambda e: None)

        saga.emit(SagaEvent("test", "step1", "a"))
        events = saga.events()
        assert len(events) == 3
        assert events[0].event_type == "a"
        assert events[1].event_type == "b"
        assert events[2].event_type == "c"

    def test_compensate(self):
        compensated = []
        saga = ChoreographySaga("test")
        saga.on("event", lambda e: None, lambda: compensated.append(1))
        saga.compensate()
        assert len(compensated) == 1


class TestSagaEvent:
    def test_create(self):
        event = SagaEvent("saga1", "step1", "created", {"id": 1})
        assert event.saga_id == "saga1"
        assert event.step_name == "step1"
        assert event.event_type == "created"


class TestSimulateSaga:
    def test_order_success(self):
        result = simulate_saga(["order_success:"])
        assert "success=True" in result[0]
        assert "COMPLETED" in result[0]

    def test_order_fail(self):
        result = simulate_saga(["order_fail:"])
        assert "success=False" in result[0]
        assert "COMPENSATED" in result[0]
        assert "inventory=False" in result[0]

    def test_builder(self):
        result = simulate_saga(["builder:"])
        assert "COMPLETED" in result[0]


class TestCompensationOrder:
    def test_reverse_order(self):
        order = []

        saga = Saga("test")
        saga.add_step(
            "step1",
            lambda: StepResult(True),
            lambda: (order.append("comp1"), StepResult(True))[1],
        )
        saga.add_step(
            "step2",
            lambda: StepResult(True),
            lambda: (order.append("comp2"), StepResult(True))[1],
        )
        saga.add_step(
            "step3",
            lambda: StepResult(False),
            lambda: StepResult(True),
        )

        saga.execute()
        assert order == ["comp2", "comp1"]  # Reverse order
