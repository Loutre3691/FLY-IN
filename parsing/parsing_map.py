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
            value_start_hub = new_dict.get("start_hub", [None])[0]
            
            ConfigStart.name_start(value_start_hub)

        except ValidationError:
            print("Error start")
        


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
    nb_drones: int = Field(ge=1, le=999999)

# class ConfigGlobal(ABC):
#     def __init__(self, zone_1, zone_2) -> None:
#         pass

# class Waypoint(ABC):
#     def __init__(self, name, x, y, zone, color, max):
#         pass

class ConfigStart():
    def __init__(self) -> None:
        pass
        # super().__init__(name, x, y, zone, color, max)

    def name_start(party) -> None:
        part = party.split("[", 1)
        part_principal = part[0].split(" ", 2)
        part_option = part[1].split(" ")
        print(part_principal)
        print (part_option)
        
        
        
            
       
