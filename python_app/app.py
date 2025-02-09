from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return {"message": "Hello, Flask is running with Poetry!"}

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image = request.files["image"]
    return jsonify({"message": "Image received", "status_image" : 1, "filename": image.filename})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
