#!/usr/bin/env python3
"""Prime Factorization CLI.

Prime number operations and factorization without external dependencies.
"""

import argparse
import sys
from math import isqrt


def is_prime(n: int) -> bool:
    """Check if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    for i in range(3, isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


def sieve_of_eratosthenes(limit: int) -> list[int]:
    """Generate all primes up to limit."""
    if limit < 2:
        return []

    is_prime_arr = [True] * (limit + 1)
    is_prime_arr[0] = is_prime_arr[1] = False

    for i in range(2, isqrt(limit) + 1):
        if is_prime_arr[i]:
            for j in range(i * i, limit + 1, i):
                is_prime_arr[j] = False

    return [i for i in range(limit + 1) if is_prime_arr[i]]


def prime_factors(n: int) -> list[int]:
    """Find prime factors (with repetition)."""
    if n < 2:
        return []

    factors = []
    d = 2

    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1

    if n > 1:
        factors.append(n)

    return factors


def prime_factorization(n: int) -> dict[int, int]:
    """Get prime factorization as {prime: exponent}."""
    factors = prime_factors(n)
    result: dict[int, int] = {}

    for p in factors:
        result[p] = result.get(p, 0) + 1

    return result


def count_divisors(n: int) -> int:
    """Count the number of divisors."""
    factorization = prime_factorization(n)
    count = 1

    for exp in factorization.values():
        count *= exp + 1

    return count


def sum_of_divisors(n: int) -> int:
    """Calculate sum of all divisors."""
    factorization = prime_factorization(n)
    total = 1

    for p, exp in factorization.items():
        # Sum of geometric series: 1 + p + p^2 + ... + p^exp
        total *= (p ** (exp + 1) - 1) // (p - 1)

    return total


def divisors(n: int) -> list[int]:
    """Find all divisors of n."""
    if n < 1:
        return []

    result = []
    for i in range(1, isqrt(n) + 1):
        if n % i == 0:
            result.append(i)
            if i != n // i:
                result.append(n // i)

    return sorted(result)


def gcd(a: int, b: int) -> int:
    """Calculate GCD using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Calculate LCM."""
    return abs(a * b) // gcd(a, b)


def gcd_multiple(numbers: list[int]) -> int:
    """Calculate GCD of multiple numbers."""
    result = numbers[0]
    for n in numbers[1:]:
        result = gcd(result, n)
    return result


def lcm_multiple(numbers: list[int]) -> int:
    """Calculate LCM of multiple numbers."""
    result = numbers[0]
    for n in numbers[1:]:
        result = lcm(result, n)
    return result


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm. Returns (gcd, x, y) where ax + by = gcd."""
    if b == 0:
        return a, 1, 0

    g, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1

    return g, x, y


def mod_inverse(a: int, m: int) -> int:
    """Calculate modular multiplicative inverse."""
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        raise ValueError("Modular inverse doesn't exist")
    return x % m


def euler_totient(n: int) -> int:
    """Calculate Euler's totient function (phi)."""
    if n < 1:
        return 0

    result = n
    factorization = prime_factorization(n)

    for p in factorization.keys():
        result -= result // p

    return result


def is_coprime(a: int, b: int) -> bool:
    """Check if two numbers are coprime."""
    return gcd(a, b) == 1


def next_prime(n: int) -> int:
    """Find the next prime after n."""
    if n < 2:
        return 2

    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1

    return candidate


def prev_prime(n: int) -> int:
    """Find the previous prime before n."""
    if n <= 2:
        raise ValueError("No prime before 2")

    candidate = n - 1
    while candidate > 1 and not is_prime(candidate):
        candidate -= 1

    if candidate < 2:
        raise ValueError("No prime found")

    return candidate


def nth_prime(n: int) -> int:
    """Find the nth prime number (1-indexed)."""
    if n < 1:
        raise ValueError("n must be positive")

    count = 0
    candidate = 1

    while count < n:
        candidate += 1
        if is_prime(candidate):
            count += 1

    return candidate


def prime_counting(n: int) -> int:
    """Count primes up to n (pi function)."""
    return len(sieve_of_eratosthenes(n))


def is_perfect_number(n: int) -> bool:
    """Check if n is a perfect number."""
    if n < 2:
        return False
    return sum_of_divisors(n) - n == n


def is_abundant(n: int) -> bool:
    """Check if n is an abundant number."""
    if n < 2:
        return False
    return sum_of_divisors(n) - n > n


def is_deficient(n: int) -> bool:
    """Check if n is a deficient number."""
    if n < 2:
        return False
    return sum_of_divisors(n) - n < n


def radical(n: int) -> int:
    """Calculate the radical (product of distinct prime factors)."""
    return product_of_list(list(prime_factorization(n).keys()))


def product_of_list(lst: list[int]) -> int:
    """Calculate product of list elements."""
    result = 1
    for x in lst:
        result *= x
    return result


def mobius(n: int) -> int:
    """Calculate Möbius function."""
    if n < 1:
        return 0

    factorization = prime_factorization(n)

    # Check for squared prime factors
    for exp in factorization.values():
        if exp > 1:
            return 0

    # (-1)^k where k is number of prime factors
    k = len(factorization)
    return (-1) ** k


def format_factorization(n: int) -> str:
    """Format prime factorization as string."""
    factorization = prime_factorization(n)

    if not factorization:
        return str(n)

    parts = []
    for p, exp in sorted(factorization.items()):
        if exp == 1:
            parts.append(str(p))
        else:
            parts.append(f"{p}^{exp}")

    return " × ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prime number operations")
    parser.add_argument("values", nargs="*", type=int, help="Numbers to process")
    parser.add_argument(
        "--mode",
        choices=[
            "factor",
            "check",
            "sieve",
            "divisors",
            "gcd",
            "lcm",
            "totient",
            "nth",
            "count",
            "classify",
        ],
        default="factor",
        help="Operation mode",
    )
    parser.add_argument("--limit", type=int, default=100, help="Limit for sieve")

    args = parser.parse_args()

    if args.mode == "sieve":
        primes = sieve_of_eratosthenes(args.limit)
        print(f"Primes up to {args.limit}: {primes}")
        print(f"Count: {len(primes)}")

    elif args.mode == "nth" and args.values:
        for n in args.values:
            p = nth_prime(n)
            print(f"Prime #{n}: {p}")

    elif args.mode == "count" and args.values:
        for n in args.values:
            count = prime_counting(n)
            print(f"π({n}) = {count}")

    elif args.values:
        if args.mode == "factor":
            for n in args.values:
                print(f"{n} = {format_factorization(n)}")
                factors = prime_factors(n)
                print(f"  Factors: {factors}")
                print(f"  Divisors: {divisors(n)}")

        elif args.mode == "check":
            for n in args.values:
                result = "prime" if is_prime(n) else "composite"
                print(f"{n}: {result}")

        elif args.mode == "divisors":
            for n in args.values:
                d = divisors(n)
                print(f"Divisors of {n}: {d}")
                print(f"  Count: {len(d)}")
                print(f"  Sum: {sum(d)}")

        elif args.mode == "gcd":
            result = gcd_multiple(args.values)
            print(f"GCD({', '.join(map(str, args.values))}) = {result}")

        elif args.mode == "lcm":
            result = lcm_multiple(args.values)
            print(f"LCM({', '.join(map(str, args.values))}) = {result}")

        elif args.mode == "totient":
            for n in args.values:
                phi = euler_totient(n)
                print(f"φ({n}) = {phi}")

        elif args.mode == "classify":
            for n in args.values:
                classifications = []
                if is_prime(n):
                    classifications.append("prime")
                if is_perfect_number(n):
                    classifications.append("perfect")
                if is_abundant(n):
                    classifications.append("abundant")
                if is_deficient(n):
                    classifications.append("deficient")

                print(f"{n}: {', '.join(classifications) or 'n/a'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
