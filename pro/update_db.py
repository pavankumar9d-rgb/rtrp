import os
import sys
from app import create_app
from models import db, Student

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

print("Starting FAST database update for specific users...")
app = create_app()
with app.app_context():
    # Update user 24p61a6235
    s0 = Student.query.filter_by(student_id='24p61a6235').first()
    if s0:
        s0.name = 'DASARI PAVAN KUMAR'
        s0.father_name = 'DASARI RAMULU'
        s0.mother_name = 'DASARI RAJYA LAKSHMI'
        s0.father_occupation = 'FITTER'
        s0.mother_occupation = 'HOUSE WIFE'
        s0.father_mobile = '8106022871'
        s0.mother_mobile = '9032694953'
        s0.admission_no = '20150554/2024'
        s0.dob = '17/11/2006'
        s0.branch = 'CYBER SECURITY'
        s0.annual_income = '180000'
        s0.set_password('webcap')

    # Update user 01 - Different Info
    s1 = Student.query.filter_by(student_id='01').first()
    if not s1:
        s1 = Student(student_id='01')
        db.session.add(s1)
    s1.name = 'KARTHIK RAMAN'
    s1.set_password('webcap')
    s1.email = 'pavankumar9.d@gmail.com'
    s1.phone = '9876543210'
    s1.aadhaar = '1234 5678 0001'
    s1.course = 'B.Tech'
    s1.branch = 'COMPUTER SCIENCE'
    s1.semester = '3/4 Semester-I'
    s1.dob = '14/05/2005'
    s1.admission_no = 'ADM/CS/2023/001'
    s1.father_name = 'RAMANATHAN K.'
    s1.mother_name = 'MEENAKSHI R.'
    s1.father_occupation = 'SOFTWARE ENGINEER'
    s1.mother_occupation = 'TEACHER'
    s1.father_mobile = '9988776655'
    s1.mother_mobile = '9944332211'
    s1.annual_income = '600000'
    s1.entrance_rank = '8500'

    # Update user 02 - Different Info
    s2 = Student.query.filter_by(student_id='02').first()
    if not s2:
        s2 = Student(student_id='02')
        db.session.add(s2)
    s2.name = 'PRAVEEN KUMAR'
    s2.set_password('webcap')
    s2.email = 'pavankumar00.d@gmail.com'
    s2.phone = '8765432109'
    s2.aadhaar = '9876 5432 0002'
    s2.course = 'B.Tech'
    s2.branch = 'INFORMATION TECHNOLOGY'
    s2.semester = '2/4 Semester-II'
    s2.dob = '22/09/2006'
    s2.admission_no = 'ADM/IT/2024/042'
    s2.father_name = 'SURESH KUMAR'
    s2.mother_name = 'SUNITHA DEVI'
    s2.father_occupation = 'BUSINESS'
    s2.mother_occupation = 'HOMEMAKER'
    s2.father_mobile = '9123456780'
    s2.mother_mobile = '9012345678'
    s2.annual_income = '450000'
    s2.entrance_rank = '15200'

    db.session.commit()
    print("Database successfully synchronized with diverse mock data for specific users!")
