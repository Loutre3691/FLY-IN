from models.zone import Normal, Blocked, Restricted, Priority
import heapq

ZONE_MAP = {
    'normal': Normal,
    'blocked': Blocked,
    'restricted': Restricted,
    'priority': Priority,
}

priority_queue = [] # liste des stations trie auto qui coute le moin cher
visited = set() # station deja visite
distances = {}      # station: coût_minimum_connu / post-it
previous  = {}      # station: station_précédente 



class Dijkstra():
    def __init__(self, stations_data, neighbor_station, connections_data) -> None:
        self.stations_data = stations_data
        self.neighbor_station = neighbor_station
        self.connections_data = connections_data
        self.graph = {}

        # permet de creer mo graph avec station: neigbor: {station1, station2, cost}
        for station, data in stations_data.items():
            zone_class = ZONE_MAP[data['zone']]
            data['cost'] = zone_class.cost
            stations_data[station] = data

            self.graph[station] = {
                'neighbors': neighbor_station.get(station, []),
                'cost': data['cost'],
            }                    
        cost = 0
        for step in self.graph:
            if not step in visited:
                visited.add(step)
                for neighbors in self.graph[step]['neighbors']:
                    print(neighbors)
                print()
                cost += self.graph[step]['cost']
                distances[step] = cost


                # print(f"{step} :{cost}")




  
            



