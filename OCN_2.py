from collections import deque
from basic_fns import adjacency, check_close
# update function name
def is_bipartite(edges, n):
    colors = [0] * n                                            # Colors show which side of which component does a vertex belong to
    component_counter = 1                                       
    X = adjacency(edges,n)                                      
    for start in range(n):                                      
        if colors[start] == 0:                                  # If the current vertex is not colored
            queue = deque([(start, component_counter)])         
            while queue:                                        
                node, color = queue.popleft()                   
                if colors[node] == 0:                           # If the node is not colored
                    colors[node] = color                        
                    for neighbor in X[node]:                    
                        queue.append((neighbor[0], -color))     # Color the neighbor with the opposite color
                else:                                           
                    if colors[node] != color:                   # If the node is already colored and the color is different, the graph is not bipartite
                        return False, [], 0                     
            component_counter += 1                              # New component found
    return True, colors, component_counter - 1

def is_eo_bip(edges, n):
    boolean, colors, component = is_bipartite(edges, n)
    adj = adjacency(edges,n)
    close_side = [True] * (2 * component + 1)
    close_in_component = [0] * (component + 1)
    if not boolean:
        return False
    for i in range(n):                                          # Labels a side of a component non-close if it contains a vertex that is not close
        if not check_close(i, adj):
            close_side[colors[i]] = False 
    for i in range(1, component + 1):
        if close_side[i]:                                       # Non-flippable component and only the + side is close
            if not close_side[-i]:
                close_in_component[i] = 1
        else:                                                   # Non-flippable component and only the - side is close
            if close_side[-i]:
                close_in_component[i] = -1
                for j in range(n):
                    if colors[j] == -i:
                        colors[j] = i
                    elif colors[j] == i:
                        colors[j] = -i                          # Makes sure that the close vertices have positive value
            else:
                return False
    return colors, close_in_component

# generate requirements for outputting the embedding for OCN 2
def req(edges, n, colors, close_in_component):                  # WILL NOT WORK PROPERLY FOR non-flippable component and only the - side is close?
    req1 = []
    req2 = []
    for i in range(len(edges)-1):
        x, y = edges[i]
        z, w = edges[i+1]
        if colors[x] < 0 and close_in_component[abs(colors[x])] == 1:
            x, y = y, x
        if colors[z] < 0:
            z, w = w, z
        if x == z:
            req2.append((y,w))
        else:
            req1.append((x,z))
    return req1, req2

def embedding_in_can_bip(edges, n, req1, req2, colors):
    part1 = []
    part2 = []
    remaining = [True] * n
    num_rem = n
    old_num_rem = n+1
    while old_num_rem > num_rem:
        old_num_rem = num_rem
        for i in range(n):
            if remaining[i]:
                if colors[i] > 0:
                    for j in range(len(req1)):
                        if req1[j][1] == i:
                            break
                    else:
                        part1.append(i)
                        num_rem -= 1
                        remaining[i] == False
                        new_req1 = []
                        for x in req1: 
                            if x[0] != i:
                                new_req1.append(x)
                        req1 = new_req1
                else:
                    for j in range(len(req2)):
                        if req2[j][1] == i:
                            break
                    else:
                        part2.append(i)
                        num_rem -= 1
                        remaining[i] == False
                        new_req2 = []
                        for x in req2: 
                            if x[0] != i:
                                new_req2.append(x)
                        req2 = new_req2
    if num_rem > 0:
        return False
    return part1, part2

def is_OCN_two(edges,n):
    step1 = is_eo_bip(edges,n)
    if not step1:
        return False
    step2 = req(edges,n,step1[0])
    step3 = embedding_in_can_bip(edges, n, step2[0], step2[1],step1[0])
    return step3

