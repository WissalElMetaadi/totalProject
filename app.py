from flask import Flask, render_template,Response,send_file
from flask import request, redirect, url_for, render_template, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
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

""" app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Utilisez la base de données que vous souhaitez
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app) """


app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:JEONjungkook123@localhost/totalbd'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = r'C:\Users\Utilisateur\Desktop\projet_flask'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 100 MB limit


db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username



with app.app_context():
    db.create_all()



class Vehicule(db.Model):
    __tablename__ = 'vehicules'
    track_id = db.Column(db.Integer, primary_key=True)
    classe = db.Column(db.String(255))
    license_plate_text = db.Column(db.String(255))
    score = db.Column(db.Float)
    LP_pompes_info = db.Column(db.String(255))
    date_entree = db.Column(db.DateTime)
    date_sortie = db.Column(db.DateTime)
    wait_time = db.Column(db.Integer)
    car_image = db.Column(db.String(255))
    license_plate_image = db.Column(db.String(255))




class Users(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    worker_type = db.Column(db.String(255), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    station = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.LargeBinary)
    def __repr__(self):
        return '<Users %r>' % self.name
    
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/test')
def testupload():
    return render_template('test.html')


@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/NouvDashboard')
def NouvDashboard():
    return render_template('NouvDashboard.html')



@app.route('/ajoutUser', methods=['GET', 'POST'])
def ajoutUser():
    if request.method == 'POST':
        try:
            # Hacher le mot de passe

            hashed_password = generate_password_hash(request.form['password'])

            

            new_user = Users(
                name=request.form['name'],
                email=request.form['email'],
                gender=request.form['gender'],
                worker_type=request.form['worker_type'],
                birthdate=request.form['birthdate'],
                station=request.form['station'],
                password_hash=hashed_password,
                profile_picture= None  # Stocker le chemin du fichier s'il est présent
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Utilisateur ajouté avec succès!', 'success')
        except IntegrityError as e:  # Attrape l'erreur d'intégrité de SQLAlchemy
            db.session.rollback()
            if 'Duplicate entry' in str(e.orig):
                flash('Cette adresse email est déjà utilisée. Veuillez en utiliser une autre.', 'error')
            else:
                flash('Une erreur est survenue lors de l ajout de l utilisateur.', 'error')
        except MySQLIntegrityError as e:  # Attrape l'erreur d'intégrité spécifique à MySQL
            db.session.rollback()
            if '1062' in str(e):
                flash('Cette adresse email est déjà utilisée. Veuillez en utiliser une autre.', 'error')
            else:
                flash('Une erreur est survenue lors de l ajout de l utilisateur.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la jout de l utilisateur.', 'error')
        return redirect(url_for('ajoutUser'))
    return render_template('ajoutUser.html')
    
@app.route('/total_zone')
def total_zone():
    return render_template('total_zone.html')



@app.route('/DragAndDrop')
def DragAndDrop():
    active_item = 'Upload Data'
    return render_template('DragAndDrop.html',active_item=active_item)

@app.route('/modele')
def modele():
    return render_template('modele.html')

@app.route('/charts_jour')
def charts_jour():
    active_item = 'statistiques'
    print(active_item)
    print('hhhhhhhhhhhhhhhhhhhhhhh')
    return render_template('charts_jour.html',active_item=active_item)

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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user1 = User.query.filter_by(username=username).first()
        if user1 and check_password_hash(user1.password_hash, password):
            session['username'] = username
            # Redirect to the protected dashboard
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')
@app.route('/logout')
def logout():
    # Supprime 'username' de la session
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    active_item = 'dashboard'
    data = read_excel('DATA.xlsx')  # Modifiez le chemin relatif ici
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', data=data,active_item=active_item)
@app.route('/dashboardwess')


def read_excel(file_name):
    # Utilisez un chemin relatif ou configurez correctement le chemin absolu
    file_path = os.path.join(os.getcwd(), file_name)
    df = pd.read_excel(file_path)
    return df.to_dict(orient='records') 

  


@app.route('/data_par_heure')
def data_par_heure():
    date_query = request.args.get('date', None)
    
    df = pd.read_excel('DATA.xlsx')
    
    if date_query:
        
        df['date d\'entrée'] = pd.to_datetime(df['date d\'entrée'])
        df = df[df['date d\'entrée'].dt.strftime('%Y-%m-%d') == date_query]
    
    df_filtered = df[df['class'] != 'Worker']
    df_filtered['hour'] = df_filtered['date d\'entrée'].dt.hour
    vehicles_per_hour = df_filtered.groupby('hour').size().to_dict()
    
    return jsonify({ 'vehicles_per_hour': vehicles_per_hour })






@app.route('/avg_wait_time_by_class')
def get_avg_wait_time_by_class():
    date_query = request.args.get('date', None)
    
    # Charger le fichier Excel
    df = pd.read_excel('DATA.xlsx')
    
    if date_query:
        # Convertir la colonne de date en datetime et filtrer par la date choisie
        df['date d\'entrée'] = pd.to_datetime(df['date d\'entrée'])
        df = df[df['date d\'entrée'].dt.strftime('%Y-%m-%d') == date_query]
    
    df_filtered = df[df['class'] != 'Worker']

    # Calculer le temps d'attente moyen par classe de véhicules
    avg_wait_time_by_class = df_filtered.groupby('class')['wait_time'].mean().sort_values().to_dict()
    
    # Retourner les données au format JSON
    return jsonify(avg_wait_time_by_class)


@app.route('/data')
def data():
    # Récupérer la date à partir des paramètres de requête
    date_query = request.args.get('date', None)
    
    # Charger le fichier Excel
    df = pd.read_excel('DATA.xlsx')
    
    # Convertir la colonne de date en datetime, si ce n'est pas déjà fait
    df['date d\'entrée'] = pd.to_datetime(df['date d\'entrée'])
    
    # Filtrer les données pour la date spécifiée, si une date est fournie
    if date_query:
        df = df[df['date d\'entrée'].dt.strftime('%Y-%m-%d') == date_query]
    
    # Exclure les données de la classe 'Worker'
    df_filtered = df[df['class'] != 'Worker']
    
    # Calculer le nombre de véhicules par classe, à l'exception de 'Worker'
    vehicle_counts = df_filtered['class'].value_counts().to_dict()
    
    # Retourner les données au format JSON
    return jsonify(vehicle_counts)



@app.route('/pump_data')
def pump_data():
    # Récupérer la date à partir des paramètres de requête
    date_query = request.args.get('date', None)
    
    # Charger le fichier Excel
    df = pd.read_excel('DATA.xlsx')
    
    # Convertir la colonne de date en datetime, si ce n'est pas déjà fait
    if 'date d\'entrée' in df.columns:
        df['date d\'entrée'] = pd.to_datetime(df['date d\'entrée'])

    # Filtrer les données pour la date spécifiée, si une date est fournie
    if date_query:
        # Assumer que 'date d'entrée' est le nom de votre colonne de date dans le DataFrame
        df = df[df['date d\'entrée'].dt.strftime('%Y-%m-%d') == date_query]
    
    # Calculer l'utilisation des pompes pour les données filtrées
    pump_usage = df['pompes_info'].value_counts().to_dict()
    
    # Retourner les données au format JSON
    return jsonify(pump_usage)


@app.route('/get-top-clients', methods=['GET'])
def get_top_clients():
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


@app.route('/registre', methods=['GET', 'POST'])
def registre():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        # Redirigez vers la page de connexion après l'inscription réussie
        return redirect(url_for('login'))

    return render_template('registre.html')


@app.route('/video_feed')
def video_feed():
    if video_path:
        # Assurez-vous que process_video retourne quelque chose que vous pouvez envoyer en réponse
        return Response(process_video(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Aucun fichier vidéo sélectionné", 400

#VIDEO_PATH = r'C:\Users\Utilisateur\Desktop\projet_flask\sampleee11.mp4'



def process_video(VIDEO_PATH):
    cap = cv2.VideoCapture(VIDEO_PATH)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame,combined_dict = process_frame(frame)  # Passer uniquement la frame
        #processed_frame = run_yolo(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        if ret:
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            process_and_send_data(combined_dict)
    cap.release() 

def process_and_send_data(detections):
    """
    Process the detections dictionary and send data to the client.
    """
    processed_data = []
    for track_id, details in detections.items():
        # Traitement pour les valeurs None et les formats de données
        processed_entry = {
            'ID': track_id,
            'Classe': details.get('class', 'N/A'),
            'Matricule': details.get('license_plate_text', 'N/A'),
            'Score': details.get('score LP', 0),
            'DateEntrée': details.get("date d'entrée", 'N/A'),
            'DateSortie': details.get("date de sortie", 'N/A'),
            'WaitTime': details.get('wait_time', 0) if details.get('wait_time') is not None else 'N/A',
            'Zone': details.get('pompes_info', 'N/A')
        }
        processed_data.append(processed_entry)
        logging.info(f"Processed data for track ID {track_id}: {processed_entry}")

    # Envoyer les données au client via SocketIO
    socketio.emit('new_data', {'data': processed_data})
    logging.info("Data sent to client.")

    
video_path = None  # Variable globale pour stocker le chemin du fichier vidéo

@app.route('/upload', methods=['POST'])
def upload_file():
    global video_path  # Utilisez la variable globale
    if 'file' in request.files:
        video_file = request.files['file']
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(r'C:\Users\Utilisateur\Desktop\projet_flask', filename)
        video_file.save(video_path)
        return jsonify({'message': 'Fichier téléchargé avec succès', 'path': video_path})
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





def open_browser():
    webbrowser.open_new('http://127.0.0.1:5001/login')

if __name__ == '__main__':
    app.secret_key = 'votre_cle_secrete'
    threading.Timer(1, open_browser).start() 
    app.run(debug=True, host='0.0.0.0', port=5001,threaded=True)

    




   


    
