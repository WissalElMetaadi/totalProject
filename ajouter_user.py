from app import app, db, User
from werkzeug.security import generate_password_hash

# Créer un utilisateur
def create_user(username, password):
    hashed_password = generate_password_hash(password)
    user = User(username=username, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()

# Exemple d'utilisation
if __name__ == '__main__':
    with app.app_context():
        create_user('john_doe', 'password123')
        create_user('jane_doe', 'secret456')
        print("Utilisateurs créés avec succès !")
