# Application-Flask-Voiture-Location

# Application de Gestion d'Agence de Location de Voitures

Ce projet est une application web développée avec Flask (Python) et MongoDB, conçue pour gérer les opérations d'une agence de location de voitures. Elle permet la gestion des voitures, des clients, des réservations, et des comptes utilisateurs avec différents niveaux de privilèges (Administrateur et Manager).

## Table des Matières

1.  [Fonctionnalités](#fonctionnalités)
2.  [Profils Utilisateurs](#profils-utilisateurs)
3.  [Technologies Utilisées](#technologies-utilisées)
4.  [Prérequis](#prérequis)
5.  [Installation et Lancement](#installation-et-lancement)
    *   [Clonage du Dépôt](#clonage-du-dépôt)
    *   [Configuration de l'Environnement](#configuration-de-lenvironnement)
    *   [Variables d'Environnement](#variables-denvironnement)
    *   [Base de Données MongoDB](#base-de-données-mongodb)
    *   [Installation des Dépendances](#installation-des-dépendances)
    *   [Création du Premier Administrateur](#création-du-premier-administrateur)
    *   [Lancement de l'Application](#lancement-de-lapplication)
6.  [Structure du Projet](#structure-du-projet)
7.  [Modèles de Données (Collections MongoDB)](#modèles-de-données-collections-mongodb)
8.  [Routes Principales (Endpoints)](#routes-principales-endpoints)
9.  [Contributions](#contributions)
10. [Pistes d'Amélioration Futures](#pistes-damélioration-futures)
11. [Licence](#licence)

---

## Fonctionnalités

L'application offre les services suivants :

*   **Visualisation des voitures disponibles** : Interface publique ou pour utilisateurs connectés.
*   **Réservation des voitures** : Effectuée par les Managers pour les clients.
*   **Visualisation des réservations** : Liste des réservations avec leur statut.
*   **Gestion des réservations** : Les Managers peuvent accepter ou refuser les réservations en attente, et marquer les réservations comme complétées.
*   **Gestion des voitures** : Les Managers peuvent ajouter, modifier, et supprimer des voitures du catalogue.
*   **Gestion des clients** : Les Managers peuvent ajouter, modifier, et supprimer des fiches clients.
*   **Gestion des comptes Managers** : Les Administrateurs peuvent ajouter, modifier, et supprimer les comptes des Managers.
*   **Authentification sécurisée** pour les Administrateurs et les Managers.

---

## Profils Utilisateurs

L'application gère deux types de profils utilisateurs :

1.  **Manager** :
    *   Doit s'authentifier.
    *   Visualise toutes les voitures.
    *   Ajoute, modifie ou supprime des voitures.
    *   Gère les clients.
    *   Crée des réservations pour les clients.
    *   Accepte ou refuse les réservations.
2.  **Administrateur** :
    *   Doit s'authentifier.
    *   A tous les privilèges d'un Manager (potentiellement, selon implémentation, ou focus uniquement sur la gestion des comptes).
    *   Gère les comptes des Managers (ajout, modification, suppression).

---

## Technologies Utilisées

*   **Backend** : Python 3.x
    *   **Framework Web** : Flask
    *   **Base de Données** : MongoDB
    *   **Driver MongoDB** : PyMongo
    *   **Gestion des mots de passe** : bcrypt (via `werkzeug.security` ou `flask-bcrypt`)
    *   **Variables d'environnement** : python-dotenv
*   **Frontend** :
    *   HTML5
    *   CSS3 (Bootstrap 4/5 pour le style de base)
    *   JavaScript (minimal, pour des interactions utilisateur si besoin)
    *   **Moteur de template** : Jinja2 (intégré à Flask)

---

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants sur votre système :

*   Python (version 3.7 ou supérieure recommandée)
*   pip (gestionnaire de paquets Python)
*   MongoDB (serveur en cours d'exécution)
*   Git (pour cloner le dépôt)

---

## Installation et Lancement

Suivez ces étapes pour mettre en place et lancer l'application localement.

### 1. Clonage du Dépôt

```bash
git clone <URL_DU_DEPOT_GIT>
cd nom-du-dossier-du-projet
