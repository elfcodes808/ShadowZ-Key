from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import random
import string

app = Flask(__name__)
CORS(app)

KEYS_FILE = "keys.json"

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def generate_key():
    prefix = "ShadowZ-"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return prefix + suffix

@app.route('/')
def index():
    return "ShadowZ Key System API is running."

@app.route('/addkey', methods=['POST'])
def add_key():
    data = request.json
    expiry_days = int(data.get("expiry_days", 7))  # default to 7 days if not specified
    hwid_lock = data.get("hwid_lock", False)

    keys = load_keys()
    key = generate_key()

    expiry_date = (datetime.utcnow() + timedelta(days=expiry_days)).isoformat()

    keys[key] = {
        "expiry_date": expiry_date,
        "hwid_lock": hwid_lock,
        "used_by": None,
        "used_hwid": None
    }

    save_keys(keys)

    return jsonify({"success": True, "key": key})

@app.route('/checkkey', methods=['POST'])
def check_key():
    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")

    if not key:
        return jsonify({"success": False, "message": "No key provided"}), 400

    keys = load_keys()

    if key not in keys:
        return jsonify({"success": False, "message": "Invalid key"})

    key_data = keys[key]
    expiry_date = datetime.fromisoformat(key_data["expiry_date"])

    if datetime.utcnow() > expiry_date:
        return jsonify({"success": False, "message": "Key expired"})

    if key_data["hwid_lock"]:
        if key_data["used_hwid"] is None:
            # First time use, lock HWID
            key_data["used_hwid"] = hwid
            save_keys(keys)
        elif key_data["used_hwid"] != hwid:
            return jsonify({"success": False, "message": "HWID mismatch"})

    return jsonify({"success": True, "message": "Key valid"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
