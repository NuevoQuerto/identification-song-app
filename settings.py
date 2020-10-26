import os
from dotenv import load_dotenv
load_dotenv()

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
WATSON_API_KEY = os.getenv("WATSON_API_KEY")
WATSON_SERVICE_URL = os.getenv("WATSON_SERVICE_URL")