from models.zone import Normal, Blocked, Restricted, Priority
import heapq
from typing import Any

ZONE_MAP: dict[str, Any] = {
    'normal': Normal,
    'blocked': Blocked,
    'restricted': Restricted,
    'priority': Priority,
}


class Dijkstra():
    """
    Implémente l'algorithme de Dijkstra pour trouver le chemin
    le moins coûteux entre deux stations dans un réseau de drones.

    Chaque station a un coût d'entrée selon sa zone :
        normal    → coût 1
        priority  → coût 1
        restricted→ coût 2
        blocked   → interdit (None)

    Le graphe construit ressemble à ça :
        {
            'start':      {'neighbors': ['loop_a'], 'cost': 1},
            'loop_a':     {'neighbors': ['start', 'loop_b', 'loop_d'], 'cost': 1},
            'exit_point': {'neighbors': ['loop_b', 'goal'],  'cost': 2},
            ...
        }

    Attributs:
        graph (dict) : le graphe complet station -> voisins + coût
    """

    def __init__(
        self,
        stations_data: dict[str, Any],
        neighbor_station: dict[str, Any],
        connections_data: dict[tuple[str, str], Any]
    ) -> None:
        self.stations_data = stations_data
        self.neighbor_station = neighbor_station
        self.connections_data = connections_data
        self.graph: dict[str, dict[str, Any]] = {}

        # Construction du graphe : pour chaque station on calcule
        # son coût via sa zone et on récupère ses voisins
        for station, data in stations_data.items():
            zone_class = ZONE_MAP[data['zone']]
            data['cost'] = zone_class.cost
            if data['cost'] is None:
                continue
            stations_data[station] = data

            self.graph[station] = {
                'neighbors': neighbor_station.get(station, []),
                'cost': data['cost'],
            }

        self.find_path('start', 'goal')

    def find_path(self, start: str, goal: str) -> list[str]:
        """
        Trouve le chemin le moins coûteux de 'start' à 'goal'.

        PRINCIPE (les post-its) :
        ┌─────────────────────────────────────────────────────┐
        │  Au départ, toutes les stations ont un coût = inf   │
        │  sauf 'start' = 0.                                  │
        │  On visite toujours la station la MOINS CHÈRE       │
        │  en premier (grâce à priority_queue).               │
        │  À chaque visite, on met à jour le coût des         │
        │  voisins si on a trouvé un chemin moins cher.       │
        └─────────────────────────────────────────────────────┘

        Variables :
            priority_queue  : file triée automatiquement par coût,
                              contient des tuples (coût, station).
                              heappop() sort toujours le moins cher.

            visited (set)   : stations déjà traitées, on ne les
                              revisite pas.

            distances (dict): le "post-it" de chaque station,
                              coût minimum connu pour l'atteindre.
                              Ex: {'start': 0, 'loop_a': 1, ...}

            previous (dict) : pour chaque station, depuis quelle
                              station on est arrivé.
                              Ex: {'loop_a': 'start',
                                   'loop_b': 'loop_a', ...}

        BOUCLE PRINCIPALE :
            1. Prendre la station la moins chère (heappop)
            2. Si déjà visitée → ignorer
            3. Pour chaque voisin :
                 new_cost = coût_actuel + coût_du_voisin
                 si new_cost < distances[voisin] :
                     → mettre à jour distances et previous
                     → ajouter le voisin dans la queue

        RECONSTRUCTION DU CHEMIN (après la boucle) :
            On repart de 'goal' et on remonte via previous
            jusqu'à 'start', puis on inverse la liste.
            Ex: goal → exit_point → loop_b → loop_a → start
                       ↓ inversé
                start → loop_a → loop_b → exit_point → goal
        """
        priority_queue: list[tuple[float, str]] = []
        heapq.heappush(priority_queue, (0, start))
        visited: set[str] = set()
        distances: dict[str, float] = {station: float('inf') for station in self.graph}
        distances[start] = 0
        previous: dict[str, str] = {}

        while priority_queue:
            current_cost, current_station = heapq.heappop(priority_queue)

            if current_station in visited:
                continue

            visited.add(current_station)

            for neighbor in self.graph[current_station]['neighbors']:
                if neighbor not in self.graph:
                    continue
                new_cost = self.graph[neighbor]['cost'] + current_cost

                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    previous[neighbor] = current_station
                    heapq.heappush(priority_queue, (new_cost, neighbor))

        # Reconstruction du chemin depuis goal → start, puis on inverse
        path: list[str] = []
        if distances[goal] == float('inf'):
            print("\033[1;31m\n 🛰  Houston, we have a problem: drones are lost "
                  "in the void, goal station is unreachable! 🛰 \n\033[0m")
            exit(1)

        while goal in previous:
            path.append(goal)
            goal = previous[goal]

        path = [start] + path[::-1]
        return (path)
