# main.py
from flask import Flask, request, jsonify
from utils import mask_pii
from models import classify_text

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok"})

@app.route("/classify", methods=["POST"])
def classify():
    data = request.get_json(force=True)
    email = data.get("input_email_body", "")
    masked_email, entities = mask_pii(email)
    category = classify_text(masked_email)
    return jsonify(
        {
            "input_email_body": email,
            "list_of_masked_entities": entities,
            "masked_email": masked_email,
            "category_of_the_email": category,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
