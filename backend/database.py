import sqlite3

def init_db():
    conn = sqlite3.connect('photos.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')

    # Création de la table photos avec une clé étrangère vers users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB NOT NULL,
            user_id INTEGER REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de données initialisée.")

if __name__ == '__main__':
    init_db()
