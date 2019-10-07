#!/usr/bin/env python3

from params import Parameters
from scene import Scene
from visualisation import VisualScene

class Simulation:
    """
    The simulation class controls all the components of the simulation.
    It converts the input flags to configuration options and augments them to the configuration file.
    It initializes the important objects and makes sure that all the event methods (step, on_exit, on_finish) are run.
    """

    def __init__(self, scene_file=None, params=None):
        """
        Create a new simulation.
        """
        self.on_step_functions = []
        # All the effects added in the simulation. keys are strings of the effect name, values are the effect objects

        if not params:
            self.params = Parameters()
        else:
            self.params = params
        if scene_file:
            self.params.scene_file = scene_file
        self.scene = Scene()

    def _prepare(self):
        """
        Register parameters and modules

        :return: None
        """
        self.scene.total_ants += self.params.num_ants
        self.on_step_functions.append(self.scene.step)
        self.vis = VisualScene(self.scene)
        self.on_step_functions.append(self.vis.loop)
        self.vis.step_callback = self.step
        self.vis.finish_callback = lambda: None

    def start(self):
        """
        Start the simulation. When the simulation is finished, self.vis.start() returns,
        and cleanup is handled through self.finish()
        :return: None
        """
        self._prepare()
        self.scene.prepare(self.params)
        self.vis.prepare(self.params)
        self.vis.start()

    def step(self):
        """
        Increase time and
        run all the event listener methods that run on each time step
        :return:
        """
        self.scene.time += self.params.dt
        self.scene.counter += 1
        [step() for step in self.on_step_functions]

    def set_params(self, params):
        """
        Set the parameters with the given object.

        :param params: Parameter object
        :return: None
        """
        self.params = params


if __name__ == '__main__':
    sim = Simulation()
    sim.start()
