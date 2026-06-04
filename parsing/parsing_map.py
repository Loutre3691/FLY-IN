import sys
from pydantic import Field, BaseModel


class ConfigParsing():
    def __init__(self, map_test) -> None:
        self.map_inside = map_test.read()

        try:
            MapKeyParsing(self.map_inside)

        except KeyError:
            print("Key error")


class MapKeyParsing():
    def __init__(self, map) -> None:

        for ligne in map:
            ligne.strip()
        for ligne in map:
            if ligne is '':
                continue
            ligne.startswith('#')

        print(map)

  



        required_keys = {"nb_drones", "start_hub", "hub", "connection", "end_hub"}
       


# class NumberDrone(BaseModel):
#     def __init__(self, map_inside) -> None:
#         drone_number: int = Field(ge=1, le=100)

