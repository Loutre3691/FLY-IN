from parsing.parsing_map import ConfigParsing
import maps.easy
import sys

def main():
    try:
        with open(sys.argv[1], "r") as file:
            ConfigParsing(file)
        

    except FileNotFoundError:
        print("\033[0;31mError: Storage vault not found\033\n[0m")
        exit()

    

if __name__ == "__main__":
    """
    Script execution guard.

    Ensures that the program only runs if the required configuration
    file exists.
    """
   
    if len(sys.argv) < 2:
        print ("\033[0;31m You must give a txt file\033[0m")
        print("Usage: python script.py fichier.txt")
        sys.exit()
    else:
        main()
