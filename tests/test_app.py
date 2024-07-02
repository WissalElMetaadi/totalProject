import pytest
from app import app, mongo
import json
from bson.objectid import ObjectId


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


#### 1- ROUTES 
############## CRUD DE LA COLLECTION GOUVERNORAT

def test_add_governorate(client):
    response = client.post('/add_governorate', json={'name': 'Test Governorate'})
    assert response.status_code == 201
    assert b'Governorate added successfully!' in response.data

def test_get_governorates(client):
    # Fetch initial number of governorates
    initial_response = client.get('/get_governorates')
    initial_data = initial_response.get_json()
    initial_count = len(initial_data)

    # Add a governorate
    response = client.post('/add_governorate', json={'name': 'Test Governorate'})
    assert response.status_code == 201

    # Fetch governorates again
    response = client.get('/get_governorates')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == initial_count + 1
    assert any(gov['name'] == 'Test Governorate' for gov in data)

def test_update_governorate(client):
    # Add a governorate and get its ID
    response = client.post('/add_governorate', json={'name': 'Test Governorate'})
    assert response.status_code == 201
    governorate_id = mongo.db.governorates.find_one({'name': 'Test Governorate'})['_id']

    # Update governorate
    update_response = client.put(f'/update_governorate/{governorate_id}', json={'name': 'Updated Governorate'})
    assert update_response.status_code == 200
    assert b'Governorate updated successfully!' in update_response.data

    # Fetch updated governorate
    response = client.get('/get_governorates')
    data = response.get_json()
    assert any(gov['name'] == 'Updated Governorate' for gov in data)

def test_delete_governorate(client):
    # Add a governorate and get its ID
    response = client.post('/add_governorate', json={'name': 'Test Governorate'})
    assert response.status_code == 201
    governorate_id = mongo.db.governorates.find_one({'name': 'Test Governorate'})['_id']

    # Delete governorate
    delete_response = client.delete(f'/delete_governorate/{governorate_id}')
    assert delete_response.status_code == 200
    assert b'Governorate deleted successfully!' in delete_response.data

    # Ensure governorate is deleted
    response = client.get('/get_governorates')
    data = response.get_json()
    assert not any(gov['id'] == str(governorate_id) for gov in data)

################ CRUD DE LA COLLECTION STATIONS
import json
from bson.objectid import ObjectId
from app import mongo

def test_add_station(client):
    # Add a governorate first
    response = client.post('/add_governorate', json={'name': 'Test Governorate'})
    assert response.status_code == 201
    governorate_id = str(mongo.db.governorates.find_one({'name': 'Test Governorate'})['_id'])

    # Add a station
    response = client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})
    assert response.status_code == 201
    assert b'Station added successfully' in response.data

def test_get_stations(client):
    # Fetch initial number of stations
    initial_response = client.get('/get_stations')
    initial_data = initial_response.get_json()
    initial_count = len(initial_data)

    # Add a governorate and a station
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})

    # Fetch stations again
    response = client.get('/get_stations')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == initial_count + 1
    assert any(station['name'] == 'Test Station' for station in data)

def test_update_station(client):
    # Add a governorate and a station
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    response = client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})
    assert response.status_code == 201
    station_id = str(mongo.db.stations.find_one({'name': 'Test Station'})['_id'])

    # Update station
    update_response = client.put(f'/update_station/{station_id}', json={'name': 'Updated Station', 'governorate_name': 'Test Governorate'})
    assert update_response.status_code == 200
    assert b'Station updated successfully!' in update_response.data

    # Fetch updated station
    response = client.get('/get_stations')
    data = response.get_json()
    assert any(station['name'] == 'Updated Station' for station in data)

def test_delete_station(client):
    # Add a governorate and a station
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    response = client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})
    assert response.status_code == 201
    station_id = str(mongo.db.stations.find_one({'name': 'Test Station'})['_id'])

    # Delete station
    delete_response = client.delete(f'/delete_station/{station_id}')
    assert delete_response.status_code == 200
    assert b'Station deleted successfully!' in delete_response.data

    # Ensure station is deleted
    response = client.get('/get_stations')
    data = response.get_json()
    assert not any(station['id'] == station_id for station in data)


############### CRUD DE LA COLLECTION USERS

def setup_governorate_and_station():
    # Add a governorate
    governorate_id = mongo.db.governorates.insert_one({'name': 'Test Governorate'}).inserted_id
    # Add a station
    station_id = mongo.db.stations.insert_one({'name': 'Test Station', 'governorate_id': governorate_id}).inserted_id
    return str(governorate_id), str(station_id)

def test_add_user1(client):
    governorate_id, station_id = setup_governorate_and_station()
    response = client.post('/add_user1', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'M',
        'worker_type': 'Admin',
        'birthdate': '1990-01-01',
        'station_name': 'Test Station',
        'cin': '12345678',
        'password': 'testpassword',
    })
    assert response.status_code == 201
    assert b'User added successfully!' in response.data

def test_get_users1(client):
    governorate_id, station_id = setup_governorate_and_station()
    # Fetch initial number of users
    initial_response = client.get('/get_users1')
    initial_data = initial_response.get_json()
    initial_count = len(initial_data)

    # Add a user
    client.post('/add_user1', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'M',
        'worker_type': 'Admin',
        'birthdate': '1990-01-01',
        'station_name': 'Test Station',
        'cin': '12345678',
        'password': 'testpassword',
    })

    # Fetch users again
    response = client.get('/get_users1')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == initial_count + 1
    assert any(user['name'] == 'Test User' for user in data)

def test_update_user(client):
    governorate_id, station_id = setup_governorate_and_station()
    # Add a user
    client.post('/add_user1', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'M',
        'worker_type': 'Admin',
        'birthdate': '1990-01-01',
        'station_name': 'Test Station',
        'cin': '12345678',
        'password': 'testpassword',
    })
    user_id = str(mongo.db.users.find_one({'name': 'Test User'})['_id'])

    # Update user
    update_response = client.put(f'/update_user/{user_id}', json={
        'name': 'Updated User',
        'email': 'updateduser@example.com',
        'gender': 'F',
        'worker_type': 'Manager',
        'birthdate': '1991-01-01',
        'station_name': 'Test Station',
        'cin': '87654321'
    })
    assert update_response.status_code == 200
    assert b'User updated successfully!' in update_response.data

    # Fetch updated user
    response = client.get('/get_users1')
    data = response.get_json()
    assert any(user['name'] == 'Updated User' and user['email'] == 'updateduser@example.com' for user in data)

def test_delete_user(client):
    governorate_id, station_id = setup_governorate_and_station()
    # Add a user
    client.post('/add_user1', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'M',
        'worker_type': 'Admin',
        'birthdate': '1990-01-01',
        'station_name': 'Test Station',
        'cin': '12345678',
        'password': 'testpassword',
    })
    user_id = str(mongo.db.users.find_one({'name': 'Test User'})['_id'])

    # Delete user
    delete_response = client.delete(f'/delete_user/{user_id}')
    assert delete_response.status_code == 200
    assert b'User deleted successfully!' in delete_response.data

    # Ensure user is deleted
    response = client.get('/get_users1')
    data = response.get_json()
    assert not any(user['id'] == user_id for user in data)





import pytest
from flask import url_for

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200

def test_test_route(client):
    response = client.get('/test')
    assert response.status_code == 200

def test_interface_user(client):
    response = client.get('/interface_user')
    assert response.status_code == 302  # Assuming this requires login and redirects



def test_statistics(client):
    response = client.get('/statistics')
    assert response.status_code == 200

def test_powerbidash(client):
    response = client.get('/PowerBiDash')
    assert response.status_code == 200

def test_ajoutuser(client):
    response = client.get('/ajoutUser')
    assert response.status_code == 200

def test_total_zone(client):
    response = client.get('/total_zone')
    assert response.status_code == 200

def test_draganddrop(client):
    response = client.get('/DragAndDrop')
    assert response.status_code == 200

def test_modele(client):
    response = client.get('/modele')
    assert response.status_code == 200

def test_pdf(client):
    response = client.get('/pdf/first_page.pdf')
    assert response.status_code == 200

def test_charts_jour(client):
    response = client.get('/charts_jour')
    assert response.status_code == 200


def test_data_table(client):
    response = client.get('/data_table')
    assert response.status_code == 302  # Assuming this requires login and redirects


def test_login(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302  # Assuming this redirects

def test_statics(client):
    response = client.get('/statics')
    assert response.status_code == 200

def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 302  # Assuming this requires login and redirects

def test_data_par_heure(client):
    response = client.get('/data_par_heure?filter_type=day&start_date=2024-06-30')
    assert response.status_code == 200

def test_avg_wait_time_by_class(client):
    response = client.get('/avg_wait_time_by_class?filter_type=day&start_date=2024-04-03')
    assert response.status_code == 200

def test_data(client):
    response = client.get('/data?filter_type=day&start_date=2024-04-03')
    assert response.status_code == 200

def test_pump_data(client):
    response = client.get('/pump_data?filter_type=day&start_date=2024-04-03')
    assert response.status_code == 200

def test_get_top_clients(client):
    response = client.get('/get-top-clients?filter_type=day&start_date=2024-04-03')
    assert response.status_code == 200

def test_get_frame_data(client):
    response = client.get('/get_frame_data')
    assert response.status_code == 200

def test_get_recent_users(client):
    response = client.get('/get_recent_users')
    assert response.status_code == 200

def test_initial_data(client):
    response = client.get('/initial_data')
    assert response.status_code == 200

def test_api_total_vehicles(client):
    response = client.get('/api/total_vehicles?date=2024-04-03&filter_type=day')
    assert response.status_code == 200

def test_api_debit_vl(client):
    response = client.get('/api/debit_vl?date=2024-04-03&filter_type=day')
    assert response.status_code == 200

def test_api_debit_vp(client):
    response = client.get('/api/debit_vp?date=2024-04-03&filter_type=day')
    assert response.status_code == 200

def test_api_unique_zones(client):
    response = client.get('/api/unique_zones')
    assert response.status_code == 200

def test_api_vehicles_by_class(client):
    response = client.get('/api/vehicles_by_class?date=2024-04-03&filter_type=day')
    assert response.status_code == 200

def test_api_analysis_by_zone(client):
    response = client.get('/api/analysis_by_zone?date=2024-04-03&filter_type=day')
    assert response.status_code == 200

def test_start_processing(client):
    response = client.post('/start_processing')
    assert response.status_code == 200

def test_stop_processing(client):
    response = client.post('/stop_processing')
    assert response.status_code == 200



###### FONCTIONS
import pandas as pd 
import datetime
import csv
from app import load_csv, save_csv, update_csv, allowed_file, read_excel, total_vehicules, debit_vehicules_j_ouvrable, debit_taxi, debit_vl, debit_pl, get_station_name, encode_utf8, process_data


def test_allowed_file():
    assert allowed_file('test.mp4')
    assert not allowed_file('test.txt')

def test_read_excel(tmpdir):
    file_path = tmpdir.join('test.xlsx')
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    df.to_excel(file_path, index=False)
    data = read_excel(file_path)
    assert len(data) == 3

def test_total_vehicules():
    # Implement a mock test for total_vehicules
    pass

def test_debit_vehicules_j_ouvrable():
    # Implement a mock test for debit_vehicules_j_ouvrable
    pass

def test_debit_taxi():
    # Implement a mock test for debit_taxi
    pass

def test_debit_vl():
    # Implement a mock test for debit_vl
    pass

def test_debit_pl():
    # Implement a mock test for debit_pl
    pass

def test_get_station_name():
    # Implement a mock test for get_station_name
    pass

def test_encode_utf8():
    df = pd.DataFrame({'A': ['é', 'è', 'ê'], 'B': ['ü', 'û', 'ù']})
    encoded_df = encode_utf8(df)
    assert all(isinstance(val, str) for val in encoded_df['A'])
    assert all(isinstance(val, str) for val in encoded_df['B'])




@pytest.fixture(autouse=True)
def clear_db_after():
    yield
    # Clear only the test data in the MongoDB collections after each test
    mongo.db.governorates.delete_many({'name': {'$regex': '^Test '}})
    mongo.db.governorates.delete_many({'name': {'$regex': '^Updated '}})

    mongo.db.stations.delete_many({'name': {'$regex': '^Test '}})
    mongo.db.stations.delete_many({'name': {'$regex': '^Updated '}})

    mongo.db.users.delete_many({'name': {'$regex': '^Test '}})
    mongo.db.users.delete_many({'name': {'$regex': '^Updated '}})

