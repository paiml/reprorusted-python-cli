"""Generic Visitor Pattern CLI.

Demonstrates visitor pattern for traversing data structures.
"""

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


class Expr(ABC):
    """Base expression type."""

    @abstractmethod
    def accept(self, visitor: "ExprVisitor[T]") -> T:
        """Accept a visitor."""
        ...


@dataclass
class Literal(Expr):
    """Literal numeric value."""

    value: float

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visit_literal(self)


@dataclass
class Variable(Expr):
    """Variable reference."""

    name: str

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visit_variable(self)


@dataclass
class BinaryOp(Expr):
    """Binary operation."""

    left: Expr
    op: str
    right: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visit_binary_op(self)


@dataclass
class UnaryOp(Expr):
    """Unary operation."""

    op: str
    operand: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visit_unary_op(self)


@dataclass
class Call(Expr):
    """Function call."""

    name: str
    args: list[Expr]

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visit_call(self)


@dataclass
class Conditional(Expr):
    """Conditional expression (ternary)."""

    condition: Expr
    then_expr: Expr
    else_expr: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visit_conditional(self)


class ExprVisitor(ABC, Generic[T]):
    """Visitor for expressions."""

    @abstractmethod
    def visit_literal(self, expr: Literal) -> T: ...

    @abstractmethod
    def visit_variable(self, expr: Variable) -> T: ...

    @abstractmethod
    def visit_binary_op(self, expr: BinaryOp) -> T: ...

    @abstractmethod
    def visit_unary_op(self, expr: UnaryOp) -> T: ...

    @abstractmethod
    def visit_call(self, expr: Call) -> T: ...

    @abstractmethod
    def visit_conditional(self, expr: Conditional) -> T: ...


class Evaluator(ExprVisitor[float]):
    """Evaluate expressions to float values."""

    def __init__(self, env: dict[str, float] | None = None) -> None:
        self.env = env or {}
        self.functions: dict[str, callable] = {
            "abs": abs,
            "min": min,
            "max": max,
            "sqrt": lambda x: x**0.5,
            "pow": pow,
        }

    def evaluate(self, expr: Expr) -> float:
        """Evaluate an expression."""
        return expr.accept(self)

    def visit_literal(self, expr: Literal) -> float:
        return expr.value

    def visit_variable(self, expr: Variable) -> float:
        if expr.name not in self.env:
            raise ValueError(f"Undefined variable: {expr.name}")
        return self.env[expr.name]

    def visit_binary_op(self, expr: BinaryOp) -> float:
        left = expr.left.accept(self)
        right = expr.right.accept(self)

        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b if b != 0 else float("inf"),
            "%": lambda a, b: a % b,
            "^": lambda a, b: a**b,
            "<": lambda a, b: float(a < b),
            ">": lambda a, b: float(a > b),
            "<=": lambda a, b: float(a <= b),
            ">=": lambda a, b: float(a >= b),
            "==": lambda a, b: float(a == b),
            "!=": lambda a, b: float(a != b),
        }

        if expr.op not in ops:
            raise ValueError(f"Unknown operator: {expr.op}")
        return ops[expr.op](left, right)

    def visit_unary_op(self, expr: UnaryOp) -> float:
        operand = expr.operand.accept(self)
        if expr.op == "-":
            return -operand
        if expr.op == "!":
            return float(not operand)
        raise ValueError(f"Unknown unary operator: {expr.op}")

    def visit_call(self, expr: Call) -> float:
        if expr.name not in self.functions:
            raise ValueError(f"Unknown function: {expr.name}")
        args = [arg.accept(self) for arg in expr.args]
        return self.functions[expr.name](*args)

    def visit_conditional(self, expr: Conditional) -> float:
        condition = expr.condition.accept(self)
        if condition:
            return expr.then_expr.accept(self)
        return expr.else_expr.accept(self)


class Printer(ExprVisitor[str]):
    """Print expressions as strings."""

    def visit_literal(self, expr: Literal) -> str:
        if expr.value == int(expr.value):
            return str(int(expr.value))
        return str(expr.value)

    def visit_variable(self, expr: Variable) -> str:
        return expr.name

    def visit_binary_op(self, expr: BinaryOp) -> str:
        left = expr.left.accept(self)
        right = expr.right.accept(self)
        return f"({left} {expr.op} {right})"

    def visit_unary_op(self, expr: UnaryOp) -> str:
        operand = expr.operand.accept(self)
        return f"({expr.op}{operand})"

    def visit_call(self, expr: Call) -> str:
        args = ", ".join(arg.accept(self) for arg in expr.args)
        return f"{expr.name}({args})"

    def visit_conditional(self, expr: Conditional) -> str:
        cond = expr.condition.accept(self)
        then = expr.then_expr.accept(self)
        else_ = expr.else_expr.accept(self)
        return f"({cond} ? {then} : {else_})"


class VariableCollector(ExprVisitor[set[str]]):
    """Collect all variable names in an expression."""

    def visit_literal(self, expr: Literal) -> set[str]:
        return set()

    def visit_variable(self, expr: Variable) -> set[str]:
        return {expr.name}

    def visit_binary_op(self, expr: BinaryOp) -> set[str]:
        return expr.left.accept(self) | expr.right.accept(self)

    def visit_unary_op(self, expr: UnaryOp) -> set[str]:
        return expr.operand.accept(self)

    def visit_call(self, expr: Call) -> set[str]:
        result: set[str] = set()
        for arg in expr.args:
            result |= arg.accept(self)
        return result

    def visit_conditional(self, expr: Conditional) -> set[str]:
        return (
            expr.condition.accept(self) | expr.then_expr.accept(self) | expr.else_expr.accept(self)
        )


class DepthCalculator(ExprVisitor[int]):
    """Calculate expression depth."""

    def visit_literal(self, expr: Literal) -> int:
        return 1

    def visit_variable(self, expr: Variable) -> int:
        return 1

    def visit_binary_op(self, expr: BinaryOp) -> int:
        return 1 + max(expr.left.accept(self), expr.right.accept(self))

    def visit_unary_op(self, expr: UnaryOp) -> int:
        return 1 + expr.operand.accept(self)

    def visit_call(self, expr: Call) -> int:
        if not expr.args:
            return 1
        return 1 + max(arg.accept(self) for arg in expr.args)

    def visit_conditional(self, expr: Conditional) -> int:
        return 1 + max(
            expr.condition.accept(self),
            expr.then_expr.accept(self),
            expr.else_expr.accept(self),
        )


class Simplifier(ExprVisitor[Expr]):
    """Simplify expressions."""

    def visit_literal(self, expr: Literal) -> Expr:
        return expr

    def visit_variable(self, expr: Variable) -> Expr:
        return expr

    def visit_binary_op(self, expr: BinaryOp) -> Expr:
        left = expr.left.accept(self)
        right = expr.right.accept(self)

        # Constant folding
        if isinstance(left, Literal) and isinstance(right, Literal):
            result = Evaluator().evaluate(BinaryOp(left, expr.op, right))
            return Literal(result)

        # Identity simplifications
        if expr.op == "+" and isinstance(right, Literal) and right.value == 0:
            return left
        if expr.op == "+" and isinstance(left, Literal) and left.value == 0:
            return right
        if expr.op == "*" and isinstance(right, Literal) and right.value == 1:
            return left
        if expr.op == "*" and isinstance(left, Literal) and left.value == 1:
            return right
        if expr.op == "*" and isinstance(right, Literal) and right.value == 0:
            return Literal(0)
        if expr.op == "*" and isinstance(left, Literal) and left.value == 0:
            return Literal(0)

        return BinaryOp(left, expr.op, right)

    def visit_unary_op(self, expr: UnaryOp) -> Expr:
        operand = expr.operand.accept(self)

        if isinstance(operand, Literal):
            if expr.op == "-":
                return Literal(-operand.value)

        return UnaryOp(expr.op, operand)

    def visit_call(self, expr: Call) -> Expr:
        args = [arg.accept(self) for arg in expr.args]

        if all(isinstance(arg, Literal) for arg in args):
            result = Evaluator().evaluate(Call(expr.name, args))
            return Literal(result)

        return Call(expr.name, args)

    def visit_conditional(self, expr: Conditional) -> Expr:
        condition = expr.condition.accept(self)
        then_expr = expr.then_expr.accept(self)
        else_expr = expr.else_expr.accept(self)

        if isinstance(condition, Literal):
            if condition.value:
                return then_expr
            return else_expr

        return Conditional(condition, then_expr, else_expr)


def parse_expr(tokens: list[str]) -> tuple[Expr, int]:
    """Simple expression parser."""
    if not tokens:
        raise ValueError("Empty expression")

    pos = 0
    token = tokens[pos]

    # Literal
    try:
        value = float(token)
        return Literal(value), 1
    except ValueError:
        pass

    # Variable
    if token.isidentifier():
        return Variable(token), 1

    raise ValueError(f"Unexpected token: {token}")


def build_expr(spec: str) -> Expr:
    """Build expression from spec string."""
    parts = spec.split()
    if len(parts) == 1:
        try:
            return Literal(float(parts[0]))
        except ValueError:
            return Variable(parts[0])
    elif len(parts) == 3:
        left = build_expr(parts[0])
        op = parts[1]
        right = build_expr(parts[2])
        return BinaryOp(left, op, right)
    raise ValueError(f"Invalid expression spec: {spec}")


def simulate_visitor(operations: list[str]) -> list[str]:
    """Simulate visitor operations."""
    results = []
    expr: Expr = Literal(0)
    env: dict[str, float] = {}

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "literal":
            expr = Literal(float(parts[1]))
            results.append("ok")
        elif cmd == "var":
            expr = Variable(parts[1])
            results.append("ok")
        elif cmd == "add":
            right = Literal(float(parts[1]))
            expr = BinaryOp(expr, "+", right)
            results.append("ok")
        elif cmd == "mul":
            right = Literal(float(parts[1]))
            expr = BinaryOp(expr, "*", right)
            results.append("ok")
        elif cmd == "set":
            name_val = parts[1].split("=")
            env[name_val[0]] = float(name_val[1])
            results.append("ok")
        elif cmd == "eval":
            try:
                value = Evaluator(env).evaluate(expr)
                results.append(str(value))
            except ValueError as e:
                results.append(f"error:{e}")
        elif cmd == "print":
            results.append(Printer().visit_literal(expr) if isinstance(expr, Literal) else "expr")
        elif cmd == "depth":
            results.append(
                str(DepthCalculator().visit_literal(expr) if isinstance(expr, Literal) else 1)
            )

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: generic_visitor_cli.py <command> [args...]")
        print("Commands: eval, print, vars, depth, simplify")
        return 1

    cmd = sys.argv[1]

    if cmd == "eval":
        if len(sys.argv) < 3:
            print("Usage: eval <expr>", file=sys.stderr)
            return 1
        expr = build_expr(sys.argv[2])
        result = Evaluator().evaluate(expr)
        print(result)

    elif cmd == "print":
        if len(sys.argv) < 3:
            print("Usage: print <expr>", file=sys.stderr)
            return 1
        expr = build_expr(sys.argv[2])
        result = Printer().visit_binary_op(expr) if isinstance(expr, BinaryOp) else str(expr)
        print(result)

    elif cmd == "vars":
        if len(sys.argv) < 3:
            print("Usage: vars <expr>", file=sys.stderr)
            return 1
        expr = build_expr(sys.argv[2])
        variables = (
            VariableCollector().visit_variable(expr) if isinstance(expr, Variable) else set()
        )
        print(", ".join(sorted(variables)) if variables else "(none)")

    elif cmd == "depth":
        if len(sys.argv) < 3:
            print("Usage: depth <expr>", file=sys.stderr)
            return 1
        expr = build_expr(sys.argv[2])
        depth = DepthCalculator().visit_literal(expr) if isinstance(expr, Literal) else 1
        print(depth)

    return 0


if __name__ == "__main__":
    sys.exit(main())
