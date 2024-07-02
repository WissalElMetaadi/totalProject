from flask import Flask, render_template,Response,send_file
from flask import request, redirect, url_for, render_template, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
from bson.objectid import ObjectId
import csv
import os ,cv2 ,io
import numpy as np
import threading
from flask import jsonify
from werkzeug.utils import secure_filename
import chardet
import mysql.connector
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy.exc import IntegrityError
from mysql.connector.errors import IntegrityError as MySQLIntegrityError
from script1 import run_yolo
from yolo_processor import process_frame
from flask_socketio import SocketIO, emit
import time
from flask import url_for 
import webbrowser #//Pour ouvrir une URL dans le navigateur par défaut.
import threading # Pour exécuter l'ouverture du navigateur après le démarrage du serveur Flask.
from datetime import datetime
import pytz
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_pymongo import PyMongo
from flask import Flask


app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici'  # Définissez votre clé secrète ici
current_frame_data = None  # Variable pour stocker les données du cadre actuel
is_processing = False  # Indicateur pour contrôler le traitement






#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:JEONjungkook123@localhost/totalbd'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/station_total'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 100 MB limit
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv'}
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
csv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.csv')


mongo = PyMongo(app)



login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, name, worker_type,station_id):
        self.id = user_id
        self.name = name
        self.worker_type = worker_type
        self.station_id = station_id




@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_id=str(user_data['_id']), name=user_data['name'], worker_type=user_data['worker_type'], station_id=user_data['station_id'])
    except Exception as e:
        logging.error(f"Error loading user: {e}")
    return None

def load_csv():
    data = {}
    if os.path.isfile(csv_file_path):
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data[row['track_id']] = row
    return data

def save_csv(data):
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['track_id', 'class', 'license_plate_text', 'score LP', "date d'entrée", 'date de sortie', 'wait_time', 'pompes_info']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data.values():
            writer.writerow(row)

def update_csv(new_data):
    data = load_csv()
    for key, value in new_data.items():
        row = {
            'track_id': str(key),  # Assurez-vous que les clés sont des chaînes pour correspondre aux clés du CSV
            'class': value.get('class', 'N/A'),
            'license_plate_text': value.get('license_plate_text', 'N/A'),
            'score LP': value.get('score LP', 'N/A'),
            "date d'entrée": value.get("date d'entrée", 'N/A'),
            'date de sortie': value.get('date de sortie', 'N/A'),
            'wait_time': value.get('wait_time', 'N/A'),
            'pompes_info': value.get('pompes_info', 'N/A')
        }
        data[str(key)] = row
    save_csv(data)




@app.route('/start_processing', methods=['POST'])
def start_processing():
    global is_processing
    is_processing = True
    # Réinitialiser le fichier CSV à chaque démarrage du traitement
    open(csv_file_path, 'w').close()  # Crée un fichier vide
    return jsonify({'message': 'Processing started'})

@app.route('/stop_processing', methods=['POST'])
def stop_processing():
    global is_processing
    is_processing = False
    return jsonify({'message': 'Processing stopped'})
@app.route('/get_recent_users', methods=['GET'])
def get_recent_users():
    try:
        logging.info("Fetching recent users.")
        since_timestamp = request.args.get('since')
        query = {}
        if since_timestamp:
            logging.debug(f"Filtering users added since {since_timestamp}")
            since_time = datetime.fromtimestamp(float(since_timestamp), pytz.timezone('Africa/Tunis'))
            query['created_at'] = {"$gt": since_time}
        
        recent_users = mongo.db.users.find(query)
        
        users_data = []
        for user in recent_users:
            birthdate = user.get('birthdate')
            created_at = user.get('created_at')
            logging.debug(f"Processing user: {user['name']} with birthdate: {birthdate} and created_at: {created_at}")
            if isinstance(birthdate, str):
                try:
                    birthdate = datetime.strptime(birthdate, '%Y-%m-%d') if birthdate else None
                except ValueError as e:
                    logging.error(f"Error parsing birthdate for user {user['name']}: {e}")
                    birthdate = None
            if isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, '%Y-%m-%d') if created_at else None
                except ValueError as e:
                    logging.error(f"Error parsing created_at for user {user['name']}: {e}")
                    created_at = None

            # Retrieve station name
            station = mongo.db.stations.find_one({'_id': user['station_id']})
            station_name = station['name'] if station else 'Unknown'
            
            user_data = {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'gender': user.get('gender'),
                'worker_type': user.get('worker_type'),
                'birthdate': birthdate.strftime('%Y-%m-%d') if birthdate else None,
                'station_id': str(user.get('station_id')),
                'station_name': station_name,
                'cin': user.get('cin'),
                'created_at': created_at.timestamp() if created_at else None
            }
            users_data.append(user_data)

        logging.info(f"Number of recent users found: {len(users_data)}")
        return jsonify(users_data)
    except Exception as e:
        logging.error(f"Error fetching recent users: {e}")
        return jsonify({'error': 'Failed to fetch recent users.'}), 500



@app.route('/add_governorate', methods=['POST'])
def add_governorate():
    try:
        data = request.get_json()
        new_governorate = {
            "name": data['name']
        }
        mongo.db.governorates.insert_one(new_governorate)
        return jsonify({'message': 'Governorate added successfully!'}), 201
    except Exception as e:
        logging.error(f'Error adding governorate: {e}')
        return jsonify({'error': str(e)}), 500



@app.route('/add_user1', methods=['POST'])
def add_user1():
    try:
        user_data = request.form
        logging.debug(f'Received data: {user_data}')
        station_name = user_data.get('station_name')

        # Log the received station_name
        app.logger.info(f"Received station_name: {station_name}")

        # Trouver l'ObjectId de la station par son nom
        station = mongo.db.stations.find_one({'name': station_name})
        if not station:
            app.logger.error(f"Station not found for name: {station_name}")
            return jsonify({'error': 'Station not found'}), 404

        # Hacher le mot de passe et créer le document utilisateur
        password_hash = generate_password_hash(user_data['password'])
        
        # Ajouter la colonne created_at avec le fuseau horaire Africa/Tunis
        tunisia_tz = pytz.timezone('Africa/Tunis')
        created_at = datetime.now(tunisia_tz)
        
        new_user = {
            'name': user_data['name'],
            'email': user_data['email'],
            'gender': user_data['gender'],
            'worker_type': user_data['worker_type'],
            'birthdate': user_data['birthdate'],
            'station_id': station['_id'],  # Utiliser l'ObjectId de la station
            'cin': user_data['cin'],
            'password_hash': password_hash,
            'profile_picture': user_data.get('profile_picture', 'default.jpg'),
            'created_at': created_at  # Ajouter le champ created_at
        }
        mongo.db.users.insert_one(new_user)
        app.logger.info("User added successfully")
        return jsonify({'message': 'User added successfully!'}), 201

    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_users1', methods=['GET'])
def get_users1():
    try:
        users = mongo.db.users.find()
        user_list = []
        for user in users:
            user_data = {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'gender': user['gender'],
                'worker_type': user['worker_type'],
                'birthdate': user['birthdate'],
                'station_id': str(user['station_id']) if user.get('station_id') else None,  # Handle ObjectId
                'cin': user['cin'],
                'profile_picture': user['profile_picture']
            }
            user_list.append(user_data)
        return jsonify(user_list)
    except Exception as e:
        logging.error(f'Error fetching users1: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/add_station', methods=['POST'])
def add_station():
    try:
        data = request.json
        # Assurez-vous que le nom de la station et le nom du gouvernorat sont fournis
        if 'name' not in data or 'governorate_name' not in data:
            return jsonify({'error': 'Missing station name or governorate name'}), 400

        # Trouver l'ObjectId correspondant au nom du gouvernorat
        governorate = mongo.db.governorates.find_one({'name': data['governorate_name']})
        if not governorate:
            return jsonify({'error': 'Governorate not found'}), 404

        # Création de la station avec l'ObjectId du gouvernorat
        new_station = {
            'name': data['name'],
            'governorate_id': governorate['_id']  # Utilisation de l'ObjectId du gouvernorat trouvé
        }
        mongo.db.stations.insert_one(new_station)
        return jsonify({'message': 'Station added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
from bson.objectid import ObjectId

@app.route('/delete_user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'message': 'User deleted successfully!'}), 200
    except Exception as e:
        logging.error(f'Error deleting user: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/delete_governorate/<string:id>', methods=['DELETE'])
def delete_governorate(id):
    try:
        result = mongo.db.governorates.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Governorate not found'}), 404
        return jsonify({'message': 'Governorate deleted successfully!'}), 200
    except Exception as e:
        logging.error(f'Error deleting governorate: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/delete_station/<string:id>', methods=['DELETE'])
def delete_station(id):
    try:
        result = mongo.db.stations.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Station not found'}), 404
        return jsonify({'message': 'Station deleted successfully!'}), 200
    except Exception as e:
        logging.error(f'Error deleting station: {e}')
        return jsonify({'error': str(e)}), 500



@app.route('/update_governorate/<string:id>', methods=['PUT'])
def update_governorate(id):
    try:
        data = request.get_json()

        governorate = mongo.db.governorates.find_one({"_id": ObjectId(id)})
        if governorate:
            mongo.db.governorates.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"name": data['name']}}
            )
            return jsonify({"message": "Governorate updated successfully!"}), 200
        else:
            return jsonify({"error": "Governorate not found!"}), 404
    except Exception as e:
        logging.error(f"Error updating governorate: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/update_station/<string:id>', methods=['PUT'])
def update_station(id):
    try:
        data = request.get_json()
        station = mongo.db.stations.find_one({"_id": ObjectId(id)})
        if not station:
            return jsonify({"error": "Station not found!"}), 404

        # Recherche de l'ObjectId du gouvernorat par son nom
        governorate = mongo.db.governorates.find_one({"name": data['governorate_name']})
        if not governorate:
            return jsonify({"error": "Governorate not found"}), 404

        # Mise à jour de la station avec le nouvel ObjectId du gouvernorat
        mongo.db.stations.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": data['name'],
                "governorate_id": governorate['_id']
            }}
        )
        return jsonify({"message": "Station updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_user/<string:id>', methods=['PUT'])
def update_user(id):
    try:
        data = request.get_json()
        user = mongo.db.users.find_one({"_id": ObjectId(id)})
        if not user:
            return jsonify({"error": "User not found!"}), 404

        # Trouver l'ObjectId de la station par son nom
        station = mongo.db.stations.find_one({'name': data['station_name']})
        if not station:
            return jsonify({'error': 'Station not found'}), 404

        # Mise à jour de l'utilisateur avec le nouvel ObjectId de la station
        mongo.db.users.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": data['name'],
                "email": data['email'],
                "gender": data['gender'],
                "worker_type": data['worker_type'],
                "birthdate": data['birthdate'],
                "station_id": station['_id'],
                "cin": data['cin']
            }}
        )
        return jsonify({"message": "User updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/get_governorates', methods=['GET'])
def get_governorates():
    try:
        governorates = mongo.db.governorates.find()
        governorate_list = [{'id': str(gov['_id']), 'name': gov['name']} for gov in governorates]
        return jsonify(governorate_list)
    except Exception as e:
        logging.error(f'Error fetching governorates: {e}')
        return jsonify({'error': str(e)}), 500
  


@app.route('/get_stations', methods=['GET'])
def get_stations():
    try:
        stations = mongo.db.stations.find()
        station_list = []
        for station in stations:
            governorate = mongo.db.governorates.find_one({"_id": station['governorate_id']})
            station_data = {
                'id': str(station['_id']),
                'name': station['name'],
                'governorate': {
                    'id': str(governorate['_id']),
                    'name': governorate['name']
                }
            }
            station_list.append(station_data)
        return jsonify(station_list)
    except Exception as e:
        logging.error(f'Error fetching stations: {e}')
        return jsonify({'error': str(e)}), 500






@app.route('/test')
def test():
    vehicles_collection = mongo.db.sentiment_data
    pipeline = [
        {"$group": {"_id": "$stars", "count": {"$sum": 1}}}
    ]
    result = list(vehicles_collection.aggregate(pipeline))
    sentiment_counts = {doc["_id"]: doc["count"] for doc in result}
    return render_template('test.html', sentiment_counts=sentiment_counts)

@app.route('/admin/promotions', methods=['GET', 'POST'])
@login_required
def manage_promotions():
    if request.method == 'POST':
        data = request.get_json()
        if data and 'promo_text' in data:
            promo_text = data['promo_text']
            promo_entry = {
                'text': promo_text,
                'timestamp': datetime.now()
            }
            mongo.db.promotions.insert_one(promo_entry)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

    promotions = list(mongo.db.promotions.find())
    return render_template('admin_dashboard.html', promotions=promotions)
@app.route('/latest_promotion', methods=['GET'])
def latest_promotion():
    promotion = mongo.db.promotions.find().sort('timestamp', -1).limit(1)
    promo_list = list(promotion)  # Convertir le curseur en liste
    if len(promo_list) > 0:
        promo = promo_list[0]
        return jsonify({
            'title': promo['title'],
            'text': promo['text'],
            'timestamp': promo['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({
            'title': 'Pas de promotions disponibles',
            'text': '',
            'timestamp': ''
        })


@app.route('/admin/add_promotion', methods=['GET', 'POST'])
@login_required
def add_promotion():
    if request.method == 'POST':
        promo_title = request.form['promo_title']
        promo_text = request.form['promo_text']
        if not promo_title or not promo_text:
            return jsonify({'success': False, 'message': 'Le titre et le texte de la promotion ne peuvent pas être vides.'}), 400

        promo_entry = {
            'title': promo_title,
            'text': promo_text,
            'timestamp': datetime.now()
        }
        mongo.db.promotions.insert_one(promo_entry)
        return jsonify({'success': True})
    
    promotions = list(mongo.db.promotions.find().sort('timestamp', -1))
    return render_template('add_promotion.html', promotions=promotions)

@app.route('/promotions', methods=['GET'])
def get_promotions():
    promotions = list(mongo.db.promotions.find().sort('timestamp', -1))
    return jsonify([{
        'title': promo['title'],
        'text': promo['text'],
        'timestamp': promo['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    } for promo in promotions])

@app.route('/reset_modal_shown')
def reset_modal_shown():
    session.pop('modal_shown', None)  # Supprime la variable de session
    return 'Session reset successful'


@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    data = request.get_json()
    feedback_text = data['feedback']
    user_id = current_user.id
    feedback_entry = {
        'user_id': ObjectId(user_id),
        'text': feedback_text,
        'timestamp': datetime.now()
    }
    mongo.db.sentiment_data.insert_one(feedback_entry)
    session['success'] = True  # Ajoutez ceci pour définir 'success' dans la session
    return jsonify({'success': True})


@app.route('/interface_user', methods=['GET'])
@login_required
def interface_user():
    if current_user.worker_type != 'Simple User':
        return redirect(url_for('dashboard'))

    user_data = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})

    if user_data and 'station_id' in user_data:
        station = mongo.db.stations.find_one({"_id": ObjectId(user_data['station_id'])})
        user_data['station_name'] = station['name'] if station else 'Unknown'

    return render_template('interface_user.html', user=user_data)



@app.route('/governorates')
def governorates():
    return render_template('governorates.html')
@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/PowerBiDash')
def PowerBiDash():
    return render_template('PowerBiDash.html')



@app.route('/ajoutUser')
def ajoutUser():
    try:
        gouvernorates = list(mongo.db.governorates.find())
        stations = list(mongo.db.stations.find())

        # Convert ObjectId to string for easier handling in templates
        for gouvernorate in gouvernorates:
            gouvernorate['_id'] = str(gouvernorate['_id'])
        for station in stations:
            station['_id'] = str(station['_id'])

        return render_template('ajoutUser.html', governorates=gouvernorates, stations=stations)
    except Exception as e:
        logging.error(f"Error fetching governorates or stations: {e}")
        return jsonify({'error': str(e)}), 500

    
@app.route('/total_zone')
def total_zone():
    return render_template('total_zone.html')



@app.route('/DragAndDrop')
def DragAndDrop():
    return render_template('DragAndDrop.html')

@app.route('/modele')
def modele():
    return render_template('modele.html')
from flask_cors import CORS
CORS(app)
from flask import Flask, send_from_directory
@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/charts_jour')
def charts_jour():
    return render_template('charts_jour.html')

@app.route('/semaine')
def charts_semaine():
    return render_template('charts_semaine.html')

@app.route('/data_table')
def data_table():
    data = read_excel('Converted_to_Excel.xlsx')
      # Modifiez le chemin relatif ici
    if 'username' not in session:
        #print(data)
        return redirect(url_for('login'))
    return render_template('data_table.html', data=data) 

""" @app.route('/data_table')
def data_table():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Faire une requête pour obtenir tous les véhicules
    data = Vehicule.query.all()
    
    # Convertir les données en format approprié si nécessaire (liste de dictionnaires, par exemple)
    data_dict = [{column.name: getattr(vehicle, column.name) for column in vehicle.__table__.columns} for vehicle in data]
    
    return render_template('data_table.html', data=data_dict) """

@app.route('/maps')
def maps():
    return render_template('maps.html')



@app.route('/admin/users')
def list_users():
    # Vous devriez ajouter une vérification d'authentification ici
    # Pour s'assurer que seuls les admins peuvent accéder à cette page
    users = User.query.all()
    return render_template('users_list.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = mongo.db.users.find_one({"name": username})

        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_id=str(user_data['_id']), name=user_data['name'], worker_type=user_data['worker_type'], station_id=user_data['station_id'])
            login_user(user)
            session['username'] = username
            session['user_id'] = str(user_data['_id'])  # Add the user_id to the session
            session['user_role'] = user.worker_type

            # Redirection basée sur le rôle de l'utilisateur
            if user.worker_type == 'Simple User':
                return redirect(url_for('interface_user'))
            else:
                return redirect(url_for('dashboard'))
        else:
            error_message = 'Nom d\'utilisateur ou mot de passe incorrect.'

    return render_template('login.html', error_message=error_message)


@app.route('/logout')
def logout():
    # Supprime 'username' de la session
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/statics')
def statics():
    
    return render_template(('statics.html'))

@app.route('/dashboard')
@login_required
def dashboard():
    gouvernorates = list(mongo.db.governorates.find())
    stations = list(mongo.db.stations.find())
    if current_user.worker_type == 'Simple User':
        return redirect(url_for('interface_user'))

    if 'username' not in session:
        return redirect(url_for('login'))

    vehicles_collection = mongo.db.vehicules
    if current_user.worker_type == 'global_admin':
        data = list(vehicles_collection.find())  # No station_id filter for global_admin
    else:
        data = list(vehicles_collection.find({"station_id": current_user.station_id}))

    vehicles_collection1 = mongo.db.sentiment_data
    pipeline = [
        {"$group": {"_id": "$stars", "count": {"$sum": 1}}}
    ]
    result = list(vehicles_collection1.aggregate(pipeline))
    sentiment_counts = {doc["_id"]: doc["count"] for doc in result}

    return render_template('dashboard.html', data=data, sentiment_counts=sentiment_counts,governorates=gouvernorates, stations=stations)





def read_excel(file_name):
    # Utilisez un chemin relatif ou configurez correctement le chemin absolu
    file_path = os.path.join(os.getcwd(), file_name)
    df = pd.read_excel(file_path)
    return df.to_dict(orient='records') 

  

from datetime import datetime, timedelta

@app.route('/data_par_heure')
def data_par_heure():
    filter_type = request.args.get('filter_type', 'day')
    start_date_query = request.args.get('start_date')
    end_date_query = request.args.get('end_date') if filter_type == 'week' else start_date_query

    if not start_date_query or not end_date_query:
        return jsonify({'error': 'Missing date parameters'}), 400

    start_date = datetime.strptime(start_date_query, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_query, '%Y-%m-%d') + timedelta(days=1)

    vehicles_collection = mongo.db.vehicules

    if filter_type == 'day':
        pipeline = [
            {"$match": {"date d'entrée": {"$gte": start_date, "$lt": end_date}}},
            {"$group": {"_id": {"$hour": "$date d'entrée"}, "count": {"$sum": 1}}}
        ]
    elif filter_type == 'week':
        pipeline = [
            {"$match": {"date d'entrée": {"$gte": start_date, "$lt": end_date}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date d'entrée"}}, "count": {"$sum": 1}}}
        ]
    else:
        return jsonify({'error': 'Invalid filter type'}), 400

    result = list(vehicles_collection.aggregate(pipeline))
    data = {doc["_id"]: doc["count"] for doc in result}

    return jsonify(data)







@app.route('/avg_wait_time_by_class')
def get_avg_wait_time_by_class():
    filter_type = request.args.get('filter_type', 'day')
    start_date_query = request.args.get('start_date')
    end_date_query = request.args.get('end_date') if filter_type == 'week' else start_date_query

    if not start_date_query or not end_date_query:
        return jsonify({'error': 'Missing date parameters'}), 400

    start_date = datetime.strptime(start_date_query, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_query, '%Y-%m-%d') + timedelta(days=1)

    vehicles_collection = mongo.db.vehicules
    match_stage = {"date d'entrée": {"$gte": start_date, "$lt": end_date}}
    pipeline = [
        {"$match": match_stage},
        {"$group": {"_id": "$class", "avg_wait_time": {"$avg": "$wait_time"}}}
    ]
    result = list(vehicles_collection.aggregate(pipeline))
    avg_wait_time_by_class = {doc["_id"]: doc["avg_wait_time"] for doc in result}

    return jsonify(avg_wait_time_by_class)


@app.route('/data')
def data():
    filter_type = request.args.get('filter_type', 'day')
    start_date_query = request.args.get('start_date')
    end_date_query = request.args.get('end_date') if filter_type == 'week' else start_date_query

    if not start_date_query or not end_date_query:
        return jsonify({'error': 'Missing date parameters'}), 400

    try:
        start_date = datetime.strptime(start_date_query, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_query, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    vehicles_collection = mongo.db.vehicules
    match_stage = {"$match": {"class": {"$ne": "Worker"}, "date d'entrée": {"$gte": start_date, "$lt": end_date}}}

    pipeline = [
        match_stage,
        {"$group": {"_id": "$class", "count": {"$sum": 1}}}
    ]
    result = list(vehicles_collection.aggregate(pipeline))
    vehicle_counts = {doc["_id"]: doc["count"] for doc in result}

    return jsonify(vehicle_counts)


mongo = PyMongo(app)
@app.route('/pump_data')
def pump_data():
    filter_type = request.args.get('filter_type', 'day')
    start_date_query = request.args.get('start_date')
    end_date_query = request.args.get('end_date') if filter_type == 'week' else start_date_query

    if not start_date_query or not end_date_query:
        return jsonify({'error': 'Missing date parameters'}), 400

    try:
        start_date = datetime.strptime(start_date_query, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_query, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    vehicules_collection = mongo.db.vehicules
    match_stage = {"date d'entrée": {"$gte": start_date, "$lt": end_date}}

    cursor = vehicules_collection.find(match_stage)
    vehicules_list = list(cursor)
    
    if not vehicules_list:
        return jsonify({"message": "No data found for the given date."}), 404

    pump_usage = {}
    for vehicule in vehicules_list:
        pump_info = vehicule.get('pompes_info')
        if pump_info:
            if pump_info in pump_usage:
                pump_usage[pump_info] += 1
            else:
                pump_usage[pump_info] = 1

    return jsonify(pump_usage)


@app.route('/get-top-clients')
def get_top_clients():
    filter_type = request.args.get('filter_type', 'day')
    start_date_query = request.args.get('start_date')
    end_date_query = request.args.get('end_date') if filter_type == 'week' else start_date_query

    if not start_date_query or not end_date_query:
        return jsonify({'error': 'Missing date parameters'}), 400

    try:
        start_date = datetime.strptime(start_date_query, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_query, '%Y-%m-%d') + timedelta(days=1)
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    vehicles_collection = mongo.db.vehicules

    match_stage = {
        "$match": {
            "date d'entrée": {"$gte": start_date, "$lt": end_date}
        }
    }

    pipeline = [
        match_stage,
        {"$group": {"_id": "$license_plate_text", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    
    result = list(vehicles_collection.aggregate(pipeline))
    top_clients = {doc["_id"]: doc["count"] for doc in result}

    pyramid_data = [{"label": lp, "value": count} for lp, count in top_clients.items()]
    
    return jsonify(pyramid_data)




@app.route('/registre', methods=['GET', 'POST'])
def registre():
    if request.method == 'POST':
        user_data = request.form.to_dict()
        station_name = user_data.get('station_name')

        # Log the received station_name
        app.logger.info(f"Received station_name: {station_name}")

        # Trouver l'ObjectId de la station par son nom
        station = mongo.db.stations.find_one({'name': station_name})
        if not station:
            app.logger.error(f"Station not found for name: {station_name}")
            flash('Station not found. Please enter a valid station name.', 'error')
            return redirect(url_for('registre'))

        # Hacher le mot de passe et créer le document utilisateur
        password_hash = generate_password_hash(user_data['password'])
        
        # Ajouter la colonne created_at avec le fuseau horaire Africa/Tunis
        tunisia_tz = pytz.timezone('Africa/Tunis')
        created_at = datetime.now(tunisia_tz)
        
        new_user = {
            'name': user_data['name'],
            'email': user_data['email'],
            'gender': user_data['gender'],
            'worker_type': 'Simple User',  # Fixer le rôle comme 'Simple User'
            'birthdate': user_data['birthdate'],
            'station_id': station['_id'],  # Utiliser l'ObjectId de la station
            'cin': user_data['cin'],
            'password_hash': password_hash,
            'profile_picture': user_data.get('profile_picture', 'default.jpg'),
            'created_at': created_at  # Ajouter le champ created_at
        }
        try:
            mongo.db.users.insert_one(new_user)
            app.logger.info("User added successfully")
            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))  # Redirect to the login page after successful registration
        except Exception as e:
            app.logger.error(f"Exception occurred: {e}")
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('registre'))

    return render_template('registre.html')


@app.route('/get-top-clients1', methods=['GET'])
def get_top_clients1():
    chosen_date = request.args.get('date', None)
    
    # Charger les données et filtrer selon la date choisie
    df = pd.read_excel('DATA.xlsx')

    # Assurez-vous que la colonne 'date d'entrée' est dans le format de date correct
    if 'date d\'entrée' in df.columns:
        df["date d\'entrée"] = pd.to_datetime(df["date d\'entrée"]).dt.date

    # Filtrer les données pour la date choisie si elle est fournie
    if chosen_date:
        df = df[df['date d\'entrée'] == pd.to_datetime(chosen_date).date()]

    # Calculer les clients fidèles pour la date choisie
    top_clients = df['license_plate_text'].value_counts().head(5).to_dict()

    # Construire les données pour le graphique en pyramide
    pyramid_data = [{"label": lp, "value": count} for lp, count in top_clients.items()]
    
    # Debug: Afficher les données dans la console du serveur
    #print('Top clients data:', pyramid_data,"date",chosen_date)

    return jsonify(pyramid_data)
@app.route('/data_par_heure1')
def data_par_heure1():
    date_query = request.args.get('date', None)
    vehicles_collection = mongo.db.vehicules

    match_stage = {"$match": {"class": {"$ne": "Worker"}}}
    if date_query:
        date = datetime.strptime(date_query, '%Y-%m-%d')
        match_stage["$match"]["date d\'entrée"] = {"$gte": date, "$lt": date + timedelta(days=1)}

    pipeline = [
        match_stage,
        {"$group": {"_id": {"$hour": "$date d\'entrée"}, "count": {"$sum": 1}}}
    ]
    result = list(vehicles_collection.aggregate(pipeline))
    vehicles_per_hour = {doc["_id"]: doc["count"] for doc in result}

    return jsonify({'vehicles_per_hour': vehicles_per_hour})
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/video_feed')
def video_feed():
    global video_capture
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    global video_path, is_processing, current_frame_data
    if video_path is None:
        return

    cap = cv2.VideoCapture(video_path)
    while cap.isOpened() and is_processing:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame, combined_dict = process_frame(frame)
        current_frame_data = combined_dict  # Mettez à jour les données du cadre actuel
        update_csv(combined_dict)  # Mise à jour du CSV en temps réel
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if ret:
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()
@app.route('/download_csv', methods=['GET'])
def download_csv():
    if os.path.exists(csv_file_path):
        return send_file(csv_file_path, as_attachment=True, download_name='output.csv')
    else:
        return jsonify({'error': 'CSV file not found'}), 404

@app.route('/get_frame_data', methods=['GET'])
def get_frame_data():
    global current_frame_data
    return jsonify(current_frame_data)




    
video_path = None  # Variable globale pour stocker le chemin du fichier vidéo
video_capture = None 
@app.route('/upload', methods=['POST'])
def upload_file():
    global video_path, video_capture  # Utilisez la variable globale
    if 'file' in request.files:
        video_file = request.files['file']
        if video_file and allowed_file(video_file.filename):
            filename = secure_filename(video_file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video_file.save(video_path)
            video_capture = cv2.VideoCapture(video_path)  # Initialisez la capture vidéo
            return jsonify({'message': 'Fichier téléchargé avec succès', 'path': video_path})
        else:
            return jsonify({'error': 'Type de fichier non autorisé'}), 400
    else:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400










@app.errorhandler(Exception)
def handle_exception(error):
    # Traite toutes les exceptions non capturées
    return jsonify({'error': 'An error occurred', 'message': str(error)}), 500


@app.route('/api/data', methods=['GET'])
def get_data():
    df = pd.read_excel('DATA.xlsx')
    zone = request.args.get('zone')
    date_str = request.args.get('date')
    
    #print(f"Received zone: {zone}, date: {date_str}")

    filtered_df = df.copy()

    # Vérifier si la colonne 'ZoneTotal' existe
    if 'ZoneTotal' not in filtered_df.columns:
        return jsonify({'error': 'An error occurred', 'message': 'No ZoneTotal column found in the data.'}), 400

    # Filtrer par zone
    if zone:
        filtered_df = filtered_df[filtered_df['ZoneTotal'] == zone]

    # Vérifier si la colonne 'date d\'entrée' existe
    if 'date d\'entrée' not in filtered_df.columns:
        return jsonify({'error': 'An error occurred', 'message': 'No date d\'entrée column found in the data.'}), 400

    # Filtrer par date
    if date_str:
        try:
            date = pd.to_datetime(date_str, format='%Y-%m-%d')
            filtered_df['date d\'entrée'] = pd.to_datetime(filtered_df['date d\'entrée'], format='%d/%m/%Y %I:%M:%S %p')
            # Filtrer les données par date (ignorer l'heure)
            filtered_df = filtered_df[filtered_df['date d\'entrée'].dt.date == date.date()]
        except Exception as e:
            return jsonify({'error': 'An error occurred', 'message': f'Date conversion error: {str(e)}'}), 400

    vehicle_classes = ['Small Truck', 'Motorcycle', 'Big Truck', 'Car', 'Taxi', 'Construction Machine']

    # Agréger les données par classe
    if 'class' in filtered_df.columns:
        class_counts = filtered_df['class'].value_counts().to_dict()
        totals = {vehicle_class: class_counts.get(vehicle_class, 0) for vehicle_class in vehicle_classes}
    else:
        return jsonify({'error': 'An error occurred', 'message': 'No class column found in the data.'}), 400

    #+(f"Filtered data totals: {totals}")

    return jsonify(totals)


@app.route('/streamlite')
def streamlite():
    return render_template('streamlite.html')
import threading
import subprocess
def run_streamlit():
    subprocess.run(['streamlit', 'run', 'streamlit_app.py'])



def total_vehicules(selected_date):
    vehicules_collection = mongo.db.vehicules
    start_date = datetime.strptime(selected_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    total = vehicules_collection.count_documents({
        'date d\'entrée': {'$gte': start_date, '$lt': end_date}
    })
    return total

def debit_vehicules_j_ouvrable(selected_date):
    vehicules_collection = mongo.db.vehicules
    start_date = datetime.strptime(selected_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=7)

    # Liste des jours ouvrables
    jours_ouvrables = [0, 1, 2, 3, 4]  # Lundi (0) à Vendredi (4)

    # Construire une requête pour inclure uniquement les jours ouvrables
    pipeline = [
        {
            '$match': {
                'date d\'entrée': {'$gte': start_date, '$lt': end_date}
            }
        },
        {
            '$project': {
                'dayOfWeek': {'$dayOfWeek': '$date d\'entrée'}
            }
        },
        {
            '$match': {
                'dayOfWeek': {'$in': [2, 3, 4, 5, 6]}  # Lundi à Vendredi dans MongoDB (1=Dimanche, 7=Samedi)
            }
        },
        {
            '$count': 'total'
        }
    ]

    result = list(vehicules_collection.aggregate(pipeline))

    if result:
        total = result[0]['total']
    else:
        total = 0

    return total


def debit_taxi(selected_date):
    vehicules_collection = mongo.db.vehicules
    start_date = datetime.strptime(selected_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)
    total = vehicules_collection.count_documents({
        'date d\'entrée': {'$gte': start_date, '$lt': end_date},
        'class': 'Taxi'
    })
    return total

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    selected_date = request.args.get('date')
    total = total_vehicules(selected_date)
    debit_ouvrable = debit_vehicules_j_ouvrable(selected_date)
    debit_taxi_value = debit_taxi(selected_date)
    debit_vl_value = debit_vl(selected_date)
    debit_pl_value = debit_pl(selected_date)
    
    return jsonify({
        'total_vehicules': total,
        'debit_ouvrable': debit_ouvrable,
        'debit_taxi': debit_taxi_value,
        'debit_vl': debit_vl_value,
        'debit_pl': debit_pl_value
    })


@app.route('/api/test_total_vehicules', methods=['GET'])
def test_total_vehicules():
    selected_date = request.args.get('date')
    total = total_vehicules(selected_date)
    return jsonify({
        'total_vehicules': total
    })
@app.route('/api/test_debit_vehicules_j_ouvrable', methods=['GET'])
def test_debit_vehicules_j_ouvrable():
    selected_date = request.args.get('date')
    total = debit_vehicules_j_ouvrable(selected_date)
    return jsonify({
        'debit_ouvrable': total
    })

@app.route('/api/test_debit_taxi', methods=['GET'])
def test_debit_taxi():
    selected_date = request.args.get('date')
    total = debit_taxi(selected_date)
    return jsonify({
        'debit_taxi': total
    })
#Test
#http://127.0.0.1:5001/api/test_total_vehicules?date=2024-04-06
#http://localhost:5000/api/test_debit_vehicules_j_ouvrable?date=2024-04-05
#http://localhost:5000/api/test_debit_taxi?date=2024-04-05
def debit_vl(selected_date):
    vehicules_collection = mongo.db.vehicules
    start_date = datetime.strptime(selected_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)

    classes_vl = ['Car', 'Motorcycle', 'Taxi']
    total = vehicules_collection.count_documents({
        'date d\'entrée': {'$gte': start_date, '$lt': end_date},
        'class': {'$in': classes_vl}
    })
    return total
def debit_pl(selected_date):
    vehicules_collection = mongo.db.vehicules
    start_date = datetime.strptime(selected_date, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1)

    classes_pl = ['Construction machine', 'Big Truck', 'Small Truck']
    total = vehicules_collection.count_documents({
        'date d\'entrée': {'$gte': start_date, '$lt': end_date},
        'class': {'$in': classes_pl}
    })
    return total


##
#station = mongo.db.stations.find_one({'_id': user['station_id']})
# station_name = station['name'] if station else 'Unknown'
#### page statistics

# Function to map station_id to station name
# Function to map station_id to station name
def get_station_name(station_id):
    try:
        logging.debug(f"Original Station ID: {station_id}")
        
        station_id = ObjectId(station_id)
        logging.debug(f"Converted Station ID: {station_id}")
        station = mongo.db.stations.find_one({'_id': station_id})
        logging.debug(f"Station Found: {station}")
        return station['name'] if station else "Unknown Station"
    except Exception as e:
        logging.error("Error fetching station name: %s", e)
        return "Unknown Station"

@app.route('/')
def index():
    return render_template('statistics.html')

def encode_utf8(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda x: x.encode('utf-8', 'ignore').decode('utf-8') if isinstance(x, str) else x)
    return df

def process_data(data):
    for record in data:
        record.pop('_id', None)
        if 'station_id' in record:
            station = mongo.db.stations.find_one({'_id': ObjectId(record['station_id'])})
            record['station'] = station['name'] if station else 'Unknown'
            record.pop('station_id', None)
        if 'date d\'entrée' in record:
            record['date d\'entrée'] = record['date d\'entrée'].strftime('%Y-%m-%d') if isinstance(record['date d\'entrée'], datetime) else str(record['date d\'entrée'])
        if 'date de sortie' in record:
            record['date de sortie'] = record['date de sortie'].strftime('%Y-%m-%d') if isinstance(record['date de sortie'], datetime) else str(record['date de sortie'])
    return data

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        date_filter_type = request.form.get('date_filter_type')
        filter_date = request.form.get('filter_date')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        query = {}
        if date_filter_type == 'day' and filter_date:
            query['date d\'entrée'] = pd.to_datetime(filter_date)
        elif date_filter_type == 'week' and start_date and end_date:
            query['date d\'entrée'] = {
                '$gte': pd.to_datetime(start_date),
                '$lte': pd.to_datetime(end_date)
            }

        vehicules_collection = mongo.db.vehicules
        data = list(vehicules_collection.find(query))
        data = process_data(data)
        df = pd.DataFrame(data)

        df = encode_utf8(df)

        return df.to_json(orient='records')
    except Exception as e:
        logging.error("Error fetching data: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/download_excel', methods=['POST'])
def download_excel():
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        query = {}
        if start_date and end_date:
            query['date d\'entrée'] = {
                '$gte': pd.to_datetime(start_date),
                '$lte': pd.to_datetime(end_date)
            }

        vehicules_collection = mongo.db.vehicules
        data = list(vehicules_collection.find(query))
        data = process_data(data)
        df = pd.DataFrame(data)

        df = encode_utf8(df)

        # Create a bytes buffer for the Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vehicules')

        output.seek(0)
        return send_file(output, attachment_filename="filtered_data.xlsx", as_attachment=True)
    except Exception as e:
        logging.error("Error generating Excel file: %s", e)
        return jsonify({'error': str(e)}), 500

@app.route('/initial_data', methods=['GET'])
def initial_data():
    try:
        vehicules_collection = mongo.db.vehicules
        data = list(vehicules_collection.find().limit(100))  # Limit to first 100 records for display
        data = process_data(data)
        df = pd.DataFrame(data)

        df = encode_utf8(df)

        return df.to_json(orient='records')
    except Exception as e:
        logging.error("Error fetching initial data: %s", e)
        return jsonify({'error': str(e)}), 500
    



# page statistics   
@app.route('/api/total_vehicles', methods=['GET'])
def get_total_vehicles():
        selected_date = request.args.get('date')
        filter_type = request.args.get('filter_type')
        vehicules_collection = mongo.db.vehicules

        if filter_type == 'day':
            start_date = datetime.strptime(selected_date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        elif filter_type == 'week':
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + timedelta(days=1)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        total = vehicules_collection.count_documents({
            'date d\'entrée': {'$gte': start_date, '$lt': end_date}
        })
        return jsonify({'total': total})



@app.route('/api/debit_vl', methods=['GET'])
def get_debit_vl():
    try:
        selected_date = request.args.get('date')
        filter_type = request.args.get('filter_type')
        vehicules_collection = mongo.db.vehicules

        if filter_type == 'day':
            start_date = datetime.strptime(selected_date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        elif filter_type == 'week':
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + timedelta(days=1)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        total_vl = vehicules_collection.count_documents({
            'date d\'entrée': {'$gte': start_date, '$lt': end_date},
            'class': {'$in': ['Big Truck', 'Construction Machine', 'Small Truck']}
        })
        return jsonify({'total_vl': total_vl})
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

@app.route('/api/debit_vp', methods=['GET'])
def get_debit_vp():
    try:
        selected_date = request.args.get('date')
        filter_type = request.args.get('filter_type')
        vehicules_collection = mongo.db.vehicules

        if filter_type == 'day':
            start_date = datetime.strptime(selected_date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        elif filter_type == 'week':
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + timedelta(days=1)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        total_vp = vehicules_collection.count_documents({
            'date d\'entrée': {'$gte': start_date, '$lt': end_date},
            'class': {'$in': ['Taxi', 'Car', 'Motorcycle']}
        })
        return jsonify({'total_vp': total_vp})
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500
    
@app.route('/api/unique_zones', methods=['GET'])
def get_unique_zones():
    try:
        vehicules_collection = mongo.db.vehicules
        unique_zones = vehicules_collection.distinct('ZoneTotal')
        return jsonify({'unique_zones': len(unique_zones)})
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500
    
@app.route('/api/vehicles_by_class', methods=['GET'])
def get_vehicles_by_class():
    try:
        selected_date = request.args.get('date')
        filter_type = request.args.get('filter_type')
        vehicules_collection = mongo.db.vehicules

        if filter_type == 'day':
            start_date = datetime.strptime(selected_date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        elif filter_type == 'week':
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + timedelta(days=1)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        pipeline = [
            {
                '$match': {
                    'date d\'entrée': {'$gte': start_date, '$lt': end_date}
                }
            },
            {
                '$group': {
                    '_id': '$class',
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'class': '$_id',
                    'count': 1
                }
            }
        ]
        result = list(vehicules_collection.aggregate(pipeline))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500
@app.route('/api/analysis_by_zone', methods=['GET'])
def get_analysis_by_zone():
    try:
        selected_date = request.args.get('date')
        filter_type = request.args.get('filter_type')
        vehicules_collection = mongo.db.vehicules

        if filter_type == 'day':
            start_date = datetime.strptime(selected_date, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
        elif filter_type == 'week':
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d') + timedelta(days=1)
        else:
            return jsonify({'error': 'Invalid filter type'}), 400

        pipeline = [
            {
                '$match': {
                    'date d\'entrée': {'$gte': start_date, '$lt': end_date}
                }
            },
            {
                '$group': {
                    '_id': '$ZoneTotal',
                    'heavy_weight': {
                        '$sum': {
                            '$cond': [{'$in': ['$class', ['Big Truck', 'Construction Machine', 'Small Truck']]}, 1, 0]
                        }
                    },
                    'light_weight': {
                        '$sum': {
                            '$cond': [{'$in': ['$class', ['Taxi', 'Car', 'Motorcycle']]}, 1, 0]
                        }
                    }
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'zone': '$_id',
                    'heavy_weight': 1,
                    'light_weight': 1
                }
            }
        ]
        result = list(vehicules_collection.aggregate(pipeline))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    


    app.run( host='127.0.0.1', port=5001,debug=True)

    




   


    