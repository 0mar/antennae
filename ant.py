import numpy as np
import random


class Ant:

    def __init__(self, scene, i):
        self.scene = scene
        self.graph = None
        self.index = i
        self.speed = 1
        self.from_node = None
        self.to_node = None
        self.edge = None
        self.process_on_edge = 0
        self.color = 'brown'

    def prepare(self):
        self.speed = self.scene.params.ant_speed
        self.graph = self.scene.graph
        self.to_node = self.scene.nest_node
        self.pick_new_edge()

    def walk(self, dt):
        progress = dt * self.speed
        self.process_on_edge += progress / self.edge['weight']
        self.position = self._compute_position()
        if self.process_on_edge > 1:
            self.deposit_pheromone()  # Todo: Don't be influenced by your own pheromone
            self.pick_new_edge()

    def _compute_position(self):
        edge_vector = self.scene.node_position_array[self.to_node] - self.scene.node_position_array[self.from_node]
        return edge_vector * self.process_on_edge + self.scene.node_position_array[self.from_node]

    def deposit_pheromone(self):
        self.graph[self.from_node][self.to_node]['pheromone'] += self.scene.params.pheromone_deposit * self.edge[
            'weight']

    def pick_new_edge(self):
        self.from_node = self.to_node
        to_nodes = list(self.graph[self.from_node])
        pheromones = np.array([edge['pheromone'] for edge in self.graph[self.from_node].values()]) + 0.001
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
