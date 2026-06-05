import sys
from pydantic import Field, BaseModel


class ConfigParsing():
    """
    Reads the drone configuration file and initializes the parsing process.

    Args:
        map_test (io.TextIOWrapper): The opened configuration file.
        
    Attributes:
        map_inside (list[str]): All raw lines read from the file.
    """
    def __init__(self, map) -> None:
        self.map_read = map.readlines()
        self.cleaned_map = ConfigMap.clean_file_txt(self.map_read)

        if not self.cleaned_map:
            print("Error: Not found file")
        
        self.config_final = self.dispatch_parsing(self.cleaned_map)
        
    def dispatch_parsing(self, map: list[str]):
        """
    Parses cleaned config lines into a dictionary.
    Splits each line on the first ':' to extract key and value.
    Repeated keys (e.g. 'hub', 'connection') are grouped into a list.

    map (list[str]): Cleaned lines from the configuration file.

    Result final after dispatch_parsing:
    {
        "nb_drones":  ["2"],
        "hub":        ["waypoint1 1 0 [color=blue]", "waypoint2 2 0 [color=blue]"],
        "connection": ["waypoint1-waypoint2"]
    }
    """
        new_dict = {}
        for line in map:
            if ':' in line:
                slice = line.split(":", 1)
                key = slice[0].strip()
                value = slice[1].strip()
                if key in new_dict:
                    new_dict[key].append(value)
                else:
                    new_dict[key] = [value]


        print (new_dict)

   


class ConfigMap():
    """
    Cleans raw text lines by removing spaces, empty lines, and comments.

    Args:
        maplines (list[str]): Raw lines from the config file.   

    Attributes:
        cleaned_line (list[str]): The filtered, data-only lines.
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
            

        # required_keys = {"nb_drones", "start_hub", "hub", "connection", "end_hub"}
       

class ConfigDrone(BaseModel):
    def __init__(self, map) -> None:
        drone_number: int = Field(ge=1)

