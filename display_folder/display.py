import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame  # noqa: E402
import sys  # noqa: E402
from typing import Any, cast  # noqa: E402
pygame.font.init()


COLOR_MAP: dict[str, tuple[int, int, int]] = {
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
# point pixel_x/pixel_y de la station (pour les icones pas centeres)
ICONS: dict[str, dict[str, Any]] = {
    'start':      {'size': (210, 200), 'radius': 120},
    'goal':       {'size': (190, 180), 'radius': 110},
    'drone':      {'size': (180, 120),  'radius': 0},
    'normal':     {'size': (190, 190), 'radius': 110},
    'blocked':    {'size': (80, 190),  'radius': 110},
    'restricted': {'size': (130, 160),   'radius': 100},
    'priority':   {'size': (140, 150),   'radius': 100},
}

USER_CHOICE_SIZE: dict[str, tuple[int, int]] = {
            'little': (1280, 720),
            'medium': (1920, 1080),
            'big': (3200, 1800),
        }


class _RestartAnimation(Exception):
    """Signale un redemarrage de l'animation (touche B), pour sortir
    d'un coup des boucles imbriquees de run_display."""


class _QuitAnimation(Exception):
    """Signale une sortie du programme (touche Q), pour sortir d'un
    coup des boucles imbriquees de run_display."""


class Display():
    """
    Gere l'affichage pygame de la simulation : dessine la carte, les
    stations, puis anime les drones qui se deplacent dessus tour par
    tour.

    Le deroulement se fait en trois temps, tous lances depuis
    __init__ :
    1) ask_size + init_display ouvrent la fenetre pygame a la taille
       choisie par l'utilisateur (little / medium / big).
    2) load_png charge et redimensionne toutes les images (fond,
       stations, drone) a la bonne echelle.
    3) run_display boucle sur chaque tour de la simulation et anime
       chaque drone de sa station de depart vers sa station
       d'arrivee, image par image.

    Attributs fixes dynamiquement par les methodes statiques de
    Calculate (donc declares ici pour que mypy les reconnaisse) :
        ratio       : coefficient de reduction selon le nb de
                      stations (voir Calculate.scale_nb_drones)
        size_cercle : rayon en pixels du dernier cercle calcule
        max_x/max_y : coordonnees logiques maximales de la carte
        range_x/range_y : etendue logique de la carte (max - min)
        police      : police pygame utilisee pour ecrire le nom
                      des drones
    """
    ratio: float
    size_cercle: float
    max_x: int
    max_y: int
    range_x: int
    range_y: int
    police: pygame.font.Font

    def __init__(
        self,
        stations_data: dict[str, dict[str, Any]],
        drones_positions: dict[int, dict[str, str]],
        connections_data
    ) -> None:
        """
        Initialise les attributs puis lance directement l'affichage.

        stations_data : dictionnaire des stations issu du parsing,
            {nom_station: {coord, couleur, zone, ...}}.
        drones_positions : position de chaque drone a chaque tour de
            la simulation, {numero_de_tour: {nom_drone: nom_station}}.

        Les attributs pygame (windows, background, ...) sont mis a
        None ici car ils ne sont reellement crees que plus loin, dans
        init_display et load_png (l'ordre d'appel en bas de cette
        methode compte : il faut la fenetre avant de charger les
        images, et les images avant de dessiner quoi que ce soit).
        """
        self.stations_data = stations_data
        self.drones_positions = drones_positions
        self.connections_data = connections_data
        self.windows: Any = None
        self.background: Any = None
        self.start_png: Any = None
        self.end_png: Any = None
        self.drone_png: Any = None
        self.zone_png: dict[str, Any] = {}
        self.icon_scale: Any = None
        self.scale_x: Any = None
        self.scale_y: Any = None
        self.min_x: Any = None
        self.min_y: Any = None
        self.marge: float = 100
        self.coef: float = 1
        self.station_pixels: dict[str, tuple[float, float]] = {}
    
        if len(stations_data) > 70:
            print(
                "\033[0;31mError: too many stations (max 70) to "
                "display cleanly\033[0m")
            sys.exit(1)

        self.NEW_SIZE_WINDOWS = self.ask_size()

        self.init_display()
        self.load_png()
        Calculate.size_marge(self)
        Calculate.scale(self)
        self.run_display()

    def ask_size(self) -> tuple[int, int]:
        """
        Demande a l'utilisateur la taille d'affichage voulue.

        Trois choix possibles : 'little', 'medium' ou 'big'. Le
        coefficient self.coef est ajuste en consequence ; il sert
        ensuite a re-echelonner la taille des icones et des cercles
        de couleur (voir Calculate.scale_nb_drones). Si la reponse ne
        correspond a aucun de ces trois choix, on retombe sur
        'medium' par defaut.
        """
        self.choice = input(
            "\033[36myou can choice size display "
            "(tape little, medium or big) :  \033[0m")

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

        return (self.NEW_SIZE_WINDOWS)

    def init_display(self) -> None:
        """
        Initialise la fenetre pygame.

        pygame.init() demarre le moteur, pygame.display.Info()
        recupere la resolution reelle de l'ecran de l'utilisateur
        (utile pour calculer les echelles dans Calculate), puis
        set_mode ouvre effectivement la fenetre a la taille choisie
        dans ask_size.
        """
        # .init : demarre  le moteur pygame
        pygame.init()
        # .Info: recupere les donnees de l'affichage notamment la
        # hauteur et la largeur de l'ecran
        self.info = pygame.display.Info()
        # set_mode : permet de creer la fenetre d affichage
        self.windows = pygame.display.set_mode(self.NEW_SIZE_WINDOWS)
        pygame.display.set_caption("Fly-in is ESQUIE")

    def load_png(self) -> None:
        """
        Charge toutes les images utilisees par l'affichage et les
        redimensionne a la bonne echelle.

        Chaque image (fond, start, goal, drone, puis les 4 zones) est
        d'abord chargee telle quelle avec pygame.image.load, puis
        redimensionnee via pygame.transform.scale a la taille
        calculee par Calculate.size_icon, qui tient compte de la
        taille de fenetre choisie et du nombre de stations sur la
        carte (plus il y a de stations, plus les icones retrecissent).
        """
        self.background = pygame.image.load(
            "display_folder/background.png").convert()
        self.background = pygame.transform.scale(
            self.background, (self.windows.get_size()))

        self.start_png = pygame.image.load(
            "display_folder/start.png").convert_alpha()
        self.start_png = pygame.transform.scale(
            self.start_png, Calculate.size_icon(self, 'start'))
        self.end_png = pygame.image.load(
            "display_folder/end.png").convert_alpha()
        self.end_png = pygame.transform.scale(
            self.end_png, Calculate.size_icon(self, 'goal'))
        self.drone_png = pygame.image.load(
            "display_folder/esquie_drone.png").convert_alpha()
        self.drone_png = pygame.transform.scale(
            self.drone_png, Calculate.size_icon(self, 'drone'))

        self.zone_png = {
            'normal': pygame.image.load(
                "display_folder/normal_zone.png").convert_alpha(),
            'priority': pygame.image.load(
                "display_folder/priority_zone.png").convert_alpha(),
            'restricted': pygame.image.load(
                "display_folder/restricted_zone.png").convert_alpha(),
            'blocked': pygame.image.load(
                "display_folder/blocked_zone.png").convert_alpha()
            }

        self.zone_png['normal'] = pygame.transform.scale(
            self.zone_png['normal'],
            Calculate.size_icon(self, 'normal'))
        self.zone_png['priority'] = pygame.transform.scale(
            self.zone_png['priority'],
            Calculate.size_icon(self, 'priority'))
        self.zone_png['restricted'] = pygame.transform.scale(
            self.zone_png['restricted'],
            Calculate.size_icon(self, 'restricted'))
        self.zone_png['blocked'] = pygame.transform.scale(
            self.zone_png['blocked'],
            Calculate.size_icon(self, 'blocked'))

    def color_zone(self, station: str) -> tuple[int, int, int] | None:
        """
        Renvoie la couleur RGB associee a la station, ou None si la
        couleur enregistree n'est pas une des couleurs connues de
        COLOR_MAP.

        En pratique le parsing garantit toujours une couleur valide
        (par defaut 'cyan' si rien n'est precise), le cas None est
        donc surtout la pour satisfaire le typage mypy.
        """
        color = self.stations_data[station]['color']
        if color in COLOR_MAP:
            return (COLOR_MAP[color])
        return None

    def draw_station_label(
        self, police: pygame.font.Font, station: str,
        x: float, y: float
    ) -> None:
        """
        Dessine le nom de la station, place en
        (x, y) (coin haut-gauche de l'encart).

        Si le nom fait plus de 8 caracteres et contient un
        underscore, il est coupe en deux lignes a cet endroit pour
        rester lisible sur les grandes cartes.
        """
        if len(station) > 8 and '_' in station:
            lines = station.split('_', 1)
        else:
            lines = [station]

        surfaces = [
            police.render(line, True, (255, 255, 255)) for line in lines]
  
        line_y = y + 3
        for surf in surfaces:
            self.windows.blit(surf, (x + 3, line_y))
            line_y += surf.get_height()

    def draw_stations(self) -> None:
        """
        Calcule et dessine la position de chaque station sur la
        carte.

        Pour chaque station, les coordonnees logiques
        (data['coord']) sont converties en pixels grace a
        self.marge (la marge autour de la carte) et self.scale_x /
        self.scale_y (le nombre de pixels par unite de coordonnee,
        calcule dans Calculate.scale).

        Un cercle de la couleur de la station est dessine derriere
        l'icone correspondant a son type : start, goal, ou l'une des
        4 zones (normal, blocked, restricted, priority). La position
        finale en pixels de chaque station est enregistree dans
        self.station_pixels, pour que draw_drones puisse ensuite
        calculer le trajet de chaque drone d'une station a l'autre.
        """
        # permet d enlever aussi la marge de chaque cote pour x et y
        # et de multiplier par le facteur scale (l'echell)

        size = 20  if self.choice == 'big' else (
            8 if self.choice == 'little' else 15)
        add_ft = 60 if self.choice == 'big' else (
            30 if self.choice == 'little' else 40)
        add_start_y = 60 if self.choice == 'big' else (
            20 if self.choice == 'little' else 40)
        add_start_x = 60 if self.choice == 'big' else (
            10 if self.choice == 'little' else 30)
        add_end = 50 if self.choice == 'big' else (
            30 if self.choice == 'little' else 30)
        police = pygame.font.SysFont("manjari", size)

        for station, data in self.stations_data.items():
            pixel_x = (
                self.marge
                + (data['coord'][0] - self.min_x) * self.scale_x)

            if data['coord'][1] == self.min_y:
                pixel_y = (
                    self.marge
                    + (data['coord'][1] - self.min_y) * self.scale_y)

            else:
                pixel_y = (
                    (data['coord'][1] - self.min_y) * self.scale_y
                    - self.marge)

            # affichage et mise en place des cercles couleur zone et
            # des icon
            if station == 'start':
                icon_scale = Calculate.size_icon(self, 'start')
                center = (
                    (pixel_x + icon_scale[0] // 2),
                    (pixel_y + self.icon_scale[1] // 2))
                pygame.draw.circle(
                    self.windows,
                    cast(tuple[int, int, int], self.color_zone(station)),
                    center,
                    Calculate.size_cercle(self, ICONS['start']['radius']))
                self.windows.blit(self.start_png, (pixel_x, pixel_y + 5))
                self.draw_station_label(
                    police, station, pixel_x + add_start_x, pixel_y - add_start_y)
                self.station_pixels['start'] = center
            elif station == 'goal':
                icon_scale = Calculate.size_icon(self, 'goal')
                center = (
                    (pixel_x - 100 * self.ratio + self.icon_scale[0] // 2),
                    (pixel_y + self.icon_scale[1] // 2))
                pygame.draw.circle(
                    self.windows,
                    cast(tuple[int, int, int], self.color_zone(station)),
                    center,
                    Calculate.size_cercle(self, ICONS['goal']['radius']))
                self.windows.blit(
                    self.end_png, (pixel_x - 100 * self.ratio, pixel_y))
                self.draw_station_label(
                    police, station, pixel_x - 40, pixel_y - add_end)
                self.station_pixels['goal'] = center
            else:
                if data['zone'] == 'normal':
                    icon_scale = Calculate.size_icon(self, 'normal')
                    center = (
                        (pixel_x + self.icon_scale[0] // 2),
                        (pixel_y + self.icon_scale[1] // 2))
                    pygame.draw.circle(
                        self.windows,
                        cast(
                            tuple[int, int, int],
                            self.color_zone(station)),
                        center,
                        Calculate.size_cercle(
                            self, ICONS['normal']['radius']))
                    self.windows.blit(
                        self.zone_png['normal'], (pixel_x, pixel_y))
                if data['zone'] == 'blocked':
                    icon_scale = Calculate.size_icon(self, 'blocked')
                    center = (
                        (pixel_x + self.icon_scale[0] // 2),
                        (pixel_y + self.icon_scale[1] // 2))
                    pygame.draw.circle(
                        self.windows,
                        cast(
                            tuple[int, int, int],
                            self.color_zone(station)),
                        center,
                        Calculate.size_cercle(
                            self, ICONS['blocked']['radius']))
                    self.windows.blit(
                        self.zone_png['blocked'], (pixel_x, pixel_y))
                if data['zone'] == 'restricted':
                    icon_scale = Calculate.size_icon(self, 'restricted')
                    center = (
                        (pixel_x + 5 + self.icon_scale[0] // 2),
                        (pixel_y + 8 + self.icon_scale[1] // 2))
                    pygame.draw.circle(
                        self.windows,
                        cast(
                            tuple[int, int, int],
                            self.color_zone(station)),
                        center,
                        Calculate.size_cercle(
                            self, ICONS['restricted']['radius']))
                    self.windows.blit(
                        self.zone_png['restricted'],
                        (pixel_x + 5, pixel_y + 8))
                if data['zone'] == 'priority':
                    icon_scale = Calculate.size_icon(self, 'priority')
                    center = (
                        (pixel_x + self.icon_scale[0] // 2),
                        (pixel_y + self.icon_scale[1] // 2))
                    pygame.draw.circle(
                        self.windows,
                        cast(
                            tuple[int, int, int],
                            self.color_zone(station)),
                        center,
                        Calculate.size_cercle(
                            self, ICONS['priority']['radius']))
                    self.windows.blit(
                        self.zone_png['priority'], (pixel_x, pixel_y))

                self.draw_station_label(
                    police, station, pixel_x, pixel_y - add_ft)
                self.station_pixels[station] = center

    def draw_drones(
        self, tour: int, previous: dict[str, str], progression: float
    ) -> None:
        """
        Dessine chaque drone a sa position courante pour ce tour.

        La position affichee est une interpolation lineaire entre l.centera
        station de depart (previous[drone]) et la station d'arrivee
        (self.drones_positions[tour][drone]) : progression vaut 0 au
        debut de l'animation du tour et 1 a la fin (voir les
        progression_steps dans run_display), donc x/y se deplacent
        petit a petit du point de depart vers le point d'arrivee.
        Le nom du drone est ecrit par-dessus son icone avec la police
        choisie ici selon la taille de fenetre.
        """
        size = 30  if self.choice == 'big' else (
            15 if self.choice == 'little' else 20)
        police = pygame.font.SysFont("puriza", size)
        add = 55 if self.choice == 'big' else (
            25 if self.choice == 'little' else 35)

        for drone, station_next in self.drones_positions[tour].items():
            station_from = previous[drone]
            start_x, start_y = self.station_pixels[station_from]
            goal_x, goal_y = self.station_pixels[station_next]

            x = start_x + (goal_x - start_x) * progression
            y = start_y + (goal_y - start_y) * progression

            text = police.render(drone, True, (255, 255, 255))
            drone_w, drone_h = self.drone_png.get_size()
            self.windows.blit(
                self.drone_png, (x - drone_w // 2, y - drone_h // 2))
            if station_next != 'start' and station_next != 'goal':
                self.windows.blit(text, (x, y - add))

    def run_display(self) -> None:
        """
        Boucle principale de l'affichage pygame.

        Pour chaque tour de la simulation, previous garde la
        position des drones au tour precedent (pour l'interpolation
        dans draw_drones) et progression_steps decoupe l'animation en
        101 petites etapes (0.00, 0.01, ... 1.00) pour un mouvement
        fluide plutot qu'un saut brusque d'une station a l'autre.

        A chaque image : on efface le fond, on redessine les
        stations, on dessine les drones a leur position interpolee,
        puis on affiche (pygame.display.flip) avant d'attendre un peu
        (pygame.time.wait) pour reguler la vitesse de l'animation.

        L'utilisateur peut appuyer sur espace pour accelerer,
        sur s pour mettre en pause, et sur b pour recommencer
        l'animation depuis le debut (voir choice_keydown).

        Une fois tous les tours joues, une boucle infinie garde la
        fenetre ouverte jusqu'a ce que l'utilisateur la ferme
        (evenement pygame.QUIT).
        """
        self.speed_index = 0
        self.speed = [50, 25, 15, 5, 1]
        tours = list(self.drones_positions)
        progression_steps = [i * 0.01 for i in range(101)]

        while True:
            self.paused = False
            previous = {
                drone: 'start' for drone in self.drones_positions[0]}

            try:
                for tour in tours:
                    for progression in progression_steps:
                        self._handle_events()
                        while self.paused:
                            self._handle_events()

                        self.draw_background()
                        self.draw_keyword_utils()
                        self.draw_stations()
                        self.draw_connections()
                        self.draw_stations()  # redessine par-dessus les traits
                        self.draw_drones(tour, previous, progression)
                        pygame.time.wait(self.speed[self.speed_index])
                        pygame.display.flip()

                    previous = self.drones_positions[tour]

                self._wait_for_restart()
            except _RestartAnimation:
                continue
            except _QuitAnimation:
                pygame.quit()
                sys.exit()

    def _handle_events(self) -> None:
        """Recupere les evenements pygame en attente et les traite :
        ferme la fenetre sur QUIT, sinon delegue les touches pressees
        a choice_keydown (qui peut lever _RestartAnimation ou
        _QuitAnimation pour interrompre l'animation en cours)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise _QuitAnimation
            if event.type == pygame.KEYDOWN:
                self.choice_keydown(event.key)


    def _wait_for_restart(self) -> None:
        """Une fois tous les tours joues, garde la fenetre ouverte et
        attend que l'utilisateur appuie sur B (redemarrer) ou ferme
        la fenetre / appuie sur Q (quitter)."""
        while True:
            self._handle_events()


    def draw_background(self) -> None:
        """Efface la map en reaffichant l'image de fond par-dessus."""
        self.windows.blit(self.background, (0, 0))



    def draw_keyword_utils(self) -> None:
        police = pygame.font.SysFont("manjari", 20)
        lignes = [
            "        PRESS keyboard",
            "",
            "- SPACE = speed run drone",
            "- S = stop run",
            "- B = restart map",
            "- Q = exit"
        ]
        padding = 15
        largeur = max(police.size(ligne)[0] for ligne in lignes) + padding * 2
        hauteur = len(lignes) * police.get_linesize() + padding * 2

        # coin bas-droit de la fenetre : zone rarement occupee par
        # une station, quelle que soit la carte chargee
        window_w, window_h = self.windows.get_size()
        x = window_w - largeur
        y = window_h - hauteur

        # fond semi-transparent : garde le texte lisible sans cacher
        # totalement ce qu'il y a sur la carte en dessous
        fond = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
        fond.fill((0, 0, 0, 130))
        self.windows.blit(fond, (x, y))

        for i, ligne in enumerate(lignes):
            text = police.render(ligne, True, (255, 255, 255))
            self.windows.blit(
                text, (x + padding, y + padding + i * police.get_linesize()))
        


    def draw_connections(self) -> None:
        """Affichage du trace entre deux station grace a self.connections_data"""
        for station_a, station_b in self.connections_data:
            start = self.station_pixels[station_a]
            end = self.station_pixels[station_b]
            pygame.draw.line(self.windows, (255, 255, 255), start, end)

    def choice_keydown(self, event_key):
        """Choix des touches du clavier pour stopper l'animation, accelerer ou recommencer"""
        if event_key == pygame.K_SPACE:
            if self.speed_index > 3:
                self.speed_index = 0
            else:
                self.speed_index += 1

        if event_key == pygame.K_s:
            self.paused = not self.paused

        if event_key == pygame.K_b:
            raise _RestartAnimation

        if event_key == pygame.K_q:
            raise _QuitAnimation



class Calculate():
    """
    Regroupe les calculs geometriques utilises par Display : mise a
    l'echelle des icones et des cercles selon la taille de fenetre et
    le nombre de stations, calcul de la marge, et calcul du facteur
    de conversion coordonnee -> pixel.

    Toutes les methodes sont statiques et prennent en premier
    argument l'instance de Display concernee (display), sur laquelle
    elles lisent et ecrivent directement les attributs necessaires.
    """

    @staticmethod
    def size_icon(display: 'Display', name: str) -> tuple[float, float]:
        """
        Calcule la taille (largeur, hauteur) en pixels d'une icone,
        d'apres sa taille de reference dans ICONS[name]['size'].

        La taille de reference est mise a l'echelle par le ratio
        fenetre choisie / ecran reel (display.NEW_SIZE_WINDOWS /
        display.info.current_w ou current_h), puis par le ratio
        renvoye par scale_nb_drones qui reduit encore les icones
        quand il y a beaucoup de stations sur la carte.
        """
        ratio = Calculate.scale_nb_drones(display)
        w_windows = (
            (display.NEW_SIZE_WINDOWS[0] * ratio)
            * ICONS[name]['size'][0] / display.info.current_w)
        h_windows = (
            (display.NEW_SIZE_WINDOWS[1] * ratio)
            * ICONS[name]['size'][1] / display.info.current_h)
        display.icon_scale = w_windows, h_windows

        return (display.icon_scale)

    @staticmethod
    def scale_nb_drones(display: 'Display') -> float:
        """
        Calcule display.ratio, le coefficient de reduction des
        icones et cercles selon le nombre de stations sur la carte.

        Plus il y a de stations, plus il faut retrecir pour que tout
        rentre dans la fenetre : le nombre de stations est compare a
        70 (le maximum autorise) pour obtenir un ratio entre 0 et 1.
        display.coef (fixe dans ask_size selon little/medium/big)
        vient encore ajuster ce ratio a la taille de fenetre choisie.
        """
        nb = len(display.stations_data)
        if nb < 30:
            display.ratio = 1 - 0.50 * display.coef * nb / 30
        elif nb > 30 and nb < 40:
            display.ratio = 1 - 0.50 * display.coef * nb / 40
        else:
            display.ratio = 1 - 0.60 * display.coef * nb / 70

        return display.ratio

    @staticmethod
    def size_cercle(display: 'Display', radius: float) -> float:
        """
        Calcule le rayon en pixels d'un cercle de couleur de station,
        a partir de son rayon de reference (radius, defini dans
        ICONS), mis a l'echelle par la taille de fenetre reelle vs
        l'ecran, puis par display.ratio (voir scale_nb_drones).
        """
        base = display.info.current_w + display.info.current_h
        new = display.NEW_SIZE_WINDOWS[0] + display.NEW_SIZE_WINDOWS[1]
        display.size_cercle = new * radius / base * display.ratio

        return (display.size_cercle)

    @staticmethod
    def size_marge(display: 'Display') -> None:
        """
        Calcule la marge (en pixels) a laisser autour de la carte,
        mise a l'echelle de la meme facon que size_cercle : par le
        ratio entre la taille de fenetre choisie et la resolution
        reelle de l'ecran.
        """
        base = display.info.current_w + display.info.current_h
        new = display.NEW_SIZE_WINDOWS[0] + display.NEW_SIZE_WINDOWS[1]
        display.marge = new * display.marge / base

    @staticmethod
    def scale(display: 'Display') -> None:
        """
        Calcule le facteur de conversion coordonnee -> pixel pour x
        et y (display.scale_x, display.scale_y), c'est-a-dire combien
        de pixels represente 1 unite de coordonnee de la carte.

        On repere d'abord les coordonnees min/max de toutes les
        stations (display.min_x/max_x/min_y/max_y), ce qui donne
        l'etendue logique de la carte (range_x, range_y). Le nombre
        de pixels disponibles (largeur/hauteur de la fenetre moins
        deux fois la marge) divise par cette etendue donne le nombre
        de pixels par unite. Si toutes les stations partagent la
        meme coordonnee (range == 0), on utilise un facteur de 1
        pour eviter une division par zero.
        """
        # On prends le minimum et le max de x et y
        coord_x = [
            display.stations_data[s]['coord'][0]
            for s in display.stations_data]
        display.min_x, display.max_x = min(coord_x), max(coord_x)

        coord_y = [
            display.stations_data[s]['coord'][1]
            for s in display.stations_data]
        display.min_y, display.max_y = min(coord_y), max(coord_y)

        width, height = display.windows.get_size()
        display.windows.blit(display.background, (0, 0))

        # On deduit la marge de la taille width et height et on
        # divise la diff entre le min et max de x et y
        display.range_x = display.max_x - display.min_x
        display.range_y = display.max_y - display.min_y
        display.scale_x = (
            (width - (display.marge * 2)) / display.range_x
            if display.range_x != 0 else 1)
        display.scale_y = (
            (height - (display.marge * 2)) / display.range_y
            if display.range_y != 0 else 1)
