## Ordre de deroulements des etapes pour FLY-IN

### 1. Makefile

### 2. main
        - petit parsing argv et fichier non present  ✅

### 3. Parsing
        - enlever espace et # dans le fichier txt de map en creant une list ✅
        - mise en dictionnaire la list precedente en gerant les doublons de key, et en creant une liste de valeurs dans les cles doublons. ✅
        - plan des cles nb_drones, start_hub, hub, end_hub, conenction respectde l'ordre ✅
        - nbr de drone, gerer chiffre, un minimum ✅
        - parse_line methode qui gere les doublons des noms de stations et les doublons de coordonnees ✅
        - gerer les doublon start_hub et end_hub ✅
        - gerer les coord de plus de deux donnees x y ✅ 
        - deuxieme partie de parse_line qui gere les metadata ✅
        - parsing sur start_hub (class Configstart) ✅
        - parsing sur hub (class ConfigHub) ✅
        - parsing sur end_hub (class ConfigEnd) ✅
        - realisation d un un dictionnaire avec station: nom: ... coord:... metadata:.... ✅

        - parsing sur connection (class ConfigConnection) ✅
        - gestion validation des stations, de l'ordre des staton par rapport a la premiere partie ✅
        - gestion metadonne max_link_capacity gestion ✅
        - gestion des metadata par default color zone max_drone max_linK_capacity ✅

### 4. Requierement
        - 

### 5. Creation des zones(normal, blocked, restricted, priority)
        # dans dossier models -> zone.py
        - creation des classes zones ✅
        - les couts pour chaque classe ✅
        - restreindre les zones bloque 

### 6. Creation des couleurs selon les zones
        # dans dossier models -> colors.py
        - creation des classes zones 

### 7. connexion entre les zones
        - creation d un dictionnaire de voisin ✅
        

### 8. Algo 
        - premeire approche de l algo avec la gestion de dijkstra algo ✅
        - gestion des zones deja visite ✅
        - gestion du previous pour recuperer le chemin le bon ✅
        - utilisation de heapq pour pouvoir recuperer le cout le plus bas a chaque tour ✅
        - gestion de la zone blocked, contourne ce dernier ✅

### 9. Max_drones
        - gestion du max drones dans simulator.py ✅
        - le nbr de tours est bon pour chaque map sauf la challenger ✅


### 10. Max_link
        - incorporer le max_link dans simulator.py 


### 10. visuel (playgame) 

### 11. docstring
        - changement docstring en anglais partout et commentaire

### 1. Readme

### 12. bonus
        - gestion du nombre de tours max pour la map challenger, actuellement -> 63 / objectif : <= 45