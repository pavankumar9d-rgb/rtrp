# ECAP: Secure Student Authentication Portal

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/framework-Flask-lightgrey.svg)

**ECAP** is a production-grade student authentication portal designed with a "Security-First" philosophy. It moves beyond simple username/password systems by implementing a real-time **Risk Engine** and **Context-Aware Authentication**.

## 🚀 Key Features

### 1. Smart Risk Engine
- **IP Analysis**: Detects logins from new locations or suspicious IP ranges.
- **Velocity Tracking**: Flags multiple account attempts from a single device.
- **Rule-Based Scoring**: Dynamically calculates a risk score for every event (Login Fail, OTP Fail, etc.).

### 2. Multi-Channel OTP Delivery
- **Flexible Choice**: Users can choose to receive their 6-digit security codes via **Email** (Gmail SMTP) or **SMS** (Azure Communication Services).
- **Simulation Mode**: Built-in "Demo Mode" for presentations—if external services are offline, codes are securely printed to the server logs.

### 3. "Zero-Trust" Privacy Blurring
- **Sensitive Data Masking**: High-risk data (Aadhaar, Phone, Email) is blurred by default on the dashboard.
- **Step-Up Authentication**: Requires a secondary OTP verification to "unblur" and view full profile details.
- **Session Protection**: Step-up access automatically expires after 3 minutes to prevent shoulder-surfing.

### 4. Admin Control Center
- **Live Audit Logs**: Track every login attempt, success, and failure in real-time.
- **Risk Monitoring**: Identify high-risk students and suspicious behavior patterns.
- **Account Management**: Admins can instantly lock or unlock accounts based on security alerts.

---

## 🛠️ Tech Stack
- **Backend**: Python / Flask
- **Database**: SQLite (SQLAlchemy ORM)
- **Security**: Bcrypt (Password Hashing), Flask-Session
- **Services**: Gmail SMTP, Azure Communication Services
- **Frontend**: Vanilla HTML5, CSS3 (Modern Glassmorphism), JavaScript (ES6)

---

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pavankumar9d-rgb/rtrp.git
   cd rtrp
   ```

2. **Install dependencies**:
   ```bash
   pip install flask flask-sqlalchemy flask-bcrypt azure-communication-sms
   ```

3. **Configure Environment**:
   Create a `.env` file in the `pro/` directory with the following:
   ```env
   SECRET_KEY=your_secret_key
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   AZURE_COMMUNICATION_CONNECTION_STRING=your_azure_string
   AZURE_SENDER_PHONE_NUMBER=your_azure_phone
   ```

4. **Initialize Database**:
   ```bash
   python pro/update_db.py
   ```

5. **Run the App**:
   ```bash
   python pro/app.py
   ```

---

## 📖 Documentation
- [Project Guide](Project_Guide.txt): Full file structure and component breakdown.
- [Q&A Defense Guide](questions.txt): Exhaustive list of 20+ security justifications and loopholes.
- [Logic Breakdown](CODE_LOGIC_EXPLAINED.txt): Detailed explanation of specific code-level choices.

---

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.
