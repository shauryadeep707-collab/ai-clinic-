"""
Flask Application Factory for AI Health Clinic & Assistant.
Integrates the clinic medical frontend with the bestproject backend services,
database abstraction, and clinical AI engine.
"""

import os
import secrets
from flask import Flask, session, request, jsonify, send_from_directory, g
from backend.config import config
from backend import db as database


def create_app():
    """Create and configure the Flask application."""
    
    app = Flask(__name__, static_folder=None)
    
    # Load configuration
    app.secret_key = config.SECRET_KEY
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Project root for resolving frontend paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    frontend_dir = os.path.join(project_root, 'frontend')
    html_dir = os.path.join(frontend_dir, 'html')
    uploads_dir = os.path.join(project_root, 'backend', 'uploads')
    reports_dir = os.path.join(uploads_dir, 'reports')
    
    # --- Database connection per request ---
    @app.before_request
    def before_request():
        """Open a DB connection and store in Flask's g object."""
        g.db = database.get_connection()
    
    @app.teardown_appcontext
    def teardown_db(exception):
        """Close the DB connection after each request."""
        db_conn = g.pop('db', None)
        if db_conn is not None:
            database.close_connection(db_conn)
    
    # --- CSRF Protection ---
    @app.before_request
    def csrf_protect():
        """Check CSRF token on state-changing requests, allowing Bearer tokens."""
        if app.config.get('TESTING'):
            return

        # Ensure session has a CSRF token
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        
        # Only check on state-changing methods to API routes
        if request.method in ('POST', 'PUT', 'DELETE') and request.path.startswith('/api/'):
            # Bearer token authenticated requests are inherently CSRF-safe
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                return

            # Multipart uploads (file upload forms)
            if request.content_type and 'multipart/form-data' in request.content_type:
                return

            # Exempt public or standard clinic endpoints
            exempt = [
                '/api/auth/login', '/api/auth/register', '/api/auth/csrf', '/api/auth/reset-password',
                '/api/medicines/ask', '/api/facial/checkup', '/api/system/storage-info',
                '/api/ai/suggest', '/api/consultations', '/api/appointments',
                '/api/medicines/allergy-check', '/api/medicines/reminders',
                '/api/doctors/applications', '/api/admin/doctors/review',
                '/api/patients/profile'
            ]
            if any(request.path.startswith(prefix) for prefix in exempt):
                return
            
            token = request.headers.get('X-CSRF-Token', '')
            if token != session.get('csrf_token'):
                return jsonify({'ok': False, 'error': 'Invalid CSRF token'}), 403
    
    # --- Security Headers ---
    @app.after_request
    def add_security_headers(response):
        """Add security headers to every response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # --- Register Route Blueprints ---
    route_modules = [
        ('backend.routes.auth', 'auth_bp'),
        ('backend.routes.patients', 'patients_bp'),
        ('backend.routes.reports', 'reports_bp'),
        ('backend.routes.timeline', 'timeline_bp'),
        ('backend.routes.pharmacies', 'pharmacies_bp'),
        ('backend.routes.appointments', 'appointments_bp'),
        ('backend.routes.consultations', 'consultations_bp'),
        ('backend.routes.assessments', 'assessments_bp'),
        ('backend.routes.doctors', 'doctors_bp'),
        ('backend.routes.notifications', 'notifications_bp'),
        ('backend.routes.health', 'health_bp'),
    ]
    
    for module_path, bp_name in route_modules:
        try:
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            app.register_blueprint(blueprint)
        except (ImportError, AttributeError) as e:
            print(f'  Note: Route {module_path} not yet available: {e}')
    
    # --- Frontend File Serving ---
    
    @app.route('/')
    def serve_index():
        """Serve the clinic landing homepage."""
        index_in_html = os.path.join(html_dir, 'index.html')
        if os.path.exists(index_in_html):
            return send_from_directory(html_dir, 'index.html')
        return send_from_directory(frontend_dir, 'index.html')
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve any assets, css, js, or html mounted under /static/."""
        return send_from_directory(frontend_dir, filename)

    @app.route('/html/<path:filename>')
    def serve_html(filename):
        """Serve html templates."""
        return send_from_directory(html_dir, filename)
    
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(frontend_dir, 'css'), filename)
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(frontend_dir, 'js'), filename)
    
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(frontend_dir, 'assets'), filename)

    @app.route('/storage/reports/<path:filename>')
    def serve_uploaded_report(filename):
        return send_from_directory(reports_dir, filename)
    
    # --- CSRF Token Endpoint ---
    @app.route('/api/auth/csrf')
    def get_csrf():
        """Return the current CSRF token for JavaScript to use."""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return jsonify({'ok': True, 'data': {'csrf_token': session['csrf_token']}})
    
    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'ok': False, 'error': 'Not found'}), 404
        # Check if requested html page exists directly in html folder
        req_clean = request.path.lstrip('/')
        potential = os.path.join(html_dir, req_clean)
        if os.path.exists(potential):
            return send_from_directory(html_dir, req_clean)
        if not req_clean.endswith('.html'):
            potential_html = os.path.join(html_dir, f"{req_clean}.html")
            if os.path.exists(potential_html):
                return send_from_directory(html_dir, f"{req_clean}.html")
        return send_from_directory(html_dir, '404.html') if os.path.exists(os.path.join(html_dir, '404.html')) else send_from_directory(html_dir, 'index.html')
    
    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'ok': False, 'error': 'Internal server error'}), 500
        return '<h1>500 Internal Server Error</h1>', 500
    
    return app
