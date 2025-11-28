#!/usr/bin/env python3
"""Binary search CLI.

Binary search implementations with various comparators.
"""

import argparse
import sys
from collections.abc import Callable


def binary_search(arr: list, target, key: Callable | None = None) -> int:
    """Basic binary search. Returns index or -1 if not found."""
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        val = key(arr[mid]) if key else arr[mid]
        target_val = key(target) if key else target

        if val == target_val:
            return mid
        elif val < target_val:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_left(arr: list, target, key: Callable | None = None) -> int:
    """Find leftmost position where target could be inserted."""
    left, right = 0, len(arr)

    while left < right:
        mid = (left + right) // 2
        val = key(arr[mid]) if key else arr[mid]
        target_val = key(target) if key else target

        if val < target_val:
            left = mid + 1
        else:
            right = mid

    return left


def binary_search_right(arr: list, target, key: Callable | None = None) -> int:
    """Find rightmost position where target could be inserted."""
    left, right = 0, len(arr)

    while left < right:
        mid = (left + right) // 2
        val = key(arr[mid]) if key else arr[mid]
        target_val = key(target) if key else target

        if val <= target_val:
            left = mid + 1
        else:
            right = mid

    return left


def count_occurrences(arr: list, target, key: Callable | None = None) -> int:
    """Count occurrences of target in sorted array."""
    left_idx = binary_search_left(arr, target, key)
    right_idx = binary_search_right(arr, target, key)
    return right_idx - left_idx


def find_range(arr: list, target, key: Callable | None = None) -> tuple[int, int]:
    """Find the range [start, end) of target in sorted array."""
    left_idx = binary_search_left(arr, target, key)
    right_idx = binary_search_right(arr, target, key)

    if left_idx == right_idx:
        return -1, -1

    return left_idx, right_idx - 1


def search_rotated(arr: list, target) -> int:
    """Search in a rotated sorted array."""
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid

        # Left half is sorted
        if arr[left] <= arr[mid]:
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


def find_peak(arr: list) -> int:
    """Find a peak element index (element greater than neighbors)."""
    if not arr:
        return -1
    if len(arr) == 1:
        return 0

    left, right = 0, len(arr) - 1

    while left < right:
        mid = (left + right) // 2

        if arr[mid] < arr[mid + 1]:
            left = mid + 1
        else:
            right = mid

    return left


def search_closest(arr: list, target) -> int:
    """Find index of element closest to target."""
    if not arr:
        return -1

    left, right = 0, len(arr) - 1

    while left < right:
        mid = (left + right) // 2

        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid

    # Check neighbors for closest
    if left == 0:
        return 0
    if left == len(arr):
        return len(arr) - 1

    if abs(arr[left] - target) < abs(arr[left - 1] - target):
        return left
    return left - 1


def search_floor(arr: list, target) -> int:
    """Find largest element <= target."""
    if not arr:
        return -1

    idx = binary_search_right(arr, target)

    if idx == 0:
        return -1 if arr[0] > target else 0

    return idx - 1


def search_ceil(arr: list, target) -> int:
    """Find smallest element >= target."""
    if not arr:
        return -1

    idx = binary_search_left(arr, target)

    if idx == len(arr):
        return -1

    return idx


def main() -> int:
    parser = argparse.ArgumentParser(description="Binary search operations")
    parser.add_argument("target", type=int, help="Target value to search")
    parser.add_argument("values", nargs="*", type=int, help="Sorted values to search in")
    parser.add_argument(
        "--mode",
        choices=["find", "left", "right", "count", "range", "closest", "floor", "ceil"],
        default="find",
        help="Search mode",
    )
    parser.add_argument("--rotated", action="store_true", help="Search rotated array")
    parser.add_argument("--peak", action="store_true", help="Find peak element")

    args = parser.parse_args()

    if not args.values:
        values = [int(x) for x in sys.stdin.read().split()]
    else:
        values = args.values

    if args.peak:
        idx = find_peak(values)
        if idx >= 0:
            print(f"Peak at index {idx}: {values[idx]}")
        else:
            print("No peak found")
        return 0

    if args.rotated:
        idx = search_rotated(values, args.target)
    elif args.mode == "find":
        idx = binary_search(values, args.target)
    elif args.mode == "left":
        idx = binary_search_left(values, args.target)
    elif args.mode == "right":
        idx = binary_search_right(values, args.target)
    elif args.mode == "count":
        count = count_occurrences(values, args.target)
        print(f"Count: {count}")
        return 0
    elif args.mode == "range":
        start, end = find_range(values, args.target)
        if start == -1:
            print("Not found")
        else:
            print(f"Range: [{start}, {end}]")
        return 0
    elif args.mode == "closest":
        idx = search_closest(values, args.target)
    elif args.mode == "floor":
        idx = search_floor(values, args.target)
    elif args.mode == "ceil":
        idx = search_ceil(values, args.target)
    else:
        idx = -1

    if idx >= 0:
        print(f"Index: {idx}, Value: {values[idx]}")
    else:
        print("Not found")

    return 0 if idx >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
