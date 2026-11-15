# Trackeerr

**Vos films. Vos séries. À votre rythme.**

Trackeerr est une application Android gratuite qui réunit votre suivi de films, séries et épisodes avec vos propres serveurs **Jellyfin et Seerr**. Aucun compte Trackeerr, aucun contenu ni serveur de streaming fourni.

**[Découvrir et télécharger](https://denysign.github.io/Trackeerr/)** · **[Guide d’utilisation](https://denysign.github.io/Trackeerr/guide.html)** · **[Versions](https://github.com/DEnySIGN/Trackeerr/releases)**

## Votre suivi

- Reprenez vos films et séries commencés, même absents de Jellyfin, avec les positions et l’ordre de dernier visionnage conservés.
- Organisez À venir, À voir, Vu, Favoris et Abandon sans perdre votre historique.
- Modifiez les états depuis les affiches ; suivez les épisodes et les saisons vues, sans inclure les spéciaux dans la complétion globale.
- Recherchez, filtrez et triez ; consultez le casting, les fiches artistes et leur filmographie.
- Comparez vos états, suivez les envois, reprenez après coupure et résolvez les conflits.
- Importez un ancien historique, identifiez les titres restants et gardez des sauvegardes locales.
- Adaptez l’apparence et les textes ; vérifiez les mises à jour manuellement ou une fois par jour à l’ouverture.

## Installer

Android **8.0 et plus**, compte Jellyfin et instance Seerr reliée au même serveur, avec authentification Jellyfin activée. Téléchargez l’unique APK de la dernière Release officielle et confirmez son installation dans Android. Pour une mise à jour, installez **par-dessus sans désinstaller**. Voir le [guide](https://denysign.github.io/Trackeerr/guide.html#installer).

Ce dépôt contient uniquement le site, sa documentation publique, les éléments de marque et des captures natives avec données fictives. **Le code Android reste privé** ; les archives de sources proposées par GitHub ici concernent le site. Les APK sont joints aux Releases, jamais à l’historique Git.

## Données et sécurité

Les profils et historiques restent sur l’appareil ; les échanges utilisent vos services configurés. Les sessions sont chiffrées, le mot de passe n’est pas conservé et les mises à jour ne transmettent aucun identifiant de vos services. Les exports JSON contiennent un historique non chiffré : gardez-les privés.

[Confidentialité](https://denysign.github.io/Trackeerr/confidentialite.html) · [Politique de sécurité](SECURITY.md) · [Signaler un bug](https://github.com/DEnySIGN/Trackeerr/issues). Ne publiez jamais de mot de passe, jeton ou historique personnel dans un ticket.

## Maintenir le site

Python 3.12, et CLI GitHub connectée uniquement pour préparer une publication :

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/build_site.py --offline
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Le site est statique, sans dépendance JavaScript externe, mesure d’audience ni formulaire de connexion. [PUBLISHING.md](PUBLISHING.md) décrit la publication : les fichiers autorisés sont construits localement dans `docs/`, puis déployés par GitHub Pages depuis la branche. Aucun APK, cache Gradle ou artefact de compilation n’est stocké dans GitHub Actions.

Inter : SIL Open Font License, licence dans `site/assets/fonts/OFL.txt`. Icône Jellyfin : Jellyfin contributors, CC BY-SA 4.0, attribution et adaptation dans le guide. Jellyfin, Seerr et TMDB restent des projets indépendants ; TMDB n’approuve ni ne certifie cette application.
