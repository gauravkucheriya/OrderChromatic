from collections import deque
from itertools import product

def initialize_graph():
	n = 6
#	edges = [[1,2],[3,4],[2,3],[1,4],[2,4],[4,5],[1,5]]
#	edges = [[1,2],[0,1],[2,3],[4,5],[3,4]] # Path 21354
	edges = [[0,1],[2,3],[1,2],[4,5], [3,4]] # Path 14325
	return edges, n

def adjacency(edges, n):
    adjacency_list = [[] for _ in range(n)]
    for i in range(len(edges)):
        a, b = edges[i]
        adjacency_list[a].append((b,i))
        adjacency_list[b].append((a,i))
    return adjacency_list

def check_close(a, X):
    X = adjacency_list[a]
    if len(X) < 2: # Isolated or leaf vertices are close.
        return True
    return X[-1][1] - X[0][1] == len(X) - 1 # Vertices whose edges (at least 2) form an interval are close.

def available(a, requirements):
    for X in requirements:
        if X[1] == a:
            return False
    return True

def is_bipartite(edges, n):
    colors = [0] * n  # Initialize colors for all vertices
    component_counter = 1
    adjacency_list = adjacency(edges,n)
    # bipartitions = [] List to store bipartitions for each connected component
    for start in range(n):
        if colors[start] == 0:  # If the current vertex is not colored
            # bipartition = [[], []] Initialize the bipartition
            queue = deque([(start, component_counter)]) 
            while queue:
                node, color = queue.popleft()
                if colors[node] == 0:  # If the node is not colored
                    colors[node] = color
                    # bipartition[color].append(node)  # Add the node to the current part of the bipartition
                    for neighbor, _ in adjacency_list[node]:
                        queue.append((neighbor, - color))  # Color the neighbor with the opposite color
                else:
                    if colors[node] != color:
                        return False, [], 0 # If the node is already colored and the color is different, the graph is not bipartite
            component_counter += 1
            # bipartitions.append(bipartition)
    return True, colors, component_counter - 1

# only the positive side is dominant

def is_eo_bip(edges, n):
    boolean, colors, component = is_bipartite(edges, n)
    adjacency_list = adjacency(edges,n)
    close_side = [True] * (2 * component + 1)
    close_in_component = [0] * (component + 1)
    if not boolean:
        return False
    for i in range(n):
        if not check_close(i, adjacency_list[i]):
            close_side[colors[i]] = False
    for i in range(1, component + 1):
        if close_side[i]:
            if not close_side[-i]:
                close_in_component[i] = 1
        else:
            if close_side[-i]:
                close_in_component[i] = 1
                for j in range(n):
                    if colors[j] == -i:
                        colors[j] = i
                    elif colors[j] == i:
                        colors[j] = -i
            else:
                return False
    return colors, close_in_component

# generate requirements for outputting the embedding for OCN 2
def req(edges, n, colors):
    req1 = []
    req2 = []
    for i in range(len(edges)-1):
        x, y = edges[i]
        z, w = edges[i+1]
        if colors[x] < 0:
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

def non_interleaving_can3():
	A1 = [1, 2]
	A2 = [2, 3]
	A3 = [1, 3]
	A4 = [1]
	A5 = [1]
	A6 = [1]
	specific_combinations = list(product(A1, A2, A3, A4, A5, A6)) # (1, 2, 1), (1, 2, 3), (1, 3, 1), (1, 3, 3), (2, 2, 1), (2, 2, 3), (2, 3, 1), (2, 3, 3)
	non_interleaving_can3 = []
	for combo in specific_combinations:
		for rest in product([-1, 1], repeat=3):
			non_interleaving_can3.append(tuple(combo) + tuple(rest))
	return non_interleaving_can3

def vertexsort(edges,n,t1,t2,can3):
	# edges, n: input graph edges, vertex number
	# t1 <= t2: thresholds separating small, medium and large edges
	# can3 encodes canonical 3-partite edge order in array of length 9 as follows:
	# small edges between V1 and V2, medium edges between V2 and V3, large edges between V3 and V1
	# can3[0],can3[1],can3[2] indicate dominant side of small, medium, large edges
	# can3[3,...,8]=1 or -1 depending on positive or negative dependence of vertex order in V1,V2,V3,V2,V3,V1 and small,small,medium,medium,large,large edges (six combinations, not used at all in this function)
	# output: array placement of length n, placement[i] indicates where vertex i could go / or False if no embedding possible
	# output array does not imply possible embedding, that should be checked, but if possible, then this sorting works
	# output False implies no embedding
	edges0=edges[:t1] # small edges
	edges1=edges[t1:t2] # medium edges
	edges2=edges[t2:] # large edges
	adj0=adjacency(edges0,n)
	adj1=adjacency(edges1,n)
	adj2=adjacency(edges2,n)
	placement=[0]*n # 0 is placeholder only, later vertex class of negative sum of two possible vertex classes
	for i in range(n):
		if adj0[i]:
			if adj1[i]:
				if adj2[i]:
					return False # all three types incident to vertex i
				placement[i]=2 # incident to small and medium edges
				if can3[0]==2:
					if not check_close(i,adj0):
						return False # closeness of small edges failed
				if can3[1]==2:
					if not check_close(i,adj1):
						return False # closeness of medium edges failed
			else:
				if adj2[i]:
					placement[i]=1 # incident to small and large edges
					if can3[0]==1:
						if not check_close(i,adj0):
							return False # closeness of small edges failed
					if can3[2]==1:
						if not check_close(i,adj2):
							return False # closeness of large edges failed
				else: # only small incident edges
					if check_close(i,adj0):
						placement[i]=-3 # undecided with small incident edge
					else:
						placement[i]=3-can3[0] # goes to the subdominant side of small edges
		else:
			if adj1[i]:
				if adj2[i]:
					placement[i]=3 # incident to medium and large edges
					if can3[1]==3:
						if not check_close(i,adj1):
							return False # closeness of medium edges failed
					if can3[2]==3:
						if not check_close(i,adj2):
							return False # closeness of large edges failed
				else: # only medium incident edges
					if check_close(i,adj1):
						placement[i]=-5 # undecided with medium incident edge
					else:
						placement[i]=5-can3[1] # goes to the subdominant side of medium edges
			else:
				if adj2[i]: #only large incident edges
					if check_close(i,adj2):
						placement[i]=-4 # undecided with large incident edge
					else:
						placement[i]=4-can3[2] # goes to the subdominant side of large edges
				else:
					placement[i]=1 # isolated vertices can be placed anywhere
	# at this point only close vertices with a single incident type are undecided
	while True:
		goflag=True
		while goflag: # do while you still place undecided vertices
			goflag=False
			for edge in edges:
				a=placement[edge[0]]
				b=placement[edge[1]]
				if a>0:
					if b==a:
						return False # adjacent vertices in same class
					if b<0:
						placement[edge[1]]=-b-a # other side of relevant bipartite graph
						goflag=True # another undecided vertex placed
				else:
					if b>0:
						placement[edge[0]]=-a-b # other side of relevant bipartite graph
						goflag=True # another undecided vertex placed
		# at this point all undecided vertices are in all-close single-type components, any one vertex can be placed arbitrarily
		for i in range(n):
			if placement[i]<0:
				if placement[i]==-5:
					placement[i]=2 # we choose V2 for a vertex with a medium edge
				else:
					placement[i]=1 # we choose V1 for other vertices
				break # arbitrary choice for a single undecided vertex only
		else: # no undecided vertex
			return placement

def checkincan3withthresholds(edges,n,t1,t2,can3):
	placement=vertexsort(edges,n,t1,t2,can3)
	if not placement:
		return False # placement failed
	vv=[0,[],[],[]] # vv[i] will be list of vertices in Vi for i=1,2,3 (not in order)
	for i in range(n):
		vv[placement[i]].append(i)
	req=[0,[],[],[]] # req[i] will contain list of requirements on order in Vi
	if t1>1: # requirements coming from small edges
		dom=can3[0] # dominant side of small edges
		sub=3-dom # subdominant side of small edges
		domsign=can3[dom+2]
		subsign=can3[sub+2]
		generatereq(edges[:t1],placement,dom,req[dom],req[sub],domsign,subsign)
	if t2>t1+1: # requirements coming from medium edges
		dom=can3[1] # dominant side of medium edges
		sub=5-dom # subdominant side of medium edges
		domsign=can3[dom+3]
		subsign=can3[sub+3]
		generatereq(edges[t1:t2],placement,dom,req[dom],req[sub],domsign,subsign)
	if n>t2+1: # requirements coming from large edges
		dom=can3[2] # dominant side of large edges
		sub=4-dom # subdominant side of large edges
		if dom==3:
			domsign=can3[7]
			subsign=can3[8]
		else:
			domsign=can3[8]
			subsign=can3[7]
		generatereq(edges[t2:],placement,dom,req[dom],req[sub],domsign,subsign)
	embedding=[] # this will be the output
	for j in range(1,4): # find order in vv[j] consistent with req[j]
		r=req[j]
		vvj=vv[j]
		vj=[] # this will contain the elements of vv[j] in a good order
		while vvj:
			for x in vvj:
				if available(x,r):
					break
			else:
				return False # no available next vertex
			vj.append(x)
			vvj.remove(x)
			s=[] # we copy the still relevant requirements here
			for z in r:
				if z[0]!=x:
					s.append(z)
			r=s
		embedding.append(vj)
	return embedding

def generatereq(edges,placement,dom,domreq,subreq,domsign,subsign):
	# domreq and subreq are requirement-lists on the dominant and subdominant sides
	# this function extends these lists to ensure the edge order given in edges
	for i in range(len(edges)-1):
		a=edges[i]
		b=edges[i+1]
		if placement[a[0]]==dom:
			adom=a[0]
			asub=a[1]
		else:
			adom=a[1]
			asub=a[0]
		if placement[b[0]]==dom:
			bdom=b[0]
			bsub=b[1]
		else:
			bdom=b[1]
			bsub=b[0]
		if adom==bdom:
			if subsign==1:
				subreq.append((asub,bsub))
			else:
				subreq.append((bsub,asub))
		else:
			if domsign==1:
				domreq.append((adom,bdom))
			else:
				domreq.append((bdom,adom))

def find_valid_result_for_config(edges, n, config):
    for t1 in range(len(edges) + 1):
        for t2 in range(t1, len(edges) + 1):
            result = checkincan3withthresholds(edges, n, t1, t2, config)
            #print(t1, t2, result)
            if result:
                return result
    return False

def check_in_non_interleaving_can3(edges, n):
	can3 = non_interleaving_can3()
	output = []
	for can3config in can3: 
		resultcan3 = find_valid_result_for_config(edges, n, can3config)
		#print(resultcan3)
		if resultcan3:
			output.append([resultcan3, can3config])
		else:
			return False, can3config
	return True, output

def vertexsort_for_interleaving(edges,n,t):
    low_edges = edges[:t]
    high_edges = edges[t:]
    low_adj = adjacency(low_edges, n)
    high_adj = adjacency(high_edges, n)
    placement=[0]*n 
    low_bip = is_eo_bip(low_edges,n)
    high_bip = is_eo_bip(high_edges,n)
    if high_bip != False and low_bip != False:
        for i in range(n):
            if high_adj[i]:
                if high_bip[0][i] < 0:
                    placement[i] = 3
                else:
                    placement[i] = -2
            elif low_adj[i]:
                if not check_close(i, low_edges):
                    placement[i] = -2 # i belongs to B or C
                else:
                    placement[i] = -1 # not enough information to place i anywhere
            else:
                placement[i] = 1 # isolated vertices are placed in A
    return placement

def placement_for_component(edges, n, t, v, k):
    placement = vertexsort_for_interleaving(edges, n, t)
    high_edges = edges[t:]
    result, components = is_bipartite(high_edges, n) # get components for high_edges
    if result:
        for component in components:
            for i in range(2):
                if v in component[i]:
                    for x in component[i]:
                        placement[x] = k
                    for y in component[1-i]:
                        placement[y] = 5-k

# use colors to place the components

def generatereq_interleaving(edges, n, t):
    placement = vertexsort_for_interleaving(edges, n, t)
    low_edges = edges[:t]
    high_edges = edges[t:]
    req = [[0] * n for _ in range(n)]
    for a, b in low_edges:
        for c, d in low_edges:
            if a == c and b == d:
                break
            else:
                if a == c and placement[a] == 1:
                    req[d][b] = 1
                elif a == d and placement[a] == 1:
                    req[c][b] = 1
                elif b == c and placement[b] == 1:
                    req[d][a] = 1
                elif b == d and placement[b] == 1:
                    req[c][a] = 1
    for x, y in high_edges:
        for u, v in high_edges:
            if x == u and y == v:
                break
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
                if placement(x) == 2 and placement(y) == 3 and req[x][y] != 1:
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
            for j in range(n):
                for k in range(n):
                    if req[i][j] == 1 and req[j][k] == 1:
                        if req[k][i] == 1:
                            return False
                        elif req[i][k] == 0:
                            req[i][k] = 1
                            goflag = True
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
                if req[x][y] == 1 and placement[y]==-2:
                    placement[y] = 3
                    placement_for_component(edges, n, t, y, 3)
                    goflag = True
                if req[x][w] == 1 and placement[w]==-2:
                    placement[w] = 3
                    placement_for_component(edges, n, t, w, 3)
                    goflag = True
                if req[z][y] == 1 and placement[y]==-2:
                    placement[y] = 3
                    placement_for_component(edges, n, t, y, 3)
                    goflag = True
                if req[z][w] == 1 and placement[w]==-2:
                    placement[w] = 3
                    placement_for_component(edges, n, t, w, 3)
                    goflag = True
    return req, placement

#def twosat(edges, n, colors):
#    for i in range(max(colors)):

if __name__ == "__main__":
    edges, n = initialize_graph()
    adjacency_list = adjacency(edges, n)
    is_bipartite(edges, n)
    print(is_eo_bip(edges,n))