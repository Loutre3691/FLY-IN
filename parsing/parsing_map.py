import sys
from pydantic import Field, BaseModel, ValidationError
from abc import ABC

class ConfigParsing():
    """
   Lit le fichier de configuration du drone et initialise le processus d'analyse.

    Arguments:
    raw_lines (io.TextIOWrapper): Le fichier de configuration ouvert.

    Attributs:
    map_read (list[str]): Toutes les lignes brutes lues dans le fichier.
    """
    def __init__(self, map) -> None:
        self.station_names: list = []               # Liste des noms de stations
        self.used_coordinates: set = set()          # Set des coordonnées utilisées
        self.stations_data: dict = {}               # Dictionnaire complet des stations
        self.connections_data: list = []            # liste de tuple  des connections
        self.raw_lines = map.readlines()            # Lignes brutes du fichier
        self.cleaned_lines = ConfigMap.clean_raw_lines(self.raw_lines)

        if not self.cleaned_lines:
            print("Error: Not found file")
        
        self.parsed_config = self.parse_config_file(self.cleaned_lines)      # Configuration finale
        
    def parse_config_file(self, map: list[str]):
        """
        Analyse les lignes de configuration nettoyées et les convertit en dictionnaire.
        Sépare chaque ligne au niveau du premier «:» pour extraire la clé et la valeur.
        Les clés répétées (par exemple, «hub», «connection») sont regroupées dans une liste.
        map (liste[str]): Lignes nettoyées du fichier de configuration.

        Résultat final après parse_config_file:
        {
        "nb_drones": ["2"],
        "hub": ["waypoint1 1 0 [color=blue]", "waypoint2 2 0 [color=blue]"],
        "connection": ["waypoint1-waypoint2"]
        }
    """
        config_dict: dict = {}          # Dictionnaire temporaire de parsing
        order_key: dict = {"nb_drones": 1, "start_hub": 2, "hub": 3, "end_hub": 4, "connection": 5}

        count_start = 0
        count_end = 0
        current_index = 0
        last_key = "nb_drones"

        # map est la liste de toutes les lignes du fichier.txt
        for line in map:
            if ':' in line:
                slice = line.split(":", 1)
                key = slice[0].strip()
                value = slice[1].strip()
            
            # gestion d'erreur si mauvaise cle inscrite dans le file.txt
            if not key in order_key:
                raise ValueError(f"{key} is not a valid key, you must write 'nb_drones / start_hub / hub / end_ub /connection'")

            # compteur pour eviter les doublons de start_hub et end_hub
            if key == "start_hub" and count_start <= 1 :
                count_start += 1
            if key == "end_hub" and count_end <= 1 :
                count_end += 1

            if count_end > 1 or count_start > 1:
                raise ValueError("❗ You can't give the keys twice 'start_hub' or 'end_hub.")

            index = order_key.get(key)
 
            # gere l'ordre de start_hub, hub, end_hub et connection. gestion d'un mauvais nom
            if index:
                if index < current_index:
                    raise ValueError(f"Order ERROR : '{key}' don't must be after '{last_key}'")
                current_index = index
                last_key = key

            if key in config_dict:
                config_dict[key].append(value)
            else:
                config_dict[key] = [value]
            
                
        # configuration de la partie drones dans le fichier.txt
        try: 
            drone_count = config_dict.get("nb_drones", [None])[0]
            ConfigDrone(nb_drones=drone_count)

        except ValidationError:
            print("Error, first line muste be 'nb_drones' end min 1 drone in value and max 999 999")
        
        # configuration de start, hub, end en envoyant dans parse_line pour gerer chaque ligne une a une
        value_start_hub = config_dict.get("start_hub", [None])
        ConfigStartHub.parse_stations(value_start_hub, self.station_names, self.used_coordinates, self.stations_data)
        value_hub = config_dict.get("hub", [None])
        ConfigHub.parse_stations(value_hub, self.station_names, self.used_coordinates, self.stations_data)
        value_end_hub = config_dict.get("end_hub", [None])
        ConfigEndHub.parse_stations(value_end_hub, self.station_names, self.used_coordinates, self.stations_data)

        # parsing de la partie connection
        value_connection = config_dict.get("connection", [None])
        Connection.parse_connection(value_connection, self.station_names, self.connections_data, self.stations_data)


class ConfigMap():
    """
    Nettoie les lignes de texte brut en supprimant les espaces, les lignes vides et les commentaires.

    Arguments:
    maplines (liste [str]): Lignes brutes du fichier de configuration.

    Attributs:
    cleaned_line (liste [str]): Lignes filtrées ne contenant que les données.
    """
    @staticmethod
    def clean_raw_lines(maplines) -> list:
        cleaned_txt = []

        for line in maplines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cleaned_txt.append(line)
        return cleaned_txt
            

class ConfigDrone(BaseModel):
    '''
    class Basemodel, permet juste de gerer le nombre de drone pour le moment, a voir pour l integre
    plus tard dans une autre classe
    '''
    nb_drones: int = Field(ge=1, le=200)


class Station(ABC):
    '''
    Waypoint qui est une classe abstraite permet  de parser chaque ligne selon sa cle (start_hub,
    hub, end_hub) ps: connection est gerer dans une autre classe car n'a pas les memes arguments
    '''
    
    @staticmethod 
    def parse_stations(value, station_names, used_coordinates, stations_data) -> None:
        '''
        parse_line permet de split chaque ligne, on separe en premier lieu le nom et x, y des option entre crochet,
        creation d'un dictionnaire avec name de la station et un tupple de coordonne x, y puis gestion des erreurs
        grace au doublon des cles du dictionnaire (nom station) et ensuite avec un set pour gerer les erreurs
        des doublons de coordonnees
        '''
        color_list = ['green', 'blue', 'red', 'orange', 'purple', 'cyan', 'gray', 'yellow', 'magenta', 'gold', 'lime', 'brown']
        zone_list = ['restricted', 'priority', 'blocked', 'normal']
        
        # split pour separer nom + coordonnees des metadata entre [] -> creation de 2 listes separees
        for first_split in value:
            part = first_split.split("[")
            station_data, metadata_items = part[0].split(), part[1].strip("]").split()
            # station_data -> Données principales (nom + coords)
            # metadata_items ->  Éléments de métadonnées
    
    
            # separation du nom de la station, des coordonnees
            station_name = station_data[0] # start, waypoint, goal ..
            if len(station_data) < 3 or not station_data[1] or not station_data[2]: # pour avoir min 2 coord
                raise ValueError("The coordinates must include 2 coordinates")
            if len(station_data) > 3 and station_data[3]: # pour eviter une 3 eme coord par erreur
                raise ValueError("The coordinates must not contain more than 2 coordinates")
           
            x, y = station_data[1], station_data[2]
            coord = (x, y)

            # gestion de la liste des noms de stations, si doublon, puis append dans 
            # la liste 'station_names' pour eutilisation  pour les connections
            if station_name in station_names:
                raise ValueError(f"Duplicate not allowed: The station '{station_name}' already exists in list.")
            else:
                station_names.append(station_name)


            # gestion du set de coordonnes avec x y, si doublon -> erreur sinon add a 'used_coordinates
            if coord in used_coordinates :
                raise ValueError(f"Duplicate not allowed: The coordinate {coord} already exists")
            else:
                used_coordinates.add(coord)

            # creation du dictionnaire des metadata (zone, color, max_drones)
            station_metadata = {}  # Dictionnaire des métadonnées
            for item in metadata_items:
                key, val = item.split("=")
                station_metadata[key] = val


    # GESTION ERREURS METADATAS:

            # gestion erreur pour les valeurs de 'color=....'
            if " " in station_metadata:
                pass

            if 'color' in station_metadata:
                if station_metadata['color'] in color_list:
                    pass
                elif not station_metadata['color']:
                    raise ValueError(f"You must write a color after key 'color=...' in file.txt" )
                else:
                    raise ValueError(f"The color '{station_metadata['color']}' don't exist in the ref colors")

            # gestion erreur pour les valeurs de 'zone=....'
            if 'zone' in station_metadata:
                if station_metadata['zone'] in zone_list:
                    pass
                elif not station_metadata['zone']:
                    raise ValueError(f"You must write a zone after key 'zone=...' in file.txt" )
                else:
                    raise ValueError(f"The zone '{station_metadata['zone']}' don't exist in the ref zone_list")

            # gestion erreur pour les valeurs de 'max_drones=....'
            if 'max_drones' in station_metadata:
                if not int(station_metadata['max_drones']):
                    raise ValueError("You must write min '1 drone' in 'max_drone=...' in file.txt" )

            # creation du dictionnaire final qui pourra etre reutilise pour l'algo avec comme cle le nom  de la station
            # et ensuite un dictionnaire des clees : coord, zone, color, max_drone)
            stations_data[station_name] = {
                'coord': coord,
                **station_metadata
            }


class ConfigStartHub(Station):
    '''
    ConfigStartHub gere la partie start dans le parsing du file.txt, relie a la staticmethod de 
    la class station
    '''
    pass

class ConfigHub(Station):
    '''
    ConfigHub gere la partie start dans le parsing du file.txt, relie a la staticmethod de 
    la class station
    '''
    pass
    
class ConfigEndHub(Station):
    '''
    ConfigendHub gere la partie start dans le parsing du file.txt, relie a la staticmethod de 
    la class station
    '''
    pass

class Connection():
    '''
    Connection gere le parsing de la partie connection dans le file.txt, gere les doublons de connection, les erreurs
    de noms, les metadatas si pas similaire au max drone dans la premiere partie avec les coordonnees, gere egalement
    les manque de stations ou le surplus. creation egalement dune liste de tuple avec les connections pour le recuperer
    plus tard pour l algo 
    '''
        
    @staticmethod
    def parse_connection(value_connection, station_names, connections_data, stations_data) -> None:
        connected_stations = []  # Stations trouvées dans les connections
        dict_max_link = {}

        for item in value_connection:
            max_link = None
            if "[" in item:
                part = item.split("[")
                connection_pair = sorted(set(part[0].split("-")))
                if part[1]:
                    max_link = part[1]
                    max_link = max_link.split("]")
                    max_link = max_link[0]
                    key, value = max_link.split("=")
                    dict_max_link[key] = value
    
            # Paire de stations d'une connection
            else:
                connection_pair = sorted(set(item.split("-")))

                     
            # gestion nbre de station min 2 
            if len(connection_pair) != 2:
                raise ValueError("You must give 2 station")

            # gestion des doublons de chaque connection + ajout a la liste
            if connection_pair in connections_data:
                raise ValueError(f"{connection_pair} is already exists, you can't have duplicate connections")
            else:
                connections_data.append(tuple(connection_pair))
            
            # gestion du nom de chaque station par rapport a la liste des stations creer dans la classe parse_stations
            for connection in connections_data:
                for station in connection:
                    if not station in connected_stations:
                        connected_stations.append(station)
     
        if set(connected_stations) != set(station_names):
            raise ValueError("the stations in 'connection' doesn't same order in list stations in first part")     

        
            

            
            



            
            
        
