"""
OTP Service - Aligned with Class Diagram OTPService class
Generates random 6-digit numerical OTPs like traditional SMS/Email services.
Sends real emails via Gmail SMTP using an App Password.
"""
import random
import time
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class OTPService:
    """
    OTPService from Class Diagram
    Attributes: otpCode, expiryTime
    Methods: generateOTP(), sendOTP(), validateOTP()
    """

    # In-memory OTP store: { username: { 'code': '123456', 'expires': timestamp } }
    _otp_store = {}

    # Azure config – populated from app config at runtime
    _azure_config = {}

    @classmethod
    def configure(cls, app_config):
        """Load SMTP and Azure settings from Flask app config."""
        cls._mail_config = {
            'server':   app_config.get('MAIL_SERVER', 'smtp.gmail.com'),
            'port':     app_config.get('MAIL_PORT', 587),
            'use_tls':  app_config.get('MAIL_USE_TLS', True),
            'username': app_config.get('MAIL_USERNAME', ''),
            'password': app_config.get('MAIL_PASSWORD', ''),
            'sender':   app_config.get('MAIL_SENDER_NAME', 'Security System'),
        }
        cls._azure_config = {
            'connection_string': app_config.get('AZURE_COMMUNICATION_CONNECTION_STRING', ''),
            'sender_phone':      app_config.get('AZURE_SENDER_PHONE_NUMBER', ''),
        }

    @staticmethod
    def generate_otp(username, expiry_seconds=120):
        """
        generateOTP() - Generate a random 6-digit numerical OTP.
        """
        otp_code = str(random.randint(100000, 999999))
        OTPService._otp_store[username] = {
            'code': otp_code,
            'expires': time.time() + expiry_seconds
        }
        return otp_code

    @staticmethod
    def send_otp(username, otp_code, method='email', target=None, purpose='Security Verification'):
        """
        sendOTP() - Send OTP via Email or SMS (Azure).
        """
        if method == 'email':
            return OTPService._send_email(username, otp_code, purpose)
        elif method == 'sms':
            return OTPService._send_sms(username, otp_code, target, purpose)
        return {'success': False, 'message': 'Invalid delivery method'}

    @staticmethod
    def _send_email(username, otp_code, purpose):
        """Internal method to send email via SMTP"""
        try:
            from models import Student
            student = Student.query.filter_by(student_id=username).first()
            # Enforce vbit domain for all except demo users 01, 02 which have specific emails in DB
            email = student.email if student and student.email else f'{username.lower()}@vbithyd.ac.in'
        except Exception:
            email = f'{username.lower()}@vbithyd.ac.in'

        cfg = OTPService._mail_config
        mail_user = cfg.get('username', '')
        mail_pass = cfg.get('password', '')

        if not mail_user or not mail_pass or mail_pass == 'your_app_password_here':
            print(f"[SIMULATION] Email OTP [{otp_code}] -> {email} (Purpose: {purpose})")
            return {'success': True, 'method': 'simulation', 'sent_to': email}

        # Build email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Your {purpose} Code'
        msg['From']    = f"Security System <{mail_user}>"
        msg['To']      = email

        plain_body = f"Hello {username},\n\nYour {purpose} code is: {otp_code}\n\nValid for 2 minutes."
        html_body = f"<html><body><h2>{purpose}</h2><p>Hello {username},</p><p>Your code is: <b>{otp_code}</b></p></body></html>"
        msg.attach(MIMEText(plain_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        def _send():
            try:
                with smtplib.SMTP(cfg['server'], cfg['port'], timeout=10) as smtp:
                    if cfg['use_tls']: smtp.starttls()
                    smtp.login(mail_user, mail_pass)
                    smtp.sendmail(mail_user, email, msg.as_string())
                print(f"[EMAIL SENT] OTP -> {email}")
            except Exception as exc:
                print(f"[EMAIL ERROR] {exc}")

        threading.Thread(target=_send, daemon=True).start()
        return {'success': True, 'method': 'email', 'sent_to': email}

    @staticmethod
    def _send_sms(username, otp_code, target_phone, purpose):
        """Internal method to send SMS via Azure Communication Services"""
        if not target_phone:
            return {'success': False, 'message': 'Phone number missing'}

        conn_str = OTPService._azure_config.get('connection_string')
        sender = OTPService._azure_config.get('sender_phone')

        message = f"Your {purpose} code is: {otp_code}. Valid for 2 minutes."

        # If Azure is not configured, simulate it
        if not conn_str or not sender:
            print(f"[AZURE SIMULATION] SMS OTP [{otp_code}] -> {target_phone} (Purpose: {purpose})")
            return {'success': True, 'method': 'simulation', 'sent_to': target_phone}

        def _send_azure():
            try:
                # Lazy import to avoid dependency issues if not installed
                from azure.communication.sms import SmsClient
                sms_client = SmsClient.from_connection_string(conn_str)
                sms_client.send(from_=sender, to=[target_phone], message=message)
                print(f"[AZURE SMS SENT] To: {target_phone}")
            except Exception as exc:
                print(f"[AZURE SMS ERROR] {exc}")

        threading.Thread(target=_send_azure, daemon=True).start()
        return {'success': True, 'method': 'sms', 'sent_to': target_phone}

    @staticmethod
    def validate_otp(username, entered_otp):
        stored = OTPService._otp_store.get(username)
        if not stored or time.time() > stored['expires']:
            OTPService._otp_store.pop(username, None)
            return False
        if stored['code'] == entered_otp:
            OTPService._otp_store.pop(username, None)
            return True
        return False

    @staticmethod
    def clear_otp(username):
        OTPService._otp_store.pop(username, None)
