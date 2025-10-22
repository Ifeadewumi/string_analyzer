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

# --------------------------
# GET /strings/{value}
# --------------------------
@app.route('/strings/<string_value>', methods=['GET'])
def get_specific_string(string_value):
    hash_value = compute_sha256(string_value)
    record = StringRecord.query.get(hash_value)

    if not record:
        return jsonify({"error": "String not found"}), 404

    return jsonify(record.to_dict()), 200


# --------------------------
# GET /strings (with filters)
# --------------------------
@app.route('/strings', methods=['GET'])
def get_all_strings():
    # Extract filters
    filters = {}
    query = StringRecord.query

    is_palindrome_param = request.args.get('is_palindrome')
    if is_palindrome_param is not None:
        filters['is_palindrome'] = is_palindrome_param.lower() == 'true'
        query = query.filter_by(is_palindrome=filters['is_palindrome'])

    min_length = request.args.get('min_length', type=int)
    if min_length is not None:
        filters['min_length'] = min_length
        query = query.filter(StringRecord.length >= min_length)

    max_length = request.args.get('max_length', type=int)
    if max_length is not None:
        filters['max_length'] = max_length
        query = query.filter(StringRecord.length <= max_length)

    word_count = request.args.get('word_count', type=int)
    if word_count is not None:
        filters['word_count'] = word_count
        query = query.filter_by(word_count=word_count)

    contains_character = request.args.get('contains_character')
    if contains_character:
        filters['contains_character'] = contains_character
        query = query.filter(StringRecord.value.contains(contains_character))

    # Get results
    records = query.all()
    data = [r.to_dict() for r in records]

    return jsonify({
        "data": data,
        "count": len(data),
        "filters_applied": filters
    }), 200


# --------------------------
# DELETE /strings/{value}
# --------------------------
@app.route('/strings/<string_value>', methods=['DELETE'])
def delete_string(string_value):
    hash_value = compute_sha256(string_value)
    record = StringRecord.query.get(hash_value)

    if not record:
        return jsonify({"error": "String not found"}), 404

    db.session.delete(record)
    db.session.commit()
    return '', 204


# --------------------------
# Natural Language Filtering
# --------------------------
@app.route('/strings/filter-by-natural-language', methods=['GET'])
def filter_by_natural_language():
    query_text = request.args.get('query', '')
    parsed_filters = {}

    if not query_text:
        return jsonify({"error": "Missing query parameter"}), 400

    # Very simple keyword-based NLP heuristic
    q = query_text.lower()

    if "palindromic" in q:
        parsed_filters["is_palindrome"] = True
    if "single word" in q or "one word" in q:
        parsed_filters["word_count"] = 1
    if "longer than" in q:
        try:
            num = int(q.split("longer than")[1].split()[0])
            parsed_filters["min_length"] = num + 1
        except Exception:
            pass
    if "contain" in q:
        for ch in "abcdefghijklmnopqrstuvwxyz":
            if f" {ch}" in q:
                parsed_filters["contains_character"] = ch
                break

    if not parsed_filters:
        return jsonify({"error": "Unable to parse natural language query"}), 400

    query = StringRecord.query
    if "is_palindrome" in parsed_filters:
        query = query.filter_by(is_palindrome=True)
    if "word_count" in parsed_filters:
        query = query.filter_by(word_count=parsed_filters["word_count"])
    if "min_length" in parsed_filters:
        query = query.filter(StringRecord.length >= parsed_filters["min_length"])
    if "contains_character" in parsed_filters:
        query = query.filter(StringRecord.value.contains(parsed_filters["contains_character"]))

    results = query.all()
    data = [r.to_dict() for r in results]

    return jsonify({
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query_text,
            "parsed_filters": parsed_filters
        }
    }), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)