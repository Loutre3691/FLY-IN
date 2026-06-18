from models.zone import Normal, Blocked, Restricted, Priority

ZONE_MAP = {
    'normal': Normal,
    'blocked': Blocked,
    'restricted': Restricted,
    'priority': Priority,
}



class Dijkstra():
    def __init__(self, stations_data, neighbor_station, connections_data) -> None:
        self.stations_data = stations_data
        self.neighbor_station = neighbor_station
        self.connections_data = connections_data

        print(neighbor_station)
        # print()

        # retourne le cout de chaque station
        for station, data in stations_data.items():
            cost = 0
            zone_class = ZONE_MAP[data['zone']]
            data['cost'] = zone_class.cost
            neighbor_station.get(station)
            # for connection in connections_data:
                

            



  
            



