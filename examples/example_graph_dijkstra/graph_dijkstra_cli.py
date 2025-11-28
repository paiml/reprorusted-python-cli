#!/usr/bin/env python3
"""Graph Dijkstra CLI.

Dijkstra's shortest path algorithm.
"""

import argparse
import heapq
import sys


class WeightedGraph:
    """Weighted adjacency list graph."""

    def __init__(self, directed: bool = False) -> None:
        self._adj: dict[int, list[tuple[int, int]]] = {}
        self._directed: bool = directed

    def add_vertex(self, v: int) -> None:
        """Add vertex if not exists."""
        if v not in self._adj:
            self._adj[v] = []

    def add_edge(self, u: int, v: int, weight: int) -> None:
        """Add weighted edge u -> v."""
        self.add_vertex(u)
        self.add_vertex(v)
        self._adj[u].append((v, weight))
        if not self._directed:
            self._adj[v].append((u, weight))

    def neighbors(self, v: int) -> list[tuple[int, int]]:
        """Get neighbors with weights."""
        return self._adj.get(v, [])

    def vertices(self) -> list[int]:
        """Get all vertices."""
        return list(self._adj.keys())


def dijkstra(graph: WeightedGraph, start: int) -> dict[int, int]:
    """Dijkstra's algorithm - returns distances from start."""
    distances: dict[int, int] = {start: 0}
    heap: list[tuple[int, int]] = [(0, start)]

    while heap:
        dist, vertex = heapq.heappop(heap)

        if dist > distances.get(vertex, float("inf")):
            continue

        for neighbor, weight in graph.neighbors(vertex):
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    return distances


def dijkstra_path(graph: WeightedGraph, start: int, end: int) -> tuple[int, list[int]]:
    """Dijkstra's algorithm - returns distance and path."""
    distances: dict[int, int] = {start: 0}
    predecessors: dict[int, int] = {}
    heap: list[tuple[int, int]] = [(0, start)]

    while heap:
        dist, vertex = heapq.heappop(heap)

        if vertex == end:
            break

        if dist > distances.get(vertex, float("inf")):
            continue

        for neighbor, weight in graph.neighbors(vertex):
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_dist
                predecessors[neighbor] = vertex
                heapq.heappush(heap, (new_dist, neighbor))

    if end not in distances:
        return (-1, [])

    path: list[int] = []
    current = end
    while current in predecessors or current == start:
        path.append(current)
        if current == start:
            break
        current = predecessors[current]

    path.reverse()
    return (distances[end], path)


def bellman_ford(graph: WeightedGraph, start: int) -> dict[int, int] | None:
    """Bellman-Ford algorithm - handles negative weights."""
    vertices = graph.vertices()
    distances: dict[int, int] = dict.fromkeys(vertices, 1000000000)
    distances[start] = 0

    for _ in range(len(vertices) - 1):
        for u in vertices:
            for v, weight in graph.neighbors(u):
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight

    # Check for negative cycles
    for u in vertices:
        for v, weight in graph.neighbors(u):
            if distances[u] + weight < distances[v]:
                return None  # Negative cycle detected

    return distances


def shortest_path_dag(graph: WeightedGraph, start: int, topo_order: list[int]) -> dict[int, int]:
    """Shortest path in DAG using topological order."""
    distances: dict[int, int] = dict.fromkeys(graph.vertices(), 1000000000)
    distances[start] = 0

    start_found = False
    for vertex in topo_order:
        if vertex == start:
            start_found = True
        if not start_found:
            continue

        if distances[vertex] < 1000000000:
            for neighbor, weight in graph.neighbors(vertex):
                if distances[vertex] + weight < distances[neighbor]:
                    distances[neighbor] = distances[vertex] + weight

    return distances


def all_pairs_shortest(graph: WeightedGraph) -> dict[tuple[int, int], int]:
    """All pairs shortest paths using repeated Dijkstra."""
    result: dict[tuple[int, int], int] = {}

    for start in graph.vertices():
        distances = dijkstra(graph, start)
        for end, dist in distances.items():
            result[(start, end)] = dist

    return result


def shortest_path_k_stops(graph: WeightedGraph, start: int, end: int, k: int) -> int:
    """Shortest path with at most k intermediate stops."""
    # BFS with distance tracking
    distances: dict[int, int] = {start: 0}
    queue: list[tuple[int, int, int]] = [(0, start, 0)]  # (dist, vertex, stops)

    result = 1000000000

    while queue:
        dist, vertex, stops = heapq.heappop(queue)

        if vertex == end:
            result = min(result, dist)
            continue

        if stops > k:
            continue

        for neighbor, weight in graph.neighbors(vertex):
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, 1000000000) or stops < k:
                distances[neighbor] = new_dist
                heapq.heappush(queue, (new_dist, neighbor, stops + 1))

    return result if result < 1000000000 else -1


def min_spanning_tree_prim(graph: WeightedGraph) -> list[tuple[int, int, int]]:
    """Prim's algorithm for minimum spanning tree."""
    if not graph.vertices():
        return []

    start = graph.vertices()[0]
    visited: set[int] = {start}
    edges: list[tuple[int, int, int]] = []
    heap: list[tuple[int, int, int]] = []

    for neighbor, weight in graph.neighbors(start):
        heapq.heappush(heap, (weight, start, neighbor))

    while heap and len(visited) < len(graph.vertices()):
        weight, u, v = heapq.heappop(heap)
        if v in visited:
            continue

        visited.add(v)
        edges.append((u, v, weight))

        for neighbor, w in graph.neighbors(v):
            if neighbor not in visited:
                heapq.heappush(heap, (w, v, neighbor))

    return edges


def graph_center(graph: WeightedGraph) -> int:
    """Find graph center (vertex minimizing max distance to others)."""
    all_distances = all_pairs_shortest(graph)
    vertices = graph.vertices()

    min_eccentricity = 1000000000
    center = -1

    for v in vertices:
        eccentricity = 0
        for u in vertices:
            if (v, u) in all_distances:
                eccentricity = max(eccentricity, all_distances[(v, u)])
        if eccentricity < min_eccentricity:
            min_eccentricity = eccentricity
            center = v

    return center


def build_weighted_graph(edges: list[str], directed: bool = False) -> WeightedGraph:
    """Build graph from edge strings like '1-2:5'."""
    graph = WeightedGraph(directed)
    for edge in edges:
        parts = edge.split(":")
        vertices = parts[0].split("-")
        u, v = int(vertices[0]), int(vertices[1])
        weight = int(parts[1]) if len(parts) > 1 else 1
        graph.add_edge(u, v, weight)
    return graph


def main() -> int:
    parser = argparse.ArgumentParser(description="Graph Dijkstra CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # dijkstra
    dij_p = subparsers.add_parser("dijkstra", help="Dijkstra's algorithm")
    dij_p.add_argument("start", type=int)
    dij_p.add_argument("edges", nargs="+")

    # path
    path_p = subparsers.add_parser("path", help="Shortest path")
    path_p.add_argument("start", type=int)
    path_p.add_argument("end", type=int)
    path_p.add_argument("edges", nargs="+")

    # mst
    mst_p = subparsers.add_parser("mst", help="Minimum spanning tree")
    mst_p.add_argument("edges", nargs="+")

    args = parser.parse_args()

    if args.command == "dijkstra":
        graph = build_weighted_graph(args.edges)
        distances = dijkstra(graph, args.start)
        print(f"Distances: {distances}")

    elif args.command == "path":
        graph = build_weighted_graph(args.edges)
        dist, path = dijkstra_path(graph, args.start, args.end)
        print(f"Distance: {dist}, Path: {path}")

    elif args.command == "mst":
        graph = build_weighted_graph(args.edges)
        edges = min_spanning_tree_prim(graph)
        total = sum(w for _, _, w in edges)
        print(f"MST weight: {total}, Edges: {edges}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
