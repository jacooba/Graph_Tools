import unittest
import numpy as np
from collections import defaultdict
from DAG_utils import is_graph_acylic_DFS, is_graph_acyclic_toplogical, topological_sort

# The number of random tests
NUM_RANDOM_TESTS = 1000
# The maximum number of nodes in a random graph
MAX_NUMBER_RANDOM_NODES = 15
# The maximum degree in a random graph
MAX_DEGREE = 5

class MDPTests(unittest.TestCase):

    def test_topolgical_sort(self):
        # Test function that creates a topological sort,
        # on "linked list" graphs, where there is only one valid sort,
        # or cases where there are only a couple valid sorts.
        # (This is not complete, so will be checked indirectly in other tests)
        self.assertEqual(topological_sort({}), [])
        self.assertEqual(topological_sort({0: {1}}), [1, 0])
        self.assertEqual(topological_sort({0: {1}, 1: {2}}), [2, 1, 0])
        self.assertTrue(tuple(topological_sort({0: {1}, 1: {2, 3}})) 
                        in {(3, 2, 1, 0), (2, 3, 1, 0)})
        self.assertTrue(tuple(topological_sort({0: {1}, 1: {2, 3}, 2: {4}, 3: {4}})) 
                        in {(4, 3, 2, 1, 0), (4, 2, 3, 1, 0)})

    def test_cycle_check(self):
        # Test DFS check and Topological Sort on known graphs #
        # Test acyclic_graphs
        acyclic_graphs = [{},
                          {0: {1}}, # 0->1 (straight)
                          {0: {1}, 1: {2}}, # 0->1->2 (straight)
                          {0: {1}, 2: {1},   1: {3}}, # 0,2->1; 1->3 (merge)
                          {0: {1}, 1: {2,3}, 2: {4}, 3: {4}}, # 0->1; 1->2,3; 2,3->4 (merge)
                          {0: {1}, 1: {2,3}, 2: {4}, 3: {4}, 5: {6}}] # above plus disjoint graph (5->6)
        for acyclic_graph in acyclic_graphs:
            self.assertTrue(is_graph_acylic_DFS(acyclic_graph), "acyclic graph: " + str(acyclic_graph))
            self.assertTrue(is_graph_acyclic_toplogical(acyclic_graph), "acyclic graph: " + str(acyclic_graph))
        # Test cyclic_graphs
        cyclic_graphs = [{0: {0}}, # 1-cycle
                         {0: {1}, 1: {0}}, # 2-cycle
                         {0: {1, 2}, 1: {0, 3}}, # 2-cycle with some extra edges
                         {0: {1}, 1: {0}, 3: {4,5}}, # 2-cycle with a disjoint acyclic graph
                         {0: {1}, 1: {2}, 2: {3}, 3: {0}}, # 4-cycle
                         {-1: {0}, 0: {1}, 1: {2}, 2: {3}, 3: {0,4}}] # 4-cycle with tails
        for cyclic_graph in cyclic_graphs:
            self.assertFalse(is_graph_acylic_DFS(cyclic_graph), "cyclic graph: " + str(cyclic_graph))
            self.assertFalse(is_graph_acyclic_toplogical(cyclic_graph), "cyclic graph: " + str(cyclic_graph))

    def test_cycle_check_random(self):
        # Test DFS and Topological algorithms against each other on random inputs #
        np.random.seed(0)
        for _ in range(NUM_RANDOM_TESTS):
            graph = defaultdict(set)
            number_of_nodes = np.random.randint(low=0, high=MAX_NUMBER_RANDOM_NODES)
            for from_node in range(number_of_nodes):
                for _ in range(MAX_DEGREE):
                    to_node = np.random.randint(low=0, high=number_of_nodes)
                    graph[from_node].add(to_node)
            self.assertEqual(is_graph_acylic_DFS(graph), is_graph_acyclic_toplogical(graph))

if __name__ == '__main__':
    unittest.main()
