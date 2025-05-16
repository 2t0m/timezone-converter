from flask import Flask, request, send_file, jsonify
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/ancien_cal=<path:calendar_url>", methods=["GET"])
def modify_and_serve(calendar_url):
    """
    Télécharge, modifie et renvoie le fichier .ics avec le fuseau horaire Europe/Paris.
    """
    try:
        # Télécharger le fichier .ics
        response = requests.get(calendar_url)
        if response.status_code != 200:
            return jsonify({"error": "Unable to download .ics file"}), 500

        content = response.text

        # Remplacement des TZID par Europe/Paris
        # Ces TZID couvrent les principaux identifiants dans le fichier
        tzid_replacements = {
            "TZID=W. Europe Standard Time": "TZID=Europe/Paris",
            "TZID=Greenwich Standard Time": "TZID=Europe/Paris",
            "TZID=Romance Standard Time": "TZID=Europe/Paris"
        }

        for old_tz, new_tz in tzid_replacements.items():
            content = content.replace(old_tz, new_tz)

        # Remplacer le bloc VTIMEZONE par une définition unique pour Europe/Paris
        vtimezone_block = """BEGIN:VTIMEZONE
TZID=Europe/Paris
BEGIN:STANDARD
DTSTART:16010101T030000
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:16010101T020000
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=3
END:DAYLIGHT
END:VTIMEZONE"""

        # Supprimer tous les blocs VTIMEZONE existants et insérer le nouveau
        content = "\n".join([
            line for line in content.splitlines() if not line.startswith("BEGIN:VTIMEZONE")
        ])
        content = content.replace("END:VTIMEZONE", "")
        content = content.replace("BEGIN:VEVENT", vtimezone_block + "\nBEGIN:VEVENT")

        # Sauvegarder le fichier modifié
        output_path = os.path.join(UPLOAD_FOLDER, "modified_cal.ics")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Envoyer le fichier
        return send_file(output_path, as_attachment=True, download_name="cal.ics")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
