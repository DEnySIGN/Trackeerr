# Publier Trackeerr sans artefacts Actions

Le code Android reste dans **DEnySIGN/Trackeerr-App, privé**. Ce dépôt public contient le site, le guide, les métadonnées de distribution et les Releases. Ne jamais y copier une archive de reprise, une clé de signature, un historique utilisateur ou les sources Android.

## Préparer une version

1. Compiler et tester localement l’APK. Garder `fr.trackeerr.app.cloudv2` et le certificat SHA-256 `f3743f0ac490d9fd17816217d3309d9fb2d439787a748185f148068f410c124f` pour préserver les mises à jour. La clé privée reste hors Git et des fichiers publics.
2. Vérifier l’identifiant, la version, le code croissant, le SDK minimal, le caractère non débogable et la signature dans le fichier final. Calculer son SHA-256 et sa taille. Reporter ces faits vérifiés dans `site/distribution.json`.
3. Créer une Release brouillon `vX.Y.Z` dans DEnySIGN/Trackeerr. Joindre exactement un APK nommé `trackeerr-X.Y.Z.apk`, son `SHA256SUMS.txt` et les métadonnées `trackeerr-release.json`. Vérifier l’actif téléchargé avant publication. L’archive de sources GitHub contient uniquement ce site, pas le code Android.
4. Publier la Release avec les changements et instructions. Conserver l’APK d’origine privé et les versions précédentes.
5. Contrôler puis construire les fichiers publics :

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/build_site.py --pages
```

Le constructeur utilise la CLI GitHub pour lire seulement les métadonnées du dépôt public. L’APK publié, sa taille et son empreinte doivent correspondre à la distribution préparée. Aucune version n’est proposée à l’application si sa Release manque, est une préversion, ou contient un binaire différent.

## GitHub Pages

L’environnement de publication doit autoriser `api.github.com` pour les métadonnées et **`uploads.github.com`** pour joindre les fichiers de Release. L’accès à `github.com`, `release-assets.githubusercontent.com` et `denysign.github.io` permet ensuite de contrôler les téléchargements et le site. Un refus `CONNECT 403` avant TLS indique un domaine bloqué par le réseau de l’environnement ; il faut faire ajouter le domaine manquant dans ses paramètres, sans contourner le proxy ni retirer les autres autorisations.

Si l’API du dépôt fonctionne mais que l’envoi sur `uploads.github.com` renvoie `401 Bad credentials`, l’authentification d’envoi n’est pas utilisable. Le propriétaire peut joindre les trois fichiers publics au brouillon depuis son navigateur, puis conserver le brouillon pour vérification de l’APK avant publication. Autre possibilité : un accès de publication dédié configuré dans les paramètres sécurisés de l’environnement. Ne jamais copier de jeton dans le chat, les commandes affichées ou Git.

Le dossier généré `docs/` est versionné dans `main`. Il contient uniquement les fichiers autorisés par `PUBLIC_FILES`, `release.json` et `update.json`. Commiter les sources du site et le résultat, puis pousser normalement. Dans Settings → Pages : **Deploy from a branch**, branche **main**, dossier **/docs**.

Si l’intégration GitHub reçoit `Resource not accessible by integration` pour ce réglage, le propriétaire doit l’enregistrer dans les paramètres du dépôt. Les droits de pousser des fichiers ne donnent pas nécessairement les droits d’administration Pages ou d’activation du signalement privé de sécurité.

Le workflow Pages qui chargeait un artefact Actions a été retiré. La compilation Android, la préparation du site et les APK ne consomment plus de stockage d’artefacts ou de caches Actions. GitHub assure le déploiement Pages de branche ; le projet ne crée pas d’artefact de workflow à conserver. Une nouvelle Release ne reconstruit plus automatiquement le site : relancer la commande locale et pousser `docs/` fait partie de chaque publication.

## Vérifier après publication

- Le site affiche la bonne version, son empreinte et son téléchargement ; guide et confidentialité sont lisibles sur mobile et ordinateur.
- `https://denysign.github.io/Trackeerr/update.json` annonce le même APK, identifiant, code, certificat, taille et SHA-256, sans secret ni adresse privée.
- Le téléchargement public correspond octet pour octet au fichier vérifié. Tester ensuite la mise à jour par-dessus sur téléphone, sans désinstaller.
- Le code Android reste privé ; aucune clé ni donnée réelle n’est publiée.

La vérification automatique est optionnelle et limitée à une tentative par 24 heures à l’ouverture, y compris après échec. Vérifier maintenant contourne ce délai à la demande. Le navigateur télécharge l’APK et Android autorise son installation : pas d’installation silencieuse ni de permission d’installation demandée par Trackeerr.
