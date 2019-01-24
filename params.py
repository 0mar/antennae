class Parameters:
    def __init__(self):
        self.connectiveness = 0.1
        self.num_ants = 50
        self.num_nodes = 26
        self.ant_size = 0.05
        self.ant_speed = 1
        self.pheromone_decay = 0.9
        self.pheromone_deposit = 1
        self.screen_size_x, self.screen_size_y = 500, 500
        self.time_delay = 10
        self.size = [2, 2]
        self.dt = 0.01
        self.random_nodes = False
        self.min_path_length = 2  # Set to high (around 4) to allow only conplex graphs
