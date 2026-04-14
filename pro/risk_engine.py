"""
Risk Detection Engine - Rule-based scoring from project.txt
Detects suspicious behavior using IP analysis and event frequency.
"""
from datetime import datetime, timedelta, timezone
import ipaddress
from models import db, AuditLog, RiskEvent
import uuid


def get_client_ip(request):
    """Get the real client IP, supporting proxies"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def log_event(username, event_type, status, request):
    """
    Central logging function - records all activity to AuditLog.
    Matches the AuditLog.recordLogin() from Class Diagram.
    """
    ip = get_client_ip(request)
    agent = request.headers.get('User-Agent', 'Unknown')

    log = AuditLog(
        log_id=str(uuid.uuid4()),
        user_id=username,
        event_type=event_type,
        ip_address=ip,
        user_agent=agent[:255],
        status=status,
    )
    db.session.add(log)
    db.session.commit()
    return log


def is_new_ip(username, ip):
    """Check if this IP has been used before by this user"""
    previous = AuditLog.query.filter_by(
        user_id=username, status='success'
    ).filter(AuditLog.ip_address != ip).first()

    # If there are previous successful logins from different IPs, this is a known user
    any_previous = AuditLog.query.filter_by(
        user_id=username, ip_address=ip, status='success'
    ).first()

    return previous is not None and any_previous is None


def multiple_ips_detected(username, window_minutes=10):
    """Check if multiple IPs used in the last N minutes"""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    recent_logs = AuditLog.query.filter(
        AuditLog.user_id == username,
        AuditLog.login_time >= cutoff
    ).all()

    unique_ips = set(log.ip_address for log in recent_logs if log.ip_address)
    return len(unique_ips) > 1


def excessive_view_full(username, window_minutes=5, threshold=3):
    """Check if too many VIEW_FULL events in short time"""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    count = AuditLog.query.filter(
        AuditLog.user_id == username,
        AuditLog.event_type == 'VIEW_FULL',
        AuditLog.login_time >= cutoff
    ).count()
    return count > threshold


def multiple_accounts_from_ip(ip, window_minutes=10):
    """Check if multiple accounts are using the same IP"""
    try:
        if ipaddress.ip_address(ip).is_private:
            return False
    except ValueError:
        pass
    
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    recent_logs = AuditLog.query.filter(
        AuditLog.ip_address == ip,
        AuditLog.login_time >= cutoff
    ).all()
    unique_users = set(log.user_id for log in recent_logs)
    return len(unique_users) > 1


def calculate_risk(username, event, request):
    """
    Risk Calculation Function from project.txt
    Rule-based scoring system using logs + IP behavior.
    """
    ip = get_client_ip(request)
    risk = 0

    if event == "LOGIN_FAIL":
        risk += 5

    if event == "OTP_FAIL":
        risk += 10

    if is_new_ip(username, ip):
        risk += 10

    if multiple_ips_detected(username):
        risk += 15

    if excessive_view_full(username):
        risk += 10

    if multiple_accounts_from_ip(ip):
        risk += 20
    if risk > 0:
        risk_event = RiskEvent(
            username=username,
            risk_type=event,
            risk_score=risk,
            ip_address=ip,
        )
        db.session.add(risk_event)
        db.session.commit()

    return risk


def check_risk_threshold(username, window_minutes=10, threshold=None):
    """Check if total risk score exceeds threshold"""
    if threshold is None:
        from flask import current_app
        threshold = current_app.config.get('RISK_THRESHOLD', 30)
        
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    events = RiskEvent.query.filter(
        RiskEvent.username == username,
        RiskEvent.timestamp >= cutoff
    ).all()

    total_risk = sum(e.risk_score for e in events)
    return total_risk > threshold, total_risk
