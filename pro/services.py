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

    # Azure config – populated from app config at runtime
    _azure_config = {}

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
    def generate_otp(username, expiry_seconds=300):
        """
        generateOTP() - Generate a random 6-digit numerical OTP and save to DB.
        """
        from datetime import datetime, timedelta, timezone
        from models import db, PersistentOTP
        
        otp_code = str(random.randint(100000, 999999))
        expiry = datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)
        
        # Upsert the OTP in DB with concurrency handling
        otp_record = PersistentOTP.query.filter_by(target_id=username).first()
        if not otp_record:
            otp_record = PersistentOTP(target_id=username)
            db.session.add(otp_record)
        
        try:
            otp_record.code = otp_code
            otp_record.expires_at = expiry
            db.session.commit()
        except Exception:
            db.session.rollback()
            # Handle race condition: if another thread inserted it simultaneously
            otp_record = PersistentOTP.query.filter_by(target_id=username).first()
            if otp_record:
                otp_record.code = otp_code
                otp_record.expires_at = expiry
                db.session.commit()
        
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
        sender_display = "ECAP Admin Control"

        if not mail_user or not mail_pass or mail_pass == 'your_app_password_here':
            print(f"[SIMULATION] Email OTP [{otp_code}] -> {email} (Purpose: {purpose})")
            return {'success': True, 'method': 'simulation', 'sent_to': email}

        # Build email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Official Alert: {purpose} Code'
        msg['From']    = f"{sender_display} <{mail_user}>"
        msg['To']      = email

        plain_body = f"Hello {username},\n\nYour official security code for {purpose} is: {otp_code}\n\nValid for 3 minutes. Please do not share this with anyone."
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
                <div style="background: #0033cc; color: #fff; padding: 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">ECAP SECURITY ADMIN</h1>
                </div>
                <div style="padding: 30px;">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>A request was made for <strong>{purpose}</strong>. Please use the following official verification code to proceed:</p>
                    <div style="background: #f4f4f4; padding: 20px; text-align: center; border-radius: 4px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #0033cc;">{otp_code}</span>
                    </div>
                    <p style="color: #666; font-size: 14px;">This code is valid for <strong>3 minutes</strong>. If you did not request this code, please ignore this email or contact the administrator immediately.</p>
                </div>
                <div style="background: #f9f9f9; padding: 15px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee;">
                    <p>&copy; 2026 ECAP Secure Campus System | Official Administration Correspondence</p>
                </div>
            </div>
        </body>
        </html>
        """
        
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

        message = f"Your {purpose} code is: {otp_code}. Valid for 3 minutes."

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
        """
        validateOTP() - Check if code is valid using persistent storage.
        """
        from datetime import datetime, timezone
        from models import db, PersistentOTP
        
        otp_record = PersistentOTP.query.filter_by(target_id=username).first()
        
        if not otp_record:
            return False
            
        if datetime.now(timezone.utc) > otp_record.expires_at.replace(tzinfo=timezone.utc):
            db.session.delete(otp_record)
            db.session.commit()
            return False
            
        if otp_record.code == entered_otp:
            # Success - burn the OTP
            db.session.delete(otp_record)
            db.session.commit()
            return True
            
        # Failed attempt - keep the OTP in store so user can try again if they mistyped
        return False

    @staticmethod
    def clear_otp(username):
        from models import db, PersistentOTP
        otp_record = PersistentOTP.query.filter_by(target_id=username).first()
        if otp_record:
            db.session.delete(otp_record)
            db.session.commit()
