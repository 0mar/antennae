import numpy as np


class Ant:
    ALWAYS = 0
    WAY_BACK = 1

    def __init__(self, scene, i):
        self.scene = scene
        self.graph = None
        self.index = i
        self.is_back_tracing = False
        self.back_trace_list = []
        self.from_node = None
        self.to_node = None
        self.edge = None
        self.process_on_edge = 0
        self._has_food = False
        self.color = 'brown'
        # Some parameters that should probably be in params.py
        self.speed = 1
        self.no_turn_back = True
        self.deposit_on = Ant.WAY_BACK
        self.back_trace = True

    def prepare(self):
        """
        Register parameters and modules

        :return: None
        """
        if self.scene.params.seed:
            np.random.seed(self.index)  # deterministic but different
        self.speed = self.scene.params.ant_speed
        self.graph = self.scene.graph
        self.to_node = self.scene.nest_node
        self.from_node = self.scene.nest_node
        self.pick_new_edge()

    def walk(self, dt):
        """
        The actions an ant takes on each time step

        :param dt: size of time step
        :return: None
        """
        progress = dt * self.speed
        self.process_on_edge += progress / self.edge['weight']
        self.position = self._compute_position()
        if self.has_food:
            self.deposit_pheromone()
        if self.process_on_edge > 1:
            if self.is_at_food() and not self.has_food:
                self.has_food = True
                self.is_back_tracing = True
                self.back_trace_list.append(self.from_node)
            elif self.is_at_nest() and self.has_food:
                self.has_food = False
                self.is_back_tracing = False
                self.back_trace_list = [self.scene.nest_node]
            self.pick_new_edge()

    def _compute_position(self):
        """
        Compute position on the edge. The process along the edge is given by self.process_on_edge

        :return:
        """
        edge_vector = self.scene.node_position_array[self.to_node] - self.scene.node_position_array[self.from_node]
        return edge_vector * self.process_on_edge + self.scene.node_position_array[self.from_node]

    def deposit_pheromone(self):
        """
        Deposit the pheromone.
        To make sure edges are not biased on length, pheromone addition is divided by the length of the edge.

        :return:
        """
        addition = self.scene.params.pheromone_deposit * self.scene.params.dt / self.edge['weight']
        # addition = self.scene.params.pheromone_deposit * self.scene.params.dt * np.sqrt(self.scene.params.num_ants)
        self.edge['pheromone'] += addition

    def is_at_nest(self):
        return self.to_node == self.scene.nest_node

    def is_at_food(self):
        return self.to_node in self.scene.food_nodes

    def pick_new_edge(self):
        """
        How to pick a new edge.
        Currently, the probability of picking an edge is proportional to the amount of pheromone on that edge
        where all probabilities (of course) sum to one.

        Additionally, ants have a preference for not turning back on the edge
        they just came from (people actually researched that, so I guess it's valid), unless they have no other choice.

        If an and just found food, it'll take the exact same path back to the nest, ignoring any loops it made.
        :return:
        """
        prev_node = self.from_node
        if self.back_trace and not self.is_back_tracing:
            self.back_trace_list.append(self.from_node)
        self.from_node = self.to_node
        if self.has_food and self.back_trace and self.is_back_tracing:
            self.to_node = self.back_trace_list[-1]
            first_occurrence = self.back_trace_list.index(self.to_node)
            self.back_trace_list = self.back_trace_list[:first_occurrence]
        else:
            sub_graph_copy = self.graph[self.from_node].copy()
            if self.no_turn_back and len(sub_graph_copy) > 1 and not (self.is_at_food() or self.is_at_nest()):
                sub_graph_copy.pop(prev_node, None)
            to_nodes = list(sub_graph_copy)
            pheromones = np.array([edge['pheromone'] for edge in sub_graph_copy.values()]) + 0.1
            pheromones /= sum(pheromones)
            self.to_node = np.random.choice(to_nodes, p=pheromones)
        self.edge = self.graph[self.from_node][self.to_node]
        self.process_on_edge = 0

    @property
    def position(self):
        """
        Position getter. Similar to velocity
        :return: Current position
        """
        return self.scene.ant_position_array[self.index]

    @position.setter
    def position(self, arr):
        """
        Position setter. This is not a safe operation; there is no check if the position is occupied.
        :param arr: New position
        :return: None
        """
        self.scene.ant_position_array[self.index] = arr

    @property
    def has_food(self):
        """
        Boolean that indicates whether the ant is currently carrying food

        :return: True if ant has food, false otherwise
        """
        return self._has_food

    @has_food.setter
    def has_food(self, boolean):
        self._has_food = boolean
        if boolean:
            self.color = 'orange'
        else:
            self.color = 'brown'
