# Première publication

## Ordre des opérations GitHub

Les noms de dépôts GitHub sont insensibles à la casse. Le dépôt Android actuellement nommé `Trackeerr` doit donc être renommé avant de pouvoir créer le dépôt public `trackeerr`.

1. Renommer le dépôt Android existant en **trackeerr-app**, en conservant sa visibilité **privée**.
2. Mettre immédiatement à jour son remote Git HTTPS pour qu’il pointe sur `https://github.com/DEnySIGN/trackeerr-app.git`. Vérifier à nouveau la visibilité privée et l’identité du dépôt. Le répertoire local Android peut conserver son nom ; ne pas copier ses fichiers dans ce dépôt du site.
3. Créer le nouveau dépôt **DEnySIGN/trackeerr**, visibilité **publique**. Vérifier qu’il s’agit bien d’un nouveau dépôt distinct, pas d’un changement de visibilité du dépôt Android.
4. Pousser uniquement le présent dépôt du site vers le nouveau remote public. La réutilisation de l’ancien nom rend son ancienne redirection inopérante : ne plus utiliser cet ancien remote pour le code Android.
5. Dans Settings → Pages du dépôt public, choisir **GitHub Actions**. Vérifier le workflow et l’adresse `https://denysign.github.io/trackeerr/`.

Ces opérations nécessitent l’accès à l’API GitHub et les droits de gestion correspondants. En l’absence de ces droits, effectuer le renommage et la création dans l’interface GitHub, puis autoriser le nouveau dépôt pour l’intégration utilisée par l’environnement. Ne jamais fournir un mot de passe ou un jeton dans le chat.

## Premier APK public — après validation téléphone

- Attendre la validation demandée par le propriétaire. Aucun APK n’est inclus dans le site ou dans cette préparation.
- Préparer l’APK de distribution et sa signature durable, conserver une sauvegarde privée de la clé, et définir le passage depuis les APK de test. Ne pas changer de clé sans prévoir ce passage : Android exige une signature compatible pour une mise à jour directe.
- Dans le **dépôt public**, créer une Release avec un tag tel que `v0.6.3` et joindre exactement un APK validé, par exemple `trackeerr-v0.6.3.apk`. Joindre éventuellement une empreinte SHA-256 et les notes de version. Ne pas marquer une version de test comme stable.
- Publier la Release. Le workflow Pages reconstruit automatiquement le catalogue de téléchargements ; son constructeur lit uniquement les métadonnées et actifs publics. Il ne compile pas l’application et n’accède pas au dépôt Android privé.
- Vérifier le téléchargement dans un navigateur puis l’installation et la mise à jour sur téléphone.

Les archives de code ZIP/TAR automatiquement proposées par GitHub dans ces Releases contiendront uniquement les fichiers du site. Le code Android reste dans son dépôt privé.

## Maintenir la page

Pour une nouvelle version, publier une nouvelle Release et son APK. Le catalogue préfère la première version stable utilisable dans la liste fournie par GitHub ; les préversions sont affichées seulement en l’absence de version stable avec APK. Une Release sans APK ou avec plusieurs APK est ignorée pour éviter un choix ambigu. Le lien vers toutes les versions reste disponible.
