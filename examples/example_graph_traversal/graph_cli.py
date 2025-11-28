#!/usr/bin/env python3
"""Graph Traversal CLI.

Graph algorithms: BFS, DFS, shortest path, cycle detection, topological sort.
"""

import argparse
import sys
from collections import deque


class Graph:
    """Adjacency list graph representation."""

    def __init__(self, directed: bool = False):
        self.directed = directed
        self.adj: dict[str, list[str]] = {}
        self.weights: dict[tuple[str, str], int] = {}

    def add_vertex(self, v: str) -> None:
        """Add a vertex to the graph."""
        if v not in self.adj:
            self.adj[v] = []

    def add_edge(self, u: str, v: str, weight: int = 1) -> None:
        """Add an edge from u to v."""
        self.add_vertex(u)
        self.add_vertex(v)

        self.adj[u].append(v)
        self.weights[(u, v)] = weight

        if not self.directed:
            self.adj[v].append(u)
            self.weights[(v, u)] = weight

    def vertices(self) -> list[str]:
        """Get all vertices."""
        return list(self.adj.keys())

    def edges(self) -> list[tuple[str, str, int]]:
        """Get all edges with weights."""
        result = []
        seen = set()

        for u in self.adj:
            for v in self.adj[u]:
                edge = (min(u, v), max(u, v)) if not self.directed else (u, v)
                if edge not in seen:
                    seen.add(edge)
                    result.append((u, v, self.weights.get((u, v), 1)))

        return result

    def neighbors(self, v: str) -> list[str]:
        """Get neighbors of vertex."""
        return self.adj.get(v, [])


def bfs(graph: Graph, start: str) -> list[str]:
    """Breadth-first search traversal."""
    if start not in graph.adj:
        return []

    visited = set()
    result = []
    queue = deque([start])

    while queue:
        v = queue.popleft()
        if v in visited:
            continue

        visited.add(v)
        result.append(v)

        for neighbor in graph.neighbors(v):
            if neighbor not in visited:
                queue.append(neighbor)

    return result


def dfs(graph: Graph, start: str) -> list[str]:
    """Depth-first search traversal (iterative)."""
    if start not in graph.adj:
        return []

    visited = set()
    result = []
    stack = [start]

    while stack:
        v = stack.pop()
        if v in visited:
            continue

        visited.add(v)
        result.append(v)

        for neighbor in reversed(graph.neighbors(v)):
            if neighbor not in visited:
                stack.append(neighbor)

    return result


def dfs_recursive(graph: Graph, start: str, visited: set | None = None) -> list[str]:
    """Depth-first search traversal (recursive)."""
    if visited is None:
        visited = set()

    if start not in graph.adj or start in visited:
        return []

    visited.add(start)
    result = [start]

    for neighbor in graph.neighbors(start):
        result.extend(dfs_recursive(graph, neighbor, visited))

    return result


def shortest_path_bfs(graph: Graph, start: str, end: str) -> list[str]:
    """Find shortest path using BFS (unweighted)."""
    if start not in graph.adj or end not in graph.adj:
        return []

    if start == end:
        return [start]

    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        v, path = queue.popleft()

        for neighbor in graph.neighbors(v):
            if neighbor == end:
                return path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []


def dijkstra(graph: Graph, start: str, end: str) -> tuple[list[str], int]:
    """Find shortest path using Dijkstra's algorithm (weighted)."""
    if start not in graph.adj or end not in graph.adj:
        return [], -1

    distances = {v: float("inf") for v in graph.vertices()}
    distances[start] = 0
    previous: dict[str, str | None] = dict.fromkeys(graph.vertices())
    unvisited = set(graph.vertices())

    while unvisited:
        current = min(unvisited, key=lambda v: distances[v])

        if distances[current] == float("inf"):
            break

        if current == end:
            break

        unvisited.remove(current)

        for neighbor in graph.neighbors(current):
            if neighbor in unvisited:
                weight = graph.weights.get((current, neighbor), 1)
                alt = distances[current] + weight

                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    previous[neighbor] = current

    if distances[end] == float("inf"):
        return [], -1

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]

    return list(reversed(path)), int(distances[end])


def has_cycle(graph: Graph) -> bool:
    """Detect if graph has a cycle."""
    if graph.directed:
        return has_cycle_directed(graph)
    return has_cycle_undirected(graph)


def has_cycle_directed(graph: Graph) -> bool:
    """Detect cycle in directed graph using colors."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph.vertices(), WHITE)

    def dfs_visit(v: str) -> bool:
        color[v] = GRAY

        for neighbor in graph.neighbors(v):
            if color[neighbor] == GRAY:
                return True
            if color[neighbor] == WHITE and dfs_visit(neighbor):
                return True

        color[v] = BLACK
        return False

    for v in graph.vertices():
        if color[v] == WHITE:
            if dfs_visit(v):
                return True

    return False


def has_cycle_undirected(graph: Graph) -> bool:
    """Detect cycle in undirected graph."""
    visited = set()

    def dfs_visit(v: str, parent: str | None) -> bool:
        visited.add(v)

        for neighbor in graph.neighbors(v):
            if neighbor not in visited:
                if dfs_visit(neighbor, v):
                    return True
            elif neighbor != parent:
                return True

        return False

    for v in graph.vertices():
        if v not in visited:
            if dfs_visit(v, None):
                return True

    return False


def topological_sort(graph: Graph) -> list[str]:
    """Topological sort using Kahn's algorithm."""
    if not graph.directed:
        return []

    in_degree = dict.fromkeys(graph.vertices(), 0)
    for u in graph.adj:
        for v in graph.adj[u]:
            in_degree[v] += 1

    queue = deque([v for v in graph.vertices() if in_degree[v] == 0])
    result = []

    while queue:
        v = queue.popleft()
        result.append(v)

        for neighbor in graph.neighbors(v):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(graph.vertices()):
        return []  # Cycle detected

    return result


def connected_components(graph: Graph) -> list[list[str]]:
    """Find connected components in undirected graph."""
    visited = set()
    components = []

    for v in graph.vertices():
        if v not in visited:
            component = bfs(graph, v)
            for node in component:
                visited.add(node)
            components.append(component)

    return components


def is_bipartite(graph: Graph) -> bool:
    """Check if graph is bipartite."""
    color = {}

    for start in graph.vertices():
        if start in color:
            continue

        queue = deque([start])
        color[start] = 0

        while queue:
            v = queue.popleft()

            for neighbor in graph.neighbors(v):
                if neighbor not in color:
                    color[neighbor] = 1 - color[v]
                    queue.append(neighbor)
                elif color[neighbor] == color[v]:
                    return False

    return True


def parse_edges(edge_strs: list[str]) -> list[tuple[str, str, int]]:
    """Parse edge strings like 'a-b' or 'a-b:5' (weighted)."""
    edges = []
    for edge_str in edge_strs:
        if ":" in edge_str:
            edge_part, weight = edge_str.rsplit(":", 1)
            u, v = edge_part.split("-")
            edges.append((u, v, int(weight)))
        else:
            u, v = edge_str.split("-")
            edges.append((u, v, 1))
    return edges


def main() -> int:
    parser = argparse.ArgumentParser(description="Graph traversal operations")
    parser.add_argument("edges", nargs="*", help="Edges: u-v or u-v:weight")
    parser.add_argument("--directed", action="store_true", help="Directed graph")
    parser.add_argument(
        "--mode",
        choices=["bfs", "dfs", "path", "dijkstra", "cycle", "topo", "components", "bipartite"],
        default="bfs",
        help="Operation mode",
    )
    parser.add_argument("--start", default=None, help="Start vertex")
    parser.add_argument("--end", default=None, help="End vertex")

    args = parser.parse_args()

    graph = Graph(directed=args.directed)

    if args.edges:
        edges = parse_edges(args.edges)
        for u, v, w in edges:
            graph.add_edge(u, v, w)

    if args.mode == "bfs":
        start = args.start or (graph.vertices()[0] if graph.vertices() else "")
        result = bfs(graph, start)
        print(f"BFS from {start}: {' -> '.join(result)}")

    elif args.mode == "dfs":
        start = args.start or (graph.vertices()[0] if graph.vertices() else "")
        result = dfs(graph, start)
        print(f"DFS from {start}: {' -> '.join(result)}")

    elif args.mode == "path":
        if not args.start or not args.end:
            print("Error: --start and --end required for path")
            return 1
        path = shortest_path_bfs(graph, args.start, args.end)
        if path:
            print(f"Path: {' -> '.join(path)}")
        else:
            print("No path found")

    elif args.mode == "dijkstra":
        if not args.start or not args.end:
            print("Error: --start and --end required for dijkstra")
            return 1
        path, dist = dijkstra(graph, args.start, args.end)
        if path:
            print(f"Path: {' -> '.join(path)} (distance: {dist})")
        else:
            print("No path found")

    elif args.mode == "cycle":
        if has_cycle(graph):
            print("Cycle: Yes")
        else:
            print("Cycle: No")

    elif args.mode == "topo":
        result = topological_sort(graph)
        if result:
            print(f"Topological order: {' -> '.join(result)}")
        else:
            print("No valid topological order (cycle or undirected)")

    elif args.mode == "components":
        components = connected_components(graph)
        print(f"Components: {len(components)}")
        for i, comp in enumerate(components):
            print(f"  {i + 1}: {', '.join(comp)}")

    elif args.mode == "bipartite":
        if is_bipartite(graph):
            print("Bipartite: Yes")
        else:
            print("Bipartite: No")

    return 0


if __name__ == "__main__":
    sys.exit(main())
