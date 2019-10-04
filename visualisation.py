import tkinter
import itertools
import numpy as np
import math

class VisualScene:
    """
    Simple visual interface based on TKinter. Please replace with awesome visual interface.
    """
    color_list = ["yellow", "green", "cyan", "magenta"]
    directed_polygon = np.array([[0, -1], [1, 1], [-1, 1]])

    def __init__(self, scene):
        """
        Initializes a visual interface for the simulation. Updates every fixed amount of seconds.
        Represents the scene on a canvas.
        Important: this class progresses the simulation. After each drawing and potential delay,
        the visualisation calls for the progression to the next time step.
        Although it might be cleaner to move that to the simulation manager.
        :param scene: Scene to be drawn. The size of the scene is independent of the size of the visualization
        :return: None
        """
        self.scene = scene
        self.graph = self.scene.graph
        self.autoloop = True
        self.window = None
        self.env = None
        self.step_callback = None  # set in manager
        self.original_env = None
        self.canvas = None

    @property
    def size(self):
        return np.array([self.canvas.winfo_width(), self.canvas.winfo_height()])

    @size.setter
    def size(self, value):
        self.window.geometry("%dx%d" % tuple(value))

    def prepare(self, params):
        """
        Called before the simulation starts. Fix all parameters and bootstrap functions.

        :params: Parameter object
        :return: None
        """
        self.params = params
        init_size = np.array([self.params.screen_size_x, self.params.screen_size_y])
        # Todo: Set initial visualisation dimensions as a function of scene size
        self.autoloop = params.time_delay > 0
        if not self.autoloop:
            print("Auto-updating of backend disabled. Press <Space> or click to advance simulation")
        self.window = tkinter.Tk()
        self.window.title("Antennae")
        self.window.geometry("%dx%d" % (init_size[0], init_size[1]))
        self.window.bind("<Button-3>", self.store_scene)
        self.window.grid()
        self.canvas = tkinter.Canvas(self.window, bd=0, highlightthickness=0)
        self.canvas.pack(fill=tkinter.BOTH, expand=1)

    def start(self):
        """
        Starts the visualization loop
        :return:
        """
        self.loop()
        self.window.mainloop()

    def disable_loop(self):
        """
        Stop automatically redrawing.
        Enables space and Left-mouse click as progressing simulation.
        :return: None
        """
        self.autoloop = False
        self.window.bind("<Button-1>", self.loop)
        self.window.bind("<space>", self.loop)

    def loop(self, _=None):
        """
        Public interface for visual scene loop. If required, has a callback reference to itself to keep the simulation going.
        :param _: Event object from tkinter
        :return: None
        """
        self.draw_scene()
        if self.autoloop:
            self.window.after(self.params.time_delay, self.step_callback)
        else:
            self.step_callback()

    def finish(self):
        """
        Cleanup. Called after self.start() returns

        :return:
        """
        self.window.destroy()
        self.autoloop = False

    def _provide_information(self, event):
        """
        When assigned to a button by tkinter, prints a live summary of the present ants to the screen.
        :param event: Event instance passed by tkinter
        :return: None
        """
        x, y = (event.x / self.size[0], 1 - event.y / self.size[1])
        scene_point = np.array([x * self.scene.size[0], y * self.scene.size[1]])
        print("Mouse location: %s" % scene_point)
        for ant in self.scene.ant_list:
            print(ant)
        for obstacle in self.scene.obstacle_list:
            print(obstacle)

    def _give_relative_position(self, event):
        """
        Return the position of the click, reverted to the standard coordinate system (in first quadrant of unit square)
        :param event: Mouse click or whatever
        :return: Coordinates relative to scene.
        """
        x, y = (event.x / self.size[0], 1 - event.y / self.size[1])
        print("Mouse location: (%.2f,%.2f)" % (x, y))

    def draw_scene(self):
        """
        Method that orders the draw commands of all objects within the scene.
        All objects are removed prior to the drawing step.
        :return: None
        """
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, image=self.env, anchor=tkinter.NW, tags="IMG")
        self.draw_nodes_and_edges()
        self.draw_ants()

    def store_scene(self, _, filename=None):
        """
        Store a snapshot of the scene as an vector image.
        :param _: Event argument supplied by tkinter, can be ignored.
        :param filename: image file name. Leave empty for time-based (unique) name.

        :return: None
        """
        directory = 'images'
        if not filename:
            import time

            name = "scene#%d" % time.time()
            filename = "%s/%s-%.2f.eps" % (directory, name, self.scene.time)
        print("Snapshot at %.2f. Storing in %s" % (self.scene.time, filename))
        self.canvas.postscript(file=filename, pageheight=self.size[1], pagewidth=self.size[0])

    def draw_ants(self):
        """
        Draws all the ants in the scene using the visual_ant coordinates.
        :return: None
        """
        start_pos_array, end_pos_array = self.get_visual_ant_coordinates()
        for ant in self.scene.ant_list:
            index = ant.index
            self.canvas.create_oval(start_pos_array[index, 0], start_pos_array[index, 1],
                                    end_pos_array[index, 0], end_pos_array[index, 1],
                                    fill=ant.color)

    def get_visual_ant_coordinates(self):
        """
        Computes the coordinates of all ant relative to the visualization.
        Uses vectorized operations for speed increments
        :return: relative start coordinates, relative end coordinates.
        """
        rel_pos_array = self.scene.ant_position_array / self.scene.size
        rel_size_array = np.ones(
            self.scene.ant_position_array.shape) * self.params.ant_size / self.scene.size * self.size
        vis_pos_array = np.hstack((rel_pos_array[:, 0][:, None], 1 - rel_pos_array[:, 1][:, None])) * self.size
        start_pos_array = vis_pos_array - 0.5 * rel_size_array
        end_pos_array = vis_pos_array + 0.5 * rel_size_array
        return start_pos_array, end_pos_array

    def draw_nodes_and_edges(self):
        """
        Method for drawing the nodes and edges of the graph that represents the environment

        The thickness of the line represents the amount of pheromone currently on that edge
        :return:
        """
        # Nodes
        start_pos_array, end_pos_array = self.get_visual_node_coordinates()
        for node in self.scene.graph.nodes():
            if node == self.scene.nest_node:
                color = 'red'
            elif node == self.scene.food_node:
                color = 'yellow'
            else:
                color = 'blue'
            self.canvas.create_oval(start_pos_array[node, 0], start_pos_array[node, 1],
                                    end_pos_array[node, 0], end_pos_array[node, 1],
                                    fill=color)
        # Edges
        centers = (start_pos_array + end_pos_array) / 2
        for n1, n2 in itertools.combinations(range(len(centers)), 2):
            if self.scene.graph.has_edge(n1, n2):
                self.canvas.create_line(centers[n1, 0], centers[n1, 1], centers[n2, 0], centers[n2, 1],
                                        width=math.log(1+self.scene.graph[n1][n2]['pheromone']),
                                        fill=self.pheromone_to_color(self.scene.graph[n1][n2]['pheromone']))

    def get_visual_node_coordinates(self):
        """
        Computes the coordinates of all ant relative to the visualization.
        Uses vectorized operations for speed increments
        :return: relative start coordinates, relative end coordinates.
        """
        rel_pos_array = self.scene.node_position_array / self.scene.size
        rel_size_array = np.ones(
            self.scene.node_position_array.shape) * 0.02 / self.scene.size * self.size
        vis_pos_array = np.hstack((rel_pos_array[:, 0][:, None], 1 - rel_pos_array[:, 1][:, None])) * self.size
        start_pos_array = vis_pos_array - 0.5 * rel_size_array
        end_pos_array = vis_pos_array + 0.5 * rel_size_array
        return start_pos_array, end_pos_array

    def draw_circ_obstacle(self, circ_object):
        """
        Draw a circular object in the middle of the scene
        :param circ_object: object object to be drawn. Needs a center, radius and color
        :return: None
        """
        rel_pos_array = circ_object.center / self.scene.size
        rel_size_array = circ_object.radius / self.scene.size * self.size
        vis_pos_array = np.array([rel_pos_array[0], 1 - rel_pos_array[1]]) * self.size
        start_pos_array = vis_pos_array - 0.5 * rel_size_array
        end_pos_array = vis_pos_array + 0.5 * rel_size_array
        self.canvas.create_oval(start_pos_array[0], start_pos_array[1], end_pos_array[0], end_pos_array[1],
                                fill=circ_object.color)

    def draw_line_segment(self, line_segment):
        """
        Draws a line segment in the scene on its relative location. Can be used for (debugging) paths
        :param line_segment: line segment to be drawn.
        :return: None
        """
        x_0 = self.convert_relative_coordinate(line_segment.begin / self.scene.size)
        x_1 = self.convert_relative_coordinate(line_segment.end / self.scene.size)
        self.canvas.create_line(tuple(x_0) + tuple(x_1), fill=line_segment.color, width=2)

    def convert_relative_coordinate(self, coord):
        """
        Converts relative coordinates (from [0,1]x[0,1]) to screen size coordinates.
        Should raise an error when coordinates fall from scene,
        but this method is used so frequently I'd rather not make the computation
        Also changes the orientation to a Carthesian coordinate system
        :param coord: coordinates (fractions to be converted)
        :return: a Size with the coordinates of screen
        """
        return [coord[0], 1 - coord[1]] * self.size

    def pheromone_to_color(self,pheromone):
        frac_val = 1-1/(1+pheromone)
        colors = (int(frac_val*255*0.9),int(frac_val*255*0.7),0)
        return "#%02x%02x%02x"%colors