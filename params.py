class Parameters:
    def __init__(self):
        # Degree two arbitrary nodes are connected by an edge
        self.edge_probability = 0.1
        # Number of ants
        self.num_ants = 50
        # Number of nodes. If random_nodes == true, this is adjusted to floor(sqrt(num_nodes))**2
        self.num_nodes = 26
        # (drawing) size of the ant
        self.ant_size = 0.05
        # Movement speed of ant
        self.ant_speed = 1
        # Decay rate (per second) : (1 - exponential growth rate)
        self.pheromone_decay = 0.1
        # Deposit rate (per second)
        self.pheromone_deposit = 1
        # Size of the animation window
        self.screen_size_x, self.screen_size_y = 500, 500
        # Extra animation delay. On mac, keep around 10 or higher, otherwise window won't close
        self.time_delay = 10
        # Size of the scene (in meters or something)
        self.size = [2, 2]
        # Time step size in seconds
        self.dt = 0.01
        # Whether to order the nodes in a lattice
        self.random_nodes = False
        # Minimal number of edges between food and nest node.
        self.min_path_length = 4
