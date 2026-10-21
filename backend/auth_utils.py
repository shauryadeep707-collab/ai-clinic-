"""
Authentication utilities for AI Health Assistant.
Provides decorators and helpers for role-based access control,
supporting both Flask sessions and JWT Bearer tokens.
"""

from functools import wraps
from flask import session, jsonify, request, g
import jwt
from datetime import datetime, timedelta, timezone
from backend import db as database
from backend.config import config


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm='HS256')


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        return jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
    except Exception:
        return None


def get_current_user():
    """Fetch the currently logged-in user from session or Bearer token.
    Returns a dict with user info, or None if not logged in.
    """
    user_id = session.get('user_id')
    if not user_id:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get('sub') or payload.get('user_id')

    if not user_id:
        return None

    user = database.fetch_one(g.db, 'SELECT id, name, email, role, is_verified FROM users WHERE id = ?', (user_id,))
    if user:
        user['user_id'] = user['id']
        user['full_name'] = user.get('name') or ''
    return user


def role_required(*roles):
    """Decorator that checks login status and role.
    Usage: @role_required('patient') or @role_required('patient', 'doctor')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if user is None:
                return jsonify({'ok': False, 'error': 'Please log in', 'detail': 'Session expired. Please log in again.'}), 401
            if user['role'] not in roles:
                return jsonify({'ok': False, 'error': 'Access denied', 'detail': f"Access denied. Required role: {', '.join(roles)}"}), 403
            return f(user, *args, **kwargs)
        return wrapped
    return decorator


def check_rate_limit(email, ip):
    """Check if login attempts are within the allowed limit."""
    cutoff = (datetime.utcnow() - timedelta(minutes=config.LOCKOUT_MINUTES)).isoformat()
    row = database.fetch_one(
        g.db,
        'SELECT COUNT(*) as cnt FROM login_attempts WHERE email = ? AND attempted_at > ?',
        (email, cutoff)
    )
    return (row['cnt'] if row else 0) < config.MAX_LOGIN_ATTEMPTS


def record_failed_attempt(email, ip):
    """Record a failed login attempt for rate limiting."""
    database.execute(
        g.db,
        'INSERT INTO login_attempts (email, ip_address) VALUES (?, ?)',
        (email, ip)
    )


def clear_attempts(email):
    """Remove failed attempts after a successful login."""
    database.execute(g.db, 'DELETE FROM login_attempts WHERE email = ?', (email,))


def check_ai_limit(user_id):
    """Check if the user has remaining AI calls for today."""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0).isoformat()
    row = database.fetch_one(
        g.db,
        'SELECT COUNT(*) as cnt FROM ai_usage WHERE user_id = ? AND used_at > ?',
        (user_id, today_start)
    )
    return (row['cnt'] if row else 0) < config.AI_DAILY_LIMIT


def record_ai_usage(user_id):
    """Record one AI API call for rate tracking."""
    database.execute(
        g.db,
        'INSERT INTO ai_usage (user_id) VALUES (?)',
        (user_id,)
    )
