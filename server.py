from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
from pathlib import Path
from digital_signature import DigitalSignature

app = Flask(__name__)
CORS(app)

CSV_FILE = 'users_db.csv'
DB_FIELDS = ['id', 'phone', 'passport', 'full_name', 'address', 'tariff', 'balance']

ds = DigitalSignature()
if not ds.load_keys():
    ds.generate_keys()

@app.route("/sign", methods=["POST"])
def sign_data():
    if not request.is_json:
        return jsonify({"error": "Требуется JSON"}), 400
    
    data = request.json.get("data")
    if not data:
        return jsonify({"error": "Не указаны данные для подписи"}), 400
    
    try:
        signature = ds.sign_data(data)
        return jsonify({"signature": signature})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify", methods=["POST"])
def verify_signature():
    if not request.is_json:
        return jsonify({"error": "Требуется JSON"}), 400
    
    data = request.json.get("data")
    signature = request.json.get("signature")
    
    if not data or not signature:
        return jsonify({"error": "Не указаны данные или подпись"}), 400
    
    try:
        is_valid = ds.verify_signature(data, signature)
        return jsonify({"valid": is_valid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def init_db():
    """Создает CSV файл, если его нет"""
    if not Path(CSV_FILE).exists():
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
            writer.writeheader()
            writer.writerow({
                'id': 1,
                'phone': '+71234567890',
                'passport': '1234 567890',
                'full_name': 'Иванов Иван Иванович',
                'address': 'Москва',
                'tariff': 'Стандарт',
                'balance': '100'
            })

def load_users():
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_users(users):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=DB_FIELDS)
        writer.writeheader()
        writer.writerows(users)

@app.route("/")
def index():
    return "<h2>✅ Сервер работает. Используйте /login, /update, /users</h2>"

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

@app.route("/login", methods=["POST"])
def login():
    print("Received login request:", request.json)
    init_db()
    if not request.is_json:
        return jsonify({"error": "Требуется JSON"}), 400

    data = request.get_json()
    phone = data.get("phone", "").strip()
    passport = data.get("passport", "").strip().replace(" ", "")  # Удаляем пробелы в паспорте

    users = load_users()
    print("Loaded users from CSV:", users)
    for user in users:
        # Нормализуем данные перед сравнением
        db_phone = user["phone"].strip()
        db_passport = user["passport"].strip().replace(" ", "")
        
        if db_phone == phone and db_passport == passport:
            return jsonify(user)

    return jsonify({"error": "Пользователь не найден"}), 404

@app.route("/update", methods=["POST"])
def update_user():
    data = request.get_json()
    user_id = str(data.get("id"))
    if not user_id:
        return jsonify({"error": "ID не указан"}), 400

    users = load_users()
    for user in users:
        if user['id'] == user_id:
            user["address"] = data.get("address", user.get("address", ""))
            user["tariff"] = data.get("tariff", user.get("tariff", ""))
            user["balance"] = data.get("balance", user.get("balance", ""))
            save_users(users)
            return jsonify({"message": "Данные обновлены"}), 200
    return jsonify({"error": "Пользователь не найден"}), 404

@app.route("/users", methods=["GET"])
def get_users():
    init_db()
    return jsonify(load_users())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
