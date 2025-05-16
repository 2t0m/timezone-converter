from flask import Flask, request, send_file, jsonify
import os
import requests
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/ancien_cal=<path:calendar_url>", methods=["GET"])
def modify_and_serve(calendar_url):
    """
    Télécharge, modifie et renvoie le fichier .ics avec le fuseau horaire Europe/Paris.
    """
    try:
        # Décoder l'URL
        calendar_url = calendar_url.strip()

        # Télécharger le fichier .ics
        response = requests.get(calendar_url)
        if response.status_code != 200:
            return jsonify({"error": "Unable to download .ics file"}), 500

        content = response.text

        # Modifier le fuseau horaire
        content = content.replace("TZID=GMT", "TZID=Europe/Paris")

        # Générer un nom de fichier basé sur le hash de l'URL
        filename = "modified_cal.ics"
        output_path = os.path.join(UPLOAD_FOLDER, filename)

        # Enregistrer le fichier modifié
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Envoyer le fichier
        return send_file(output_path, as_attachment=True, download_name="cal.ics")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Récupère le port assigné par Render (ou 5000 par défaut pour le développement local)
    port = int(os.getenv("PORT", 5000))
    # Écoute sur 0.0.0.0 pour être accessible
    app.run(host="0.0.0.0", port=port, debug=True)

