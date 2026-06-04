import sys

class Parsing():
    def __init__(self, map_test) -> None:
        self.map_inside = map_test.read()

    def step_parsing(self) -> None:
        Drone.number_drone_valid(self.map_inside)


class Drone(Parsing):
    def __init__(self, map_inside) -> None:
        super().__init__(map_inside)
    
    def number_drone_valid(self) -> None:
        print(self.map_inside)
