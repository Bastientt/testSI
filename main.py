import os
import sqlite3
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

def save_to_db(image_data):
    conn = sqlite3.connect('photos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO photos (image) VALUES (?)", (image_data,))
    conn.commit()
    photo_id = cursor.lastrowid
    conn.close()
    return photo_id

def get_images():
    conn = sqlite3.connect('photos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, image FROM photos")
    photos = cursor.fetchall()
    conn.close()
    return photos

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    image_data = file.read()
    photo_id = save_to_db(image_data)

    return jsonify({'message': 'Image enregistrée', 'id': photo_id})

@app.route('/photos')
def photos():
    photos = get_images()
    photo_list = [{'id': id, 'image': image.hex()} for id, image in photos]
    return jsonify(photo_list)

if __name__ == '__main__':
    app.run(debug=True)
