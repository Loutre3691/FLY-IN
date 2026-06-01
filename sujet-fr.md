⚠️  Dans ce readme, je vais en premier lieu decrire exactement  les differentes choses a faire pour le projet Fly-in, ce sera ma reference pour avancer sans rien oublier dans le projet 


##  📦 Les regles generales

-   Utilisation de try/except por gerer les erreurs pour eviter que ca plante
-  Privilégiez les gestionnaires de contexte pour les ressources telles que les fichiers ou les connexions lorsque cela est possible pour une gestion automatique (open, close ....)
-  Mypy
-  Inclure des docstrings  dans les fonctions et les classes

## 📦 Makefile

⚠️  Pour l'automatisation des taches dans le projets les regles du makefile:
-`-- strict`: pour la verif
- install :  pour installer les depednances avec pip, uv, pipx ou autre
- run: Exécutez le script principal en mode débogage à l’aide du débogueur intégré de Python (par exemple, pdb).
- clean :  supprimer fichiers temporaire : `__pycache__ ou __.mypy_cache__`
- lint: execute la commande flake8 . and mypy . `--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
-  lint-strict: optional execute `flake8 . and mypy . --strict`

## 📦 Readme

- login *  (This project has been created as part of the 42 curriculum by)*
- “Description”
- “Instructions”
- “Resources”
-  Parties supplementaire selon le projet
-  detail algo
-  documenter la representaiton visuelle et pk c'est mieu
## 📦 Directives supplementaires

- creer des programmes tests pour verifier la fonctionnalite du projet, utilisation de framework comme 'pytest' ou 'unittest'
-  inclure .gitignore pour exclure les artefact
-  Il est recommande d utiliser un environnement virtuel pour isoler les dependances pendant le dev

## 📦 Les contraintes

-  Toute bibliothèque facilitant la logique des graphes est interdite (telle que networkx, graphlib, etc.).
-  OOBJET
-  f8 mypy


## 📦 Le BUT du projet 

concevoir un système qui achemine efficacement une flotte de drones d'une base centrale (départ) vers un emplacement cible (arrivée), tout en naviguant dans ce réseau dynamique sous un ensemble de contraintes strictes et d'objectifs d'optimisation.

Vous recevrez un graphe représentant le réseau de zones, ainsi qu'un ensemble de contraintes à respecter. Ce graphe est représenté comme un réseau de zones interconnectées, les connexions définissant les itinéraires de déplacement possibles entre les zones.


# 1️⃣  Reseau de zone

```
nb_drones: 5 

start_hub: hub 0 0 [color=green] 
end_hub: goal 10 10 [color=yellow] 
hub: roof1 3 4 [zone=restricted color=red] 
hub: roof2 6 2 [zone=normal color=blue] 
hub: corridorA 4 3 [zone=priority color=green max_drones=2] 
hub: tunnelB 7 4 [zone=normal color=red] 
hub: obstacleX 5 5 [zone=blocked color=gray] 
connection: hub-roof1 
connection: hub-corridorA 
connection: roof1-roof2 
connection: roof2-goal 
connection: corridorA-tunnelB [max_link_capacity=2] 
connection: tunnelB-goal
```

### 💡 <span style="color: cyan;">Explication</span>

➡️  nb_drones: permet de definir le nombre de drones :  <number>
➡️  definition de zone :
		-  `start_hub: <name> <x> <y> [metadata]`  == zone de depart 
		-  `end_hub: <name> <x> <y> [metadata]`  == zone de fin
		-  `hub: <name> <x> <y> [metadata]`  == zone de regulation
		-  Interdiction des tirets dans le nom des zones

➡️ toutes les metadatas sont optionnelles et placees entre brackets [...] avec des valeurs par defauts:
			-  `zone=<type>`   (default: normal)
			-  `color=<value>`   (defaults: none)
			-  `max_drones=<number>`  (default: 1)  c'est le nombre maximum de drones pouvant occuper simultanement cette zone
			-  les balises entre crochets peuvent apparaitre dans n'importe quel ordre

➡️  Types de zones:
			- <span style="color: cyan;">normal</span> (zone standard avec 1 cout de deplacemnt par tour) default
			- <span style="color: red;">blocked</span> ( zone innaccessible, les drones ne doivent pas entrer ou passer a travers cette zone, tous cheminl l'utilisant est invalid )
			-  <span style="color: orange;">restricted</span> (zone sensible ou dangereuse, chaque mouvement dans cette zone coute 2 tours)'
			-  <span style="color: green;">priority</span> ( se deplacer vers cette zone  coute 1 tour mais doit etre priorise lors de la recherche de chemin)

➡️  Les couleurs:
			- Les couleurs sont optionnelles et peuvent etre utilise pour une representation visuelles (terminal ou affichage graphique) playgame  pour le visu 
			- les valeurs pour les couleurs acceptees son un seul mot (ex: red, blue, gray) il n'existe pas de liste fixe autorise pour les couleurs
			- quand les couleurs sont specifiees, l'implementation doit fournir un retour visuel via une sortie terminale colorée ou une représentation graphique.

➡️  Les connections sont definis : `<name1>-<name2> [metadata]`
			- Definir une connection bidirectionnelle entre 2 zones
			-  la syntaxes de connection interdit les tirets dans le nom des zones
			-  Des métadonnées facultatives peuvent être spécifiées entre crochets.
					 *-  `max_link_capacity=<number>` (default: 1) - Max de drones qui peuvent traverses simultanement cette connection
	
➡️  commentaire commencant par `#` sont ignores

➡️ Les coordonnées des zones seront toujours des nombres entiers, et il y aura toujours une zone de départ unique et une zone d'arrivée unique.


# 2️⃣ Partie obligatoire



#### ➡️ <span style="color: purple;">ALGORITHM</span>

-  Les drones peuvent se déplacer simultanément.
-  planification des trajectoire pour optimiser le debit
-  gestion de la distribution  des drones sur plusieurs trajectoires
-  gestion de l'attente strategique quand le mouvement n'est pas possible
-  eviter les conflits de chemin et les blocages
-  tenir compte de la longueur des trajets et des couts de deplacements selon les zones
-  planification des rotations (evite les blockage et collisions)
-  structure graphique  qui permet de determiner les chemins dispo disjoins ou cheveauchant
-  tenir compte des contraintes des capacite des zones `(max_drones)`et des capacites de connection `(max_link_capacity)`
-  algo adaptable, differentes cartes peuvent demander des strategies de routes diff, selon la toplogie et les zones
- l implémentation doit fournir un retour visuel de la simulation 
			- affichage en couleur des mouvements et des zones sur le terminal
			- une interface graphique qui affiche les position des drones et le reseau


# 💡
``` 
- Votre algorithme est-il efficace ?
- Peut-il gérer un grand nombre de drones ?
- Quelle est sa complexité (par exemple, O(n), O(log n), etc.) ?
- Recalculez-vous ou mettez-vous en cache les trajectoires ? 
- Quel est l’impact sur l’utilisation de la mémoire ? 
- Comment votre représentation visuelle facilite-t-elle la compréhension de la simulation ?
```

#### ➡️ <span style="color: purple;">REGLES OCCUPATIONS DES ZONES</span>

- par default 1 seule drone par zone a chaque tour
- les zones avec `max_drones=N` peuvent contenir jusqu'a N drones en simultanes
-  deux exceptions aux regles d'occupations:
				-  la zone start: tous les drones commencent ici et partagent l'espace
				-  la zone end: plusieurs drones peuvent arrives 
- 2 drones ne peuvent entrer dans la meme zone au cours du même tour, sauf si la capacité de la zone le permet.
- 1 drone ne peut pas penetrer a l'interieur d'une zone si sa capacite max est atteintes
-  la capacite de connexion `(max_link_capacity)`  limite le nombre de drones pouvant emprunter simultanement la meme connexion
-  si toutes les contraintes sont respectes alors les drones peuvent bouger simultanement


#### ➡️ <span style="color: purple;">MOUVEMENTS ET ROTATIONS</span>

A chaque tour chaque drone peut:
	- se deplacer vers une zone connectée adjacente (si la capacité le permet).\
	- se deplacer  vers une connexion menant à une zone restreinte (nécessitant 2 tours pour être atteinte). Dans ce cas, le drone DOIT atteindre sa destination au prochain tour. Il ne peut pas attendre de tours supplémentaires sur la connexion. 
	- Restez sur place (par exemple, pour attendre ou si le mouvement est bloqué).

- les drones qui quittent une zone libere pour ce meme tour la zone
- Pour les manœuvres à plusieurs virages (zones réglementées), le drone occupe la voie de correspondance pendant le transit et DOIT arriver à destination après le nombre de virages spécifié. Il ne peut pas attendre qu'un emplacement se libère dans la zone de destination.

Chaque mouvement entre les zones a un cout en tours base sur `zone==type` de la destination:
			- <span style="color: cyan;">normal</span> : 1 tour (par default)
			- <span style="color: red;">blocked</span> : interdit
			-  <span style="color: orange;">restricted</span> : 2 tours
			-  <span style="color: green;">priority</span>: 1 tour (mais devra etre privilegie dans l algo)


#### ➡️ <span style="color: purple;">PARSING - LES CONTRAINTES</span>

• La première ligne doit définir le nombre de drones à l'aide de `nb_drones: <positive_integer>`.

• Le programme doit pouvoir gérer un nombre quelconque de drones.

• Il doit y avoir exactement une zone `start_hub: zone` et une zone `end_hub: zone`.

• Chaque zone doit avoir un nom unique et des coordonnées entières valides.

• Les noms de zone peuvent contenir tous les caractères valides, à l'exception des tirets et des espaces.

• Les connexions doivent relier uniquement les zones préalablement définies à l'aide de `connection: <zone1>-<zone2>
[métadonnées]`.

• Une même connexion ne doit pas apparaître plus d'une fois (par exemple, `a-b` et `b-a` sont considérés comme des doublons).

• Tout bloc de métadonnées (par exemple, `[zone=... color=...]` pour les zones, `[max_link_capacity=...]` pour les connexions) doit être syntaxiquement valide.

• Les types de zone doivent être : `normal`, `blocked`, `restricted`, `priority`. Tout type invalide doit générer une erreur d'analyse. • Les valeurs de capacité (`max_drones` pour les zones, `max_link_capacity` pour les connexions) doivent
être des entiers positifs.

• Toute autre erreur d'analyse doit interrompre le programme et renvoyer un message d'erreur clair indiquant la ligne et la cause.


# 💡
 ```
 Il est grandement recommande de faire ses propres fichiers de map pour gerer tous les cas particulier
 ```
 
#### ➡️ <span style="color: purple;">FORMAT DE SORTIE DE SIMULATION</span>

- la simulation doit reproduite etape par etape le mouvement des drones
-  chaque tour de simulation est represente par une ligne
-  Chaque ligne doit lister tous les mouvements de drones effectués pendant ce tour, séparés par des espaces.
- Chaque mouvement doit respecter le format : `D<ID>-<zone>` or `D<ID>-<connection>`en cas de drones survolant encore des zones réglementées
					- `D<ID>` se refere a l'id unique du drone (ex: D1, D2)
					- `<zone>` est le nom de la zone de destination
					- `<connection>` est le nom de la conenxion vers une zone reglementee
-  Les drones qui ne se déplacent pas lors d'un tour donné sont omis de cette ligne
-  les drones dans `end` ne seront plus suivis
-  fin de simuation -> quand tous les drones sont a `end`

### 💡 <span style="color: cyan;">Exemple</span>

```
D1-roof1 D2-corridorA 
D1-roof2 D2-tunnelB 
D1-goal D2-goal
```


#### ➡️ <span style="color: purple;">SYSTEM DE NOTATION</span>

- performance evaluee en fonction du nombre de tours de `start` a `end`
- moin il y a de tours -> meilleurs score
-  une simulation valide doit gerer les regles, les couts des tours, les capacites, les contraintes
- Optionnel mais recommandes pour la correction:
			- le nombre de drones deplaces par tour
			- le nombre moyen de virages par drone et le coût total du trajet (somme des couts pour tous les drones)
			-  Qualité et utilité de la représentation visuelle


#### ➡️ <span style="color: purple;">INDICATEURS DE PERFORMANCES</span>

###### <span style="color: cyan;">Performances attendues:</span>
-  <span style="color: green;">Easy maps</span>: moins de `10 tours`
-  <span style="color: yellow;">Medium maps</span>: entre `10 - 30 tours`
-  <span style="color: red;">Hard maps</span>: moins de `60 tours`
-  <span style="color: pink;">Challenger map (optionnal) : </span> viser à battre le record de référence de `45 tours`



### 💡 <span style="color: cyan;">Aide de reference de performances</span>

```
• Easy Maps: 
	◦ Linear path with 2 drones: Target ≤ 6 turns 
	◦ Simple fork with 4 drones: Target ≤ 8 turns 
	◦ Basic capacity with 4 drones: Target ≤ 6 turns
• Medium Maps: 
	◦ Dead end trap with 5 drones: Target ≤ 12 turns 
	◦ Circular loop with 6 drones: Target ≤ 15 turns 
	◦ Priority puzzle with 5 drones: Target ≤ 12 turns 
• Hard Maps: 
	◦ Maze nightmare with 8 drones: Target ≤ 30 turns 
	◦ Capacity hell with 12 drones: Target ≤ 35 turns 
	◦ Ultimate challenge with 15 drones: Target ≤ 45 turns 
• Challenger Map (optional — for exceptional implementations):
	◦ The Impossible Dream with 25 drones: Reference record: 45 turns 
	◦ This quasi-unsolvable challenge is designed for algorithmic research and optimization 
	◦ Solving this map demonstrates exceptional pathfinding and optimization skills 
	◦ Note: This level is purely optional and does not affect
```

# 💡
```
•  l'algo peut il atteindre les seuils de performance?
•  Comment votre solution se compare-t-elle aux cibles de référence ?
•  Quelles optimisations avez-vous mises en œuvre pour obtenir de meilleures performances ? 
•  Parviendrez-vous à résoudre la carte Challenger et à battre le record des 45 tours ?
```



# 3️⃣ BONUS


Cette partie bonus ne sera examinée que si toutes les conditions obligatoires sont remplies. Voici les fonctionnalités que vous pouvez implémenter pour améliorer votre projet : 

- `Performances exceptionnelles` : Vous atteignez parfaitement les objectifs de performance de référence pour toutes les cartes fournies. « Parfaitement » signifie que vous atteignez ou dépassez le nombre de tours cible. 


- `Carte défi `: La carte « Impossible Dream » est résolue et bat le record de référence de 45 tours.


#  4️⃣ EVALUATION

Il y a une instruction dans la correction qui demande de modifier le code, se renseigner