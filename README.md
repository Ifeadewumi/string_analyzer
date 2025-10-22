# String Analyzer API

A RESTful API service that analyzes strings and stores their computed properties.  
Built with **Flask**, **SQLAlchemy**, and deployed on **Railway** for HNG Stage 1 (Backend).

---

## Features

For each analyzed string, the API computes and stores:
- `length`: Number of characters
- `is_palindrome`: Boolean for palindrome check (case-insensitive)
- `unique_characters`: Count of distinct characters
- `word_count`: Number of words separated by whitespace
- `sha256_hash`: SHA-256 hash (unique identifier)
- `character_frequency_map`: Mapping of each character to its occurrence count

---

## API Endpoints

### 1.  Create / Analyze String
**POST** `/strings`

**Request Body:**
```json
{
  "value": "racecar"
}
````

**Response (201 Created):**

```json
{
  "id": "e3b0...hash...",
  "value": "racecar",
  "properties": {
    "length": 7,
    "is_palindrome": true,
    "unique_characters": 4,
    "word_count": 1,
    "sha256_hash": "e3b0...hash...",
    "character_frequency_map": {
      "r": 2,
      "a": 2,
      "c": 2,
      "e": 1
    }
  },
  "created_at": "2025-10-20T12:00:00Z"
}
```

**Errors:**

* `400` Missing `value`
* `422` `value` not string
* `409` String already exists

---

### 2. Get Specific String

**GET** `/strings/{string_value}`
Example: `/strings/racecar`

**Response:**

```json
{
  "id": "...",
  "value": "racecar",
  "properties": { /* computed props */ },
  "created_at": "..."
}
```

---

### 3. Get All Strings (with filters)

**GET** `/strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a`

**Response:**

```json
{
  "data": [ /* array of strings */ ],
  "count": 15,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5,
    "max_length": 20,
    "word_count": 2,
    "contains_character": "a"
  }
}
```

**Error:** `400 Bad Request` for invalid parameter types.

---

### 4. Natural Language Filtering

**GET** `/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`

Supports examples like:

* `all single word palindromic strings`
* `strings longer than 10 characters`
* `palindromic strings that contain the letter z`

**Response:**

```json
{
  "data": [ /* results */ ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
```

---

### 5️. Delete String

**DELETE** `/strings/{string_value}`
Returns `204 No Content` on success.

---

## Local Setup

### Requirements

* Python 3.9 +
* pip
* virtualenv (recommended)

### Installation

```bash
git clone https://github.com/<your-username>/string-analyzer.git
cd string-analyzer
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate (for Windows)
pip install -r requirements.txt
```

### Run locally

```bash
python app.py
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Deployment (Railway)

1. Create a new Railway project.
2. Connect your GitHub repo.
3. Railway auto-detects Flask and deploys it.
4. Add an environment variable (if needed):

   * `PORT` → `8000`
5. Once deployed, test live:

   ```
   https://<your-app>.up.railway.app/health
   ```
Here's my live link: https://stringanalyzer-production-384b.up.railway.app/

---

## Testing (Examples)

### Create string

```bash
curl -X POST https://<your-app>.up.railway.app/strings \
     -H "Content-Type: application/json" \
     -d '{"value": "madam"}'
```

### Get string

```bash
curl https://<your-app>.up.railway.app/strings/madam
```

### Delete string

```bash
curl -X DELETE https://<your-app>.up.railway.app/strings/madam
```

---

## 🧑‍💻 Stack

* **Language:** Python 3
* **Framework:** Flask
* **Database:** SQLite + SQLAlchemy ORM
* **Hosting:** [Railway](https://stringanalyzer-production-384b.up.railway.app/)

---

## 👤 Author

* **Full Name:** *Ifeoluwa Adewumi*
* **Track:** Backend (Python/Flask)
* **HNG Stage:** 1

---

## 📄 License

MIT License — feel free to fork and improve.