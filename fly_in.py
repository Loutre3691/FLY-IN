from parsing import parsing_map
import maps.easy
import sys

def main():
    try:
        file = open(sys.argv[1], "r")
        parsing_map.Parsing(file)
        

    except FileNotFoundError:
        print("\033[0;31mError: Storage vault not found\033\n[0m")
        exit()

    file.close()

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
