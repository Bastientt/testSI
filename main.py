import os
import sqlite3
import base64
import bcrypt
from flask import Flask, request, render_template, jsonify, session
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.secret_key = "secret_key"  # Change cette clé pour plus de sécurité

# Connexion à la base de données
def get_db():
    conn = sqlite3.connect('photos.db')
    conn.row_factory = sqlite3.Row
    return conn

def save_to_db(image_data, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO photos (image, user_id) VALUES (?, ?)", (image_data, user_id))
    conn.commit()
    photo_id = cursor.lastrowid
    conn.close()
    return photo_id

def get_images():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, image FROM photos")
    photos = cursor.fetchall()
    conn.close()
    return photos

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Champs manquants"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return jsonify({"message": "Utilisateur créé avec succès"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Nom d'utilisateur déjà pris"}), 409
    finally:
        conn.close()


@app.route('/photosPage', methods=['GET'])
def photo_page():
    if "user_id" not in session:
        return jsonify({"error": "Non autorisé"}), 401  # Vérifie si l'utilisateur est connecté

    return render_template('index.html') 


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Champs manquants"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({"message": "Connexion réussie"}), 200
    else:
        return jsonify({"error": "Identifiants incorrects"}), 401

@app.route('/upload', methods=['POST'])
def upload_file():
    if "user_id" not in session:
        return jsonify({"error": "Non autorisé"}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    image_data = file.read()
    photo_id = save_to_db(image_data, session["user_id"])

    return jsonify({'message': 'Image enregistrée', 'id': photo_id})

@app.route('/photos')
def photos():
    if "user_id" not in session:
        return jsonify({"error": "Non autorisé"}), 401

    photos = get_images()
    photo_list = []
    for id, image_data in photos:
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        photo_list.append({'id': id, 'image': image_base64})
    return jsonify(photo_list)

if __name__ == '__main__':
    app.run(debug=True)
