"""
Database Models - Aligned with Class Diagram
Classes: Student, Admin, AuditLog, RiskEvent
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class Student(db.Model):
    """Student entity from Class Diagram"""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)  # Roll number
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    aadhaar = db.Column(db.String(16), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked = db.Column(db.Boolean, default=False)
    last_login_ip = db.Column(db.String(45), nullable=True)
    last_login_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Student profile data (stored as JSON-like text for demo)
    course = db.Column(db.String(50), default='B.Tech')
    branch = db.Column(db.String(100), default='CYBER SECURITY')
    semester = db.Column(db.String(50), default='2/4 Semester-II')
    admission_no = db.Column(db.String(30), default='20150554/2024')
    dob = db.Column(db.String(15), default='17/11/2006')
    gender = db.Column(db.String(10), default='Male')
    nationality = db.Column(db.String(20), default='Indian')
    religion = db.Column(db.String(20), default='Hindu')
    caste = db.Column(db.String(20), default='SC')
    entrance_type = db.Column(db.String(20), default='EAMCET')
    entrance_rank = db.Column(db.String(20), default='102656')
    seat_type = db.Column(db.String(20), default='Convener')
    joining_date = db.Column(db.String(15), default='01/08/2024')
    father_name = db.Column(db.String(100), default='DASARI RAMULU')
    mother_name = db.Column(db.String(100), default='DASARI RAJYA LAKSHMI')
    father_occupation = db.Column(db.String(50), default='FITTER')
    mother_occupation = db.Column(db.String(50), default='HOUSE WIFE')
    father_mobile = db.Column(db.String(15), default='8106022871')
    mother_mobile = db.Column(db.String(15), default='9032694953')
    annual_income = db.Column(db.String(20), default='180000')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Admin(db.Model):
    """Admin entity from Class Diagram"""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='administrator')
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class AuditLog(db.Model):
    """AuditLog entity from Class Diagram - records all login activity"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False)  # success / fail
    login_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<AuditLog {self.event_type} - {self.user_id} - {self.status}>'


class RiskEvent(db.Model):
    """Risk events table for tracking suspicious activity"""
    __tablename__ = 'risk_events'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    risk_type = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Integer, default=0)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


def init_db(app):
    """Initialize database and seed default student user + 200 mock users"""
    with app.app_context():
        db.create_all()

        # Create primary testing student if not exists
        if not Student.query.filter_by(student_id='24p61a6235').first():
            student = Student(
                student_id='24p61a6235',
                name='DASARIPAVANKUMAR',
                email='24p61a6235@vbithyd.ac.in',
                phone='8125654248',
                aadhaar='1234 5678 9012',
            )
            student.set_password('webcap')
            db.session.add(student)

        # Create 200 mock students for scale testing
        existing_count = Student.query.count()
        if existing_count < 200:
            for i in range(1, 201):
                sid = f'24p61a62{i:03d}'
                if sid == '24p61a6235' or Student.query.filter_by(student_id=sid).first():
                    continue
                
                s = Student(
                    student_id=sid,
                    name=f'STUDENT {i:03d}',
                    email=f'{sid}@vbithyd.ac.in',
                    phone=f'987654{i:04d}',
                    aadhaar=f'5678 1234 {i:04d}',
                    course='B.Tech',
                    branch='CSE' if i % 2 == 0 else 'CYBER SECURITY',
                    semester='2/4 Semester-II'
                )
                s.set_password('webcap')
                db.session.add(s)

        # Create default admin if not exists
        if not Admin.query.filter_by(admin_id='admin').first():
            admin = Admin(
                admin_id='admin',
                name='Administrator',
                role='administrator',
            )
            admin.set_password('admin123')
            db.session.add(admin)

        db.session.commit()
