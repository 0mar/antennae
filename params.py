class Parameters:
    def __init__(self):
        self.connectiveness = 0.1
        self.num_ants = 20
        self.num_nodes = 17
        self.ant_size = 0.05
        self.ant_speed = 1
        self.pheromone_decay = 0.8
        self.pheromone_deposit = 1
        self.screen_size_x, self.screen_size_y = 500, 500
        self.time_delay = 10
        self.size = [2, 2]
        self.dt = 0.01
        self.random_nodes = False
