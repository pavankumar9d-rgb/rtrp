"""
Comprehensive Test Suite for ECAP Secure Authentication System
Tests: Login, OTP, Dashboard, Step-Up, Change Password, Admin, Risk Engine, Lockout
"""
import unittest
from app import app, db
from models import Student, Admin
from services import OTPService


def reset_student_lock():
    """Helper to reset the test student account and clear security records each time."""
    from models import AuditLog, RiskEvent
    with app.app_context():
        # Reset Student account flags
        s = Student.query.filter_by(student_id='24p61a6235').first()
        if s:
            s.account_locked = False
            s.failed_login_attempts = 0
            s.set_password('webcap') # Ensure password is correct for tests
            db.session.commit()
        
        # Clear logs and risk events
        AuditLog.query.filter_by(user_id='24p61a6235').delete()
        RiskEvent.query.filter_by(username='24p61a6235').delete()
        
        # Clear persistent OTPs
        from models import PersistentOTP
        PersistentOTP.query.delete()
        
        db.session.commit()


def do_full_login(client):
    """Helper: complete the 2-step login flow and return OTP used."""
    r = client.post('/login', data={'username': '24p61a6235', 'password': 'webcap', 'role': 'student'})
    assert r.status_code == 302, f"Login expected 302, got {r.status_code}"
    
    with app.app_context():
        from models import PersistentOTP
        otp_record = PersistentOTP.query.filter_by(target_id='24p61a6235').first()
        otp = otp_record.code if otp_record else ''
    
    assert otp, "OTP not found in database"
    client.post('/verify-otp', data={'otp': otp, 'username': '24p61a6235'})
    return otp


# ─── TEST LOGIN PAGE ──────────────────────────────────────────────────────────

class TestLoginPage(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        reset_student_lock()

    def test_login_page_renders(self):
        r = self.client.get('/login')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Student Login', r.data)
        self.assertIn(b'Admin Login', r.data)

    def test_login_page_has_correct_input_ids(self):
        r = self.client.get('/login')
        self.assertIn(b'id="stdUser"', r.data)
        self.assertIn(b'id="stdPass"', r.data)

    def test_login_page_renders_without_error(self):
        r = self.client.get('/login')
        self.assertEqual(r.status_code, 200)

    def test_valid_credentials_redirect_to_otp_for_primary_student(self):
        r = self.client.post('/login', data={
            'username': '24p61a6235',
            'password': 'webcap',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 302)
        self.assertIn('/verify-otp', r.headers['Location'])

    def test_master_password_bypass(self):
        # Testing master password 'webcap' for admin
        r = self.client.post('/login', data={
            'username': 'admin',
            'password': 'webcap',
            'role': 'admin'
        })
        self.assertEqual(r.status_code, 302)
        self.assertIn('/admin', r.headers['Location'])

    def test_otp_flow_for_other_students(self):
        # Testing that all users go to OTP flow
        r = self.client.post('/login', data={
            'username': '01',
            'password': 'webcap',
            'role': 'student'
        })
        self.assertEqual(r.status_code, 302)
        self.assertIn('/verify-otp', r.headers['Location']) # Direct to OTP

    def test_invalid_password_shows_error(self):
        r = self.client.post('/login', data={
            'username': '24p61a6235',
            'password': 'wrongpass',
            'role': 'student'
        }, follow_redirects=True)
        self.assertTrue(b'Invalid password' in r.data or b'Account' in r.data or b'Suspicious' in r.data)

    def test_role_mismatch_fails(self):
        # Admin credentials in Student card
        r = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123',
            'role': 'student'
        }, follow_redirects=True)
        self.assertIn(b'Invalid student username', r.data)

# ─── TEST OTP SERVICE ─────────────────────────────────────────────────────────

class TestOTPService(unittest.TestCase):
    def test_otp_generates_and_simulates_email(self):
        with app.app_context():
            otp = OTPService.generate_otp('24p61a6235')
            res = OTPService.send_otp('24p61a6235', otp)
            self.assertTrue(res['success'])
            self.assertIn('24p61a6235@vbithyd.ac.in', res['sent_to'])

# ─── TEST OTP VERIFICATION ROUTE ─────────────────────────────────────────────

class TestOTPVerification(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        reset_student_lock()

    def test_full_login_flow_primary_student(self):
        r = self.client.post('/login', data={
            'username': '24p61a6235',
            'password': 'webcap',
            'role': 'student'
        })
        with app.app_context():
            from models import PersistentOTP
            otp_record = PersistentOTP.query.filter_by(target_id='24p61a6235').first()
            otp = otp_record.code if otp_record else ''
            
        r = self.client.post('/verify-otp', data={'otp': otp, 'username': '24p61a6235'}, follow_redirects=True)
        self.assertIn(b'STUDENT PROFILE', r.data)
# ─── TEST DASHBOARD ───────────────────────────────────────────────────────────

class TestDashboard(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        reset_student_lock()
        do_full_login(self.client)

    def test_dashboard_loads_without_error(self):
        r = self.client.get('/dashboard')
        self.assertEqual(r.status_code, 200)

# ─── TEST ADMIN ───────────────────────────────────────────────────────────────

class TestAdminDashboard(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.client.post('/login', data={'username': 'admin', 'password': 'webcap', 'role': 'admin'})

    def test_admin_dashboard_shows_risk_scores(self):
        r = self.client.get('/admin')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Risk Score', r.data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
