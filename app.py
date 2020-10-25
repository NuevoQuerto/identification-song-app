from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import os
from tinytag import TinyTag

UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("FormUpload.html", alert=True), 200
    
@app.route("/songs", methods=["POST"])
def upload_audio():
    data = [
        {
            "artist": "a",
            "lyrics": "sdasadsda"
        },
        {
            "artist": "b",
            "lyrics": "sdasadsda"
        }
    ]
    audio = request.files["audio"]
    language = request.form["language"]
    allowed_mimes = ["audio/mp3", "audio/mpeg", "audio/ogg", "audio/wav"]
    allowed_language_models = ["en-US_NarrowbandModel"]
    
    # Cek MIME Type
    if audio.content_type not in allowed_mimes:
        return "File Harus {0}".format(",".join(supported_mimes)), 400
        
    # Cek Durasi
    filename = secure_filename(audio.filename)
    audio.save(os.path.join(app.config["UPLOAD_FOLDER"], filename)) # Simpan file ke folder uploads
    tag = TinyTag.get("{0}/{1}".format(UPLOAD_FOLDER, filename))
    if int(tag.duration) > 15:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # Hapus file
        return "Durasi maksimal audio adalah 15 detik", 400
        
    # Cek Bahasa
    if language not in allowed_language_models:
        return "Maaf Bahasa Tidak Disupport", 400
        
    # Mengirim file audio ke IBM Speech to Text API
    
    
    return render_template("ResultPage.html", songs=data), 200
