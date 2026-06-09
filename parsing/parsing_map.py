import sys
from pydantic import Field, BaseModel, ValidationError
from abc import ABC


name_and_coordinate = {}

class ConfigParsing():
    """
   Lit le fichier de configuration du drone et initialise le processus d'analyse.

    Arguments:
    map_read (io.TextIOWrapper): Le fichier de configuration ouvert.

    Attributs:
    map_read (list[str]): Toutes les lignes brutes lues dans le fichier.
    """
    def __init__(self, map) -> None:
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

        try:
            value_drones = new_dict.get("nb_drones", [None])[0]
            ConfigDrone(nb_drones=value_drones)

        except ValidationError:
            print("Error, first line muste be 'nb_drones' end min 1 drone in value and max 999 999")
        
        try:
            value_start_hub = new_dict.get("start_hub", [None])
            ConfigStartHub.parse_line(value_start_hub)
            value_hub = new_dict.get("hub", [None])
            ConfigHub.parse_line(value_hub)
            value_end_hub = new_dict.get("end_hub", [None])
            ConfigEndHub.parse_line(value_end_hub)
        

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
    Petite classe Basemodel, permet juste de gerer le nombre de drone pour le moment, a voir pour l integre
    plus tard dans une autre classe
    '''
    nb_drones: int = Field(ge=1, le=200)


class Waypoint(ABC):
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
    

    def parse_line(value) -> None:
        '''
        parse_line permet de split chaque ligne, on separe en premier lieu le nom et x, y des option entre crochet,
        creation d'un dictionnaire avec name de la station et un tupple de coordonne x, y puis gestion des erreurs
        grace au doublon des cles du dictionnaire (nom station) et ensuite avec un set pour gerer les erreurs
        des doublons de coordonnees
        '''
        for first_split in value:
            part = first_split.split("[")
            main_part = part[0].split(" ")
            name_station, x, y = main_part[0], main_part[1], main_part[2]
            option_part = part[1].split("[")

            if name_station in name_and_coordinate:
                raise ValueError(f"Duplicate not allowed: The station '{name_station}' already exists in the dictionary.")
            else:
                name_and_coordinate[name_station]= x, y
        
        single_coordinate = list(name_and_coordinate.values())
        set_coordinate = set(single_coordinate)

        if len(single_coordinate) != len(set_coordinate):
            raise ValueError((f"Duplicate not allowed: coordinate exists in duplicate"))

        



class ConfigStartHub(Waypoint):
    pass


class ConfigHub(Waypoint):
    pass
    
class ConfigEndHub(Waypoint):
    pass