class Parameters:
    def __init__(self):
        # Number of ants
        self.num_ants = 300
        # Number of nodes.
        self.num_nodes = 20
        # (drawing) size of the ant
        self.ant_size = 0.007
        # Movement speed of ant
        self.ant_speed = 1
        # Decay rate (per second) : (1 - exponential growth rate)
        self.pheromone_decay = 0.8
        # Deposit rate (per second)
        self.pheromone_deposit = 3
        # Size of the animation window
        self.screen_size_x, self.screen_size_y = 1000, 1000
        # Extra animation delay. On mac, keep around 10 or higher, otherwise window won't close
        self.time_delay = 10
        # Time step size in seconds
        self.dt = 0.003
        # Whether to order the nodes in a lattice
        self.random_nodes = True
        # Minimal number of edges between food and nest node.
        self.min_path_length = 4
        # Seed for reproducing simulations
        self.seed = 22
