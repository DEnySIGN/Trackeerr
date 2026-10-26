# Trackeerr

Site public de présentation et distribution gratuite de l’application Android **Trackeerr**, connectée à vos propres serveurs Jellyfin et Seerr.

Site prévu : **https://denysign.github.io/trackeerr/**.

Ce dépôt contient uniquement le site, des éléments de marque et des captures de démonstration. Le code Android n’est pas publié ici. Les APK validés seront joints aux [Releases](https://github.com/DEnySIGN/trackeerr/releases), jamais ajoutés à l’historique Git du site.

## Prévisualiser

Aucune dépendance à installer : Python 3.12 et un navigateur suffisent.

```sh
python3 scripts/build_site.py --offline
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Ouvrir http://127.0.0.1:4173/. Le mode local affiche volontairement la préparation de la première version. Les chemins relatifs fonctionnent aussi sous `/trackeerr/` dans GitHub Pages.

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

## Publication

Le workflow `pages.yml` publie uniquement les fichiers explicitement autorisés par `scripts/build_site.py`. Dans Settings → Pages, choisir **GitHub Actions**. Un push sur `main` ou une modification des Releases reconstruit le site. Le constructeur refuse de créer le catalogue de téléchargements depuis un dépôt privé.

Aucun APK n’est proposé avant la validation sur téléphone. Lorsqu’une Release publique contient exactement un APK, le site affiche automatiquement son téléchargement, son numéro de version et son empreinte SHA-256 si GitHub la fournit. Une version stable est préférée à une préversion ; une préversion seule est explicitement identifiée. Sans Release utilisable, le site conserve son message de préparation.

Voir [PUBLISHING.md](PUBLISHING.md) pour l’ordre de création des dépôts et la première livraison.

## Ressources

Identité graphique Trackeerr et captures natives de démonstration. Police Inter distribuée sous SIL Open Font License ; licence incluse dans `site/assets/fonts/OFL.txt` (@fontsource-variable/inter 5.3.0). Les identifiants de connexion et adresses des serveurs de développement ne figurent pas dans ce dépôt.
