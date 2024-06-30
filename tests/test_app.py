import pytest
from app import app as flask_app
from flask import json
import io

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    client = flask_app.test_client()

    yield client

def test_add_governorate(client):
    data = {'name': 'Test Governorate'}
    response = client.post('/add_governorate', json=data)
    assert response.status_code == 201
    assert response.get_json()['message'] == 'Governorate added successfully!'

def test_add_station(client):
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    
    data = {
        'name': 'Test Station',
        'governorate_name': 'Test Governorate'
    }
    response = client.post('/add_station', json=data)
    assert response.status_code == 201
    assert response.get_json()['message'] == 'Station added successfully'

def test_get_recent_users(client):
    response = client.get('/get_recent_users')
    assert response.status_code == 200

def test_add_user1(client):
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})

    user_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'male',
        'worker_type': 'admin',
        'birthdate': '2000-01-01',
        'station_name': 'Test Station',
        'cin': '123456',
        'password': 'password123'
    }
    response = client.post('/add_user1', data=user_data)
    assert response.status_code == 201
    assert response.get_json()['message'] == 'User added successfully!'

def test_get_users1(client):
    response = client.get('/get_users1')
    assert response.status_code == 200

def test_update_user(client):
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})
    user_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'male',
        'worker_type': 'admin',
        'birthdate': '2000-01-01',
        'station_name': 'Test Station',
        'cin': '123456',
        'password': 'password123'
    }
    response = client.post('/add_user1', data=user_data)
    user_id = response.get_json().get('id')

    updated_user_data = {
        'name': 'Updated User',
        'email': 'updateduser@example.com',
        'gender': 'female',
        'worker_type': 'admin',
        'birthdate': '2000-02-02',
        'station_name': 'Test Station',
        'cin': '654321'
    }
    response = client.put(f'/update_user/{user_id}', json=updated_user_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User updated successfully!'

def test_delete_user(client):
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})
    user_data = {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'gender': 'male',
        'worker_type': 'admin',
        'birthdate': '2000-01-01',
        'station_name': 'Test Station',
        'cin': '123456',
        'password': 'password123'
    }
    response = client.post('/add_user1', data=user_data)
    user_id = response.get_json().get('id')

    response = client.delete(f'/delete_user/{user_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'User deleted successfully!'

def test_get_governorates(client):
    response = client.get('/get_governorates')
    assert response.status_code == 200

def test_get_stations(client):
    response = client.get('/get_stations')
    assert response.status_code == 200

def test_data_par_heure(client):
    response = client.get('/data_par_heure?filter_type=day&start_date=2023-01-01')
    assert response.status_code == 200

def test_get_avg_wait_time_by_class(client):
    response = client.get('/avg_wait_time_by_class?filter_type=day&start_date=2023-01-01')
    assert response.status_code == 200

def test_data(client):
    response = client.get('/data?filter_type=day&start_date=2023-01-01')
    assert response.status_code == 200

def test_pump_data(client):
    response = client.get('/pump_data?filter_type=day&start_date=2023-01-01')
    assert response.status_code == 200

def test_get_top_clients(client):
    response = client.get('/get-top-clients?filter_type=day&start_date=2023-01-01')
    assert response.status_code == 200

def test_delete_governorate(client):
    response = client.post('/add_governorate', json={'name': 'Test Governorate'})
    governorate_id = response.get_json().get('id')

    response = client.delete(f'/delete_governorate/{governorate_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Governorate deleted successfully!'

def test_delete_station(client):
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    response = client.post('/add_station', json={'name': 'Test Station', 'governorate_name': 'Test Governorate'})
    station_id = response.get_json().get('id')

    response = client.delete(f'/delete_station/{station_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Station deleted successfully!'

def test_get_stations(client):
    response = client.get('/get_stations')
    assert response.status_code == 200
    stations = response.get_json()
    assert isinstance(stations, list)
    # Add more assertions based on the expected data



def test_update_station(client):
    client.post('/add_governorate', json={'name': 'Test Governorate'})
    response = client.post('/add_station', json={'name': 'Old Station', 'governorate_name': 'Test Governorate'})
    station_id = response.get_json().get('id')

    updated_station_data = {'name': 'New Station', 'governorate_name': 'Test Governorate'}
    response = client.put(f'/update_station/{station_id}', json=updated_station_data)
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Station updated successfully!'

def test_start_processing(client):
    response = client.post('/start_processing')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Processing started'

def test_stop_processing(client):
    response = client.post('/stop_processing')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Processing stopped'

def test_interface_user(client):
    # Assuming the user is already logged in and session is set correctly
    with client.session_transaction() as session:
        session['username'] = 'testuser'
        session['user_role'] = 'Simple User'

    response = client.get('/interface_user')
    assert response.status_code == 200

def test_fetch_data(client):
    response = client.post('/fetch_data', data={
        'date_filter_type': 'day',
        'filter_date': '2023-01-01'
    })
    assert response.status_code == 200

def test_download_excel(client):
    response = client.post('/download_excel', data={
        'start_date': '2023-01-01',
        'end_date': '2023-01-02'
    })
    assert response.status_code == 200

def test_initial_data(client):
    response = client.get('/initial_data')
    assert response.status_code == 200

def test_get_total_vehicles(client):
    response = client.get('/api/total_vehicles?filter_type=day&date=2023-01-01')
    assert response.status_code == 200

def test_get_debit_vl(client):
    response = client.get('/api/debit_vl?filter_type=day&date=2023-01-01')
    assert response.status_code == 200

def test_get_debit_vp(client):
    response = client.get('/api/debit_vp?filter_type=day&date=2023-01-01')
    assert response.status_code == 200

def test_get_unique_zones(client):
    response = client.get('/api/unique_zones')
    assert response.status_code == 200

def test_get_vehicles_by_class(client):
    response = client.get('/api/vehicles_by_class?filter_type=day&date=2023-01-01')
    assert response.status_code == 200

def test_get_analysis_by_zone(client):
    response = client.get('/api/analysis_by_zone?filter_type=day&date=2023-01-01')
    assert response.status_code == 200

def test_registre(client):
    response = client.get('/registre')
    assert response.status_code == 200

def test_get_frame_data(client):
    response = client.get('/get_frame_data')
    assert response.status_code == 200

def test_upload(client):
    data = {
        'file': (io.BytesIO(b'my file contents'), 'test.mp4')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200

def test_video_feed(client):
    response = client.get('/video_feed')
    assert response.status_code == 200
