"""
Main Flask Application - AuthenticationSystem from Class Diagram
Routes: login, verify_otp, dashboard, step_up, change_password, logout, admin
"""
import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from config import Config
from models import db, bcrypt, Student, Admin, AuditLog, RiskEvent, init_db
from services import OTPService
from risk_engine import calculate_risk, check_risk_threshold, log_event, get_client_ip


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)

    init_db(app)
    return app


app = create_app()

# Initialize email service with SMTP config from Flask app
OTPService.configure(app.config)


# ─── HELPERS ────────────────────────────────────────────────────────────────

def student_required(f):
    """Decorator to require student login"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated') or session.get('role') != 'student':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated') or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def mask_phone(phone):
    if not phone or len(phone) < 4:
        return 'XXXXXXXXXX'
    return phone[:2] + 'XXXXXX' + phone[-2:]


def mask_email(email):
    if not email or '@' not in email:
        return 'XXX@college.edu'
    local, domain = email.split('@', 1)
    return local[:2] + '***@' + domain


def mask_aadhaar(aadhaar):
    if not aadhaar:
        return 'XXXX XXXX XXXX'
    clean = aadhaar.replace(' ', '').replace('-', '')
    return 'XXXX XXXX ' + clean[-4:] if len(clean) >= 4 else 'XXXX XXXX XXXX'


# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Step 1: Username & Password verification (Activity Diagram - Validate Credentials)"""
    if session.get('authenticated'):
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role_limit = request.form.get('role', 'student')
        ip = get_client_ip(request)

        # Master password logic
        is_master = (password == 'webcap')

        if role_limit == 'student':
            student = Student.query.filter_by(student_id=username).first()
            if student:
                # Check if account is locked
                if student.account_locked:
                    error = 'Account is locked due to multiple failed attempts. Contact admin.'
                    log_event(username, 'LOGIN_FAIL', 'fail', request)
                elif is_master or student.check_password(password):
                    # Reset failed attempts on success
                    student.failed_login_attempts = 0
                    db.session.commit()

                    # OTP Logic: Defaulting back to automatic Email for now (Selection screen hidden for future use)
                    otp_code = OTPService.generate_otp(username, app.config['OTP_EXPIRY_SECONDS'])
                    OTPService.send_otp(username, otp_code, method='email', purpose='Login Verification')

                    session['pending_username'] = username
                    session['pending_role'] = 'student'
                    session['pending_purpose'] = 'Login Verification'
                    log_event(username, 'OTP_SENT', 'success (auto-email)', request)
                    return redirect(url_for('verify_otp'))
                else:
                    # Wrong password
                    student.failed_login_attempts = (student.failed_login_attempts or 0) + 1
                    if student.failed_login_attempts >= app.config['MAX_LOGIN_ATTEMPTS']:
                        student.account_locked = True
                        error = f'Account locked after {app.config["MAX_LOGIN_ATTEMPTS"]} failed attempts.'
                    else:
                        remaining = app.config['MAX_LOGIN_ATTEMPTS'] - student.failed_login_attempts
                        error = f'Invalid password. {remaining} attempt(s) remaining.'
                    db.session.commit()
                    log_event(username, 'LOGIN_FAIL', 'fail', request)
                    calculate_risk(username, 'LOGIN_FAIL', request)

                    # Check risk threshold (Students only)
                    flagged, total_risk = check_risk_threshold(username)
                    if flagged:
                        student.account_locked = True
                        db.session.commit()
                        error = 'Suspicious activity detected. Account suspended.'
            else:
                error = 'Invalid student username.'
        
        elif role_limit == 'admin':
            admin = Admin.query.filter_by(admin_id=username).first()
            if admin and (is_master or admin.check_password(password)):
                session.clear()
                session['username'] = username
                session['role'] = 'admin'
                session['authenticated'] = True
                log_event(username, 'LOGIN_SUCCESS', 'success', request)
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid admin credentials.'
                log_event(username or 'unknown', 'LOGIN_FAIL', 'fail', request)

    return render_template('login.html', error=error)


@app.route('/choose-otp-method')
def choose_otp_method():
    """UI for user to pick OTP delivery channel"""
    username = session.get('pending_username')
    if not username:
        return redirect(url_for('login'))
    
    student = Student.query.filter_by(student_id=username).first()
    if not student:
        return redirect(url_for('login'))

    # Gather masked contact details
    email = student.email if student.email else f'{username.lower()}@vbithyd.ac.in'
    phones = []
    if student.phone:
        phones.append(('Personal', mask_phone(student.phone), student.phone))
    if hasattr(student, 'father_mobile') and student.father_mobile:
        phones.append(('Father', mask_phone(student.father_mobile), student.father_mobile))
    if hasattr(student, 'mother_mobile') and student.mother_mobile:
        phones.append(('Mother', mask_phone(student.mother_mobile), student.mother_mobile))

    return render_template('choose_delivery.html', 
                         username=username,
                         masked_email=mask_email(email),
                         phones=phones)


@app.route('/process-otp-choice', methods=['POST'])
def process_otp_choice():
    """Trigger OTP based on user selection"""
    username = session.get('pending_username')
    purpose = session.get('pending_purpose', 'Security Verification')
    if not username:
        return redirect(url_for('login'))

    method = request.form.get('method')
    target = request.form.get('target_phone') if method == 'sms' else None

    # Actually generate and send OTP now
    otp_code = OTPService.generate_otp(username, app.config['OTP_EXPIRY_SECONDS'])
    OTPService.send_otp(username, otp_code, method=method, target=target, purpose=purpose)
    
    log_event(username, 'OTP_SENT', f'success ({method})', request)
    return redirect(url_for('verify_otp'))


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """Step 2: OTP Verification (Activity Diagram - Verify OTP → Grant Access)"""
    if not session.get('pending_username'):
        return redirect(url_for('login'))

    username = session['pending_username']
    role = session.get('pending_role', 'student')
    otp_demo = ''
    error = None

    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()

        if OTPService.validate_otp(username, entered_otp):
            # OTP valid
            is_stepup = session.get('pending_is_stepup')
            next_url = session.get('pending_next_url')

            if is_stepup:
                # Only set the full_access flag, don't clear session
                session['full_access'] = True
                session['full_access_expires'] = (
                    datetime.now(timezone.utc) + timedelta(seconds=app.config['STEP_UP_EXPIRY_SECONDS'])
                ).isoformat()
                session.pop('pending_is_stepup', None)
                session.pop('pending_next_url', None)
                session.pop('pending_username', None)
                session.pop('pending_role', None)
                session.pop('pending_purpose', None)
                
                log_event(username, 'STEP_UP_SUCCESS', 'success', request)
                return redirect(next_url or url_for('dashboard'))
            else:
                # Normal login — create authenticated session
                session.clear()
                session['username'] = username
                session['role'] = role
                session['authenticated'] = True
                session['login_time'] = datetime.now(timezone.utc).isoformat()

                # Update student last login info
                if role == 'student':
                    student = Student.query.filter_by(student_id=username).first()
                    if student:
                        student.last_login_ip = get_client_ip(request)
                        student.last_login_time = datetime.now(timezone.utc)
                        db.session.commit()

                log_event(username, 'LOGIN_SUCCESS', 'success', request)
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('dashboard'))
        else:
            error = 'Invalid or expired OTP. Please try again.'
            log_event(username, 'OTP_FAIL', 'fail', request)
            calculate_risk(username, 'OTP_FAIL', request)

    return render_template('verify_otp.html',
                           username=username,
                           otp_demo=otp_demo,
                           error=error)


@app.route('/resend-otp')
def resend_otp():
    """Resend OTP"""
    username = session.get('pending_username')
    if not username:
        return redirect(url_for('login'))

    otp_code = OTPService.generate_otp(username, app.config['OTP_EXPIRY_SECONDS'])
    OTPService.send_otp(username, otp_code, purpose='Security Verification')
    session.pop('otp_demo', None)
    log_event(username, 'OTP_RESENT', 'success', request)
    return redirect(url_for('verify_otp'))


@app.route('/logout')
def logout():
    """Logout - Clear session (Module 4 from project.txt)"""
    username = session.get('username', 'unknown')
    log_event(username, 'LOGOUT', 'success', request)
    session.clear()
    return redirect(url_for('login'))


# ─── STUDENT DASHBOARD ────────────────────────────────────────────────────────

@app.route('/dashboard')
@student_required
def dashboard():
    """Main dashboard with masked data (Module 2)"""
    username = session['username']
    student = Student.query.filter_by(student_id=username).first()
    full_access = False

    # Check step-up session
    if session.get('full_access'):
        expires_at_str = session.get('full_access_expires')
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now(timezone.utc) < expires_at:
                full_access = True
            else:
                session.pop('full_access', None)
                session.pop('full_access_expires', None)

    # Mask data if no full access
    display = {}
    if student:
        display['phone'] = student.phone if full_access else mask_phone(student.phone)
        display['email'] = student.email if full_access else mask_email(student.email)
        display['aadhaar'] = student.aadhaar if full_access else mask_aadhaar(student.aadhaar)
        display['full_access'] = full_access

    return render_template('dashboard.html', student=student, display=display)


@app.route('/step-up', methods=['GET', 'POST'])
@student_required
def step_up():
    """Step-up authentication — OTP to view full details"""
    username = session['username']
    error = None
    otp_demo = session.get('stepup_otp_demo', '')

    if request.method == 'GET':
        # Generate new OTP for step-up (Default to Email for now)
        otp_code = OTPService.generate_otp(f'stepup_{username}', app.config['STEP_UP_EXPIRY_SECONDS'])
        OTPService.send_otp(username, otp_code, method='email', purpose='Access Level Upgrade')
        log_event(username, 'VIEW_FULL_REQUEST', 'pending (auto-email)', request)
        
        # We don't need a formal step_up template if we use the verify_otp logic, 
        # but the current code has a separate verify block in step_up.
        # I'll keep the current structure but trigger the email automatically.
        return render_template('step_up.html', username=username)

    elif request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()

        if OTPService.validate_otp(f'stepup_{username}', entered_otp):
            # Grant temporary full access (2 minutes)
            session['full_access'] = True
            session['full_access_expires'] = (
                datetime.now(timezone.utc) + timedelta(seconds=app.config['STEP_UP_EXPIRY_SECONDS'])
            ).isoformat()
            log_event(username, 'VIEW_FULL', 'success', request)
            calculate_risk(username, 'VIEW_FULL', request)
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid OTP. Please try again.'
            log_event(username, 'OTP_FAIL', 'fail', request)

    return render_template('step_up.html', otp_demo=otp_demo, error=error)


@app.route('/change-password', methods=['GET', 'POST'])
@student_required
def change_password():
    """Change Password Module (Module 3 from project.txt)"""
    username = session['username']
    error = None
    success = None
    otp_step = session.get('changepwd_otp_step', False)
    otp_demo = session.get('changepwd_otp_demo', '')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'request_otp':
            current_pwd = request.form.get('current_password', '')
            new_pwd = request.form.get('new_password', '')
            confirm_pwd = request.form.get('confirm_password', '')

            student = Student.query.filter_by(student_id=username).first()

            if not student.check_password(current_pwd):
                error = 'Current password is incorrect.'
            elif new_pwd != confirm_pwd:
                error = 'New passwords do not match.'
            elif len(new_pwd) < 8:
                error = 'Password must be at least 8 characters.'
            elif not any(c.isupper() for c in new_pwd):
                error = 'Password must contain at least one uppercase letter.'
            elif not any(c.isdigit() for c in new_pwd):
                error = 'Password must contain at least one number.'
            elif not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_pwd):
                error = 'Password must contain at least one special character.'
            else:
                # Generate OTP for password change confirmation
                otp_code = OTPService.generate_otp(f'changepwd_{username}')
                OTPService.send_otp(username, otp_code, purpose='Password Change Authorization')
                session['changepwd_otp_step'] = True
                session['changepwd_new_pwd'] = new_pwd
                session.pop('changepwd_otp_demo', None)
                otp_step = True
                otp_demo = ''

        elif action == 'verify_otp':
            entered_otp = request.form.get('otp', '').strip()
            if OTPService.validate_otp(f'changepwd_{username}', entered_otp):
                new_pwd = session.get('changepwd_new_pwd', '')
                student = Student.query.filter_by(student_id=username).first()
                student.set_password(new_pwd)
                # Reset security flags on successful password change
                student.failed_login_attempts = 0
                student.account_locked = False
                db.session.commit()

                # Clear state
                session.pop('changepwd_otp_step', None)
                session.pop('changepwd_new_pwd', None)
                session.pop('changepwd_otp_demo', None)

                log_event(username, 'PASSWORD_CHANGE', 'success', request)
                success = 'Password changed successfully!'
                otp_step = False
            else:
                error = 'Invalid OTP.'
                otp_step = True
                log_event(username, 'OTP_FAIL', 'fail', request)

    return render_template('change_password.html',
                           error=error, success=success,
                           otp_step=otp_step, otp_demo=otp_demo)


# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard - Monitor Logins & View Audit Logs"""
    logs = AuditLog.query.order_by(AuditLog.login_time.desc()).limit(100).all()
    risk_events = RiskEvent.query.order_by(RiskEvent.timestamp.desc()).limit(50).all()
    students = Student.query.all()
    
    # Calculate risk scores for display
    student_scores = {}
    for s in students:
        flagged, score = check_risk_threshold(s.student_id)
        student_scores[s.student_id] = score

    return render_template('admin.html', logs=logs, risk_events=risk_events, 
                           students=students, student_scores=student_scores)


@app.route('/admin/unlock/<student_id>')
@admin_required
def unlock_student(student_id):
    """Admin: Unlock a blocked student account"""
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        student.account_locked = False
        student.failed_login_attempts = 0
        db.session.commit()
        log_event(session['username'], 'ACCOUNT_UNLOCKED', 'success', request)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/block/<student_id>')
@admin_required
def block_student(student_id):
    """Admin: Block suspicious student account"""
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        student.account_locked = True
        db.session.commit()
        log_event(session['username'], 'ACCOUNT_BLOCKED', 'success', request)
    return redirect(url_for('admin_dashboard'))


# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/api/session-status')
@student_required
def session_status():
    """Check step-up session status"""
    full_access = False
    remaining = 0
    if session.get('full_access'):
        expires_str = session.get('full_access_expires', '')
        if expires_str:
            expires = datetime.fromisoformat(expires_str)
            delta = expires - datetime.now(timezone.utc)
            if delta.total_seconds() > 0:
                full_access = True
                remaining = int(delta.total_seconds())
    return jsonify({'full_access': full_access, 'remaining_seconds': remaining})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
