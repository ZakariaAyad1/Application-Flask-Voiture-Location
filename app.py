import os
from datetime import datetime
from functools import wraps
from bson import ObjectId

from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv() # Charge les variables de .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configuration MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client.car_rental_agency # Nom de votre base de données

# Collections
users_collection = db.users
cars_collection = db.cars
clients_collection = db.clients
reservations_collection = db.reservations

# --- Helpers & Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role_name:
                flash(f"Accès non autorisé. Vous devez être {role_name}.", 'danger')
                # On pourrait rediriger vers une page d'erreur 403
                return redirect(url_for('login')) # ou une page de dashboard par défaut
            return f(*args, **kwargs)
        return decorated_function
    return decorator

admin_required = role_required('admin')
manager_required = role_required('manager')

# --- Routes d'Authentification ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Connexion réussie!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

# --- Routes Administrateur ---
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/managers')
@login_required
@admin_required
def manage_managers():
    managers = list(users_collection.find({'role': 'manager'}))
    return render_template('admin/manage_managers.html', managers=managers)

@app.route('/admin/managers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_manager():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users_collection.find_one({'username': username}):
            flash('Ce nom d\'utilisateur existe déjà.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({
                'username': username,
                'password_hash': hashed_password,
                'role': 'manager'
            })
            flash('Manager ajouté avec succès.', 'success')
            return redirect(url_for('manage_managers'))
    return render_template('admin/manager_form.html', action="add")

@app.route('/admin/managers/edit/<manager_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_manager(manager_id):
    manager = users_collection.find_one({'_id': ObjectId(manager_id), 'role': 'manager'})
    if not manager:
        flash('Manager non trouvé.', 'danger')
        return redirect(url_for('manage_managers'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password') # Optionnel

        update_data = {'username': username}
        if password: # Si un nouveau mot de passe est fourni
            update_data['password_hash'] = generate_password_hash(password)
        
        # Vérifier si le nouveau username est déjà pris par un AUTRE utilisateur
        existing_user = users_collection.find_one({'username': username, '_id': {'$ne': ObjectId(manager_id)}})
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé par un autre compte.', 'danger')
        else:
            users_collection.update_one({'_id': ObjectId(manager_id)}, {'$set': update_data})
            flash('Manager mis à jour avec succès.', 'success')
            return redirect(url_for('manage_managers'))
    return render_template('admin/manager_form.html', action="edit", manager=manager)

@app.route('/admin/managers/delete/<manager_id>', methods=['POST']) # Utiliser POST pour la suppression
@login_required
@admin_required
def delete_manager(manager_id):
    result = users_collection.delete_one({'_id': ObjectId(manager_id), 'role': 'manager'})
    if result.deleted_count > 0:
        flash('Manager supprimé avec succès.', 'success')
    else:
        flash('Manager non trouvé ou non supprimé.', 'danger')
    return redirect(url_for('manage_managers'))


# --- Routes Manager ---
@app.route('/manager/dashboard')
@login_required
@manager_required
def manager_dashboard():
    return render_template('manager/dashboard.html')

# --- Gestion des Voitures (Manager) ---
@app.route('/manager/cars')
@login_required
@manager_required
def list_cars():
    cars = list(cars_collection.find())
    return render_template('manager/cars_list.html', cars=cars)

@app.route('/manager/cars/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_car():
    if request.method == 'POST':
        # TODO: Ajouter la validation des données
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        registration_number = request.form['registration_number']
        daily_rate = float(request.form['daily_rate'])
        status = request.form.get('status', 'available') # 'available' par défaut
        image_url = request.form.get('image_url')

        if cars_collection.find_one({'registration_number': registration_number}):
            flash('Une voiture avec ce numéro d\'immatriculation existe déjà.', 'danger')
        else:
            cars_collection.insert_one({
                'make': make, 'model': model, 'year': year,
                'registration_number': registration_number,
                'daily_rate': daily_rate, 'status': status, 'image_url': image_url
            })
            flash('Voiture ajoutée avec succès.', 'success')
            return redirect(url_for('list_cars'))
    return render_template('manager/car_form.html', action="add")

@app.route('/manager/cars/edit/<car_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_car(car_id):
    car = cars_collection.find_one({'_id': ObjectId(car_id)})
    if not car:
        flash('Voiture non trouvée.', 'danger')
        return redirect(url_for('list_cars'))

    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        registration_number = request.form['registration_number']
        daily_rate = float(request.form['daily_rate'])
        status = request.form.get('status', car.get('status')) # Conserver l'ancien si non fourni
        image_url = request.form.get('image_url', car.get('image_url'))
        
        # Vérifier l'unicité de l'immatriculation si elle a changé
        existing_car = cars_collection.find_one({'registration_number': registration_number, '_id': {'$ne': ObjectId(car_id)}})
        if existing_car:
            flash('Une autre voiture avec ce numéro d\'immatriculation existe déjà.', 'danger')
        else:
            cars_collection.update_one({'_id': ObjectId(car_id)}, {'$set': {
                'make': make, 'model': model, 'year': year,
                'registration_number': registration_number,
                'daily_rate': daily_rate, 'status': status, 'image_url': image_url
            }})
            flash('Voiture mise à jour avec succès.', 'success')
            return redirect(url_for('list_cars'))
    return render_template('manager/car_form.html', action="edit", car=car)

@app.route('/manager/cars/delete/<car_id>', methods=['POST'])
@login_required
@manager_required
def delete_car(car_id):
    # TODO: Vérifier si la voiture a des réservations actives avant de supprimer
    result = cars_collection.delete_one({'_id': ObjectId(car_id)})
    if result.deleted_count > 0:
        flash('Voiture supprimée avec succès.', 'success')
    else:
        flash('Voiture non trouvée ou non supprimée.', 'danger')
    return redirect(url_for('list_cars'))

# --- Gestion des Clients (Manager) ---
@app.route('/manager/clients')
@login_required
@manager_required
def list_clients():
    clients = list(clients_collection.find())
    return render_template('manager/clients_list.html', clients=clients)



# ... (edit_client, delete_client similaires à ceux des voitures/managers) ...
@app.route('/manager/clients/add', methods=['GET', 'POST'])
@login_required
@manager_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form.get('address')

        if clients_collection.find_one({'email': email}):
            flash('Un client avec cet email existe déjà.', 'danger')
        else:
            clients_collection.insert_one({
                'name': name, 'email': email, 'phone': phone, 'address': address
            })
            flash('Client ajouté avec succès.', 'success')
            return redirect(url_for('list_clients'))
    return render_template('manager/client_form.html', action="add") # Passer action="add"


@app.route('/manager/clients/edit/<client_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_client(client_id):
    client = clients_collection.find_one({'_id': ObjectId(client_id)})
    if not client:
        flash('Client non trouvé.', 'danger')
        return redirect(url_for('list_clients'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form.get('address')

        # Vérifier si l'email a changé et s'il est déjà utilisé par un AUTRE client
        if client['email'] != email and clients_collection.find_one({'email': email, '_id': {'$ne': ObjectId(client_id)}}):
            flash('Cet email est déjà utilisé par un autre client.', 'danger')
        else:
            clients_collection.update_one(
                {'_id': ObjectId(client_id)},
                {'$set': {'name': name, 'email': email, 'phone': phone, 'address': address}}
            )
            flash('Client mis à jour avec succès.', 'success')
            return redirect(url_for('list_clients'))
            
    return render_template('manager/client_form.html', action="edit", client=client) # Passer action="edit" et l'objet client


# --- Gestion des Réservations (Manager) ---
@app.route('/manager/reservations')
@login_required
@manager_required
def list_reservations():
    # Récupérer les réservations et enrichir avec les noms de voiture et client
    reservations_raw = list(reservations_collection.find().sort('start_date', -1))
    reservations = []
    for res in reservations_raw:
        car = cars_collection.find_one({'_id': res['car_id']})
        client = clients_collection.find_one({'_id': res['client_id']})
        res['car_info'] = f"{car['make']} {car['model']} ({car['registration_number']})" if car else "Voiture Inconnue"
        res['client_name'] = client['name'] if client else "Client Inconnu"
        reservations.append(res)
    return render_template('manager/reservations_list.html', reservations=reservations)

@app.route('/manager/reservations/new', methods=['GET', 'POST'])
@login_required
@manager_required
def new_reservation():
    # Voitures disponibles (on pourrait affiner ce critère)
    available_cars = list(cars_collection.find({'status': 'available'}))
    all_clients = list(clients_collection.find())

    if request.method == 'POST':
        car_id = ObjectId(request.form['car_id'])
        client_id = ObjectId(request.form['client_id'])
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            flash("Format de date invalide. Utilisez YYYY-MM-DD.", "danger")
            return render_template('manager/reservation_form.html', cars=available_cars, clients=all_clients, action="new")

        if end_date <= start_date:
            flash("La date de fin doit être après la date de début.", "danger")
            return render_template('manager/reservation_form.html', cars=available_cars, clients=all_clients, action="new")

        # TODO: Vérifier la disponibilité de la voiture pour les dates demandées (plus complexe)
        # Pour l'instant, on se base sur le statut 'available' de la voiture

        car = cars_collection.find_one({'_id': car_id})
        if not car:
            flash("Voiture sélectionnée non valide.", "danger")
            return render_template('manager/reservation_form.html', cars=available_cars, clients=all_clients, action="new")

        num_days = (end_date - start_date).days + 1 # +1 pour inclure le jour de début et fin
        total_price = num_days * car['daily_rate']

        reservations_collection.insert_one({
            'car_id': car_id,
            'client_id': client_id,
            'manager_id': ObjectId(session['user_id']),
            'start_date': start_date,
            'end_date': end_date,
            'total_price': total_price,
            'status': 'pending' # Statut initial
        })
        flash('Réservation créée avec succès, en attente de confirmation.', 'success')
        return redirect(url_for('list_reservations'))

    return render_template('manager/reservation_form.html', cars=available_cars, clients=all_clients, action="new")

@app.route('/manager/reservations/manage/<reservation_id>/<action>', methods=['POST'])
@login_required
@manager_required
def manage_reservation_status(reservation_id, action):
    reservation = reservations_collection.find_one({'_id': ObjectId(reservation_id)})
    if not reservation:
        flash('Réservation non trouvée.', 'danger')
        return redirect(url_for('list_reservations'))

    new_status = ""
    if action == 'confirm':
        new_status = 'confirmed'
        # Optionnel: Mettre à jour le statut de la voiture à 'rented'
        # cars_collection.update_one({'_id': reservation['car_id']}, {'$set': {'status': 'rented'}})
        flash_msg = 'Réservation confirmée.'
    elif action == 'refuse':
        new_status = 'refused'
        flash_msg = 'Réservation refusée.'
    elif action == 'complete': # Quand la voiture est rendue
        new_status = 'completed'
        # Optionnel: Mettre à jour le statut de la voiture à 'available'
        # cars_collection.update_one({'_id': reservation['car_id']}, {'$set': {'status': 'available'}})
        flash_msg = 'Réservation complétée.'
    else:
        flash('Action non valide.', 'danger')
        return redirect(url_for('list_reservations'))

    if new_status:
        reservations_collection.update_one(
            {'_id': ObjectId(reservation_id)},
            {'$set': {'status': new_status, 'manager_id': ObjectId(session['user_id'])}}
        )
        flash(flash_msg, 'success')
    return redirect(url_for('list_reservations'))


# --- Visualisation des voitures disponibles (Publique ou Manager) ---
@app.route('/') # Page d'accueil, pourrait être la liste des voitures disponibles
@app.route('/cars/available')
# @login_required # Décommentez si seuls les utilisateurs connectés peuvent voir
def view_available_cars():
    # Critère simple de disponibilité. Pourrait être affiné en vérifiant les réservations.
    available_cars = list(cars_collection.find({'status': 'available'}))
    # Ou pour une recherche plus poussée (ignorer 'status' de la voiture, regarder les réservations)
    # today = datetime.now()
    # non_available_car_ids = [
    # r['car_id'] for r in reservations_collection.find({
    # 'status': 'confirmed',
    # 'start_date': {'$lte': today},
    # 'end_date': {'$gte': today}
    # })
    # ]
    # available_cars = list(cars_collection.find({'_id': {'$nin': non_available_car_ids}}))
    return render_template('manager/cars_list.html', cars=available_cars, public_view=True)


# --- Script pour créer le premier admin (si aucun utilisateur n'existe) ---
def create_initial_admin():
    if users_collection.count_documents({}) == 0:
        username = "admin"
        password = "adminpassword" # Changez ceci!
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            "username": username,
            "password_hash": hashed_password,
            "role": "admin"
        })
        print(f"Utilisateur Admin '{username}' créé avec le mot de passe '{password}'. Changez-le dès que possible!")
    else:
        print("Des utilisateurs existent déjà. Aucun admin initial créé.")

if __name__ == '__main__':
    # create_initial_admin() # Décommentez pour créer l'admin au premier lancement
    app.run(debug=True)