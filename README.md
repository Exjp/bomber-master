# Documentation
Ce jeu est une copie du célèbre jeu 'Bomber-Man'. Cette démo a été produite par Aurelien Esnard. Cette archive a été modifié sous la forme d'un projet en groupe à _l'Université de Bordeaux_, pour la _Licence 2 d'Informatique_, par Arnaud Quatrehomme et Jacques Pourtier (groupe TM6K). Vous pouvez retrouvez l'archive original [ici](https://github.com/orel33/bomber).

## Organisation de l'Archive
+ **images**: contient les textures du jeu
+ **model.py**: contient la définition du model
+ **bomber_client.py**: `main()` du client ( affichage et interaction de l'utilisateur)
+ **bomber_server.py**: `main()` du serveur (gestion de l'instance du jeu)
+ **keyboard.py**: contient la gestion de l'interaction du clavier
+ **view.py**: contient la gestion de l'affichage du jeu
+ **maps**: contient les différentes maps du jeu
+ **bomber.py**: Version initiale du jeu

## Installation
Vous diposez de **bomber_server.py** et **bomber_client.py** pour pouvoir lancer le jeu. Le premier fichier correspond au serveur centralisé. Il n'a pas d'affichage graphique mais maintient l'état du jeu à jour. Le second fichier correspond à l'affichage graphique et l'interaction avec l'utilisateur. Chaque client dispose d'une copie du client mise à jour par le serveur.
Le jeu utilise la librairie **pygame**, donc si ce module n'est pas trouvé, vous pouvez l'installer par cette commande :
```
pip3 install pygame
```

### Version initiale
Pour pouvoir lancer le jeu à un seul joueur, il vous suffit de taper cette commande :
```
./bomber.py
```

### Version multi-joueurs
Pour pouvoir lancer une session multi-joueurs du jeu, vous devez d'abord instancier le jeu par cette commande :
```
./bomber_server.py 7777 maps/maps0
```
Vous pouvez choisir un autre port existant et libre que `7777` et pour pouvoir jouer sur une autres map que celle-ci, vous pouvez remplacer `maps/maps0` par `maps/maps1` ou `maps/maps2`.

Ensuite, en fonction du serveur lancé juste avant, les joueurs doivent se connecter au serveur, pour pouvoir lancer le jeu, avec cette commande :
```
./bomber_server.py localhost 7777 player1
```
`localhost` ne doit jamais changer, `7777` et le port du serveur où le jeu se déroule et `player1` correspond au pseudonyme que vous pouvez changez.
