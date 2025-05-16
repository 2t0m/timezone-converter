from flask import Flask, request, jsonify, send_file
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/convert", methods=["POST"])
def convert_timezone():
    url = request.json.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    if not url.endswith(".ics"):
        return jsonify({"error": "Invalid URL format"}), 400

    try:
        # Télécharger le fichier .ics
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download .ics file"}), 500

        content = response.text

        # Modifier le fuseau horaire
        content = content.replace("TZID=GMT", "TZID=Europe/Paris")

        # Sauvegarder le fichier modifié
        output_path = os.path.join(UPLOAD_FOLDER, "modified_calendar.ics")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
