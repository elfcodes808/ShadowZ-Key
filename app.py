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
    expiry_days = int(data.get("expiry_days", 7))  # default 7 days
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

@app.route('/checkkey', methods=
