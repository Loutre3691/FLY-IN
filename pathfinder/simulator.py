from .algo import Dijkstra


class SimulatorDrones():
    # tous les drones commencent a start ignorer le max capacity de drone
    # gestion du nombre de drones
    # verification capacites (stations + liens)
    # on appel dijkstra quand un drone a besoin dun chemin 
    # dijkstra renvoi le chemin pour un drone le best
    def __init__(self, nb_drones, stations_data, neighbor_station, connections_data) -> None:
        self.nb_drones = nb_drones
        self.current_drones = {} # max drone par station et quantite de drone par station
        self.stations_data = stations_data

        for station in stations_data:
            if stations_data[station].get('max_drones'):
                self.current_drones[station] = {"max": int(stations_data[station]['max_drones']), "current": 0}
            else:
                self.current_drones[station] = {"max": float('inf'), "current": 0}

        self.current_drones['start']['current'] = nb_drones

        dijkstra = Dijkstra(stations_data, neighbor_station, connections_data)
        
        # parcourir les stations une a une, et recupereer son voisin voir si chaque voisin a la possibilite 
        # d accueillir un drone grace a la diff entre current et max, si de la place le current de la station de base
        # se vide et lautre se rempli selon le calcul dijkstra
        while self.current_drones['goal']['current'] != nb_drones:
                copy_current = self.current_drones
                paths = dijkstra.find_path('start', 'goal')
                for station in self.current_drones:
                    for path in paths:

                        if path == station:
                            continue

                        if self.current_drones[path]['current'] < self.current_drones[path]['max']:
                            if (self.current_drones[path]['current'] < nb_drones and 
                                self.current_drones[station]['current'] > 0):
                                    self.current_drones[path]['current'] += 1
                                    self.current_drones[station]['current'] -= 1
                            
                        print(self.current_drones)
                        print()
                    
                    paths = dijkstra.find_path(path, 'goal')
            
                   
                        
                
                
            
                
                            
        
        
                            

