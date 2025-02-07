from basic_fns import adjacency
from OCN_2 import is_eo_bip
from itertools import product, groupby
import pycosat

def vertexsort_for_interleaving(edges,n,t,ican3):
    print('inside vertex sort')
    if ican3[0] == 0:
        low_edges = edges[:t]
        high_edges = edges[t:]
    else:
        low_edges = edges[t:]
        high_edges = edges[:t]
    low_adj = adjacency(low_edges,n) 
    high_adj = adjacency(high_edges,n)
    low_bip = is_eo_bip(low_edges,n)
    high_bip = is_eo_bip(high_edges,n)
    placement = [0]*n                                   # initially every vertex is assigned zero
    if high_bip is not False and low_bip is not False:  # they should be two non-trivial (with at least one edge each) edge-ordered bigraphs 
        for i in range(n):
            k = high_bip[0][i]
            l = low_bip[0][i]
            if high_adj[i]:
                if low_adj[i]:
                    # First we modify the flippability
                    if l < 0 and low_bip[1][-l] == 0: # Low comp is not flippable anymore
                        low_bip[1][l] = 1 
                    elif l > 0 and low_bip[1][l] == 0: # Low comp is not flippable anymore
                        low_bip[1][l] = -1 
                    elif l > 0 and low_bip[1][l] == 1: # i must be placed in A, so a contradiction
                        return False
                    elif l < 0 and low_bip[1][-l] == -1: # i must be placed in A, so a contradiction
                        return False
                # Now we start the placement of the vertices that have high_edges incident to them
                if high_bip[1][abs(k)] == 0: # If high_bip of the component of i is flippable
                    placement[i] = -2 # i is undecided between B or C
                elif high_bip[1][abs(k)] == 1:
                    # The below loops can be replaced by exor: placement[i] = 2 if (k > 0) ^ (ican3[1] != 0) else 3
                    if (ican3[1] == 0 and k > 0) or (ican3[1] != 0 and k < 0):
                        placement[i] = 2 # i belongs to B (high-dom)
                    else:
                        placement[i] = 3 # i belongs to C (high-subdom)                
                elif high_bip[1][abs(k)] == -1:
                    if (ican3[1] == 0 and k > 0) or (ican3[1] != 0 and k < 0):
                        placement[i] = 2 # i belongs to B (high-dom)
                    else:
                        placement[i] = 3 # i belongs to C (high-subdom)
        # Now we start placing vertices that have only low_edges incident to them (or isolated)
        for i in range(n):
            k = high_bip[0][i]
            l = low_bip[0][i]
            if placement[i] == 0:
                if l > 0: 
                    if low_bip[1][l] != -1:
                        placement[i] = 1 # i belongs to A
                    elif low_bip[1][l] == -1:
                        placement[i] = -2 # i is undecided between B or C
                else:
                    if low_bip[1][-l] != -1: 
                        placement[i] = -2 # i is undecided between B or C
                    elif low_bip[1][-l] == -1:
                        placement[i] = 1 # i belongs to A
        return placement
    return False

def generatereq_interleaving(edges, n, t, ican3): 
    print('inside generatereq interleaving')
    print('calling vertex sort')
    placement = vertexsort_for_interleaving(edges, n, t, ican3)
    print('outside vertex sort')
    if ican3[0] == 0:
        low_edges = edges[:t]
        high_edges = edges[t:]
    else:
        low_edges = edges[t:]
        high_edges = edges[:t]
    high_bip = is_eo_bip(high_edges,n)
    req = [[0] * n for _ in range(n)]
    if placement is not False: 
        for i in range(len(low_edges)-1):
            a, b = low_edges[i]
            c, d = low_edges[i+1]
            if a == c and placement[a] == 1:
                req[d][b] = 1
            elif a == d and placement[a] == 1:
                req[c][b] = 1
            elif b == c and placement[b] == 1:
                req[d][a] = 1
            elif b == d and placement[b] == 1:
                req[c][a] = 1

        for j in range(len(high_edges)-1):
            x, y = low_edges[j]
            u, v = low_edges[j+1]
            # If x and y in C have a common neighbor z in B and xz<yz, then we have x<y in the + case.
            # If x and y are undecided vertices with a common undecided neighbor z, and xz<yz, then we have x<y as a requirement in the + case
            if x == u:
                req[v][y] = 1
            elif x == v:
                req[u][y] = 1
            elif y == u:
                req[v][x] = 1
            elif y == v:
                req[u][x] = 1
        goflag = True
        while goflag:
            goflag = False
            # If x is sorted to B and has y is sorted to C we have x<y as a requirement
            for x in range(n):
                for y in range(n):
                    if placement[x] == 2 and placement[y] == 3 and req[x][y] != 1:
                        req[x][y] = 1
                        goflag = True
            # If x is sorted in B and is incident to a high edge xz, and xz<yw (for another high edge yw not incident to x), then we have x<y and x<w as requirements.
            # This is because one of y and w will be in C (and thus higher than x), while the other will be in B, also higher than x from xz<yw.
            for x, y in high_edges:
                for u, v in high_edges:
                    if x == u and y == v:
                        break
                    else:
                        if placement[u] == 2 and x != u and y != u:
                            if req[u][x] == 0 or req[u][y] == 0:
                                req[u][x] = 1
                                req[u][y] = 1
                                goflag = True
                        elif placement[v] == 2 and x != v and y != v:
                            if req[v][x] == 0 or req[v][y] == 0:
                                req[v][x] = 1
                                req[v][y] = 1
                                goflag = True
            for i in range(n):
                for j in range(n):                          # Is the range function used correctly?
                    for k in range(n):
                        #print(i,j,k)
                        if i == j or j == k or i == k:
                            continue
                        if req[i][j] == 1 and req[j][k] == 1:
                            if req[k][i] == 1:
                                return False             
                            elif req[i][k] == 0:
                                req[i][k] = 1
                                goflag = True
                #print("completed")
            for i in range(n):
                for j in range(n):
                    if req[i][j] == 1:
                        if placement[i] == 3 and placement[j] == -2:
                            placement[j] = 3
                            goflag = True
                        if placement[j] == 2 and placement[i] == -2:
                            placement[i] = 2
                            goflag = True
            for x, z in high_edges:
                for y, w in high_edges:
                    if x == y and z == w:
                        break
                    if req[x][y] == 1 and placement[y] == -2:
                        # PLACE the whole component of [y]
                        k = high_bip[0][y] 
                        for i in range(n):
                            if placement[i] == -2:
                                if high_bip[0][i] == k:
                                    placement[i] = 3
                                    high_bip[1][k] = 1 # 
                                elif high_bip[0][i] == -k:
                                    placement[i] = 2
                                    high_bip[1][k] = -1 # 
                        goflag = True
                    if req[x][w] == 1 and placement[w] == -2:
                        k = high_bip[0][w] 
                        for i in range(n):
                            if placement[i] == -2:
                                if high_bip[0][i] == k:
                                    placement[i] = 3
                                    high_bip[1][k] = 1 # 
                                elif high_bip[0][i] == -k:
                                    placement[i] = 2
                                    high_bip[1][k] = -1 # 
                        goflag = True
                    if req[z][y] == 1 and placement[y] == -2:
                        k = high_bip[0][y] 
                        for i in range(n):
                            if placement[i] == -2:
                                if high_bip[0][i] == k:
                                    placement[i] = 3
                                    high_bip[1][k] = 1 # 
                                elif high_bip[0][i] == -k:
                                    placement[i] = 2
                                    high_bip[1][k] = -1 # 
                        goflag = True
                    if req[z][w] == 1 and placement[w] == -2:
                        k = high_bip[0][w] 
                        for i in range(n):
                            if placement[i] == -2:
                                if high_bip[0][i] == k:
                                    placement[i] = 3
                                    high_bip[1][k] = 1 # 
                                elif high_bip[0][i] == -k:
                                    placement[i] = 2
                                    high_bip[1][k] = -1 # 
                        goflag = True
    return req, placement

def clauses_for_2SAT(edges, n, t, ican3):
    print('calling generatereq interleaving')
    result = generatereq_interleaving(edges, n, t, ican3)
    if not result:
        return False
    req, placement = result
    if ican3[0] == 0:
        high_edges = edges[t:]
    else:
        high_edges = edges[:t]
    colors, component = is_eo_bip(high_edges, n)
    clauses = []
    # Generate 2-SAT clauses
    for i in range(n):
        for j in range(n):
            k = colors[i]
            l = colors[j]
            if component[abs(k)] == 0 and component[abs(l)] == 0:
                if req[i][j] == 1:
                    clauses.append([k, l])
    # Solve the 2-SAT problem
    solution = pycosat.solve(clauses)
    if solution == "UNSAT":
        print("UNSATISFIABLE")
    elif solution == "UNKNOWN":
        print("Solver returned UNKNOWN")
    else:
        for x in range(n):
            if placement[x] == -2:
                for i in solution:
                    if i > 0:
                        if colors[x] > 0:
                            placement[x] = 2
                        elif colors[x] < 0:
                            placement[x] = 3
                    elif i < 0:
                        if colors[x] > 0:
                            placement[x] = 3
                        elif colors[x] < 0:
                            placement[x] = 2
    return placement

def checkinican3(edges, n, t, ican3):
    print('calling clasue for 2sat')
    placement = clauses_for_2SAT(edges, n, t, ican3)
    if not placement:
        return False
    if ican3[0] == 0:
        low_edges = edges[:t]
        high_edges = edges[t:]
    else:
        low_edges = edges[t:]
        high_edges = edges[:t]
    vv=[0,[],[],[]] # vv[i] will be list of vertices in Vi for i=1,2,3 (not in order)
    if ican3[2] == 0:
        for i in range(len(low_edges)):
            a, b = low_edges[i]
            if placement[a] == 1:
                vv[1].append(a)
            else:
                vv[1].append(b)
    vv1 = [ key for key, _ in groupby(vv[1])]
    return vv1

n = 11
#edges = [[0,4],[0,1],[0,6],[0,2],[3,1],[3,2],[5,1],[5,2],[6,1],[6,4],[2,1],[2,4],[7,8],[9,10]] # G with OCN 3
edges = [[1,3],[2,3],[0,4],[0,1],[0,6],[0,2],[1,5],[2,5],[1,6],[4,6],[1,2],[2,4],[7,8],[9,10]] # G with OCN 3
result = checkinican3(edges,n,8,[0,0,0,0])
print(result)