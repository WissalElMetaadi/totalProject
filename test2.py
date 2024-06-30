from pymongo import MongoClient
from bson.objectid import ObjectId

# Configuration
MONGO_URI = 'mongodb://localhost:27017/station_total'  # Update with your MongoDB URI
DATABASE_NAME = 'station_total'

# Test data identifiers
TEST_GOVERNORATE_NAME = 'Test Governorate'
TEST_STATION_NAME = 'Test Station'
TEST_USER_EMAIL = 'testuser@example.com'

def clean_test_data():
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]

    # Remove test governorates
    governorates_deleted = db.governorates.delete_many({'name': TEST_GOVERNORATE_NAME}).deleted_count
    print(f'Removed {governorates_deleted} test governorates')

    # Remove test stations
    stations_deleted = db.stations.delete_many({'name': TEST_STATION_NAME}).deleted_count
    print(f'Removed {stations_deleted} test stations')

    # Remove test users
    users_deleted = db.users.delete_many({'email': TEST_USER_EMAIL}).deleted_count
    print(f'Removed {users_deleted} test users')

    # Close connection
    client.close()

if __name__ == '__main__':
    clean_test_data()
