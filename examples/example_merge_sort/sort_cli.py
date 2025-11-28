#!/usr/bin/env python3
"""Merge sort CLI.

Various sorting algorithms with different strategies.
"""

import argparse
import sys
from collections.abc import Callable


def merge_sort(arr: list, key: Callable | None = None, reverse: bool = False) -> list:
    """Classic merge sort with optional key function."""
    if len(arr) <= 1:
        return arr.copy()

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, reverse)
    right = merge_sort(arr[mid:], key, reverse)

    return merge(left, right, key, reverse)


def merge(left: list, right: list, key: Callable | None = None, reverse: bool = False) -> list:
    """Merge two sorted arrays."""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        left_val = key(left[i]) if key else left[i]
        right_val = key(right[j]) if key else right[j]

        if reverse:
            if left_val >= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if left_val <= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort_inplace(arr: list, start: int = 0, end: int | None = None) -> None:
    """In-place merge sort (modifies original array)."""
    if end is None:
        end = len(arr)

    if end - start <= 1:
        return

    mid = (start + end) // 2
    merge_sort_inplace(arr, start, mid)
    merge_sort_inplace(arr, mid, end)
    merge_inplace(arr, start, mid, end)


def merge_inplace(arr: list, start: int, mid: int, end: int) -> None:
    """Merge two sorted subarrays in place."""
    left = arr[start:mid]
    right = arr[mid:end]

    i = j = 0
    k = start

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1

    while i < len(left):
        arr[k] = left[i]
        i += 1
        k += 1

    while j < len(right):
        arr[k] = right[j]
        j += 1
        k += 1


def merge_sort_iterative(arr: list) -> list:
    """Bottom-up iterative merge sort."""
    if len(arr) <= 1:
        return arr.copy()

    result = arr.copy()
    width = 1

    while width < len(result):
        i = 0
        while i < len(result):
            left = i
            mid = min(i + width, len(result))
            right = min(i + 2 * width, len(result))

            merged = merge(result[left:mid], result[mid:right])
            result[left : left + len(merged)] = merged

            i += 2 * width
        width *= 2

    return result


def natural_merge_sort(arr: list) -> list:
    """Natural merge sort - takes advantage of existing runs."""
    if len(arr) <= 1:
        return arr.copy()

    runs = find_runs(arr)

    while len(runs) > 1:
        new_runs = []
        i = 0
        while i < len(runs):
            if i + 1 < len(runs):
                merged = merge(runs[i], runs[i + 1])
                new_runs.append(merged)
                i += 2
            else:
                new_runs.append(runs[i])
                i += 1
        runs = new_runs

    return runs[0] if runs else []


def find_runs(arr: list) -> list[list]:
    """Find natural runs in the array."""
    if not arr:
        return []

    runs = []
    current_run = [arr[0]]

    for i in range(1, len(arr)):
        if arr[i] >= arr[i - 1]:
            current_run.append(arr[i])
        else:
            runs.append(current_run)
            current_run = [arr[i]]

    runs.append(current_run)
    return runs


def count_inversions(arr: list) -> tuple[list, int]:
    """Count inversions using merge sort."""
    if len(arr) <= 1:
        return arr.copy(), 0

    mid = len(arr) // 2
    left, left_inv = count_inversions(arr[:mid])
    right, right_inv = count_inversions(arr[mid:])
    merged, split_inv = merge_count(left, right)

    return merged, left_inv + right_inv + split_inv


def merge_count(left: list, right: list) -> tuple[list, int]:
    """Merge and count split inversions."""
    result = []
    inversions = 0
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            inversions += len(left) - i
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result, inversions


def is_sorted(arr: list, reverse: bool = False) -> bool:
    """Check if array is sorted."""
    if len(arr) <= 1:
        return True

    for i in range(1, len(arr)):
        if reverse:
            if arr[i] > arr[i - 1]:
                return False
        else:
            if arr[i] < arr[i - 1]:
                return False
    return True


def merge_k_sorted(arrays: list[list]) -> list:
    """Merge k sorted arrays."""
    if not arrays:
        return []

    while len(arrays) > 1:
        merged = []
        i = 0
        while i < len(arrays):
            if i + 1 < len(arrays):
                merged.append(merge(arrays[i], arrays[i + 1]))
                i += 2
            else:
                merged.append(arrays[i])
                i += 1
        arrays = merged

    return arrays[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge sort operations")
    parser.add_argument("values", nargs="*", type=int, help="Values to sort")
    parser.add_argument(
        "--mode",
        choices=["sort", "inplace", "iterative", "natural", "inversions", "check"],
        default="sort",
        help="Sort mode",
    )
    parser.add_argument("--reverse", action="store_true", help="Sort in reverse order")

    args = parser.parse_args()

    if not args.values:
        values = [int(x) for x in sys.stdin.read().split()]
    else:
        values = args.values

    if args.mode == "sort":
        result = merge_sort(values, reverse=args.reverse)
        print(" ".join(map(str, result)))
    elif args.mode == "inplace":
        merge_sort_inplace(values)
        if args.reverse:
            values.reverse()
        print(" ".join(map(str, values)))
    elif args.mode == "iterative":
        result = merge_sort_iterative(values)
        if args.reverse:
            result.reverse()
        print(" ".join(map(str, result)))
    elif args.mode == "natural":
        result = natural_merge_sort(values)
        if args.reverse:
            result.reverse()
        print(" ".join(map(str, result)))
    elif args.mode == "inversions":
        _, inv_count = count_inversions(values)
        print(f"Inversions: {inv_count}")
    elif args.mode == "check":
        if is_sorted(values, args.reverse):
            print("Sorted: Yes")
        else:
            print("Sorted: No")

    return 0


if __name__ == "__main__":
    sys.exit(main())
