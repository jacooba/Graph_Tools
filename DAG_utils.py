from collections import defaultdict


def is_graph_acylic_DFS(edge_dictionary):
    """
    A recursive DFS algorithm for finding whether a directed graph is acyclic (a DAG) 
    We check every possible path through the graph, and if we find a repeat node, we have found a cycle.
    Args:
        edge_dictionary (dict<T,set<T>>): A dictionary representing an edge from key to items in value.
    Returns:
        (bool): Whether the graph is a DAG

    Time Complexity: O(number of paths in graph without a node repeated)
                     O(n!), where n is the number of nodes in the graph
                     (Although we could find a tighter bound knowing the maximum degree of the graph)

    Note: The time complexity is terrible. This algorithm is mostly for verifying is_graph_acyclic_toplogical
          Also, if we wanted to avoid stack overflow for large graphs, we would likely want to use
          an orderedDict, which both would act as a stack and also keep track of which nodes are in our stack
          (This would provide us the additional debugging benefit of being able to print the current stack,
          without having to add a third argument to the helper function or following the stack trace.)
    """

    # Wrap edge_dictionary in defaultdict so that edges with no outgoing edges don't throw a key error
    edge_dictionary = defaultdict(set, edge_dictionary)

    def is_graph_acylic_helper(set_seen_so_far, current_node):
        """
        A recursive DFS algorithm for finding whether a directed graph is acyclic (a DAG) 
        Args:
            set_seen_so_far (set<T>): Nodes past so far in the search
            current_node (T): the current node in our DFS
        Returns:
            (bool): Whether the graph is a DAG
        """
        if current_node in set_seen_so_far:
            return False
        set_seen_so_far.add(current_node)
        for next_node in edge_dictionary[current_node]:
            if not is_graph_acylic_helper(set_seen_so_far, next_node):
                return False
        set_seen_so_far.remove(current_node)
        return True

    # Graph is a DAG if DFS does not find a loop from any possible start location
    all_nodes_set = edge_dict_to_node_set(edge_dictionary)
    return all(map(lambda start_node: is_graph_acylic_helper(set(), start_node), all_nodes_set))


def is_graph_acyclic_toplogical(edge_dictionary):
    """
    An algorithm for finding whether a directed graph is acyclic (a DAG) by trying to find a valid
    topological sort.
    Args:
        edge_dictionary (dict<T,set<T>>): A dictionary representing an edge from key to items in value
    Returns:
        (bool): Whether the graph is a DAG

    Time Complexity: O(n^2) (See topological_sort())
    """
    return topological_sort(edge_dictionary) is not None


def topological_sort(edge_dictionary):
    """
    An algorithm for finding a topological sort if possible, i.e. an ordering such that b appears before a 
    if there is an edge a->b. In this way, an edge represents a dependency of a on b. At a high level, we 
    will walk backwards from the terminal states with no dependencies. If, when we get to a node, we have 
    visited/added all of its dependencies, we can safely add it also to the ordering. (Otherwise, we skip
    it, knowing that we will come back to it later if it is at all possible.)
    
    Args:
        edge_dictionary (dict<T,set<T>>): A dictionary representing an edge from key to items in value
    Returns:
        (list<T> or None): A valid topological sort or None


    Time Complexity: O(n^2), where n is the number of node in the graph, since we expand each node once and
                             do at most n work for the expansion. Could also be expressed as O(n+v), since
                             we iterate over each n, but then use the inverse of each edge once in our search
                             Note that v is bounded by n^2, so O(n^2) is the bounded just dependent on n.
    
    Brief sketch of an inductive proof:
        1) If it is possible to insert a node into the sorted ordering (i.e. with all of its
           dependencies met), then our algorithm will:
        Inductive Step
            Assume, for node n, that we have added all its dependencies to the sorted order if possible. 
            (That is, our algorithm has been correct up until node n.)
            Now, when the last dependency for node n has been added, 
            we add node n to sorted order (by adding everything possible that depends on the last dependency) 
            Thus, it is correctly added to the sorted ordering 
            if all the dependencies can be met. 
        Base case:
            -terminal states have all their dependencies met, since they have none, and our algorithm adds 
             all terminal states to the sorted ordering to start
            -if there are no terminal states, then a path can never terminate, and all states have
             cyclical dependencies, so it is not possible to add any state with all of its dependencies
             already in the sorted ordering. So it is trivially true that our algorithm will add nodes to 
             the ordering if possible. 

        2) We never add a node incorrectly to the set before all of its dependencies are met

        3) Therefore, we add a node if it should appear in the sorted ordering and we add it correctly
    """
    # The sorted ordering we will return
    sorted_ordering = []
    # Wrap dict in edge_dict so that edges with no outgoing edges don't throw a key error
    edge_dictionary = defaultdict(set, edge_dictionary)
    # Find the inverted edge dictionary so, given a node, we can get the nodes that depend on it
    inverted_edge_dict = invert_edge_dict(edge_dictionary)

    # Make 2 sets: all_nodes_set, so we can known all the nodes in the graph
    #              terminal_node_set, so we know which nodes have no dependencies (where to start)
    all_nodes_set = edge_dict_to_node_set(edge_dictionary)
    terminal_node_set = set()
    for node in all_nodes_set: 
        if not edge_dictionary[node]:
            terminal_node_set.add(node)

    # Make 2 dictionaries: node_to_is_added, so we can mark which nodes we have added to sorted order
    #                      node_to_num_dependencies_met, so we can know in constant time if they are all met 
    node_to_is_added, node_to_num_dependencies_met = {}, {}
    for node in all_nodes_set:
        node_to_is_added[node] = False
        node_to_num_dependencies_met[node] = 0

    # Frontier starts as terminal nodes
    frontier = terminal_node_set
    while frontier:
        current_node = frontier.pop()
        # If not all dependencies have already been added to sorted_ordering, give up
        if node_to_num_dependencies_met[current_node] < len(edge_dictionary[current_node]):
            continue
        # All dependencies must have been met (or no dependencies). Add to sorted ordering.
        sorted_ordering.append(current_node)
        # Add children that depend on current node to frontier and increase its number of dependencies met
        for dependant_node in inverted_edge_dict[current_node]:
            frontier.add(dependant_node)
            node_to_num_dependencies_met[dependant_node] += 1
        # mark the current node as added to sorted_ordering
        node_to_is_added[current_node] = True

    # Check to make sure all nodes have been added to sorted_ordering
    if not all(node_to_is_added.values()):
        return None # There was a cycle

    # No cycle. Return sorted order.
    return sorted_ordering


def invert_edge_dict(edge_dictionary):
    """
    Given a dictionary of dict<T,set<T>>, that represents edges from a->b,
    creates a new dictionary of the same type representing b->a
    Args:
        edge_dictionary (dict<T,set<T>>): A dictionary representing an edge from key to value
    Returns:
        (dict<T,set<T>>): A dictionary representing the inverted edges
    """
    new_dict = defaultdict(set)
    for from_node, to_nodes in edge_dictionary.items():
        for to_node in to_nodes:
            if to_node in new_dict:
                new_dict[to_node].add(from_node)
            else:
                new_dict[to_node] = {from_node}
    return new_dict


def edge_dict_to_node_set(edge_dictionary):
    """
    Used for getting all of the nodes in a dictionary that represents edges.
    More generally, converts a dict<T,set<T>> to set<T>, including all T
    in both the key and values
    Args:
        edge_dictionary (dict<T,set<T>>): A dictionary representing an edge from key to value
    Returns:
        (set<T>): A set containing all items of type T
    """
    all_nodes = set()
    for from_node, to_node_set in edge_dictionary.items():
        all_nodes.update({from_node} | to_node_set)
    return all_nodes

