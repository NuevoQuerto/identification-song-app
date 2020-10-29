from flask import request, render_template
from app import app, settings
from werkzeug.utils import secure_filename
import os
import logging
import json
from pydub import AudioSegment # Manipulate Audio
from ibm_watson import SpeechToTextV1 # Audio to Text
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator # AUTH
from app.models.song import Song

@app.route("/")
def index():
    return render_template("FormUpload.html", alert=True), 200
    
@app.route("/songs", methods=["POST"])
def upload_audio():
    audio = request.files["audio"]
    language = request.form["language"]
    allowed_mimes = ["audio/mp3", "audio/mpeg", "audio/ogg", "audio/wav"]
    allowed_language_models = ["en-US_BroadbandModel"]
    songs = [] # Data JSON untuk ditampilkan
    
    # Cek MIME Type
    #return audio.content_type.split("/",1)[1]
    if audio.content_type not in allowed_mimes:
        return "File Harus {0}".format(",".join(allowed_mimes)), 400
        
    # Cek Bahasa
    if language not in allowed_language_models:
        return "Maaf Bahasa Tidak Disupport", 400    
    
    # Save audio file
    filename = secure_filename(audio.filename)
    save_path = os.path.join(settings.UPLOAD_FOLDER, filename) # Simpan audio file ke folder uploads
    audio.save(save_path)
    
    # Manipulate audio
    song = AudioSegment.from_file(save_path, format=audio.content_type.split("/",1)[1])
    song_duration_in_seconds = len(song) / 1000
    # Cek durasi audio
    if int(song_duration_in_seconds) > 15:
        os.remove(save_path) # Hapus audio file
        return "Durasi maksimal audio adalah 15 detik", 400
    # Normalize audio volume
    save_path = os.path.join(settings.UPLOAD_FOLDER, "normalize-" + filename)
    normalizing_song = song.normalize()
    normalizing_song.export(save_path, format=audio.content_type.split("/",1)[1])
        
    # Mengirim file audio ke IBM Speech to Text API
    # Authentication
    authenticator = IAMAuthenticator(settings.WATSON_API_KEY)
    speech_to_text = SpeechToTextV1(
        authenticator=authenticator
    )
    speech_to_text.set_service_url(settings.WATSON_SERVICE_URL)
    # Sending/Recognizing
    with open(save_path, "rb") as audio_file:
        speech_recognition_results = speech_to_text.recognize(
            audio=audio_file,
            content_type=audio.content_type,
            model=language,
            speech_detector_sensitivity=0.5,
            background_audio_suppression=0.5,
            smart_formatting=True,
            profanity_filter=False
        ).get_result()
        logging.error(json.dumps(speech_recognition_results, indent=2))
        
        # Cek apakah mendapatkan hasil transkrip
        if len(speech_recognition_results["results"]) > 0:
            # Simpan transkrip audio
            transcripts = {"data": []}
            for transcript in speech_recognition_results["results"]:
                transcripts["data"].append(transcript["alternatives"][0])
            max_confidence_transcript = max(transcripts["data"], key=lambda x:x["confidence"]) # Ambil transkrip audio dengan nilai confidence tertinggi
            # Cari lagu berdasarkan lirik yang didapat dari hasil max_confidence_transcript
            for song in Song.query.filter(Song.lyrics.match(max_confidence_transcript["transcript"])).limit(10).all():
                logging.error(song)
                songs.append({"artist": song.artist, "releases": song.releases, "title": song.title}) # Masukkan data lagu
    
    return render_template("ResultPage.html", songs=songs), 200 # Tampilkan hasil