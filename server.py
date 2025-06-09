from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

users_db = [
    {"id": 1, "phone": "+71234567890", "passport": "1234 567890", "full_name": "Иванов Иван Иванович",
     "address": "Москва", "tariff": "Стандарт", "balance": "100"}
]
next_id = 2

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    phone = data.get("phone")
    passport = data.get("passport")
    for user in users_db:
        if user["phone"] == phone and user["passport"] == passport:
            return jsonify(user)
    # Добавляем нового пользователя, если не найден
    global next_id
    new_user = {
        "id": next_id,
        "phone": phone,
        "passport": passport,
        "full_name": data.get("full_name", "Новый пользователь"),
        "address": "",
        "tariff": "",
        "balance": "0"
    }
    users_db.append(new_user)
    next_id += 1
    return jsonify(new_user)

@app.route("/update", methods=["POST"])
def update_user():
    data = request.get_json()
    user_id = data.get("id")
    if user_id is None:
        return jsonify({"error": "ID пользователя не указан"}), 400
    for user in users_db:
        if user["id"] == user_id:
            user["address"] = data.get("address", user.get("address", ""))
            user["tariff"] = data.get("tariff", user.get("tariff", ""))
            user["balance"] = data.get("balance", user.get("balance", ""))
            return jsonify({"message": "Данные обновлены"}), 200
    return jsonify({"error": "Пользователь не найден"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)