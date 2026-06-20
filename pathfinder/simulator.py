class SimulatorDrones():
    # tous les drones commencent a start ignorer le max capacity de drone
    # gestion du nombre de drones
    # verification capacites (stations + liens)
    # on appel dijkstra quand un drone a besoin dun chemin 
    # dijkstra renvoi le chemin pour un drone le best
    def __init__(self, nb_drones, stations_data, neighbor_station, connections_data) -> None:
        self.nb_drones = nb_drones
        self.current_drones = {}
        self.stations_data = stations_data


        self.current_drones['start']['current'] = nb_drones
        self.current_drones['goal']['current'] = float('inf')


        for station in stations_data:
            if stations_data[station].get('max_drones'):
                self.current_drones[station] = {"max": int(stations_data[station]['max_drones']), "current": 0}
            else:
                self.current_drones[station] = {"max": float('inf'), "current": 0}


        while nb_drones:
            for station in self.current_drones:
                for neighbor in neighbor_station:
                    if station == neighbor:
                        for neighbor_station[neighbor] in neighbor:
                            if self.current_drones[station]['current'] <= self.current_drones[station]['max']:
                                self.current_drones[station]['current'] += 1
                        
            nb_drones -= 1
                            


