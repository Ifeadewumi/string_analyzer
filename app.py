from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import json

app = Flask(__name__)

# --- Database setup ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///strings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Helper Functions ---

def compute_sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def is_palindrome(value: str) -> bool:
    cleaned = ''.join(c.lower() for c in value if c.isalnum())
    return cleaned == cleaned[::-1]

def get_character_frequency_map(value: str) -> dict:
    freq = {}
    for c in value:
        freq[c] = freq.get(c, 0) + 1
    return freq

def analyze_string(value: str) -> dict:
    words = value.split()
    return {
        "length": len(value),
        "is_palindrome": is_palindrome(value),
        "unique_characters": len(set(value)),
        "word_count": len(words),
        "sha256_hash": compute_sha256(value),
        "character_frequency_map": get_character_frequency_map(value)
    }

# --- Model ---
class StringRecord(db.Model):
    id = db.Column(db.String(64), primary_key=True)  # SHA-256 hash as ID
    value = db.Column(db.Text, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    is_palindrome = db.Column(db.Boolean, nullable=False)
    unique_characters = db.Column(db.Integer, nullable=False)
    word_count = db.Column(db.Integer, nullable=False)
    character_frequency_map = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "value": self.value,
            "properties": {
                "length": self.length,
                "is_palindrome": self.is_palindrome,
                "unique_characters": self.unique_characters,
                "word_count": self.word_count,
                "sha256_hash": self.id,
                "character_frequency_map": self.character_frequency_map
            },
            "created_at": self.created_at.isoformat() + "Z"
        }

# --- Routes ---
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to String Analyzer API 🚀",
        "status": "running"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Flask app with database connected!"
    })

@app.route('/strings', methods=['POST'])
def analyze_and_store_string():
    data = request.get_json()

    if not data or 'value' not in data:
        return jsonify({"error": "Missing 'value' field"}), 400

    value = data['value']
    if not isinstance(value, str):
        return jsonify({"error": "'value' must be a string"}), 422

    # Analyze
    props = analyze_string(value)
    string_id = props["sha256_hash"]

    # Check if already exists
    existing = StringRecord.query.get(string_id)
    if existing:
        return jsonify({"error": "String already exists"}), 409

    # Create new record
    record = StringRecord(
        id=string_id,
        value=value,
        length=props["length"],
        is_palindrome=props["is_palindrome"],
        unique_characters=props["unique_characters"],
        word_count=props["word_count"],
        character_frequency_map=props["character_frequency_map"]
    )

    db.session.add(record)
    db.session.commit()

    return jsonify(record.to_dict()), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)