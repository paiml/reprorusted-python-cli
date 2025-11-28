#!/usr/bin/env python3
"""Graph BFS/DFS CLI.

Breadth-first and depth-first search algorithms.
"""

import argparse
import sys
from collections import deque


class Graph:
    """Adjacency list graph representation."""

    def __init__(self, directed: bool = False) -> None:
        self._adj: dict[int, list[int]] = {}
        self._directed: bool = directed

    def add_vertex(self, v: int) -> None:
        """Add vertex if not exists."""
        if v not in self._adj:
            self._adj[v] = []

    def add_edge(self, u: int, v: int) -> None:
        """Add edge u -> v."""
        self.add_vertex(u)
        self.add_vertex(v)
        self._adj[u].append(v)
        if not self._directed:
            self._adj[v].append(u)

    def neighbors(self, v: int) -> list[int]:
        """Get neighbors of vertex."""
        return self._adj.get(v, [])

    def vertices(self) -> list[int]:
        """Get all vertices."""
        return list(self._adj.keys())

    def vertex_count(self) -> int:
        """Get number of vertices."""
        return len(self._adj)


def bfs(graph: Graph, start: int) -> list[int]:
    """Breadth-first search traversal."""
    visited: set[int] = set()
    result: list[int] = []
    queue: deque[int] = deque([start])

    while queue:
        vertex = queue.popleft()
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            for neighbor in sorted(graph.neighbors(vertex)):
                if neighbor not in visited:
                    queue.append(neighbor)

    return result


def dfs(graph: Graph, start: int) -> list[int]:
    """Depth-first search traversal (iterative)."""
    visited: set[int] = set()
    result: list[int] = []
    stack: list[int] = [start]

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            for neighbor in sorted(graph.neighbors(vertex), reverse=True):
                if neighbor not in visited:
                    stack.append(neighbor)

    return result


def dfs_recursive(graph: Graph, start: int) -> list[int]:
    """Depth-first search traversal (recursive)."""
    visited: set[int] = set()
    result: list[int] = []

    def dfs_visit(v: int) -> None:
        visited.add(v)
        result.append(v)
        for neighbor in sorted(graph.neighbors(v)):
            if neighbor not in visited:
                dfs_visit(neighbor)

    dfs_visit(start)
    return result


def bfs_shortest_path(graph: Graph, start: int, end: int) -> list[int]:
    """Find shortest path using BFS (unweighted)."""
    if start == end:
        return [start]

    visited: set[int] = {start}
    queue: deque[tuple[int, list[int]]] = deque([(start, [start])])

    while queue:
        vertex, path = queue.popleft()
        for neighbor in graph.neighbors(vertex):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []


def bfs_distance(graph: Graph, start: int) -> dict[int, int]:
    """Calculate distances from start to all reachable vertices."""
    distances: dict[int, int] = {start: 0}
    queue: deque[int] = deque([start])

    while queue:
        vertex = queue.popleft()
        for neighbor in graph.neighbors(vertex):
            if neighbor not in distances:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)

    return distances


def bfs_level_order(graph: Graph, start: int) -> list[list[int]]:
    """BFS with level grouping."""
    if start not in graph.vertices():
        return []

    levels: list[list[int]] = []
    visited: set[int] = {start}
    current_level: list[int] = [start]

    while current_level:
        levels.append(current_level)
        next_level: list[int] = []
        for vertex in current_level:
            for neighbor in sorted(graph.neighbors(vertex)):
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_level.append(neighbor)
        current_level = next_level

    return levels


def is_connected(graph: Graph) -> bool:
    """Check if undirected graph is connected."""
    vertices = graph.vertices()
    if not vertices:
        return True

    visited = set(bfs(graph, vertices[0]))
    return len(visited) == len(vertices)


def connected_components(graph: Graph) -> list[list[int]]:
    """Find all connected components."""
    visited: set[int] = set()
    components: list[list[int]] = []

    for vertex in graph.vertices():
        if vertex not in visited:
            component = bfs(graph, vertex)
            visited.update(component)
            components.append(sorted(component))

    return components


def has_path(graph: Graph, start: int, end: int) -> bool:
    """Check if path exists between start and end."""
    return end in set(bfs(graph, start))


def cycle_detect_undirected(graph: Graph) -> bool:
    """Detect cycle in undirected graph using DFS."""
    visited: set[int] = set()

    def dfs_cycle(v: int, parent: int) -> bool:
        visited.add(v)
        for neighbor in graph.neighbors(v):
            if neighbor not in visited:
                if dfs_cycle(neighbor, v):
                    return True
            elif neighbor != parent:
                return True
        return False

    for vertex in graph.vertices():
        if vertex not in visited:
            if dfs_cycle(vertex, -1):
                return True

    return False


def bipartite_check(graph: Graph) -> bool:
    """Check if graph is bipartite using BFS coloring."""
    color: dict[int, int] = {}

    for start in graph.vertices():
        if start in color:
            continue

        queue: deque[int] = deque([start])
        color[start] = 0

        while queue:
            vertex = queue.popleft()
            for neighbor in graph.neighbors(vertex):
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    queue.append(neighbor)
                elif color[neighbor] == color[vertex]:
                    return False

    return True


def build_graph(edges: list[str], directed: bool = False) -> Graph:
    """Build graph from edge strings like '1-2'."""
    graph = Graph(directed)
    for edge in edges:
        parts = edge.split("-")
        u, v = int(parts[0]), int(parts[1])
        graph.add_edge(u, v)
    return graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Graph BFS/DFS CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # bfs
    bfs_p = subparsers.add_parser("bfs", help="BFS traversal")
    bfs_p.add_argument("start", type=int)
    bfs_p.add_argument("edges", nargs="+")

    # dfs
    dfs_p = subparsers.add_parser("dfs", help="DFS traversal")
    dfs_p.add_argument("start", type=int)
    dfs_p.add_argument("edges", nargs="+")

    # path
    path_p = subparsers.add_parser("path", help="Shortest path")
    path_p.add_argument("start", type=int)
    path_p.add_argument("end", type=int)
    path_p.add_argument("edges", nargs="+")

    # components
    comp_p = subparsers.add_parser("components", help="Connected components")
    comp_p.add_argument("edges", nargs="+")

    args = parser.parse_args()

    if args.command == "bfs":
        graph = build_graph(args.edges)
        result = bfs(graph, args.start)
        print(f"BFS: {result}")

    elif args.command == "dfs":
        graph = build_graph(args.edges)
        result = dfs(graph, args.start)
        print(f"DFS: {result}")

    elif args.command == "path":
        graph = build_graph(args.edges)
        result = bfs_shortest_path(graph, args.start, args.end)
        print(f"Path: {result}")

    elif args.command == "components":
        graph = build_graph(args.edges)
        result = connected_components(graph)
        print(f"Components: {result}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
