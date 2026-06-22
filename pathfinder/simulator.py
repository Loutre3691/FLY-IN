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
        print(self.current_drones)
        print()
        print(neighbor_station)
        print()
        self.current_drones['start']['current'] = nb_drones
        print(self.current_drones)
        
        # parcourir les stations une a une, et recupereer son voisin voir si chaque voisin a la possibilite 
        # d accueillir un drone grace a la diff entre current et max, si de la place le current de la station de base
        # se vide et lautre se rempli selon le calcul dijkstra
        while nb_drones > 0:
            for station in self.current_drones:
                
                check_neighbors = neighbor_station[station]
                for neighbor in check_neighbors:
                    if neighbor in self.current_drones:
                  
        
            
                    

                # if neighbor_station[station]['current'] <= neighbor_station[station]['max']:
                #     neighbor_station[station]['current'] += 1
                        
                # print() 
                # print(self.current_drones)
                # print("-----------------------------------------")
            # nb_drones -= 1
                
                            
        
        
                            

