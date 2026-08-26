# Aldes Local

Intégration Home Assistant locale pour les pompes à chaleur Aldes pilotées par
[Aldes Bridge](https://github.com/saniho/aldes-bridge).

Le projet a pour objectif de créer des entités Home Assistant directement utilisables
à partir de l’état local de la PAC, sans appeler ni reproduire l’API cloud officielle
Aldes. Cette première version découvre les zones exposées par Aldes Bridge, crée une
entité `climate` par zone et permet de lire puis modifier leur température de consigne.

## Prérequis

[saniho/aldes-bridge](https://github.com/saniho/aldes-bridge) doit être installé,
connecté à la PAC et accessible depuis Home Assistant. Son API locale doit être activée
en définissant la variable d’environnement `ALDES_CLOUD2CLOUD_TOKEN`.

Cette intégration suppose que la version installée d’Aldes Bridge fournit :

- `GET /api/local/device` ;
- `POST /api/local/zones/{zone}/setpoint` ;
- l’authentification `Authorization: Bearer <token>`.

## Installation avec HACS

Tant que le projet n’est pas présent dans le catalogue HACS par défaut :

1. ouvrir HACS dans Home Assistant ;
2. ajouter `https://github.com/Jv1i3nn/hacs-aldes-local` comme dépôt personnalisé de
   catégorie **Integration** ;
3. installer **Aldes Local** ;
4. redémarrer Home Assistant ;
5. ajouter l’intégration depuis **Paramètres → Appareils et services**.

Le formulaire demande l’URL d’Aldes Bridge, par exemple `http://192.168.1.20:8080`,
ainsi que la valeur de `ALDES_CLOUD2CLOUD_TOKEN`.

## Fonctionnalités

- découverte des zones depuis l’API locale ;
- température actuelle et consigne pour chaque zone ;
- modification de la consigne par pas de `0,5 °C` ;
- disponibilité liée à la connexion réelle de la PAC ;
- aucune communication avec le cloud Aldes.

## État du projet

Le projet est en développement initial. Les commandes de modes air, eau chaude et
planning seront ajoutées lorsque leurs endpoints locaux seront disponibles dans Aldes
Bridge.
