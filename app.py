from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import settings # Reading Environment Variables
import os
import logging
import json
from pydub import AudioSegment # Manipulate Audio
from ibm_watson import SpeechToTextV1 # Audio to Text
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator # AUTH

app = Flask(__name__)

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
    allowed_language_models = ["en-US_BroadbandModel"]
    
    # Cek MIME Type
    #return audio.content_type.split("/",1)[1]
    if audio.content_type not in allowed_mimes:
        return "File Harus {0}".format(",".join(allowed_mimes)), 400
        
    # Cek Durasi
    filename = secure_filename(audio.filename)
    audio.save(os.path.join(settings.UPLOAD_FOLDER, filename)) # Simpan audio file ke folder uploads
    song = AudioSegment.from_file("{0}/{1}".format(settings.UPLOAD_FOLDER, filename), format=audio.content_type.split("/",1)[1])
    song_duration_in_seconds = len(song) / 1000
    if int(song_duration_in_seconds) > 15:
        os.remove(os.path.join(settings.UPLOAD_FOLDER, filename)) # Hapus file
        return "Durasi maksimal audio adalah 15 detik", 400
    louder_song = song.normalize()
    louder_song.export("{0}/louder-{1}".format(settings.UPLOAD_FOLDER, filename), format=audio.content_type.split("/",1)[1])
        
    # Cek Bahasa
    if language not in allowed_language_models:
        return "Maaf Bahasa Tidak Disupport", 400
        
    # Mengirim file audio ke IBM Speech to Text API
    # Authentication
    authenticator = IAMAuthenticator(settings.WATSON_API_KEY)
    speech_to_text = SpeechToTextV1(
        authenticator=authenticator
    )
    speech_to_text.set_service_url(settings.WATSON_SERVICE_URL)
    # Sending/Recognizing
    with open("{0}/louder-{1}".format(settings.UPLOAD_FOLDER, filename), "rb") as audio_file:
        speech_recognition_results = speech_to_text.recognize(
            audio=audio_file,
            content_type=audio.content_type,
            model=language
        ).get_result()
        logging.error(json.dumps(speech_recognition_results, indent=2))
        return speech_recognition_results
    
    
    return render_template("ResultPage.html", songs=data), 200
