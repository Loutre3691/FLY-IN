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
        - creation des classes zones 

### 6. Creation des couleurs selon les zones
        # dans dossier models -> colors.py
        - creation des classes zones 

### 7. connexion entre les zones

### 8. Algo (easy, medium, hard, challenge)

### 9. visuel (playgame) 

### 10. docstring

### 11. Readme

### 12. bonus