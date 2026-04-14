import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load .env file manually if it exists so we don't depend on python-dotenv
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key.strip()] = val.strip(' "\'')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ecap-secure-key-2026-vbit')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "instance", "ecap.db")}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    OTP_EXPIRY_SECONDS = 120  # OTP valid for 2 minutes
    MAX_LOGIN_ATTEMPTS = 5
    STEP_UP_EXPIRY_SECONDS = 120  # Step-up access expires in 2 minutes

    # --- Email / SMTP Settings ---
    # Use a Gmail account with an App Password (NOT your real Gmail password).
    # To generate: Google Account → Security → 2FA → App Passwords
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your_gmail@gmail.com')  # <-- change this
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'your_app_password_here') # <-- change this
    MAIL_SENDER_NAME = 'VBIT ECAP System'
