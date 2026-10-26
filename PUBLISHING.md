# Première publication

## Dépôts et GitHub Pages

- **DEnySIGN/Trackeerr-App** conserve le code Android et reste privé.
- **DEnySIGN/Trackeerr** contient uniquement ce site et les futures Releases publiques.
- Le site est publié à l’adresse **https://denysign.github.io/Trackeerr/**. Conserver la majuscule dans ce chemin de projet.

Les noms de dépôts GitHub sont insensibles à la casse. Le remote du code Android doit pointer sur `https://github.com/DEnySIGN/Trackeerr-App.git` ; le nom `Trackeerr` désigne maintenant le dépôt public. Ne jamais utiliser ce dernier remote pour pousser le code Android.

Dans Settings → Pages du dépôt public, choisir **GitHub Actions**. Le workflow `pages.yml` construit uniquement les fichiers publics autorisés, puis les déploie. Il se relance lors d’un push sur `main`, d’une modification de Release ou d’un déclenchement manuel. Un premier README existe déjà dans l’historique du dépôt ; le conserver par une fusion normale, sans push forcé.

Les accès GitHub sont fournis par l’intégration de l’environnement. Ne jamais fournir de mot de passe ou de jeton dans le chat.

## Premier APK public — après validation téléphone

- Attendre la validation demandée par le propriétaire. Aucun APK n’est inclus dans le site ou dans cette préparation.
- Préparer l’APK de distribution et sa signature durable, conserver une sauvegarde privée de la clé, et définir le passage depuis les APK de test. Ne pas changer de clé sans prévoir ce passage : Android exige une signature compatible pour une mise à jour directe.
- Dans le **dépôt public**, créer une Release avec un tag tel que `v0.6.3` et joindre exactement un APK validé, par exemple `trackeerr-v0.6.3.apk`. Joindre éventuellement une empreinte SHA-256 et les notes de version. Ne pas marquer une version de test comme stable.
- Publier la Release. Le workflow Pages reconstruit automatiquement le catalogue de téléchargements ; son constructeur lit uniquement les métadonnées et actifs publics. Il ne compile pas l’application et n’accède pas au dépôt Android privé.
- Vérifier le téléchargement dans un navigateur puis l’installation et la mise à jour sur téléphone.

Les archives de code ZIP/TAR automatiquement proposées par GitHub dans ces Releases contiendront uniquement les fichiers du site. Le code Android reste dans son dépôt privé.

## Maintenir la page

Pour une nouvelle version, publier une nouvelle Release et son APK. Le catalogue préfère la première version stable utilisable dans la liste fournie par GitHub ; les préversions sont affichées seulement en l’absence de version stable avec APK. Une Release sans APK ou avec plusieurs APK est ignorée pour éviter un choix ambigu. Le lien vers toutes les versions reste disponible.
