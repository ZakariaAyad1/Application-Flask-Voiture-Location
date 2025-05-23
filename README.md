# Application de Gestion d'Agence de Location de Voitures

Ce projet est une application web développée avec Flask (Python) et MongoDB, conçue pour gérer les opérations d'une agence de location de voitures. Elle permet la gestion des voitures, des clients, des réservations, et des comptes utilisateurs avec différents niveaux de privilèges (Administrateur et Manager).

## Fonctionnalités Principales

*   **Gestion Complète des Voitures :**
    *   Ajout, modification, et suppression de véhicules.
    *   Détails : marque, modèle, année, immatriculation, tarif journalier, statut (disponible, louée, en maintenance), image.
    *   Visualisation de la liste des voitures avec leurs statuts.
*   **Gestion des Clients :**
    *   Création, mise à jour et suppression des fiches clients.
    *   Informations : nom, email, téléphone, adresse.
*   **Système de Réservation :**
    *   Création de réservations par les managers pour les clients.
    *   Sélection de la voiture, du client, et des dates de début et de fin.
    *   Calcul automatique du prix total.
    *   Visualisation de toutes les réservations avec filtres possibles (par statut, date, etc.).
*   **Modération des Réservations :**
    *   Les managers peuvent :
        *   **Accepter** une réservation en attente (changeant son statut à "confirmée").
        *   **Refuser** une réservation en attente.
        *   Marquer une réservation comme "**complétée**" une fois la voiture retournée.
        *   (Optionnel) Annuler une réservation confirmée.
*   **Gestion des Utilisateurs et Rôles :**
    *   **Administrateur :**
        *   Gestion des comptes des Managers (CRUD : Create, Read, Update, Delete).
        *   Authentification sécurisée.
    *   **Manager :**
        *   Authentification sécurisée.
        *   Accès à toutes les fonctionnalités de gestion des voitures, clients, et réservations.
*   **Interface Utilisateur :**
    *   Interface web intuitive pour chaque profil utilisateur.
    *   Affichage des messages flash pour les retours d'action (succès, erreur, information).
    *   Navigation claire basée sur le rôle de l'utilisateur connecté.

## Profils Utilisateurs et Permissions

1.  **Administrateur :**
    *   **Authentification :** Obligatoire.
    *   **Permissions :**
        *   Créer de nouveaux comptes Manager.
        *   Modifier les informations des comptes Manager (nom d'utilisateur, mot de passe).
        *   Supprimer des comptes Manager.
        *   Visualiser la liste des Managers.
        *   *(Optionnel : Peut avoir les mêmes droits qu'un Manager pour la gestion des opérations de location).*
2.  **Manager :**
    *   **Authentification :** Obligatoire.
    *   **Permissions (Voitures) :**
        *   Visualiser toutes les voitures de l'agence.
        *   Ajouter de nouvelles voitures au catalogue.
        *   Modifier les détails des voitures existantes.
        *   Supprimer des voitures (avec vérification si des réservations actives/futures existent).
    *   **Permissions (Clients) :**
        *   Visualiser la liste des clients.
        *   Ajouter de nouveaux clients.
        *   Modifier les informations des clients existants.
        *   Supprimer des clients (avec vérification si des réservations actives/futures existent).
    *   **Permissions (Réservations) :**
        *   Visualiser toutes les réservations.
        *   Créer une nouvelle réservation pour un client et une voiture spécifique.
        *   Modifier le statut d'une réservation (accepter, refuser, marquer comme complétée).
        *   Visualiser l'historique des réservations d'un client ou d'une voiture.

## Technologies Utilisées

*   **Langage Backend :** Python 3.x
*   **Framework Web :** Flask
    *   *Templating :* Jinja2
    *   *Routing, gestion des requêtes/réponses, sessions, messages flash.*
*   **Base de Données :** MongoDB (NoSQL, orientée document)
    *   *Driver Python :* PyMongo
*   **Sécurité :**
    *   *Hachage des mots de passe :* `werkzeug.security` (fonctions `generate_password_hash`, `check_password_hash`) ou `bcrypt`.
    *   *Protection CSRF :* (Recommandé d'ajouter via Flask-WTF).
*   **Gestion des Variables d'Environnement :** `python-dotenv` (pour `SECRET_KEY`, `MONGO_URI`, etc.)
*   **Frontend (Styling et Structure) :**
    *   HTML5
    *   CSS3
    *   Bootstrap (version 4 ou 5) pour une mise en page responsive et des composants UI prêts à l'emploi.
*   **Contrôle de Version :** Git

## Structure Détaillée des Données (Collections MongoDB)

1.  **`users`**
    *   `_id`: `ObjectId` (Clé primaire, auto-générée)
    *   `username`: `String` (Nom d'utilisateur unique pour la connexion, **indexé**)
    *   `password_hash`: `String` (Mot de passe haché)
    *   `role`: `String` (Valeurs possibles : "admin", "manager")
    *   `created_at`: `DateTime` (Date de création du compte)
    *   `updated_at`: `DateTime` (Date de dernière modification du compte)

2.  **`cars`**
    *   `_id`: `ObjectId`
    *   `make`: `String` (Ex: "Toyota", "BMW")
    *   `model`: `String` (Ex: "Corolla", "X5")
    *   `year`: `Integer` (Ex: 2022)
    *   `registration_number`: `String` (Plaque d'immatriculation, unique, **indexé**)
    *   `daily_rate`: `Float` (Prix de location par jour, ex: 55.99)
    *   `status`: `String` (Valeurs : "available", "rented", "maintenance")
    *   `image_url`: `String` (Optionnel, lien vers une photo de la voiture)
    *   `description`: `String` (Optionnel, plus de détails sur la voiture)
    *   `features`: `Array` of `String` (Optionnel, ex: ["GPS", "Climatisation", "Bluetooth"])
    *   `created_at`: `DateTime`
    *   `updated_at`: `DateTime`

3.  **`clients`**
    *   `_id`: `ObjectId`
    *   `name`: `String` (Nom complet du client)
    *   `email`: `String` (Adresse email unique, **indexé**)
    *   `phone`: `String` (Numéro de téléphone)
    *   `address`: `String` (Optionnel, adresse postale)
    *   `driving_license_number`: `String` (Optionnel, numéro de permis de conduire)
    *   `date_of_birth`: `DateTime` (Optionnel)
    *   `created_at`: `DateTime`
    *   `updated_at`: `DateTime`

4.  **`reservations`**
    *   `_id`: `ObjectId`
    *   `car_id`: `ObjectId` (Référence à `cars._id`, **indexé**)
    *   `client_id`: `ObjectId` (Référence à `clients._id`, **indexé**)
    *   `manager_id`: `ObjectId` (Référence à `users._id` du manager ayant géré la réservation)
    *   `start_date`: `DateTime` (Date et heure de début de la location)
    *   `end_date`: `DateTime` (Date et heure de fin prévue de la location)
    *   `actual_return_date`: `DateTime` (Optionnel, date et heure de retour effectif)
    *   `total_price`: `Float` (Prix total calculé de la location)
    *   `status`: `String` (Valeurs : "pending", "confirmed", "refused", "completed", "cancelled", "active" (si en cours))
    *   `notes`: `String` (Optionnel, notes additionnelles sur la réservation)
    *   `created_at`: `DateTime` (Date de création de la demande de réservation)
    *   `updated_at`: `DateTime` (Date de la dernière modification du statut ou des détails)

## Installation et Exécution

### Prérequis Techniques
*   Python 3.7+
*   pip (gestionnaire de paquets Python)
*   MongoDB Server (version 4.x ou supérieure recommandée)
*   Git

### Étapes d'Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone <URL_DU_DEPOT>
    cd <NOM_DU_DOSSIER_PROJET>
    ```

2.  **Créer et activer un environnement virtuel :**
    ```bash
    python -m venv venv
    # Windows:
    # venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
    (Assurez-vous que `requirements.txt` contient au minimum : `Flask`, `pymongo`, `python-dotenv`, `bcrypt` ou `werkzeug` pour le hachage)

4.  **Configurer les variables d'environnement :**
    Créez un fichier `.env` à la racine du projet avec le contenu suivant (adaptez les valeurs) :
    ```env
    FLASK_APP=app.py
    FLASK_ENV=development  # (ou production)
    FLASK_DEBUG=1          # (0 en production)
    SECRET_KEY='une_cle_secrete_tres_longue_et_aleatoire_ici'
    MONGO_URI='mongodb://localhost:27017/car_rental_agency_db' # Nom de votre base de données
    ```

5.  **S'assurer que MongoDB est en cours d'exécution.**

6.  **Créer le premier utilisateur Administrateur (si applicable) :**
    Consultez la fonction `create_initial_admin()` dans `app.py`. Si elle est présente et que vous lancez l'application pour la première fois, décommentez son appel dans la section `if __name__ == '__main__':`, exécutez `python app.py`, puis recommentez l'appel.
    *   Identifiants par défaut (exemple) : `admin` / `adminpassword` (À CHANGER IMMÉDIATEMENT APRÈS LA PREMIÈRE CONNEXION).

7.  **Lancer l'application Flask :**
    ```bash
    flask run
    ```
    Ou, si `app.run()` est dans `app.py` :
    ```bash
    python app.py
    ```
    L'application sera généralement accessible à `http://127.0.0.1:5000/`.

## Utilisation

1.  **Accéder à l'application** via votre navigateur web.
2.  **Page de connexion (`/login`) :**
    *   Les Administrateurs et Managers utilisent cette page pour s'authentifier.
3.  **Tableau de Bord Administrateur (`/admin/dashboard`) :**
    *   Accès à la gestion des comptes Manager.
4.  **Tableau de Bord Manager (`/manager/dashboard`) :**
    *   Liens vers la gestion des voitures, des clients et des réservations.
5.  **Sections de Gestion (Manager) :**
    *   `/manager/cars` : Visualiser, ajouter, modifier, supprimer des voitures.
    *   `/manager/clients` : Visualiser, ajouter, modifier, supprimer des clients.
    *   `/manager/reservations` : Visualiser, créer, accepter/refuser des réservations.
6.  **Visualisation des voitures disponibles (`/` ou `/cars/available`) :**
    *   Peut être une page publique ou nécessiter une connexion selon la configuration.

## Pistes d'Amélioration et Fonctionnalités Futures

*   **Validation Avancée :** Implémenter une validation robuste des formulaires (côté client avec JavaScript, côté serveur avec Flask-WTF).
*   **Recherche et Filtrage :** Ajouter des options de recherche et de filtrage puissantes pour les listes (voitures par caractéristiques, réservations par date/client/statut).
*   **Gestion de la Disponibilité :** Logique affinée pour vérifier la disponibilité réelle d'une voiture sur une période donnée (gestion des chevauchements de réservations).
*   **Notifications :** Système de notifications (par email ou in-app) pour les confirmations/refus de réservation, rappels.
*   **Paiements :** Intégration d'une passerelle de paiement (Stripe, PayPal) pour les réservations.
*   **Interface Utilisateur (UI/UX) :** Améliorations esthétiques et ergonomiques, potentiellement avec un framework JS (Vue, React) pour plus d'interactivité.
*   **API RESTful :** Exposer des endpoints API pour une éventuelle application mobile ou des intégrations tierces.
*   **Tests :** Écriture de tests unitaires et d'intégration pour assurer la robustesse du code.
*   **Sécurité Renforcée :** Audits de sécurité réguliers, implémentation de headers de sécurité HTTP, rate limiting.
*   **Reporting et Statistiques :** Tableau de bord avec des indicateurs clés (taux d'occupation, revenus, voitures populaires).
*   **Internationalisation (i18n) et Localisation (l10n) :** Support de plusieurs langues.
*   **Conteneurisation :** Utiliser Docker pour faciliter le déploiement et la portabilité.

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :
1.  Forker le dépôt.
2.  Créer une nouvelle branche (`git checkout -b feature/nom-de-la-feature`).
3.  Effectuer les modifications.
4.  S'assurer que le code est propre et, si possible, testé.
5.  Soumettre une Pull Request avec une description claire des changements.
