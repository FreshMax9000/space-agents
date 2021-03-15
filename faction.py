



class Faction:

    def __init__(self, boids: ):
        self.boids = boids
        self.old_distress = []
        self.new_distress = []

    def update(self, dt):
        self.old_distress = self.new_distress
        self.new_distress = []
        