def initialize_graph():
#	n = 6
#	edges = [[1,2],[3,4],[2,3],[1,4],[2,4],[4,5],[1,5]]
#	edges = [[1,2],[0,1],[2,3],[4,5],[3,4]] # Path 21354
#	edges = [[0,1],[2,3],[1,2],[4,5],[3,4]] # Path 14325

    n = 11
    #edges = [[0,4],[0,1],[0,6],[0,2],[3,1],[3,2],[5,1],[5,2],[6,1],[6,4],[2,1],[2,4],[7,8],[9,10]] # G with OCN 3
    edges = [[0,4],[0,1],[0,6],[0,2],[1,3],[2,3],[1,5],[2,5],[1,6],[4,6],[1,2],[2,4],[7,8],[9,10]] # G with OCN 3

    return edges, n

"""
def initialize_graph():
    n = int(input("Enter the number of vertices: "))
    edges = []
    while True:
        edge_input = input("Enter an edge (u, v) or 'done' to finish: ")
        if edge_input.lower() == 'done':
            break
        u, v = map(int, edge_input.split())
        edges.append((u, v))
    return edges, n
"""

def adjacency(edges, n):
    adjacency_list = [[] for _ in range(n)]
    for i in range(len(edges)):
        a = edges[i][0]
        b = edges[i][1]
        adjacency_list[a].append((b,i))
        adjacency_list[b].append((a,i))
    return adjacency_list

def check_close(a, adjacency_list):
    X = adjacency_list[a]
    if len(X) < 2: # Isolated or leaf vertices are close.
        return True
    return X[-1][1] - X[0][1] == len(X) - 1 # Vertices whose edges (at least 2) form an interval are close.

def available(a, requirements):
    for X in requirements:
        if X[1] == a:
            return False
    return True

def selection(u, v, remaining, adjacency_list, requirements):
    for X in list(remaining):
        if available(X, requirements) and len(adjacency_list[X]) == 0:
            return X
    if available(u, requirements) and len(adjacency_list[u]) == 1:
        return u
    if available(v, requirements) and len(adjacency_list[v]) == 1:
        return v
    if available(u, requirements) and check_close(u, adjacency_list):
        return u
    if available(v, requirements) and check_close(v, adjacency_list):
        return v
    return "error"

