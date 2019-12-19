import itertools
import math
import random

import networkx as nx
import numpy as np

from ant import Ant


class Scene:
    """
    Models a scene. A scene is the environment in which the path graph and the ants are contained.
    """

    def __init__(self):
        """
        Initializes a Scene using the settings in the configuration file augmented with command line parameters
        :return: scene instance.
        """
        self.time = 0
        self.counter = 0
        self.total_ants = 0
        self.nest_node = 0
        self.food_nodes = [-1]
        self.size = np.array([1, 1])
        self.params = None
        self.graph = None

        self.on_step_functions = []

        self.ant_position_array = self.node_position_array = None
        self.ant_list = []

        self.on_step_functions.append(self.move)

    def _create_colony(self):
        for i in range(self.total_ants):
            ant = Ant(self, i)
            self.ant_list.append(ant)
            ant.prepare()

    def prepare(self, params):
        """
        Method called directly before simulation start. All parameters need to be registered.
        :param params: Parameter object
        :return: None
        """
        self.params = params
        if self.params.seed:
            random.seed(self.params.seed)
        self._create_graph()
        self._create_colony()
        self.ant_position_array = np.zeros([self.total_ants, 2])
        self.ant_position_array[:] = self.node_position_array[self.nest_node]

    def create_random_configuration(self):
        return np.random.rand(self.params.num_nodes, 2) * self.size

    def create_cellular_configuration(self, eps=0.05):
        n = int(math.sqrt(self.params.num_nodes))
        range_ = np.linspace(0 + eps, 1 - eps, n)
        x, y = np.meshgrid(range_, range_)
        return (np.hstack([x.flatten()[:, None], y.flatten()[:, None]]) + eps * (
                np.random.random([n ** 2, 2]) - 0.5)) * self.size

    def _create_graph(self):
        def distance(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        if self.params.random_nodes:
            path_exists = False
            while not path_exists:
                connectivity = 1.75
                self.graph = nx.random_geometric_graph(self.params.num_nodes,
                                                       connectivity / math.sqrt(self.params.num_nodes))
                pos = nx.get_node_attributes(self.graph, 'pos')
                self.node_position_array = np.array(list(pos.values()))
                difficulty = 0.1
                len_param = int(len(pos) * difficulty)
                self.nest_node = np.argmin(np.linalg.norm(self.node_position_array - self.size / 2, axis=1))
                if len(self.food_nodes) > 1:
                    self.food_nodes = [random.randint(0, len(pos) - 1) for _ in self.food_nodes]
                else:
                    self.food_nodes = [np.argmax(
                        np.linalg.norm(self.node_position_array[:len_param, :] - self.size / 2, axis=1))]
                try:
                    path = nx.bidirectional_dijkstra(self.graph, self.nest_node, self.food_nodes[0])
                    if self.nest_node not in self.food_nodes:
                        path_exists = True
                except:
                    path_exists = False
            nx.set_node_attributes(self.graph, pos, 'pos')

            for edge in self.graph.edges():
                i, j = edge
                self.graph[i][j]['weight'] = distance(pos[i], pos[j])
                self.graph[i][j]['pheromone'] = 0.1
            return
        else:
            self.node_position_array = self.create_cellular_configuration()

        def create_nodes(graph, positions):
            nodes = list(positions)
            for i in range(len(nodes)):
                graph.add_node(i)

        def create_edges(graph, positions, degree=None):
            if not degree:
                degree = self.params.edge_probability
            nodes = list(positions)
            path_exists = False
            while not path_exists:
                for n1, n2 in itertools.combinations(range(len(nodes)), 2):
                    if np.random.random() < degree:
                        dist = distance(nodes[n1], nodes[n2])
                        graph.add_edge(n1, n2, weight=dist, pheromone=.1)
                try:
                    path = nx.bidirectional_dijkstra(self.graph, self.nest_node, self.food_nodes[0])
                    if len(path[1]) > self.params.min_path_length:
                        path_exists = True
                    else:
                        graph.remove_edges_from(list(graph.edges()))
                except nx.exception.NetworkXNoPath:
                    graph.remove_edges_from(list(graph.edges()))

        self.graph = nx.Graph()
        create_nodes(self.graph, self.node_position_array)
        create_edges(self.graph, self.node_position_array)

    @staticmethod
    def plot_graph(graph, positions, interactive=False):
        import matplotlib
        matplotlib.use('tkAgg')
        import matplotlib.pyplot as plt
        pos_dict = {}
        for node in graph.nodes():
            pos_dict[node] = positions[node, :]
        nx.draw_networkx_nodes(graph, pos_dict)
        nx.draw_networkx_edges(graph, pos_dict)
        if not interactive:
            plt.show()

    def move(self):
        """
        Performs a vectorized move of all the ants.
        Assumes that all accelerations and velocities have been set accordingly.
        :return: None
        """
        for ant in self.ant_list:
            ant.walk(self.params.dt)
        for n1, n2 in self.graph.edges():
            self.graph[n1][n2]['pheromone'] *= (1 - self.params.pheromone_decay) ** self.params.dt

    def step(self):
        """
        Compute all step functions in scene not related to planner functions.
        :return: None
        """
        [step() for step in self.on_step_functions]
