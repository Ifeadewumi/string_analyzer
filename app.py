from flask import Flask, jsonify

app = Flask(__name__)

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
        "message": "Flask app is working fine!"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
