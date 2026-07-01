import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys
from parsing.parsing_map import ConfigParsing

COLOR_MAP = {
    'green':   (34, 139, 34),
    'blue':    (30, 144, 255),
    'red':     (220, 20, 60),
    'orange':  (255, 140, 0),
    'purple':  (148, 0, 211),
    'cyan':    (0, 206, 209),
    'gray':    (128, 128, 128),
    'yellow':  (255, 215, 0),
    'magenta': (255, 0, 255),
    'gold':    (255, 185, 0),
    'lime':    (50, 205, 50),
    'brown':   (139, 69, 19)
}


class Display():
    def __init__(self, stations_data, connections_data):
        self.stations_data = stations_data
        self.connections_data = connections_data
        self.windows = None
        self.background = None
        self.start_png = None
        self.end_png = None
        self.drone_png = None
        self.zone_png = {}

        self.init_display()

    


    def init_display(self):
        '''
        definit l'initalisation de laffichage de pygame
        '''
        pygame.init()
        self.windows = pygame.display.set_mode((1600, 1150))         

        print (self.dict_data_display)
        print()
        print(self.stations_data)
        print()
        print(self.connections_data)



    def load_png(self):
        '''
        telechargement des images dans pygame 
        '''
        self.background = pygame.image.load("display_folder/background.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, (1600, 1150))
        self.start_png = pygame.image.load("display_folder/start.png").convert_alpha()
        self.start_png = pygame.transform.scale(self.start_png, (120, 110))
        self.end_png = pygame.image.load("display_folder/end.png").convert_alpha()
        self.end_png = pygame.transform.scale(self.end_png, (100, 100))
        self.drone_png = pygame.image.load("display_folder/esquie_drone.png").convert_alpha()
        self.drone_png = pygame.transform.scale(self.drone_png,(130, 90))
        self.zone_png = {
            'normal': pygame.image.load("display_folder/normal_zone.png").convert_alpha(),
            'priority':  pygame.image.load("display_folder/priority_zone.png").convert_alpha(),
            'restricted':  pygame.image.load("display_folder/restricted_zone.png").convert_alpha(),
            'blocked': pygame.image.load("display_folder/blocked_zone.png").convert_alpha()
            }

        self.zone_png['normal']= pygame.transform.scale(self.zone_png['normal'],(110, 90))
        self.zone_png['priority']= pygame.transform.scale(self.zone_png['priority'],(110, 90))
        self.zone_png['restricted']= pygame.transform.scale(self.zone_png['restricted'],(100, 120))
        self.zone_png['blocked']= pygame.transform.scale(self.zone_png['blocked'],(70, 150))


    def run_display(self):
        '''Affichage du pygame'''
        pygame.display.flip()

        while True :
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()