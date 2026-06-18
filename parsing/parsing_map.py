from pydantic import Field, BaseModel, ValidationError
from abc import ABC
from typing import IO, Any


class ConfigParsing():
    """
   Lit le fichier de configuration du drone et initialise le processus
   d'analyse.

    Arguments:
    raw_lines (io.TextIOWrapper): Le fichier de configuration ouvert.

    Attributs:
    map_read (list[str]): Toutes les lignes brutes lues dans le fichier.
    """
    def __init__(self, map: IO[str]) -> None:
        self.station_names: list[str] = []  # Liste des noms de stations
        self.used_coordinates: set[tuple[int, int]] = set()
        # Set des coordonnées utilisées
        self.stations_data: dict[str, Any] = {}
        # Dictionnaire complet des stations
        self.connections_data: dict[tuple[str, str], Any] = {}
        # {(stationA, stationB): {metadata}}
        self.neighbor_station: dict[str, Any] = {}
        # dict des stations voisines
        self.raw_lines = map.readlines()  # Lignes brutes du fichier
        self.cleaned_lines = ConfigMap.clean_raw_lines(self.raw_lines)

        if not self.cleaned_lines:
            print("Error: Not found file")

        self.parse_config_file(self.cleaned_lines)

    def parse_config_file(self, map: list[tuple[int, str]]) -> None:
        """
        Analyse les lignes de configuration nettoyées et les convertit en
        dictionnaire.
        Sépare chaque ligne au niveau du premier «:» pour extraire la clé
        et la valeur. Les clés répétées (par exemple, «hub», «connection»)
        sont regroupées dans une liste.
        map (liste[str]): Lignes nettoyées du fichier de configuration.

        Résultat final après parse_config_file:
        {
        "nb_drones": ["2"],
        "hub": ["waypoint1 1 0 [color=blue]", "waypoint2 2 0 [color=blue]"],
        "connection": ["waypoint1-waypoint2"]
        }
        """
        config_dict: dict[str, Any] = {}  # Dictionnaire temporaire de parsing
        order_key: dict[str, int] = {
            "nb_drones": 1,
            "start_hub": 2,
            "hub": 3,
            "end_hub": 4,
            "connection": 5
            }

        count_start = 0
        count_drone = 0
        count_end = 0
        current_index = 0
        last_key = "nb_drones"

        # map est la liste de toutes les lignes du fichier.txt
        for i, line in self.cleaned_lines:
            if ':' in line:
                slice = line.split(":", 1)
                key = slice[0].strip()
                value = slice[1].strip()
                if not slice[1]:
                    raise ValueError("you must give a station and coordonates")

            # gestion d'erreur si mauvaise cle inscrite dans le file.txt
            if key not in order_key:
                raise ValueError(
                    f"Line {i}: {key} is not a valid key, you must write"
                    f" 'nb_drones / start_hub / hub / end_ub /connection'")

            # compteur pour eviter les doublons de start_hub et end_hub
            if key == "nb_drones" and count_drone <= 1:
                count_drone += 1
                if count_drone > 1:
                    raise ValueError(f"Line {i}: 'nb_drones' is defined twice")

            if key == "start_hub" and count_start <= 1:
                count_start += 1
                if count_start > 1:
                    raise ValueError(f"Line {i}: 'start_hub' is defined twice")

            if key == "end_hub" and count_end <= 1:
                count_end += 1
                if count_end > 1:
                    raise ValueError(f"Line {i}: 'end_hub' is defined twice")

            index = order_key.get(key)

            # gere l'ordre de start_hub, hub, end_hub et connection. gestion
            #  d'un mauvais nom
            if index:
                if index < current_index:
                    raise ValueError(
                        f"Line: {i}:Order ERROR : '{key}' don't must be"
                        f" after '{last_key}'")
                current_index = index
                last_key = key

            if key in config_dict:
                config_dict[key].append((i, value))
            else:
                config_dict[key] = [(i, value)]

        if count_drone != 1:
            raise ValueError(f"Line {i} (end of file): 'nb_drones' is missing")
        if count_start != 1:
            raise ValueError(f"Line {i} (end of file): 'start_hub' is missing")
        if count_end != 1:
            raise ValueError(f"Line {i} (end of file): 'end_hub' is missing")

        # configuration de la partie drones dans le fichier.txt
        try:
            line_num, drone_count = config_dict.get(
                "nb_drones", [(None, None)])[0]
            ConfigDrone(nb_drones=drone_count)
        except ValidationError:
            line_num, _ = config_dict.get("nb_drones", [(None, None)])[0]
            raise ValueError(f"Line {line_num}: 'nb_drones' must be a number "
                             f"between 1 and 200")

        # configuration de start, hub, end en envoyant dans parse_line pour
        # gerer chaque ligne une a une
        value_start_hub = config_dict.get("start_hub", [(None, None)])
        ConfigStartHub.parse_stations(
            value_start_hub, self.station_names,
            self.used_coordinates, self.stations_data)
        value_hub = config_dict.get("hub", [(None, None)])
        ConfigHub.parse_stations(
            value_hub, self.station_names, self.used_coordinates,
            self.stations_data)
        value_end_hub = config_dict.get("end_hub", [(None, None)])
        ConfigEndHub.parse_stations(
            value_end_hub, self.station_names, self.used_coordinates,
            self.stations_data)

        # parsing de la partie connection
        value_connection = config_dict.get("connection", [(None, None)])
        Connection.parse_connection(
            value_connection, self.station_names,
            self.connections_data, self.neighbor_station)


class ConfigMap():
    """
    Nettoie les lignes de texte brut en supprimant les espaces,
    les lignes vides et les commentaires.

    Arguments:
    maplines (liste [str]): Lignes brutes du fichier de configuration.

    Attributs:
    cleaned_line (liste [str]): Lignes filtrées ne contenant que les données.
    """
    @staticmethod
    def clean_raw_lines(maplines: list[str]) -> list[tuple[int, str]]:
        """
        Nettoie les lignes brutes du fichier de configuration
        en supprimant les commentaires,
        les lignes vides et les espaces superflus.

        Pour chaque ligne, la méthode :
        - supprime les espaces en début et fin de ligne
        - ignore les lignes vides et celles commençant par '#'
        - tronque les lignes contenant un '#' en milieu de ligne
        (commentaire inline)
        - numérote chaque ligne conservée (à partir de 1) pour
        faciliter les messages d'erreur
        """

        cleaned_txt = []

        # gestion des # dans le .txt
        for i, line in enumerate(maplines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '#' in line:
                line = line[:line.index('#')].strip()
            if not line:
                continue
            cleaned_txt.append((i, line))
        return cleaned_txt


class ConfigDrone(BaseModel):
    '''
    class Basemodel, permet juste de gerer le nombre de drone
    pour le moment, a voir pour l integre plus tard dans une
    autre classe
    '''
    nb_drones: int = Field(ge=1, le=200)


class Station(ABC):
    '''
    Waypoint qui est une classe abstraite permet  de parser
    chaque ligne selon sa cle (start_hub,
    hub, end_hub) ps: connection est gerer dans une autre
    classe car n'a pas les memes arguments
    '''

    @staticmethod
    def parse_stations(
        value: list[Any], station_names: list[str],
        used_coordinates: set[tuple[int, int]], stations_data: dict[str, Any]
    ) -> None:
        '''
        parse_line permet de split chaque ligne, on separe en
        premier lieu le nom et x, y des option entre crochet,
        creation d'un dictionnaire avec name de la station et
        un tupple de coordonne x, y puis gestion des erreurs
        grace au doublon des cles du dictionnaire (nom station)
        et ensuite avec un set pour gerer les erreurs
        des doublons de coordonnees
        '''
        color_list = ['green', 'blue', 'red', 'orange',
                      'purple', 'cyan', 'gray', 'yellow',
                      'magenta', 'gold', 'lime', 'brown', 'white']
        zone_list = ['restricted', 'priority', 'blocked', 'normal']

        # split pour separer nom + coordonnees des metadata entre
        #  [] -> creation de 2 listes separees
        for i, line in value:
            if '#' in line:
                line = line[:line.index('#')].strip()
            if not line:
                continue
            part = line.split("[")
            station_data = part[0].split()
            m = part[1].strip("]").split() if len(part) > 1 else []
            metadata_items = m
            # station_data -> Données principales (nom + coords)
            # metadata_items ->  Éléments de métadonnées

            # separation du nom de la station, des coordonnees
            station_name = station_data[0]  # start, waypoint, goal..
            if (
                len(station_data) < 3 or not station_data[1]
                or not station_data[2]
            ):
                raise ValueError(f"Line {i}: the coordinates must"
                                 f"include 2 coordinates")
            if len(station_data) > 3 and station_data[3]:
                raise ValueError(f"Line {i}: the coordinates must not contain "
                                 f"more than 2 coordinates")

            x, y = int(station_data[1]), int(station_data[2])
            coord = (x, y)

            # gestion de la liste des noms de stations, si doublon,
            # puis append dans la liste 'station_names' pour utilisation
            # pour les connections
            if station_name in station_names:
                raise ValueError(f"Line {i}: duplicate station "
                                 f" '{station_name}' already exists")
            else:
                station_names.append(station_name)

            #  gestion du set de coordonnes avec x y,
            #  si doublon -> erreur sinon add a 'used_coordinates
            if coord in used_coordinates:
                raise ValueError(f"Line {i}: duplicate coordinate {coord}"
                                 f" already exists")
            else:
                used_coordinates.add(coord)

            # creation du dictionnaire des metadata (zone, color, max_drones)
            station_metadata = {}  # Dictionnaire des métadonnées
            for item in metadata_items:
                key, val = item.split("=")
                if key in station_metadata:
                    raise ValueError(f"Line {i}: duplicate metadata key"
                                     f" '{key}' in station '{station_name}'")
                station_metadata[key] = val

    # GESTION ERREURS METADATAS:
            # gestion erreur pour les valeurs de 'color=....'
            if 'color' in station_metadata:
                if not station_metadata['color']:
                    raise ValueError(
                        f"Line {i}: you must write a color after 'color='")
                elif station_metadata['color'] not in color_list:
                    station_metadata['color'] = 'white'
            # gestion erreur pour les valeurs de 'zone=....'
            if 'zone' in station_metadata:
                if not station_metadata['zone']:
                    raise ValueError(
                        f"Line {i}: you must write a zone after 'zone='")
                if station_metadata['zone'] not in zone_list:
                    station_metadata['zone'] = 'normal'

            # gestion erreur pour les valeurs de 'max_drones=....'
            if 'max_drones' in station_metadata:
                if (
                    not station_metadata['max_drones']
                    or int(station_metadata['max_drones']) < 1
                ):
                    station_metadata['max_drones'] = 1

            # pour l'algo avec comme cle le nom  de la station
            # et ensuite un dictionnaire des clees :
            #  coord, zone, color, max_drone)
            stations_data[station_name] = {
                'coord': coord,
                **station_metadata
            }


class ConfigStartHub(Station):
    '''
    ConfigStartHub gere la partie start dans le parsing du file.txt,
    relie a la staticmethod de la class station
    '''
    pass


class ConfigHub(Station):
    '''
    ConfigHub gere la partie start dans le parsing du file.txt,
    relie a la staticmethod de la class station
    '''
    pass


class ConfigEndHub(Station):
    '''
    ConfigendHub gere la partie start dans le parsing du file.txt,
    relie a la staticmethod de la class station
    '''
    pass


class Connection():
    '''
    Connection gere le parsing de la partie connection dans le file.txt,
    gere les doublons de connection, les erreurs
    de noms, les metadatas si pas similaire au max drone dans la premiere
    partie avec les coordonnees, gere egalement
    les manque de stations ou le surplus. creation egalement dune liste de
    tuple avec les connections pour le recuperer plus tard pour l algo
    '''

    @staticmethod
    def parse_connection(
        value_connection: list[Any], station_names: list[str],
        connections_data: dict[tuple[str, str], Any],
        neigbhor_station: dict[str, Any]
    ) -> None:
        """
        Analyse les lignes de connexion du fichier de configuration et
        construit les structures de données du graphe(voisin).

        Pour chaque connexion déclarée, la méthode :
        - sépare la paire de stations et les métadonnées optionnelles entre
        crochets (ex: [max_link_capacity=3])
        - vérifie qu'une connexion relie exactement 2 stations
        - détecte les connexions en double (paires identiques dans
        n'importe quel ordre)
        - vérifie que l'ensemble des stations connectées correspond
        exactement aux stations déclarées
        - stocke la connexion et ses métadonnées dans connections_data
        - enregistre les voisins directionnels dans neigbhor_station
          pour la construction du graphe

        """
        check_list_dubble = []
        connected_stations = set()

        for i, item in value_connection:
            if item is None:
                continue
            link_connection = {}

            if "[" in item:
                part = item.split("[")
                connection_pair = [s.strip() for s in part[0].split("-")]

                key, value = part[1].strip("]").split("=")
                if key == "max_link_capacity" and int(value) < 1:
                    raise ValueError(
                        f"Line {i}: 'max_link_capacity' must be at least 1")
                link_connection[key] = int(value)
            # Paire de stations d'une connection
            else:
                connection_pair = [s.strip() for s in item.split("-")]

            # gestion nbre de station min 2
            if len(connection_pair) != 2:
                raise ValueError(
                    f"Line {i}: a connection must have exactly 2 stations")

            connected_stations.add(connection_pair[0])
            connected_stations.add(connection_pair[1])

            # gestion des doublons de pair de station
            if sorted(connection_pair) in check_list_dubble:
                raise ValueError(
                    f"Line {i}: duplicate connection {connection_pair}")
            else:
                check_list_dubble.append(sorted(connection_pair))

            # stockage de la connexion avec ses metadata (vide si aucune)
            connections_data[tuple(connection_pair)] = link_connection

            # ajout du voisin directionnel pour le graphe
            neigbhor_station.setdefault(connection_pair[0],
                                        []).append(connection_pair[1])

        if connected_stations != set(station_names):
            raise ValueError(
                f"Line {i} (end of file): stations in 'connection'"
                f" don't match declared stations")
