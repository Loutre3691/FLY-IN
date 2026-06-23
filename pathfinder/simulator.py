import copy
from .algo import Dijkstra


class SimulatorDrones():
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

    def __init__(self, nb_drones, stations_data, neighbor_station, connections_data) -> None:
        self.nb_drones = nb_drones
        self.current_drones = {}
        self.stations_data = stations_data

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

        dijkstra = Dijkstra(stations_data, neighbor_station, connections_data)
        nb_tr = 0

        # Boucle principale : on tourne tant que tous les drones ne sont pas à goal
        while self.current_drones['goal']['current'] != nb_drones:

            # Snapshot de l'état au début du tour : permet les mouvements simultanés.
            # On lit toujours depuis le snapshot (état figé) et on écrit dans
            # current_drones, donc un drone arrivé ce tour ne repart pas ce même tour.
            snapshot = copy.deepcopy(self.current_drones)

            for station in snapshot:
                # Calcul du chemin optimal depuis cette station jusqu'à goal
                paths = dijkstra.find_path(station, 'goal')

                # Si la station est déjà goal (chemin d'un seul élément), rien à faire
                if len(paths) >= 2:
                    next_st = paths[1]

                    # Place disponible dans la prochaine station
                    place = snapshot[next_st]['max'] - snapshot[next_st]['current']

                    # Nombre de drones pouvant bouger : limité par les drones disponibles
                    # et la place dans la station suivante
                    min_drones = min(snapshot[station]['current'], place)

                    # On déplace seulement si la station suivante a de la place
                    # et que la station courante a des drones à envoyer
                    if snapshot[next_st]['current'] < snapshot[next_st]['max']:
                        if snapshot[station]['current'] > 0:
                            self.current_drones[next_st]['current'] += min_drones
                            self.current_drones[station]['current'] -= min_drones

            nb_tr += 1
            print(self.current_drones)
            print()

        print(nb_tr)
