import sys
from pydantic import Field, BaseModel, ValidationError
from abc import ABC

class ConfigParsing():
    """
   Lit le fichier de configuration du drone et initialise le processus d'analyse.

    Arguments:
    map_read (io.TextIOWrapper): Le fichier de configuration ouvert.

    Attributs:
    map_read (list[str]): Toutes les lignes brutes lues dans le fichier.
    """
    def __init__(self, map) -> None:
        self.list_station = []     
        self.set_coords = set()
        self.dict_metadata = {}
        self.dict_for_algo = {}
        self.map_read = map.readlines()
        self.cleaned_map = ConfigMap.clean_file_txt(self.map_read)

        if not self.cleaned_map:
            print("Error: Not found file")
        
        self.config_final = self.dispatch_parsing(self.cleaned_map)
        
    def dispatch_parsing(self, map: list[str]):
        """
        Analyse les lignes de configuration nettoyées et les convertit en dictionnaire.
        Sépare chaque ligne au niveau du premier «:» pour extraire la clé et la valeur.
        Les clés répétées (par exemple, «hub», «connection») sont regroupées dans une liste.
        map (liste[str]): Lignes nettoyées du fichier de configuration.

        Résultat final après dispatch_parsing:
        {
        "nb_drones": ["2"],
        "hub": ["waypoint1 1 0 [color=blue]", "waypoint2 2 0 [color=blue]"],
        "connection": ["waypoint1-waypoint2"]
        }
    """
        new_dict: dict = {}
        order_key = {
        "nb_drones": 1, "start_hub": 2, "hub": 3, "end_hub": 4, "connection": 5
        }
        current_index = 0
        last_key = "nb_drones"

        # map est la liste de toutes les lignes du fichier.txt
        for line in map:
            if ':' in line:
                slice = line.split(":", 1)
                key = slice[0].strip()
                value = slice[1].strip()

                index = order_key.get(key)
                if index is not None:
                    if index < current_index:
                        raise ValueError(f"Order ERROR : '{key}' don't must be after '{last_key}'")
                    current_index = index
                    last_key = key

                if key in new_dict:
                    new_dict[key].append(value)
                else:
                    new_dict[key] = [value]
        
        # configuration de la partie drones dans le fichier.txt
        try: 
            value_drones = new_dict.get("nb_drones", [None])[0]
            ConfigDrone(nb_drones=value_drones)

        except ValidationError:
            print("Error, first line muste be 'nb_drones' end min 1 drone in value and max 999 999")
        
        # configuration de start, hub, end en envoyant dans parse_line pour gerer chaque ligne une a une
        try:
            value_start_hub = new_dict.get("start_hub", [None])
            ConfigStartHub.parse_line(value_start_hub, self.list_station, self.set_coords, self.dict_for_algo)
            value_hub = new_dict.get("hub", [None])
            ConfigHub.parse_line(value_hub, self.list_station, self.set_coords, self.dict_for_algo)
            value_end_hub = new_dict.get("end_hub", [None])
            ConfigEndHub.parse_line(value_end_hub, self.list_station, self.set_coords, self.dict_for_algo)

        except ValidationError:
            print("Error,  start_hub")



class ConfigMap():
    """
    Nettoie les lignes de texte brut en supprimant les espaces, les lignes vides et les commentaires.

    Arguments:
    maplines (liste [str]): Lignes brutes du fichier de configuration.

    Attributs:
    cleaned_line (liste [str]): Lignes filtrées ne contenant que les données.
    """
    @staticmethod
    def clean_file_txt(maplines) -> list:
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
    def __init__(self, name, x, y, zone, color, max_drones):
        self.name = name
        self.x = x
        self.y = y
        self. zone = zone
        self.color = color
        self.max = max_drones
    
    @staticmethod 
    def parse_line(value, list_station, set_coords, dict_for_algo) -> None:
        '''
        parse_line permet de split chaque ligne, on separe en premier lieu le nom et x, y des option entre crochet,
        creation d'un dictionnaire avec name de la station et un tupple de coordonne x, y puis gestion des erreurs
        grace au doublon des cles du dictionnaire (nom station) et ensuite avec un set pour gerer les erreurs
        des doublons de coordonnees
        '''
        color_list = ['green', 'blue', 'red', 'orange', 'purple', 'cyan', 'gray' 'yellow', 'magenta', 'gold', 'lime', 'brown']
        zone_list = ['restricted', 'priority', 'blocked', 'normal']

        # split pour separer nom + coordonnees des metadata entre [] -> creation de 2 listes separees
        for first_split in value:
            part = first_split.split("[")
            main_part, metadata_part = part[0].split(" "), part[1].strip("]").split(" ")
    
    
            # separation de la nom de station des coordonnees
            name_station = main_part[0] # start, waypoint, goal ..
            x, y = main_part[1], main_part[2]
            coord = (x, y)
        

            # gestion de la liste des noms de stations, si doublon, puis append dans 
            # la liste 'list_station' pour eutilisation  pour les connections
            if name_station in list_station:
                raise ValueError(f"Duplicate not allowed: The station '{name_station}' already exists in list.")
            else:
                list_station.append(name_station)


            # gestion du set de coordonnes avec x y, si doublon -> erreur sinon add a 'set_coords
            if coord in set_coords :
                raise ValueError(f"Duplicate not allowed: The coordinate {coord} already exists")
            else:
                set_coords.add(coord)

            # creation du dictionnaire des metadata (zone, color, max_drones)
            metadata_in_dict = {}
            for item in metadata_part:
                key, val = item.split("=")
                metadata_in_dict[key] = val


    # GESTION ERREURS METADATAS:

            # gestion erreur pour les valeurs de 'color=....'
            if 'color' in metadata_in_dict:
                if metadata_in_dict['color'] in color_list:
                    print(f"color : {metadata_in_dict['color']}")
                elif not metadata_in_dict['color']:
                    raise ValueError(f"You must write a color after key 'color=...' in file.txt" )
                else:
                    raise ValueError(f"The color '{metadata_in_dict['color']}' don't exist in the ref colors")

            # gestion erreur pour les valeurs de 'zone=....'
            if 'zone' in metadata_in_dict:
                if metadata_in_dict['zone'] in zone_list:
                    print(f"zone : {metadata_in_dict['zone']}")
                elif not metadata_in_dict['zone']:
                    raise ValueError(f"You must write a zone after key 'zone=...' in file.txt" )
                else:
                    raise ValueError(f"The zone '{metadata_in_dict['zone']}' don't exist in the ref zone_list")

            # gestion erreur pour les valeurs de 'max_drones=....'
            if 'max_drones' in metadata_in_dict:
                if int(metadata_in_dict['max_drones']):
                    print(f"max_drones : {metadata_in_dict['max_drones']}")
                else:
                    raise ValueError("You must write min '1 drone' in 'max_drone=...' in file.txt" )

            # creation du dictionnaire final qui pourra etre reutilise pour l'algo avec comme cle le nom  de la station
            # et ensuite un dictionnaire des clees : coord, zone, color, max_drone)
            dict_for_algo[name_station] = {
                'coord': coord,
                **metadata_in_dict
            }
            

class ConfigStartHub(Station):
    pass

class ConfigHub(Station):
    pass
    
class ConfigEndHub(Station):
    pass