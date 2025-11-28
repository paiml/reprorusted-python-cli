#!/usr/bin/env python3
"""Union-Find (Disjoint Set) CLI.

Union-Find data structure with path compression and union by rank.
"""

import argparse
import sys


class UnionFind:
    """Union-Find with path compression and union by rank."""

    def __init__(self, n: int) -> None:
        self._parent: list[int] = list(range(n))
        self._rank: list[int] = [0] * n
        self._size: list[int] = [1] * n
        self._count: int = n

    def find(self, x: int) -> int:
        """Find root with path compression."""
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: int, y: int) -> bool:
        """Union by rank. Returns True if merged."""
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        if self._rank[root_x] < self._rank[root_y]:
            root_x, root_y = root_y, root_x

        self._parent[root_y] = root_x
        self._size[root_x] += self._size[root_y]

        if self._rank[root_x] == self._rank[root_y]:
            self._rank[root_x] += 1

        self._count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        """Check if x and y are in same set."""
        return self.find(x) == self.find(y)

    def component_count(self) -> int:
        """Get number of disjoint sets."""
        return self._count

    def component_size(self, x: int) -> int:
        """Get size of component containing x."""
        return self._size[self.find(x)]

    def get_components(self) -> list[list[int]]:
        """Get all components as lists."""
        components: dict[int, list[int]] = {}
        for i in range(len(self._parent)):
            root = self.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)
        return list(components.values())


class WeightedUnionFind:
    """Union-Find with weights (potentials)."""

    def __init__(self, n: int) -> None:
        self._parent: list[int] = list(range(n))
        self._rank: list[int] = [0] * n
        self._weight: list[int] = [0] * n  # weight[i] = potential from i to parent[i]

    def find(self, x: int) -> tuple[int, int]:
        """Find root and return (root, weight from x to root)."""
        if self._parent[x] == x:
            return (x, 0)

        root, w = self.find(self._parent[x])
        self._parent[x] = root
        self._weight[x] += w
        return (root, self._weight[x])

    def union(self, x: int, y: int, w: int) -> bool:
        """Union x and y with weight w (potential of y relative to x)."""
        root_x, wx = self.find(x)
        root_y, wy = self.find(y)

        if root_x == root_y:
            return False

        if self._rank[root_x] < self._rank[root_y]:
            self._parent[root_x] = root_y
            self._weight[root_x] = wy - wx - w
        else:
            self._parent[root_y] = root_x
            self._weight[root_y] = wx - wy + w
            if self._rank[root_x] == self._rank[root_y]:
                self._rank[root_x] += 1

        return True

    def diff(self, x: int, y: int) -> int | None:
        """Get weight difference between x and y if connected."""
        root_x, wx = self.find(x)
        root_y, wy = self.find(y)

        if root_x != root_y:
            return None

        return wy - wx


def kruskal_mst(n: int, edges: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    """Kruskal's MST algorithm using Union-Find."""
    uf = UnionFind(n)
    sorted_edges = sorted(edges, key=lambda e: e[2])
    mst: list[tuple[int, int, int]] = []

    for u, v, w in sorted_edges:
        if not uf.connected(u, v):
            uf.union(u, v)
            mst.append((u, v, w))
            if len(mst) == n - 1:
                break

    return mst


def count_islands(grid: list[list[int]]) -> int:
    """Count connected components in grid (1 = land, 0 = water)."""
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    uf = UnionFind(rows * cols)

    def index(r: int, c: int) -> int:
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                if r > 0 and grid[r - 1][c] == 1:
                    uf.union(index(r, c), index(r - 1, c))
                if c > 0 and grid[r][c - 1] == 1:
                    uf.union(index(r, c), index(r, c - 1))

    roots: set[int] = set()
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                roots.add(uf.find(index(r, c)))

    return len(roots)


def is_connected_graph(n: int, edges: list[tuple[int, int]]) -> bool:
    """Check if graph is connected."""
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.component_count() == 1


def redundant_connection(n: int, edges: list[tuple[int, int]]) -> tuple[int, int] | None:
    """Find edge that creates cycle (redundant connection)."""
    uf = UnionFind(n)
    for u, v in edges:
        if uf.connected(u, v):
            return (u, v)
        uf.union(u, v)
    return None


def earliest_connection(n: int, edges: list[tuple[int, int]]) -> int:
    """Find earliest time when all nodes are connected."""
    uf = UnionFind(n)
    for i, (u, v) in enumerate(edges):
        uf.union(u, v)
        if uf.component_count() == 1:
            return i
    return -1


def largest_component(n: int, edges: list[tuple[int, int]]) -> int:
    """Find size of largest connected component."""
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)

    max_size = 0
    for i in range(n):
        max_size = max(max_size, uf.component_size(i))
    return max_size


def simulate_uf(n: int, ops: list[str]) -> list[int]:
    """Simulate Union-Find operations."""
    uf = UnionFind(n)
    results: list[int] = []

    for op in ops:
        parts = op.split(":")
        cmd = parts[0]

        if cmd == "union":
            x, y = int(parts[1]), int(parts[2])
            uf.union(x, y)
        elif cmd == "find":
            x = int(parts[1])
            results.append(uf.find(x))
        elif cmd == "connected":
            x, y = int(parts[1]), int(parts[2])
            results.append(1 if uf.connected(x, y) else 0)
        elif cmd == "count":
            results.append(uf.component_count())
        elif cmd == "size":
            x = int(parts[1])
            results.append(uf.component_size(x))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Union-Find CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # ops
    ops_p = subparsers.add_parser("ops", help="Union-Find operations")
    ops_p.add_argument("n", type=int)
    ops_p.add_argument("ops", nargs="+")

    # mst
    mst_p = subparsers.add_parser("mst", help="Kruskal MST")
    mst_p.add_argument("n", type=int)
    mst_p.add_argument("edges", nargs="+", help="u-v:w format")

    # connected
    conn_p = subparsers.add_parser("connected", help="Check connectivity")
    conn_p.add_argument("n", type=int)
    conn_p.add_argument("edges", nargs="+", help="u-v format")

    args = parser.parse_args()

    if args.command == "ops":
        results = simulate_uf(args.n, args.ops)
        print(f"Results: {results}")

    elif args.command == "mst":
        edges = []
        for e in args.edges:
            parts = e.split(":")
            verts = parts[0].split("-")
            u, v = int(verts[0]), int(verts[1])
            w = int(parts[1])
            edges.append((u, v, w))
        mst = kruskal_mst(args.n, edges)
        total = sum(w for _, _, w in mst)
        print(f"MST weight: {total}")

    elif args.command == "connected":
        edges = []
        for e in args.edges:
            parts = e.split("-")
            edges.append((int(parts[0]), int(parts[1])))
        connected = is_connected_graph(args.n, edges)
        print(f"Connected: {connected}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
