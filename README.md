# ZList manual

## English

### Description

The purpose of this list is to :
1. Perform analysis on player statistics in regard to their category.
2. Possibly take action if a listed player is met in battle.

The clan emblem of each listed player is replaced by the color code associated with his name.
There exist five main categories, each associated with a color code and a PNG file (".\<CATEGORY\>.png") :
- ASSHOLE : red
- CAMPER : purple
- GOLD : yellow
- REROLL : black
- TEAMKILL : cyan

Complex categories (e.g.: ASSHOLE_GOLD) can be created by merging main categories in alphabetical order and associating a new PNG file (e.g.: ".ASSHOLE_GOLD.png").

- ASSHOLE : Attributed to players being exaggeratedly offensive or having unsportsmanlike conduct.
- CAMPER : Attributed to players camping in order to spare their tank or farm damages to the detriment of their team.
- GOLD : Attributed to players shooting premium ammunition on a player whose name is not associated with the code GOLD in this list.
- REROLL : Attributed to players whose account is likely to be a second account/reset/first account on a second server, regardless of the motivation.
- TEAMKILL : Attributed to players who kill teammates either voluntarily or by lack of prudence (with the exception of life saving attempts).

### Mod Installation

This list requires that [XVM](https://modxvm.com/en/download-xvm/) is installed in order to work. The activation of statistics is however not necessary.
To install the ZList, extract the content of this archive in the game folder et replace all files if asked.

### Python scripts

A few Python scripts are provided in this repository for you to draw some graphs based on the names and categories present in the ZList.
As they are not included in the archive downloadable from the release page, it is required to clone the repository in order to get them.

#### Toolset acquisition (Windows)

1. Download and install [Git](https://git-scm.com/downloads). Customize git to your liking but make sure to check "Use Git from the Windows Command Prompt" when asked.
2. Download and install [Python 3.6](https://www.python.org/downloads/) or higher. Check "Add Python 3.6 to PATH" and click "Install Now".
3. Open a terminal with administrator privileges (search for "cmd" in the Start Menu > right click on it > "Execute as administator")
4. Enter `pip install requests Pillow matplotlib`
5. Enter `cd %HOMEDRIVE%%HOMEPATH%`
6. Enter `git clone https://github.com/Zedd7/ZList.git`
7. Enter `cd ZList/src`

#### Scripts manipulation

You are now free to play with the different Python scripts. To do so, enter "python <script_name.py>" in the terminal and follow the instructions.
Please note that each script has its own purpose and can depend on the output of another :

- player_identifier.py : Register account ids of players from the ZList in a CSV file.
- player_lister.py : Register account ids of random players from the cluster in a CSV file.
- player_categorizer.py : Register account ids of players from the ZList according to their assigned color in a CSV file.
- player_profiler.py : Display customs graphs of players' statistics.

As such, they should be executed in the following order : player_identifier.py, player_lister (facultative), player_categorizer, player_profiler.

By default, each script connects itself to the Wargaming API by using the application id "demo" which is open to all but is limited in the number of requests. Thus, results of different scripts may be truncated. If you wish to perform an analysis on the entirety of the ZList, it is necessary that you create an application through the tab "[My Applications](https://developers.wargaming.net/applications/)" and that you replace "demo" by the id of your new application in the config file located at "res/config.txt".

## Français

### Description

L'intérêt de cette liste est de :
1. Faire des analyses des statistiques des joueurs par rapport à leur catégorie.
2. Possiblement agir en conséquence si un joueur listé est recontré en bataille.

Le logo de clan de chaque joueur listé est remplacé par le code de couleur associé à son nom.
Il existe cinq catégories principales, chacune d'elles associée à un code de couleur et un fichier PNG (".\<CATEGORY\>.png") :
- ASSHOLE : rouge
- CAMPER : mauve
- GOLD : jaune
- REROLL : noir
- TEAMKILL : cyan

Des catégories complexes (ex.: ASSHOLE_GOLD) peuvent être crées en fusionnant des catégories principales dans l'ordre alphabétique et en associant un nouveau fichier PNG (ex.: ".ASSHOLE_GOLD.png").

- ASSHOLE : Attribué aux joueurs étant excessivement injurieux ou ayant une conduite anti-sportive.
- CAMPER : Attribué aux joueurs campant de façon à épargner leur char ou à farmer des dégâts au détriment de leur équipe.
- GOLD : Attribué aux joueurs tirant des munitions premium sur un joueur dont le nom n'est pas associé au code GOLD dans cette liste.
- REROLL : Attribué aux joueurs dont le compte est vraisemblablement un second compte/reset/premier compte sur un second serveur, sans considération des motivations.
- TEAMKILL : Attribué aux joueurs tuant des alliés soit volontairement, soit par manque de prudence (à l'exception des tentative de sauvetage).

### Installation du mod

Cette liste nécessite qu'[XVM](http://www.modxvm.com/fr/telecharger-xvm/) soit installé pour fonctionner. L'activation des statistiques n'est cependant pas nécessaire.
Pour installer la ZList, extrayez le contenu de cette archive dans le dossier de jeu et remplacez tous les fichiers si demandé.

### Scripts Python

Quelques scripts Python sont fournis dans ce dépôt afin que vous puissiez dessiner quelques graphiques basés sur les noms and catégories présents dans la ZList.
Etant donné qu'ils ne sont pas inclus dans l'archive téléchargeable depuis la page "releases", il est nécessaire de clôner le dépôt afin de les obtenir.

#### Acquision des outils (Windows)

1. Téléchargez et installez [Git](https://git-scm.com/downloads). Customisez git selon vos goûts mais prenez garde à cocher "Use Git from the Windows Command Prompt" lorsque demandé.
2. Téléchargez et installez [Python 3.6](https://www.python.org/downloads/) ou ultérieur. Cochez "Add Python 3.6 to PATH" et cliquez sur "Install Now".
3. Ouvrez un terminal avec les privilèges administrateur (cherchez "cmd" dans le Menu Démarrer > clic droit dessus > "Exécuter en tant qu'administrateur")
4. Entrez `pip install requests Pillow matplotlib`
5. Entrez `cd %HOMEDRIVE%%HOMEPATH%`
6. Entrez `git clone https://github.com/Zedd7/ZList.git`
7. Entrez `cd ZList/src`

#### Manipulation des scripts

Vous êtes maintenant libre de jouer avec les différents scripts Python. Pour ce faire, entrez "python <nom_de_script.py>" et suivez les instructions.
Veuillez notez que chaque script a sa propre fonction et peut dépendre du résultat d'un autre :

- player_identifier.py : Enregistre les ids de compte des joueurs de la ZList dans un fichier CSV.
- player_lister.py : Enregistre les ids de compte de joueurs aléatoires du cluster dans un fichier CSV.
- player_categorizer.py : Enregistre les ids de compte des joueurs de la ZList selon la catégorie qui leur est assignée dans un fichier CSV.
- player_profiler.py : Affiche des graphiques personnalisés des statistiques des joueurs.

Cela pris en considération, ils devraient être exécutés dans l'ordre suivant : player_identifier.py, player_lister (facultatif), player_categorizer, player_profiler.

Par défaut, chaque script se connecte à l'API de Wargaming en utilisant l'id d'application "demo" qui est accessible à tous mais est limitée en nombre de requêtes. Ainsi, les résultats des différents scripts peuvent être tronqués. Si vous souhaitez effectuer une analyse sur l'entièreté de la ZList, il est nécessaire que vous créiez une application via l'onglet "[My Applications](https://developers.wargaming.net/applications/)" et que vous remplaciez "demo" par l'id de votre nouvelle application dans le fichier de config situé dans "res/config.txt".
