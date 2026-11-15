# Signaler une vulnérabilité

Pour une vulnérabilité de l’application Android ou du site, utilisez le bouton **Report a vulnerability** de l’onglet Security lorsqu’il est disponible. Sinon, ouvrez un ticket demandant un canal de contact privé, sans décrire la faille ni joindre de fichier sensible. Le signalement privé nécessite une activation par l’administrateur du dépôt ; l’intégration de publication n’a pas le droit de modifier ce réglage. Évitez tout détail d’exploitation dans un ticket public, ainsi que les mots de passe, jetons, cookies, adresses privées ou historiques personnels.

Précisez la version de Trackeerr, la version Android et les étapes de reproduction, avec des données fictives si possible. Les bugs ordinaires et demandes d’évolution restent dans les Issues.

La dernière version publique est la version maintenue. Les corrections sont distribuées dans les Releases officielles ; une ancienne installation peut vérifier manuellement la disponibilité d’une mise à jour dans Profil à partir de la 0.6.54.

## Distribution et données

- APK officiel : [Releases DEnySIGN/Trackeerr](https://github.com/DEnySIGN/Trackeerr/releases). Android doit accepter la signature pour mettre à jour une installation existante. Ne désinstallez pas pour contourner un refus de signature.
- Les contrôles de mise à jour utilisent uniquement un catalogue HTTPS public et des liens de Release officiels. Ils n’installent rien et ne reçoivent aucun identifiant Jellyfin/Seerr.
- Les sessions sont chiffrées avec Android Keystore. Le mot de passe de connexion n’est pas conservé ; les sauvegardes Android automatiques sont désactivées.
- HTTP est un choix explicite pour des installations locales ; il ne chiffre pas les échanges. Privilégiez HTTPS, particulièrement hors de votre réseau de confiance.
- Les exports JSON sont dépourvus de secrets de connexion mais contiennent un historique personnel non chiffré. Conservez-les dans un emplacement de confiance.

La revue du 15 novembre 2026 n’a relevé aucune alerte connue dans les 127 composants Maven de l’application interrogés dans GitHub Advisory Database. Cette vérification datée et les tests automatisés ne constituent ni un audit indépendant ni une garantie d’absence de vulnérabilité.
