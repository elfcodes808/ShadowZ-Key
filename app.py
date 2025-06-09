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
    return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def generate_key():
    prefix = "SHADOWZ-"
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return (prefix + suffix).upper()

@app.route('/')
def index():
    return "ShadowZ Key System API is running."

@app.route('/addkey', methods=['POST'])
def add_key():
    data = request.json
    expiry_days = data.get("expiry_days")  # Can be "lifetime" or int
    hwid_lock = data.get("hwid_lock", False)

    keys = load_keys()
    key = generate_key()

    if expiry_days == "lifetime":
        expiry_date = "lifetime"
    else:
        try:
            expiry_days = int(expiry_days)
        except (TypeError, ValueError):
            expiry_days = 7  # default
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
    key = data.get("key", "").strip().upper()
    hwid = data.get("hwid", "").strip()

    if not key:
        return jsonify({"success": False, "message": "No key provided"}), 400

    keys = load_keys()

    if key not in keys:
        return jsonify({"success": False, "message": "Invalid key"})

    key_data = keys[key]
    expiry_date_raw = key_data.get("expiry_date", "")

    if expiry_date_raw != "lifetime":
        try:
            expiry_date = datetime.fromisoformat(expiry_date_raw)
            if datetime.utcnow() > expiry_date:
                return jsonify({"success": False, "message": "Key expired"})
        except ValueError:
            return jsonify({"success": False, "message": "Invalid expiry format"})

    if key_data.get("hwid_lock", False):
        if key_data.get("used_hwid") is None:
            key_data["used_hwid"] = hwid
            save_keys(keys)
        elif key_data["used_hwid"] != hwid:
            return jsonify({"success": False, "message": "HWID mismatch"})

    return jsonify({
        "success": True,
        "message": "Key valid",
        "type": "lifetime" if expiry_date_raw == "lifetime" else "timed"
    })

@app.route('/delkey', methods=['DELETE'])
def delete_key():
    data = request.json
    key_to_delete = data.get("key", "").strip().upper()

    keys = load_keys()

    if key_to_delete in keys:
        del keys[key_to_delete]
        save_keys(keys)
        return jsonify({"success": True, "message": f"Key {key_to_delete} deleted successfully."})
    else:
        return jsonify({"success": False, "message": "Key not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
