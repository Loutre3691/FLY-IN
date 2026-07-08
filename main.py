from parsing.parsing_map import ConfigParsing
from pathfinder.simulator import DroneSimulator
from display_folder import display
import sys


def main() -> dict:
    """
    Script execution guard.

    Ensures that the program only runs if the required configuration
    file exists.
    """
    try:
        with open(sys.argv[1], "r") as file:
            config = ConfigParsing(file)
            return config


    except PermissionError:
        print("\033[0;31mError: permission not valid\033\n[0m")
        exit(1)

    except FileNotFoundError:
        print("\033[0;31mError: Storage vault not found\033\n[0m")
        exit(1)

    except (ValueError, SyntaxError) as e:
        # Erreur si le parsing plante
        print(f"\033[0;31mError: {e}\033[0m\n")
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\033[0;31m You must give a txt file\033[0m")
        print("Usage: python script.py fichier.txt")
        sys.exit()
    else:
        config = main()
        sim = DroneSimulator(config.drones, config.stations_data, config.neighbor_station, config.connections_data)
        sim.run()
        display.Display(config.stations_data)



        
        
