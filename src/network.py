from collections import deque

def dfs(start):
    search_queue = []
    visited = []
    search_queue.append(start)
    while search_queue:
        node = search_queue.pop()
        if node not in visited:
            search_queue += node.get_linked_nodes()
            visited.append(node)
    
    visited.remove(start)
    return visited


def bfs(start):
    search_queue = deque()
    visited = []
    search_queue.append(start)
    while search_queue:
        node = search_queue.popleft()
        if node not in visited:
            search_queue += node.get_linked_nodes()
            visited.append(node)

    visited.remove(start)
    return visited


def dijkstra(start):
    costs = {start: 0}
    parents = {start: None}
    visited = []

    node = find_lowest_cost_node(costs, visited)
    while node is not None:
        neighbors = node.get_link_costs()
        for n, c in neighbors.items():
            if n not in costs:
                costs[n] = float('inf')
            if n not in parents:
                parents[n] = node
            new_cost = costs[node] + c
            if costs[n] > new_cost:
                costs[n] = new_cost
                parents[n] = node
        visited.append(node)
        node = find_lowest_cost_node(costs, visited)
    
    del costs[start]
    del parents[start]
    return (costs, parents)


def find_lowest_cost_node(costs, visited):
    lowest_cost = float('inf')
    lowest_cost_node = None
    for n, c in costs.items():
        if n not in visited and c < lowest_cost:
            lowest_cost = c
            lowest_cost_node = n

    return lowest_cost_node
