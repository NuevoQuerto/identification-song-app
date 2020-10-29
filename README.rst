Identification Song APP
=======================

Untuk Memenuhi Tugas Rekayasa Perangkat Lunak

Installing
----------
- Buat akun IBM dan service Speech to Text disini: https://www.ibm.com/cloud/watson-speech-to-text 
- Download dan install FFmpeg disini: https://ffmpeg.org/
- Import identification_song.sql ke database (MySQL)
- Ubah .env.example menjadi .env, lalu sesuaikan WATSON_API_KEY, WATSON_SERVICE_URL dan SQLALCHEMY_DATABASE_URI
- Jalankan perintah ``pip install -r requirements.txt``
- Jalankan perintah ``flask run``

Enjoy
