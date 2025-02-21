import sqlite3

def init_db():
    conn = sqlite3.connect('photos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("ok")

if __name__ == '__main__':
    init_db()
