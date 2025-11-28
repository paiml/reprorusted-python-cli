#!/usr/bin/env python3
"""Standard Library Random CLI.

Random number generation using Python's random module.
"""

import argparse
import random
import sys


def random_float() -> float:
    """Random float in [0.0, 1.0)."""
    return random.random()


def random_uniform(a: float, b: float) -> float:
    """Random float in [a, b]."""
    return random.uniform(a, b)


def random_int(a: int, b: int) -> int:
    """Random integer in [a, b] inclusive."""
    return random.randint(a, b)


def random_range(start: int, stop: int, step: int = 1) -> int:
    """Random from range(start, stop, step)."""
    return random.randrange(start, stop, step)


def random_choice(items: list) -> any:
    """Random choice from sequence."""
    return random.choice(items)


def random_choices(items: list, k: int) -> list:
    """Random choices with replacement."""
    return random.choices(items, k=k)


def random_sample(items: list, k: int) -> list:
    """Random sample without replacement."""
    return random.sample(items, k)


def shuffle_list(items: list) -> list:
    """Shuffle list in place and return."""
    result = items.copy()
    random.shuffle(result)
    return result


def random_gauss(mu: float, sigma: float) -> float:
    """Gaussian distribution."""
    return random.gauss(mu, sigma)


def random_normalvariate(mu: float, sigma: float) -> float:
    """Normal distribution."""
    return random.normalvariate(mu, sigma)


def random_triangular(low: float, high: float, mode: float) -> float:
    """Triangular distribution."""
    return random.triangular(low, high, mode)


def random_expovariate(lambd: float) -> float:
    """Exponential distribution."""
    return random.expovariate(lambd)


def random_betavariate(alpha: float, beta: float) -> float:
    """Beta distribution."""
    return random.betavariate(alpha, beta)


def random_gammavariate(alpha: float, beta: float) -> float:
    """Gamma distribution."""
    return random.gammavariate(alpha, beta)


def random_paretovariate(alpha: float) -> float:
    """Pareto distribution."""
    return random.paretovariate(alpha)


def random_weibullvariate(alpha: float, beta: float) -> float:
    """Weibull distribution."""
    return random.weibullvariate(alpha, beta)


def set_seed(seed: int) -> None:
    """Set random seed for reproducibility."""
    random.seed(seed)


def get_state() -> tuple:
    """Get random state."""
    return random.getstate()


def set_state(state: tuple) -> None:
    """Set random state."""
    random.setstate(state)


def generate_password(
    length: int, use_upper: bool = True, use_digits: bool = True, use_special: bool = False
) -> str:
    """Generate random password."""
    chars = "abcdefghijklmnopqrstuvwxyz"
    if use_upper:
        chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if use_digits:
        chars += "0123456789"
    if use_special:
        chars += "!@#$%^&*"
    return "".join(random.choices(chars, k=length))


def generate_uuid_like() -> str:
    """Generate UUID-like string."""
    hex_chars = "0123456789abcdef"
    parts = [
        "".join(random.choices(hex_chars, k=8)),
        "".join(random.choices(hex_chars, k=4)),
        "".join(random.choices(hex_chars, k=4)),
        "".join(random.choices(hex_chars, k=4)),
        "".join(random.choices(hex_chars, k=12)),
    ]
    return "-".join(parts)


def weighted_choice(items: list, weights: list[float]) -> any:
    """Weighted random choice."""
    return random.choices(items, weights=weights, k=1)[0]


def reservoir_sample(items: list, k: int) -> list:
    """Reservoir sampling for streaming data."""
    result = []
    for i, item in enumerate(items):
        if i < k:
            result.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                result[j] = item
    return result


def dice_roll(num_dice: int, sides: int) -> list[int]:
    """Roll dice."""
    return [random.randint(1, sides) for _ in range(num_dice)]


def coin_flips(n: int) -> list[str]:
    """Flip coins."""
    return [random.choice(["H", "T"]) for _ in range(n)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Random number CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # float
    subparsers.add_parser("float", help="Random float [0,1)")

    # uniform
    uniform_p = subparsers.add_parser("uniform", help="Uniform distribution")
    uniform_p.add_argument("a", type=float)
    uniform_p.add_argument("b", type=float)

    # int
    int_p = subparsers.add_parser("int", help="Random integer")
    int_p.add_argument("a", type=int)
    int_p.add_argument("b", type=int)

    # choice
    choice_p = subparsers.add_parser("choice", help="Random choice")
    choice_p.add_argument("items", nargs="+")

    # sample
    sample_p = subparsers.add_parser("sample", help="Random sample")
    sample_p.add_argument("items", nargs="+")
    sample_p.add_argument("-k", type=int, default=1)

    # shuffle
    shuffle_p = subparsers.add_parser("shuffle", help="Shuffle items")
    shuffle_p.add_argument("items", nargs="+")

    # password
    pwd_p = subparsers.add_parser("password", help="Generate password")
    pwd_p.add_argument("-l", "--length", type=int, default=12)
    pwd_p.add_argument("--no-upper", action="store_true")
    pwd_p.add_argument("--no-digits", action="store_true")
    pwd_p.add_argument("--special", action="store_true")

    # dice
    dice_p = subparsers.add_parser("dice", help="Roll dice")
    dice_p.add_argument("-n", type=int, default=1, help="Number of dice")
    dice_p.add_argument("-s", "--sides", type=int, default=6)

    # coin
    coin_p = subparsers.add_parser("coin", help="Flip coins")
    coin_p.add_argument("-n", type=int, default=1)

    # gauss
    gauss_p = subparsers.add_parser("gauss", help="Gaussian distribution")
    gauss_p.add_argument("--mu", type=float, default=0.0)
    gauss_p.add_argument("--sigma", type=float, default=1.0)

    # seed
    seed_p = subparsers.add_parser("seed", help="Set seed")
    seed_p.add_argument("seed", type=int)

    args = parser.parse_args()

    if args.command == "float":
        print(random_float())
    elif args.command == "uniform":
        print(random_uniform(args.a, args.b))
    elif args.command == "int":
        print(random_int(args.a, args.b))
    elif args.command == "choice":
        print(random_choice(args.items))
    elif args.command == "sample":
        print(random_sample(args.items, args.k))
    elif args.command == "shuffle":
        print(shuffle_list(args.items))
    elif args.command == "password":
        print(generate_password(args.length, not args.no_upper, not args.no_digits, args.special))
    elif args.command == "dice":
        rolls = dice_roll(args.n, args.sides)
        print(f"Rolls: {rolls}, Sum: {sum(rolls)}")
    elif args.command == "coin":
        flips = coin_flips(args.n)
        print(f"Flips: {flips}")
    elif args.command == "gauss":
        print(random_gauss(args.mu, args.sigma))
    elif args.command == "seed":
        set_seed(args.seed)
        print(f"Seed set to {args.seed}")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
