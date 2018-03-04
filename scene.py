import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt
import itertools
from ant import Ant


class Scene:
    """
    Models a scene. A scene is a rectangular object with obstacles and ants inside.
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
        self.food_node = 1
        self.size = None
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
        self.size = np.array(self.params.size)
        self._create_graph()
        self._create_colony()
        self.ant_position_array = np.zeros([self.total_ants, 2])
        self.ant_position_array[:] = self.node_position_array[self.nest_node]

    def _create_graph(self):
        self.node_position_array = np.random.rand(self.params.num_ants, 2) * self.size

        def distance(a, b):
            return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

        def create_nodes(graph, positions):
            nodes = list(positions)
            for i in range(len(nodes)):
                graph.add_node(i)

        def create_edges(graph, positions, degree=0.2):
            nodes = list(positions)
            path_exists = False
            while not path_exists:
                for n1, n2 in itertools.combinations(range(len(nodes)), 2):
                    if np.random.random() < degree:
                        dist = distance(nodes[n1], nodes[n2])
                        graph.add_edge(n1, n2, weight=dist)
                if nx.bidirectional_dijkstra(self.graph, self.nest_node, self.food_node):
                    path_exists = True
                else:
                    graph.remove_edges_from(graph.edges())

        self.graph = nx.Graph()
        create_nodes(self.graph, self.node_position_array)
        create_edges(self.graph, self.node_position_array)

    @staticmethod
    def plot_graph(graph, positions, interactive=False):
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

    def step(self):
        """
        Compute all step functions in scene not related to planner functions.
        :return: None
        """
        [step() for step in self.on_step_functions]
