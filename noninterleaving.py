from itertools import product
from basic_fns import adjacency, check_close, available

def non_interleaving_can3():
	specific_combinations = list(product([1, 2], [2, 3], [1, 3], [1], [1], [1])) 
	non_interleaving_can3 = []
	for combo in specific_combinations:
		for rest in product([-1, 1], repeat=3):
			non_interleaving_can3.append(tuple(combo) + tuple(rest))
	return non_interleaving_can3

def vertexsort(edges,n,t1,t2,can3):
	"""
	edges, n: input graph edges, vertex number
	t1 <= t2: thresholds separating small, medium and large edges
	can3 encodes canonical 3-partite edge order in array of length 9 as follows:
	small edges between V1 and V2, medium edges between V2 and V3, large edges between V3 and V1
	can3[0],can3[1],can3[2] indicate dominant side of small, medium, large edges
	can3[3,...,8]=1 or -1 depending on positive or negative dependence of vertex order in V1,V2,V3,V2,V3,V1 and small,small,medium,medium,large,large edges (six combinations, not used at all in this function)
	output: array placement of length n, placement[i] indicates where vertex i could go / or False if no embedding possible
	output array does not imply possible embedding, that should be checked, but if possible, then this sorting works
	output False implies no embedding
	"""
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