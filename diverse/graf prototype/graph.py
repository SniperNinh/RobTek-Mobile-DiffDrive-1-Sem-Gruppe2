import networkx as nx
import matplotlib.pyplot as plt
from math import inf

from os import chdir
chdir("common/graf prototype")

# create a graph
G = nx.Graph()

# list of edges given as a tuple of 2 nodes an an edge weight which represents the distance between the nodes
# (node_1, node_2, edge_weight)
weighted_edge_list = [
    ('START', 'P1', 0.46),
    ('P1', 'P2', 0.40),
    ('P2', 'W5', 0.36),
    ('P2', 'P3', 0.39),
    ('P3', '1', 0.69),
    ('P3', 'P9', 0.87),
    ('P9', 'R2', 0.36),
    ('P9', 'P8', 0.28),
    ('P8', 'P13', 0.47),
    ('P13', 'W3', 0.37),
    ('P13', 'P12', 0.36),
    ('P12', 'P15', 0.81),
    ('P15', 'P21', 0.20),
    ('P21', 'W4', 0.15),
    ('P21', 'P25', 0.93),
    ('P25', 'P24', 0.49),
    ('P24', 'P22', 1.57),
    ('P22', 'R4', 0.37),
    ('P22', 'P19', 0.51),
    ('P19', 'P20', 0.88),
    ('P19', 'P18', 0.28),
    ('P18', 'P17', 0.30),
    ('P17', 'P16', 0.24),
    ('P16', 'P20', 0.53),
    ('P21', 'P20', 0.87),
    ('P10', 'P16', 1.36),
    ('P5', 'P10', 0.59),
    ('P1', 'P5', 0.57),
    ('P10', 'P8', 0.79),
    ('P5', 'P6', 0.77),
    ('P6', 'W1', 0.58),
    ('P6', 'R1', 0.92),
    ('P6', 'P11', 0.73),
    ('P11', 'W2', 0.33),
    ('P11', 'P14', 0.75),
    ('P14', 'R5', 0.57),
    ('P14', 'P17', 0.79),
    ('P24', 'R3', 0.37),
    ('P18', '2', 1.29)
]

# list of node positions (used for visual drawing only)
node_pos = {
    "START": (1.67312, 0.52371),
    "P1": (1.68229, 0.98222),
    "P2": (2.08578, 0.97305),
    "P3": (2.47371, 0.97237),
    "P5": (1.68229, 1.55076),
    "R1": (0.89974, 0.64004),
    "1": (3.15868, 0.95471),
    "W5": (2.07660, 1.33068),
    "P6": (0.91323, 1.55751),
    "W1": (0.33307, 1.56426),
    "P9": (2.48009, 1.84421),
    "R2": (2.84295, 1.83548),
    "P10": (1.68904, 2.13768),
    "P8": (2.47833, 2.12164),
    "W2": (1.24379, 2.30633),
    "P11": (0.91323, 2.28609),
    "P13": (2.47519, 2.58767),
    "W3": (2.85003, 2.59794),
    "P12": (2.46912, 2.94687),
    "P14": (0.90649, 3.03491),
    "R5": (0.33307, 3.05515),
    "P15": (2.90651, 3.6249),
    "P21": (2.91165, 3.82002),
    "W4": (3.06569, 3.80976),
    "P16": (1.68229, 3.49365),
    "P20": (2.03984, 3.83095),
    "P17": (1.45967, 3.60158),
    "P18": (1.33149, 3.85119),
    "2": (0.04129, 3.85597),
    "P19": (1.42594, 4.1008),
    "P22": (1.06393, 4.45821),
    "R4": (0.69341, 4.45674),
    "P24": (2.42897, 4.75969),
    "R3": (2.44438, 4.38999),
    "P25": (2.91678, 4.75456)
}

# extract list of nodes from weighted edge list
nodes = []
for edge in weighted_edge_list:
    nodes.append(edge[0])
    nodes.append(edge[1])

# remove duplicated from node list
nodes = list(set(nodes))

adj_dict = {}

for node in nodes:
    adj_dict[node] = []

for edge in weighted_edge_list:
    adj_dict[edge[0]].append((edge[1], edge[2]))
    adj_dict[edge[1]].append((edge[0], edge[2]))

class Graph:
    def __init__(self, weighted_edge_list: list, directed = False):
        
        self.weighted_edge_list = weighted_edge_list
        self. directed = directed

        # extract nodes from weighted edge list
        nodes = []
        for edge in self.weighted_edge_list:
            nodes.append(edge[0])
            nodes.append(edge[1])

        # remove duplicates from node list
        self.nodes = list(set(nodes))

        # create adjecency list
        self.adj_dict = {}

        for node in self.nodes:
            self.adj_dict[node] = []

        for edge in self.weighted_edge_list:
            self.adj_dict[edge[0]].append((edge[1], edge[2]))
            if not self.directed:
                self.adj_dict[edge[1]].append((edge[0], edge[2]))

        # set up dict to keep track of predecessors
        self.prev = {}

        # set up dict to keep track of distance label
        self.dist = {}

        # set up dict to keep track of which nodes have been visited
        self.visited = {}

    def sum_edge_weights(self, path: list):
        """
        Returns the sum of all edges given a path

        Args:
            path (list): a list of strings representing the names of nodes in the path 
        """
        sum = 0
        
        for i in range(len(path)-1):
            a = path[i]
            b = path[i+1]
            for adj in self.adj_dict[a]:
                if adj[0] == b:
                    sum += adj[1]

        return sum


    def minUnvisited(self):
        """
        Returns the unvisited node in the graph with the smallest distance label.
        """
        current_min = inf
        current_min_node = None

        for node in self.nodes:
            if self.dist[node] < current_min and self.visited[node] == False:
                current_min_node = node
                current_min = self.dist[node]

        return current_min_node

    def dijkstra(self, start: str, end: str):
        """
        Solves Dijkstra's algorithm for a start and end node in the graph.
        Returns a path in the form of a list of strings.

        Args:
            start (str): Starting node in pathfinding
            end (str): Target node in pathfinding
        """
        for node in self.nodes:
            self.dist[node] = inf
            self.prev[node] = None
            self.visited[node] = False

        self.dist[start] = 0

        u = start

        while u != end:
            u = self.minUnvisited()
            self.visited[u] = True

            for adj in self.adj_dict[u]:
                if self.dist[adj[0]] > self.dist[u] + adj[1]:
                    self.dist[adj[0]] = self.dist[u] + adj[1]
                    self.prev[adj[0]] = u

        k = end
        path = []

        while k != start:
            path.insert(0, k)
            k = self.prev[k]

        path.insert(0, start)

        return path


if __name__ == "__main__":
    # add edges from weighted_edge_list
    G.add_weighted_edges_from(weighted_edge_list)

    # get edge weights list for displaying in draw function
    edge_weights = nx.get_edge_attributes(G, 'weight')
    
    nx.draw(
        G,
        pos=node_pos, 
        with_labels=True, 
        node_color='lightblue', 
        edge_color='black', 
        font_color='black', 
        font_weight='bold', 
        font_size='medium'
    )

    nx.draw_networkx_edge_labels(
        G, 
        node_pos, 
        edge_labels=edge_weights, 
        font_size="x-small", 
        rotate=False
    )

    plt.show()
    