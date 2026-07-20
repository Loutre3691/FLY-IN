import copy
from typing import Any
from .algo import Dijkstra


class DroneSimulator():
    """
    Simule le déplacement de drones de 'start' vers 'goal' tour par tour.

    À chaque tour, tous les drones avancent simultanément d'une station
    vers la prochaine étape de leur chemin optimal (calculé par Dijkstra),
    dans la limite de la capacité de la station suivante.

    Le snapshot en début de tour garantit que les mouvements sont bien
    simultanés : un drone qui arrive dans une station ne peut pas en repartir
    dans le même tour.

    Attributs :
        nb_drones (int)       : nombre total de drones à faire arriver à goal
        current_drones (dict) : état courant de chaque station
                                {'max': capacité max, 'current': drones présents}
        stations_data (dict)  : données brutes des stations issues du parsing
    """

    def __init__(
        self,
        nb_drones: int,
        stations_data: dict[str, Any],
        neighbor_station: dict[str, Any],
        connections_data: dict[tuple[str, str], Any]
    ) -> None:
        self.nb_drones = nb_drones
        self.current_drones: dict[str, dict[str, float]] = {}
        self.stations_data = stations_data
        self.connections_data = connections_data

        # Construction du dict de capacités : max depuis les métadonnées,
        # inf si pas de max_drones défini dans la map
        for station in stations_data:
            if stations_data[station].get('max_drones'):
                self.current_drones[station] = {"max": int(stations_data[station]['max_drones']), "current": 0}
            else:
                self.current_drones[station] = {"max": float('inf'), "current": 0}

        # Tous les drones partent de start (max de start ignoré selon le sujet)
        self.current_drones['start']['current'] = nb_drones
        # goal n'a pas de limite : tous les drones doivent pouvoir s'y accumuler
        self.current_drones['goal']['max'] = float('inf')

        self.dijkstra = Dijkstra(stations_data, neighbor_station, connections_data)

    def run(self) -> None:
        """Lance la simulation tour par tour jusqu'à ce que tous les drones atteignent goal."""
        nb_tr = 0
        # position courante de chaque drone (D1 = drone1, etc.)
        self.drones_positions: dict[str, str] = {f'D{i+1}': 'start' for i in range(self.nb_drones)}

        self.history_drones: dict[int, dict[str, str]] = {}

        # Boucle principale : on tourne tant que tous les drones ne sont pas à goal
        while self.current_drones['goal']['current'] != self.nb_drones:

            # Snapshot de l'état au début du tour : permet les mouvements simultanés.
            # On lit toujours depuis le snapshot (état figé) et on écrit dans
            # current_drones, donc un drone arrivé ce tour ne repart pas ce même tour.
            snapshot = copy.deepcopy(self.current_drones)
            turn_moves: list[str] = []

            for station in snapshot:
                if station not in self.dijkstra.graph:
                    continue

                # Calcul du chemin optimal depuis cette station jusqu'à goal
                paths = self.dijkstra.find_path(station, 'goal')

                # Si la station est déjà goal (chemin d'un seul élément), rien à faire
                if len(paths) >= 2:
                    next_st = paths[1]

                    link = (self.connections_data.get((station, next_st))
                            or self.connections_data.get((next_st, station)))

                    max_link = (link.get('max_link_capacity') if link else None) or 1

                    # Place disponible dans la prochaine station
                    place = snapshot[next_st]['max'] - snapshot[next_st]['current']

                    # Nombre de drones pouvant bouger : limité par les drones disponibles
                    # et la place dans la station suivante
                    min_drones = min(snapshot[station]['current'], place, max_link)

                    # On déplace seulement si la station suivante a de la place
                    # et que la station courante a des drones à envoyer
                    if min_drones > 0:
                        self.current_drones[next_st]['current'] += min_drones
                        self.current_drones[station]['current'] -= min_drones

                        # Récupère les IDs des drones actuellement à 'station'
                        # (ceux dont la position dans drone_positions correspond à station),
                        # puis garde seulement les min_drones premiers (ceux qui bougent ce tour).
                        # Pour chacun : on met à jour sa position et on note le mouvement
                        # au format 'D1-next_station' dans turn_moves pour l'affichage.
                        moved = [d for d, pos in self.drones_positions.items() if pos == station][:int(min_drones)]

                        for d in moved:
                            self.drones_positions[d] = next_st
                            turn_moves.append(f'{d}-{next_st}')

            self.history_drones[nb_tr] = copy.deepcopy(self.drones_positions)
            print(' '.join(turn_moves))

            nb_tr += 1
        print(f"\nTotal number tour: {nb_tr}")
