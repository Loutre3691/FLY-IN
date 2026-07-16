import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys
from parsing.parsing_map import ConfigParsing
from pathfinder.simulator import DroneSimulator
pygame.font.init()


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

# tailles/rayons calibres a l'oeil pour info. Si la fenetre reelle
# (self.windows) fait une autre taille, icon_scale (calcule dans load_png)
# grandit/retrecit tout ca en meme temps.
# size: taille de l'image (w, h) ; radius: rayon du cercle couleur ;
# offset: decalage (x, y) du coin haut-gauche de l'image par rapport au
# point pixel_x/pixel_y de la station (pour les icones pas centrees)
ICONS = {
    'start':      {'size': (210, 200), 'radius': 120},
    'goal':       {'size': (190, 180), 'radius': 110},
    'drone':      {'size': (180, 120),  'radius': 0},
    'normal':     {'size': (190, 190), 'radius': 110},
    'blocked':    {'size': (80, 190),  'radius': 110},
    'restricted': {'size': (130, 160),   'radius': 100},
    'priority':   {'size': (140, 150),   'radius': 100},
}

USER_CHOICE_SIZE = {
            'little': (1280, 720),
            'medium': (1920, 1080),
            'big': (3200, 1800),
        }
        

class Display():
    def __init__(self, stations_data, drones_positions):
        self.stations_data = stations_data
        self.drones_positions = drones_positions
        self.windows = None
        self.background = None
        self.start_png = None
        self.end_png = None
        self.drone_png = None
        self.zone_png = {}
        self.icon_scale = None
        self.scale_x = None
        self.scale_y = None
        self.min_x = None
        self.min_y = None
        self.marge = 100
        self.coef = 1
        self.station_pixels = {}

        if len(stations_data) > 70:
            print("\033[0;31mError: too many stations (max 70) to display cleanly\033[0m")
            sys.exit(1)

        self.NEW_SIZE_WINDOWS = self.ask_size()

        
        self.init_display()
        self.load_png()
        Calculate.size_marge(self)
        Calculate.scale(self)
        self.run_display()

    def ask_size(self):
        self.choice = input("\033[36myou can choice size display (tape medium or big) :  \033[0m")

        if self.choice == 'little':
            self.NEW_SIZE_WINDOWS = USER_CHOICE_SIZE['little']
            self.coef = 1.2
        elif self.choice == 'medium':
            self.NEW_SIZE_WINDOWS = USER_CHOICE_SIZE['medium']
        elif self.choice == 'big':
           self.NEW_SIZE_WINDOWS = USER_CHOICE_SIZE['big']
           self.coef = 0.8
        else:
            self.NEW_SIZE_WINDOWS = USER_CHOICE_SIZE['medium']
        
        return(self.NEW_SIZE_WINDOWS)


    def init_display(self):
        '''
        definit l'initalisation de laffichage de pygame
        '''
        # .init : demarre  le moteur pygame
        pygame.init()
        # .Info: recupere les donnees de l'affichage notamment la haut et la largeur de l'ecran
        self.info = pygame.display.Info()
        # set_mode : permet de creer la fenetre d affichage
        self.windows = pygame.display.set_mode(self.NEW_SIZE_WINDOWS)
        pygame.display.set_caption("Fly-in is ESQUIE")  
        


    def load_png(self):
        '''
        telechargement des images dans pygame 
        '''

        self.background = pygame.image.load("display_folder/background.png").convert()
        self.background = pygame.transform.scale(self.background, (self.windows.get_size()))
        
        self.start_png = pygame.image.load("display_folder/start.png").convert_alpha()
        self.start_png = pygame.transform.scale(self.start_png, Calculate.size_icon(self, 'start'))
        self.end_png = pygame.image.load("display_folder/end.png").convert_alpha()
        self.end_png = pygame.transform.scale(self.end_png, Calculate.size_icon(self, 'goal'))
        self.drone_png = pygame.image.load("display_folder/esquie_drone.png").convert_alpha()
        self.drone_png = pygame.transform.scale(self.drone_png, Calculate.size_icon(self, 'drone'))

        self.zone_png = {
            'normal': pygame.image.load("display_folder/normal_zone.png").convert_alpha(),
            'priority': pygame.image.load("display_folder/priority_zone.png").convert_alpha(),
            'restricted': pygame.image.load("display_folder/restricted_zone.png").convert_alpha(),
            'blocked': pygame.image.load("display_folder/blocked_zone.png").convert_alpha()
            }

        self.zone_png['normal']= pygame.transform.scale(self.zone_png['normal'], Calculate.size_icon(self, 'normal'))
        self.zone_png['priority']= pygame.transform.scale(self.zone_png['priority'], Calculate.size_icon(self, 'priority'))
        self.zone_png['restricted']= pygame.transform.scale(self.zone_png['restricted'], Calculate.size_icon(self, 'restricted'))
        self.zone_png['blocked']= pygame.transform.scale(self.zone_png['blocked'], Calculate.size_icon(self, 'blocked'))


    def color_zone(self, station):
        color = self.stations_data[station]['color']
        if color in COLOR_MAP: 
            return (COLOR_MAP[color])


    def draw_stations(self):
        '''
        Dans cette methode on calculera chaque emplacement de chaque station presentent
        dans self.stations_data
        '''
        # permet d enlever aussi la marge de chaque cote pour x et y et de multiplier
        # par le facteur scale (l'echelle)


        for station, data in self.stations_data.items():
            pixel_x = self.marge + (data['coord'][0] - self.min_x) * self.scale_x

            if data['coord'][1] == self.min_y:
                pixel_y = self.marge + (data['coord'][1] - self.min_y) * self.scale_y 

            else:
                pixel_y = ((data['coord'][1] - self.min_y) * self.scale_y) - self.marge

            # affichage et mise en place des cercles couleur zone et des icon
            if station == 'start':
                icon_scale = Calculate.size_icon(self, 'start')
                centre = (pixel_x + icon_scale[0] // 2), (pixel_y + self.icon_scale[1] // 2)
                pygame.draw.circle(self.windows, self.color_zone(station), centre, Calculate.size_cercle(self, ICONS['start']['radius']))
                self.windows.blit(self.start_png, (pixel_x , pixel_y + 5))
                self.station_pixels['start'] = (pixel_x, pixel_y)
            elif station == 'goal':
                icon_scale = Calculate.size_icon(self, 'goal')
                centre = (pixel_x - 100 * self.ratio + self.icon_scale[0] // 2), (pixel_y + self.icon_scale[1] // 2)
                pygame.draw.circle(self.windows, self.color_zone(station), centre, Calculate.size_cercle(self, ICONS['goal']['radius']))
                self.windows.blit(self.end_png, (pixel_x - 100 * self.ratio, pixel_y))
                self.station_pixels['goal'] = (pixel_x, pixel_y)
            else:
                if data['zone'] == 'normal':
                    icon_scale = Calculate.size_icon(self, 'normal')
                    centre = (pixel_x + self.icon_scale[0] // 2), (pixel_y + self.icon_scale[1] // 2)
                    pygame.draw.circle(self.windows, self.color_zone(station), centre, Calculate.size_cercle(self, ICONS['normal']['radius']))
                    self.windows.blit(self.zone_png['normal'], (pixel_x, pixel_y))
                if data['zone'] == 'blocked':
                    icon_scale = Calculate.size_icon(self, 'blocked')
                    centre = (pixel_x + self.icon_scale[0] // 2), (pixel_y + self.icon_scale[1] // 2)
                    pygame.draw.circle(self.windows, self.color_zone(station), centre, Calculate.size_cercle(self, ICONS['blocked']['radius']))
                    self.windows.blit(self.zone_png['blocked'], (pixel_x, pixel_y))
                if data['zone'] == 'restricted':
                    icon_scale = Calculate.size_icon(self, 'restricted')
                    centre = (pixel_x + 5 + self.icon_scale[0] // 2), (pixel_y + 8 + self.icon_scale[1] // 2)
                    pygame.draw.circle(self.windows, self.color_zone(station), centre, Calculate.size_cercle(self, ICONS['restricted']['radius']))
                    self.windows.blit(self.zone_png['restricted'], (pixel_x + 5 , pixel_y + 8))
                if data['zone'] == 'priority':
                    icon_scale = Calculate.size_icon(self, 'priority')
                    centre = (pixel_x + self.icon_scale[0] // 2), (pixel_y + self.icon_scale[1] // 2)
                    pygame.draw.circle(self.windows, self.color_zone(station), centre, Calculate.size_cercle(self, ICONS['priority']['radius']))
                    self.windows.blit(self.zone_png['priority'], (pixel_x, pixel_y))
                self.station_pixels[station] = (pixel_x, pixel_y)
            
          
    
    def draw_drones(self, tour, previous, progression):
        ''' Dessine les drones selon lemplacement des stations en calculant une progesssion lieneaire
        grace a progression qui est les etapes de la porgression dans run_display
        choix de la police egalement et de la taille selon taille map
        previous est la station de depart ce qui permet de faire le calcul entre la station de depart 
        la station d arrivee et la progression'''

        size = 40 if self.choice == 'big' else 20 if self.choice == 'little' else 30
        self.police = pygame.font.SysFont("Arial", size)
        for drone, station_arrivee in self.drones_positions[tour].items():
            station_depart = previous[drone]
            depart_x, depart_y = self.station_pixels[station_depart]
            arrivee_x, arrivee_y = self.station_pixels[station_arrivee]

            x = depart_x + (arrivee_x - depart_x) * progression
            y = depart_y + (arrivee_y - depart_y) * progression

            text = self.police.render(drone, True, (255, 255, 255))
            self.windows.blit(self.drone_png, (x, y))
            self.windows.blit(text, (x, y))
     

    def run_display(self):
        '''Affichage du pygame'''
        previous = {drone: 'start' for drone in self.drones_positions[0]}
        progression_steps = [i * 0.05 for i in range(21)]

        for tour in self.drones_positions:
            for progression in progression_steps:
                pygame.event.pump()
                self.draw_background()
                self.draw_stations()
                self.draw_drones(tour, previous, progression)
                pygame.display.flip()
                pygame.time.wait(30)

            previous = self.drones_positions[tour]


        while True :
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()


    def draw_background(self):
        '''Efface la map'''
        self.windows.blit(self.background, (0, 0))


class Calculate():
    @staticmethod
    def size_icon(display, name):
        
        ratio = Calculate.scale_nb_drones(display)
        w_windows = ((display.NEW_SIZE_WINDOWS[0] * ratio) * ICONS[name]['size'][0] / display.info.current_w)
        h_windows = ((display.NEW_SIZE_WINDOWS[1] * ratio) * ICONS[name]['size'][1] / display.info.current_h)
        display.icon_scale = w_windows, h_windows

        return(display.icon_scale)
    
    @staticmethod
    def scale_nb_drones(display):
        # permet de calculer le ratio de diminution selon nb on divise par 70 qui est le max 
        nb = len(display.stations_data)
        if nb < 30:
            display.ratio = 1 - 0.50 * display.coef * nb  / 30
        elif nb > 30 and nb < 40:
            display.ratio = 1 - 0.50 * display.coef * nb  / 40 
        else:
            display.ratio = 1 - 0.60 * display.coef * nb / 70 

        return display.ratio

    
    @staticmethod
    def size_cercle(display, radius):
        ''' Calcul taille cercle'''
        base = display.info.current_w + display.info.current_h
        new = display.NEW_SIZE_WINDOWS[0] + display.NEW_SIZE_WINDOWS[1]
        display.size_cercle = new * radius / base * display.ratio

        return(display.size_cercle)
    
    @staticmethod
    def size_marge(display):
        '''calcul taille marge'''
        base = display.info.current_w + display.info.current_h
        new = display.NEW_SIZE_WINDOWS[0] + display.NEW_SIZE_WINDOWS[1]
        display.marge = new * display.marge / base

    @staticmethod
    def scale(display):
        ''' calcul du facteur de multiplication, display.ratio pour donner le nbr de pixels represente 
        1 unite de coordonne de la map
        '''

        # On prends le minimum et le max de x et y 
        coord_x = [display.stations_data[s]['coord'][0] for s in display.stations_data]
        display.min_x, display.max_x = min(coord_x), max(coord_x)

        coord_y = [display.stations_data[s]['coord'][1] for s in display.stations_data]
        display.min_y, display.max_y = min(coord_y), max(coord_y)
    
        width, height = display.windows.get_size()
        display.windows.blit(display.background, (0, 0))

        # On deduit la marge de la taille width et height et on divise la diff entre le min et max de x et y 
        display.range_x = display.max_x - display.min_x
        display.range_y = display.max_y - display.min_y
        display.scale_x = (width - (display.marge * 2)) / display.range_x if display.range_x != 0 else 1
        display.scale_y = (height - (display.marge * 2)) / display.range_y if display.range_y != 0 else 1
    