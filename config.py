import os

# Flask settings
SECRET_KEY = os.environ.get("SECRET_KEY") 
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True


# Google Calendar API
CREDENTIALS_FILE = os.environ.get("CREDENTIALS_FILE")  # path to .json
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = os.environ.get("REDIRECT_URI")
