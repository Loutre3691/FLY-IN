import sys
from pydantic import Field, BaseModel


class ConfigParsing():
    def __init__(self, map_test) -> None:
        self.map_inside = map_test.readlines()

        try:
            MapKeyParsing(self.map_inside)

        except KeyError:
            print("Key error")


class MapKeyParsing():
    def __init__(self, maplines) -> None:

        self.cleaned_line = []

        for line in maplines:
            line = line.strip()
            if not line or  line.startswith('#'):
                continue
            self.cleaned_line.append(line)


        print(self.cleaned_line)

  



        # required_keys = {"nb_drones", "start_hub", "hub", "connection", "end_hub"}
       


# class NumberDrone(BaseModel):
#     def __init__(self, map_inside) -> None:
#         drone_number: int = Field(ge=1, le=100)

