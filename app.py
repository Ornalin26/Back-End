from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

# MongoDB Connection URI (replace with your credentials securely)
uri = "mongodb+srv://ByeByeExpired:VlbKjtFuYvgw0lAS@cluster0.rcivs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Connect to MongoDB
client = MongoClient(uri)
db = client["ByeByeExpired"]
users_collection = db['users']
items_collection = db['items']

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# API สำหรับดึงข้อมูลสินค้าของผู้ใช้
@app.route('/get_items/<user_id>', methods=['GET'])
def get_items(user_id):
    items = list(items_collection.find({"user_id": ObjectId(user_id)}))
    for item in items:
        item['_id'] = str(item['_id'])
        item['user_id'] = str(item['user_id'])
    return jsonify(items), 200

# API สำหรับการเพิ่มสินค้า
@app.route('/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    item = {
        "photo": data['photo'],
        "name": data['name'],
        "storage": data['storage'],
        "storage_date": data['storage_date'],
        "expiration_date": data['expiration_date'],
        "quantity": data['quantity'],
        "note": data['note'],
        "user_id": ObjectId(data['user_id'])
    }
    result = items_collection.insert_one(item)
    return jsonify({"message": "Item added successfully", "id": str(result.inserted_id)}), 201

# API สำหรับการเข้าสู่ระบบ
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users_collection.find_one({"email": data['email']})
    
    # ตรวจสอบว่ารหัสผ่านถูกเก็บในรูปแบบ hash หรือ plain text
    if user and check_password_hash(user['password'], data['password']):
        user_id = user['_id']
        items = list(items_collection.find({"user_id": user_id}))
        for item in items:
            item['_id'] = str(item['_id'])
        return jsonify({"message": "Login successful", "items": items}), 200
    elif user and user['password'] == data['password']:  # ใช้ตรง ๆ ถ้ารหัสผ่านไม่ถูกแฮช
        user_id = user['_id']
        items = list(items_collection.find({"user_id": user_id}))
        for item in items:
            item['_id'] = str(item['_id'])
        return jsonify({"message": "Login successful", "items": items}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # ตรวจสอบว่า password กับ confirmPassword ตรงกันหรือไม่
    if data['password'] != data['confirmPassword']:
        return jsonify({"message": "Passwords do not match"}), 400

    # เก็บรหัสผ่านโดยการแฮช
    user = {
        "full_name": data['fullName'],  # เก็บชื่อเต็ม
        "email": data['email'],
        "password": generate_password_hash(data['password']),  # เข้ารหัสรหัสผ่าน
        "created_at": "2025-03-13T12:00:00Z"
    }

    result = users_collection.insert_one(user)
    
    return jsonify({"message": "User registered successfully", "id": str(result.inserted_id)}), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)