import numpy as np
import random


class Ant:
    ALWAYS = 0
    WAY_BACK = 1

    def __init__(self, scene, i):
        self.scene = scene
        self.graph = None
        self.index = i
        self.speed = 1
        self.from_node = None
        self.to_node = None
        self.edge = None
        self.process_on_edge = 0
        self._has_food = False
        self.color = 'brown'
        self.no_turn_back = True
        self.deposit_on = Ant.WAY_BACK

    def prepare(self):
        self.speed = self.scene.params.ant_speed
        self.graph = self.scene.graph
        self.to_node = self.scene.nest_node
        self.from_node = self.scene.nest_node
        self.pick_new_edge()

    def walk(self, dt):
        progress = dt * self.speed
        self.process_on_edge += progress / self.edge['weight']
        self.position = self._compute_position()
        if self.has_food:
            self.deposit_pheromone()
        if self.process_on_edge > 1:
            if self.is_at_food():
                self.has_food = True
            elif self.is_at_nest():
                self.has_food = False
            self.pick_new_edge()

    def _compute_position(self):
        edge_vector = self.scene.node_position_array[self.to_node] - self.scene.node_position_array[self.from_node]
        return edge_vector * self.process_on_edge + self.scene.node_position_array[self.from_node]

    def deposit_pheromone(self):
        addition = self.scene.params.pheromone_deposit * self.scene.params.dt / self.edge['weight']
        self.edge['pheromone'] += addition

    def is_at_nest(self):
        return self.to_node == self.scene.nest_node

    def is_at_food(self):
        return self.to_node == self.scene.food_node

    def pick_new_edge(self):
        prev_node = self.from_node
        self.from_node = self.to_node
        sub_graph_copy = self.graph[self.from_node].copy()
        if self.no_turn_back and len(sub_graph_copy)>1 and not (self.is_at_food() or self.is_at_nest()):
            sub_graph_copy.pop(prev_node,None)
        to_nodes = list(sub_graph_copy)
        pheromones = np.array([edge['pheromone'] for edge in sub_graph_copy.values()]) + 0.001
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
        return self._has_food

    @has_food.setter
    def has_food(self,boolean):
        self._has_food = boolean
        if boolean:
            self.color = 'orange'
        else:
            self.color = 'brown'