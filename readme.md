## Peer-to-Text

### Description du projet

Peer-to-Text sera une application cross-platforme permettant de lier des éditeurs de texte existant, stable et connu  entre eux. Le but étant que le texte qui sera tapé d'un coté sera automatiquement ajouté de l'autre permettant ainsi la *collaboration en temps réelle de plusieurs développeurs de part le monde sans qu'ils aient à changer leur environnement de travail.* Peer-to-Text ne sera qu'une surcouche se présentant sous le forme de plugin pour les éditeurs de texte acutels. Peer-to-Text *ne sera pas* un éditeur de texte en lui-même.

### Implémentation

Chaque plugin sera codé dans le langage utilisé par l'éditeur de texte dans sa gestion des plugins. À savoir:
* JavaScript (Atom)
* Python (Sublime Text)
* C++ (Notepad++)

L'application principale sera d'abord développée en mode console sous Python avant d'être migré vers un langage plus robuste et muni d'une interface graphique.

La communication entre chaque application se fera dans la mesure du possible de manière décentralisé (établissement des connexions, authentification, discussion.) L'inscription, l'hébergement des fichiers et la recherche de nouveau utilisateur passera par nos serveurs.

## Contributions

* Julien CASTIAUX - Chef de projet, développeur back-end
* Emilien DEVOS - ~~Administrateur Système~~
* Norman FELTZ - ~~Développeur back-end~~
* William ZAJAC - Chef de projet, juriste
