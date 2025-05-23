from basic_fns import initialize_graph, adjacency



if __name__ == "__main__":
    edges, n = initialize_graph()
    adjacency_list = adjacency(edges, n)
    """
    result = check_OCN_infinite(edges, n)
    if result:
        print('OCN is finite. Checking for bipartiteness.')
        result_, bipartitions = is_bipartite(adjacency_list, n)
        for bipartition in bipartitions:
            print("Part 1:", bipartition[0])
            print("Part 2:", bipartition[1])
            if result_:
            # Check if every vertex in bipartition[0] or bipartition[1] is close
                if all(check_close(a, adjacency_list) for a in bipartition[0]) or all(check_close(a, adjacency_list) for a in bipartition[1]):
                    print("The edge-ordered graph is bipartite.")
                else:
                    print("The graph is not bipartite.")
    """
    t1 = int(input("Enter the first threshold: "))
    t2 = int(input("Enter the second threshold: "))