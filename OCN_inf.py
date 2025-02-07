from basic_fns import adjacency, available, selection

def update_requirements(a, requirements, adjacency_list, reverse=False):
    Y = adjacency_list[a]
    new_requirements = [X for X in requirements if a != X[0]]
    requirements.clear()
    requirements.extend(new_requirements)
    if len(Y) > 1:
        increment = -1 if reverse else 1
        for i in range(1, len(Y)):
            prev_index = i - increment
            if 0 <= prev_index < len(Y):
                requirements.append((Y[prev_index][0], Y[i][0]))

def check_in_min(edges, n):
    remaining = list(range(n))
    min_embedding = []
    requirements = []
    adj_min = adjacency(edges, n)
    e_min = edges[:]
    while e_min:
        a = selection(e_min[0][0], e_min[0][1], remaining, adj_min, requirements)
        if a == "error":
            return []
        else:
            min_embedding.append(a)
            remaining.remove(a)
            new_requirements = [X for X in requirements if a != X[0]]
            requirements.clear()
            requirements.extend(new_requirements)
            Y = adj_min[a]
            if len(Y) > 1:
                for i in range(1, len(Y)):
                    requirements.append((Y[i-1][0], Y[i][0]))
            new_e_min = [edge for edge in e_min if a not in edge]
            e_min.clear()
            e_min.extend(new_e_min)
            for vertex, _ in Y:
                adj_min[vertex] = [(v, i) for v, i in adj_min[vertex] if v != a]
    while remaining:
        for a in remaining:
            if available(a, requirements):
                break
        else: 
            return []
        min_embedding.append(a)
        remaining.remove(a)
        new_requirements = [X for X in requirements if a != X[0]]
        requirements.clear()
        requirements.extend(new_requirements)
    return min_embedding

def check_in_inv_min(edges, n):
    remaining = list(range(n))
    inv_min_embedding = []
    requirements = []
    adj_inv_min = adjacency(edges, n)
    e_inv_min = edges[:]
    while e_inv_min:
        a = selection(e_inv_min[0][0], e_inv_min[0][1], remaining, adj_inv_min, requirements)
        if a == "error":
            return []
        else:
            inv_min_embedding.append(a)
            remaining.remove(a)
            new_requirements = [X for X in requirements if a != X[0]]
            requirements.clear()
            requirements.extend(new_requirements)
            Y = adj_inv_min[a]
            if len(Y) > 1:
                for i in range(1, len(Y)):
                    requirements.append((Y[i][0], Y[i-1][0]))
            new_e_inv_min = [edge for edge in e_inv_min if a != edge[0] and a != edge[1]]
            e_inv_min.clear()
            e_inv_min.extend(new_e_inv_min)
            for vertex, _  in Y:
                adj_inv_min[vertex] = [(v, i) for v, i in adj_inv_min[vertex] if v != a]
    while remaining:
        for a in remaining:
            if available(a, requirements):
                break
        else: 
            return []
        inv_min_embedding.append(a)
        remaining.remove(a)
        new_requirements = [X for X in requirements if a != X[0]]
        requirements.clear()
        requirements.extend(new_requirements)
    return inv_min_embedding

def check_in_max(edges, n):
    r_max_embedding = check_in_min(list(reversed(edges)), n)
    if not r_max_embedding:
        return []
    else:
        return r_max_embedding

def check_in_inv_max(edges, n):
    r_inv_max_embedding = check_in_inv_min(list(reversed(edges)), n)
    if not r_inv_max_embedding:
        return []
    else:
        return r_inv_max_embedding

def check_OCN_infinite(edges, n):
    in_min = check_in_min(edges, n)
    print(f'Min embedding: {in_min}')
    in_inv_min = check_in_inv_min(edges, n)
    print(f'Inv min embedding: {in_inv_min}')
    in_max = check_in_max(edges, n)
    print(f'Max embedding: {in_max}')
    in_inv_max = check_in_inv_max(edges, n)
    print(f'Inv max embedding: {in_inv_max}')
    return all([in_min, in_inv_min, in_max, in_inv_max])


