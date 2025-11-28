#!/usr/bin/env python3
"""Graph Topological Sort CLI.

Topological sorting algorithms for DAGs.
"""

import argparse
import sys
from collections import deque


class DirectedGraph:
    """Directed graph for topological sort."""

    def __init__(self) -> None:
        self._adj: dict[int, list[int]] = {}
        self._in_degree: dict[int, int] = {}

    def add_vertex(self, v: int) -> None:
        """Add vertex if not exists."""
        if v not in self._adj:
            self._adj[v] = []
            self._in_degree[v] = 0

    def add_edge(self, u: int, v: int) -> None:
        """Add directed edge u -> v."""
        self.add_vertex(u)
        self.add_vertex(v)
        self._adj[u].append(v)
        self._in_degree[v] += 1

    def neighbors(self, v: int) -> list[int]:
        """Get outgoing neighbors."""
        return self._adj.get(v, [])

    def vertices(self) -> list[int]:
        """Get all vertices."""
        return list(self._adj.keys())

    def in_degree(self, v: int) -> int:
        """Get in-degree of vertex."""
        return self._in_degree.get(v, 0)


def topo_sort_kahn(graph: DirectedGraph) -> list[int] | None:
    """Kahn's algorithm - BFS-based topological sort."""
    in_degree = {v: graph.in_degree(v) for v in graph.vertices()}
    queue: deque[int] = deque([v for v in graph.vertices() if in_degree[v] == 0])
    result: list[int] = []

    while queue:
        vertex = queue.popleft()
        result.append(vertex)

        for neighbor in graph.neighbors(vertex):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph.vertices()):
        return None  # Cycle detected

    return result


def topo_sort_dfs(graph: DirectedGraph) -> list[int] | None:
    """DFS-based topological sort."""
    visited: set[int] = set()
    temp_mark: set[int] = set()
    result: list[int] = []
    has_cycle = False

    def visit(v: int) -> None:
        nonlocal has_cycle
        if has_cycle:
            return
        if v in temp_mark:
            has_cycle = True
            return
        if v in visited:
            return

        temp_mark.add(v)
        for neighbor in graph.neighbors(v):
            visit(neighbor)
        temp_mark.remove(v)
        visited.add(v)
        result.append(v)

    for vertex in graph.vertices():
        if vertex not in visited:
            visit(vertex)
            if has_cycle:
                return None

    result.reverse()
    return result


def all_topo_sorts(graph: DirectedGraph) -> list[list[int]]:
    """Find all possible topological orderings."""
    in_degree = {v: graph.in_degree(v) for v in graph.vertices()}
    result: list[list[int]] = []
    current: list[int] = []

    def backtrack() -> None:
        candidates = [v for v in graph.vertices() if in_degree[v] == 0 and v not in current]

        if not candidates:
            if len(current) == len(graph.vertices()):
                result.append(current.copy())
            return

        for v in sorted(candidates):
            current.append(v)
            for neighbor in graph.neighbors(v):
                in_degree[neighbor] -= 1

            backtrack()

            current.pop()
            for neighbor in graph.neighbors(v):
                in_degree[neighbor] += 1

    backtrack()
    return result


def has_cycle(graph: DirectedGraph) -> bool:
    """Check if directed graph has a cycle."""
    return topo_sort_kahn(graph) is None


def longest_path_dag(graph: DirectedGraph) -> int:
    """Find longest path in DAG."""
    topo = topo_sort_kahn(graph)
    if topo is None:
        return -1  # Has cycle

    distances: dict[int, int] = dict.fromkeys(graph.vertices(), 0)

    for vertex in topo:
        for neighbor in graph.neighbors(vertex):
            distances[neighbor] = max(distances[neighbor], distances[vertex] + 1)

    return max(distances.values()) if distances else 0


def critical_path(graph: DirectedGraph, durations: dict[int, int]) -> tuple[int, list[int]]:
    """Find critical path (longest path with node weights)."""
    topo = topo_sort_kahn(graph)
    if topo is None:
        return (-1, [])

    earliest: dict[int, int] = {}
    predecessor: dict[int, int] = {}

    for vertex in topo:
        max_pred = 0
        best_pred = -1
        for v in graph.vertices():
            if vertex in graph.neighbors(v):
                pred_time = earliest.get(v, 0) + durations.get(v, 0)
                if pred_time > max_pred:
                    max_pred = pred_time
                    best_pred = v
        earliest[vertex] = max_pred
        if best_pred >= 0:
            predecessor[vertex] = best_pred

    # Find the vertex with maximum completion time
    max_time = 0
    end_vertex = -1
    for v in topo:
        completion = earliest[v] + durations.get(v, 0)
        if completion >= max_time:
            max_time = completion
            end_vertex = v

    # Reconstruct critical path
    path: list[int] = []
    current = end_vertex
    while current >= 0:
        path.append(current)
        current = predecessor.get(current, -1)

    path.reverse()
    return (max_time, path)


def dependency_levels(graph: DirectedGraph) -> list[list[int]]:
    """Group vertices by dependency level (parallelizable groups)."""
    in_degree = {v: graph.in_degree(v) for v in graph.vertices()}
    current = [v for v in graph.vertices() if in_degree[v] == 0]
    levels: list[list[int]] = []

    while current:
        levels.append(sorted(current))
        next_level: list[int] = []
        for v in current:
            for neighbor in graph.neighbors(v):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_level.append(neighbor)
        current = next_level

    return levels


def is_dag(graph: DirectedGraph) -> bool:
    """Check if graph is a DAG."""
    return not has_cycle(graph)


def source_vertices(graph: DirectedGraph) -> list[int]:
    """Find all source vertices (in-degree 0)."""
    return sorted([v for v in graph.vertices() if graph.in_degree(v) == 0])


def sink_vertices(graph: DirectedGraph) -> list[int]:
    """Find all sink vertices (out-degree 0)."""
    return sorted([v for v in graph.vertices() if len(graph.neighbors(v)) == 0])


def build_directed_graph(edges: list[str]) -> DirectedGraph:
    """Build directed graph from edge strings like '1-2'."""
    graph = DirectedGraph()
    for edge in edges:
        parts = edge.split("-")
        u, v = int(parts[0]), int(parts[1])
        graph.add_edge(u, v)
    return graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Graph topological sort CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # sort
    sort_p = subparsers.add_parser("sort", help="Topological sort")
    sort_p.add_argument("edges", nargs="+")

    # cycle
    cycle_p = subparsers.add_parser("cycle", help="Cycle detection")
    cycle_p.add_argument("edges", nargs="+")

    # levels
    levels_p = subparsers.add_parser("levels", help="Dependency levels")
    levels_p.add_argument("edges", nargs="+")

    # longest
    longest_p = subparsers.add_parser("longest", help="Longest path")
    longest_p.add_argument("edges", nargs="+")

    args = parser.parse_args()

    if args.command == "sort":
        graph = build_directed_graph(args.edges)
        result = topo_sort_kahn(graph)
        if result:
            print(f"Topological order: {result}")
        else:
            print("Cycle detected - no valid ordering")

    elif args.command == "cycle":
        graph = build_directed_graph(args.edges)
        if has_cycle(graph):
            print("Cycle detected")
        else:
            print("No cycle")

    elif args.command == "levels":
        graph = build_directed_graph(args.edges)
        levels = dependency_levels(graph)
        print(f"Levels: {levels}")

    elif args.command == "longest":
        graph = build_directed_graph(args.edges)
        length = longest_path_dag(graph)
        print(f"Longest path: {length}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
