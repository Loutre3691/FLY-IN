import copy
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
        self.current_drones['goal']['max'] = float('inf')

        dijkstra = Dijkstra(stations_data, neighbor_station, connections_data)
        nb_tr = 0

        # pour chaque station faire l algo dijkstra et retoruner le chemin, verifier qu' il y esy au moin 2 stations
        # et du conditions pour diff entre max et current et rajouter un drone a la next station et enlver a la stations actuelle 
        while self.current_drones['goal']['current'] != nb_drones:  
            snapshot = copy.deepcopy(self.current_drones) # copie a la base pour la fluidite pour envoyer au fur et a mesure
            for station in snapshot:
                paths = dijkstra.find_path(station, 'goal')

                # verification qu'il ya bien deux arguments dans le paths
                if len(paths) >= 2:
                    
                    place = snapshot[paths[1]]['max'] - snapshot[paths[1]]['current']
                    
                    min_drones =  min(snapshot[station]['current'], place)

                    if snapshot[paths[1]]['current'] < snapshot[paths[1]]['max']:
                        if snapshot[station]['current'] > 0:
                            self.current_drones[paths[1]]['current'] += min_drones
                            self.current_drones[station]['current'] -= min_drones
            nb_tr += 1
            print(self.current_drones)

            print()
        print(nb_tr)
                
                
                    
            
            
                   
                        
                
                
            
                
                            
        
        
                            

