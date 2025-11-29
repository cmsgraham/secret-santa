"""
Secret Santa Application - Multi-Event Architecture
Flask application for organizing multiple Secret Santa gift exchanges
"""
import os
import secrets
import random
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from models import Base, User, Event, Participant, Assignment, AuthToken, EventStatus
from event_names import generate_event_name, generate_event_code, get_random_event_names

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///secretsanta.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# SMTP Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'

# ============================================================================
# Authentication Helpers
# ============================================================================

def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the currently logged in user"""
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None

def create_or_get_user(email, name):
    """Create a new user or get existing one"""
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()
    return user

def create_magic_link_token(user):
    """Create a magic link token for passwordless authentication"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    auth_token = AuthToken(
        token=token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.session.add(auth_token)
    db.session.commit()
    
    return token

def send_magic_link_email(user, token):
    """Send magic link email for authentication"""
    magic_link = url_for('verify_magic_link', token=token, _external=True)
    
    subject = "🎄 Your Secret Santa Login Link"
    body = f"""
    Hi {user.name}!
    
    Click the link below to log in to your Secret Santa account:
    
    {magic_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this, you can safely ignore this email.
    
    Happy gifting! 🎁
    """
    
    return send_email(user.email, subject, body)

# ============================================================================
# Email Functions
# ============================================================================

def send_email(to_email, subject, body):
    """Send an email via SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        if SMTP_USE_TLS:
            server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False

def send_assignment_email(participant, receiver_name, event):
    """Send Secret Santa assignment email to participant"""
    subject = f"🎅 Your Secret Santa Assignment - {event.name}"
    body = f"""
    Hi {participant.name}!
    
    Your Secret Santa assignment for "{event.name}" is ready! 🎁
    
    You are the Secret Santa for: {receiver_name}
    
    Keep it secret, and have fun shopping for the perfect gift!
    
    Event Details:
    - Event: {event.name}
    - Organized by: {event.organizer.name}
    
    Happy gifting! 🎄
    """
    
    success = send_email(participant.email, subject, body)
    
    if success:
        participant.assignment_email_sent = True
        participant.assignment_email_sent_at = datetime.now(timezone.utc)
        db.session.commit()
    
    return success

# ============================================================================
# Secret Santa Algorithm
# ============================================================================

def create_secret_santa_assignments(event):
    """
    Create Secret Santa assignments for an event
    Ensures no one gets themselves
    """
    participants = list(event.participants)
    
    if len(participants) < event.min_participants:
        raise ValueError(f"Need at least {event.min_participants} participants")
    
    # Clear existing assignments
    for assignment in event.assignments:
        db.session.delete(assignment)
    
    # Shuffle participants to create random assignments
    givers = participants.copy()
    receivers = participants.copy()
    
    max_attempts = 100
    for attempt in range(max_attempts):
        random.shuffle(receivers)
        
        # Check if anyone got themselves
        valid = True
        for i, giver in enumerate(givers):
            if not event.allow_self_assignment and giver.id == receivers[i].id:
                valid = False
                break
        
        if valid:
            # Create assignments
            for i, giver in enumerate(givers):
                assignment = Assignment(
                    event_id=event.id,
                    giver_id=giver.id,
                    receiver_id=receivers[i].id
                )
                db.session.add(assignment)
            
            # Update event status
            event.status = EventStatus.DRAW_COMPLETED
            event.draw_date = datetime.now(timezone.utc)
            db.session.commit()
            
            return True
    
    raise ValueError("Could not create valid assignments after multiple attempts")

# ============================================================================
# Routes - Landing and Authentication
# ============================================================================

@app.route('/')
def index():
    """Landing page"""
    user = get_current_user()
    return render_template('landing.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with magic link"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        
        # Validate email
        try:
            validated = validate_email(email)
            email = validated.normalized
        except EmailNotValidError:
            return jsonify({'success': False, 'error': 'Invalid email address'}), 400
        
        # Create or get user
        user = create_or_get_user(email, name or email.split('@')[0])
        
        # Create magic link token
        token = create_magic_link_token(user)
        
        # Send magic link email
        if send_magic_link_email(user, token):
            return jsonify({
                'success': True,
                'message': 'Check your email for the login link!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send login email'
            }), 500
    
    return render_template('login.html')

@app.route('/auth/verify/<token>')
def verify_magic_link(token):
    """Verify magic link token and log in user"""
    auth_token = AuthToken.query.filter_by(token=token).first()
    
    if not auth_token or not auth_token.is_valid:
        flash('Invalid or expired login link', 'error')
        return redirect(url_for('login'))
    
    # Mark token as used
    auth_token.used = True
    auth_token.used_at = datetime.now(timezone.utc)
    
    # Update user last login
    user = auth_token.user
    user.last_login = datetime.now(timezone.utc)
    
    # Log in user
    session['user_id'] = user.id
    session['user_email'] = user.email
    session['user_name'] = user.name
    
    db.session.commit()
    
    flash(f'Welcome back, {user.name}!', 'success')
    
    # Redirect to next URL or dashboard
    next_url = request.args.get('next') or url_for('dashboard')
    return redirect(next_url)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ============================================================================
# Routes - Event Creation
# ============================================================================

@app.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new Secret Santa event"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        event_name = data.get('event_name', '').strip()
        description = data.get('description', '').strip()
        
        # Generate event code
        code = generate_event_code()
        while Event.query.filter_by(code=code).first():
            code = generate_event_code()
        
        # Create event
        event = Event(
            code=code,
            name=event_name,
            description=description,
            organizer_id=session['user_id']
        )
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'event_id': event.id,
            'event_code': event.code,
            'management_url': event.management_url
        })
    
    # GET request - show form with name suggestions
    suggestions = get_random_event_names(5)
    return render_template('create_event.html', suggestions=suggestions)

# ============================================================================
# Routes - Event Management
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing all their events"""
    user = get_current_user()
    events = Event.query.filter_by(organizer_id=user.id).order_by(Event.created_at.desc()).all()
    return render_template('dashboard.html', events=events, user=user)

@app.route('/event/<code>/manage')
@login_required
def manage_event(code):
    """Event management page for organizers"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id']:
        flash('You do not have permission to manage this event', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('manage_event.html', event=event)

@app.route('/event/<code>/run-draw', methods=['POST'])
@login_required
def run_draw(code):
    """Run the Secret Santa draw for an event"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    # Check permissions
    if event.organizer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Check if draw can be run
    if not event.can_run_draw:
        return jsonify({
            'success': False,
            'error': f'Need at least {event.min_participants} participants and registration must be open'
        }), 400
    
    try:
        # Create assignments
        create_secret_santa_assignments(event)
        
        # Send emails to all participants
        emails_sent = 0
        for assignment in event.assignments:
            receiver_name = assignment.receiver.name
            if send_assignment_email(assignment.giver, receiver_name, event):
                emails_sent += 1
        
        return jsonify({
            'success': True,
            'message': f'Draw completed! {emails_sent} emails sent.',
            'emails_sent': emails_sent,
            'participant_count': event.participant_count
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/event/<code>/reopen', methods=['POST'])
@login_required
def reopen_event(code):
    """Reopen event registration"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    if event.organizer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    event.status = EventStatus.REGISTRATION_OPEN
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Registration reopened'})

@app.route('/event/<code>/close', methods=['POST'])
@login_required
def close_event(code):
    """Close the event"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    if event.organizer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    event.status = EventStatus.EVENT_CLOSED
    event.closed_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Event closed'})

# ============================================================================
# Routes - Participant Registration
# ============================================================================

@app.route('/event/<code>/register', methods=['GET', 'POST'])
def register_participant(code):
    """Public registration page for participants"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Check if registration is open
        if event.status != EventStatus.REGISTRATION_OPEN:
            return jsonify({
                'success': False,
                'error': 'Registration is closed for this event'
            }), 400
        
        # Check participant limit
        if event.participant_count >= event.max_participants:
            return jsonify({
                'success': False,
                'error': 'Event is full'
            }), 400
        
        name = data.get('name', '').strip()
        nickname = data.get('nickname', '').strip()
        email = data.get('email', '').strip().lower()
        
        # Validate
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        try:
            validated = validate_email(email)
            email = validated.normalized
        except EmailNotValidError:
            return jsonify({'success': False, 'error': 'Invalid email address'}), 400
        
        # Auto-generate nickname if not provided
        if not nickname:
            from nickname_generator import generate_nickname
            nickname = generate_nickname()
        
        # Check if already registered
        existing = Participant.query.filter_by(event_id=event.id, email=email).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'This email is already registered for this event'
            }), 400
        
        # Create participant
        participant = Participant(
            event_id=event.id,
            name=name,
            nickname=nickname,
            email=email
        )
        db.session.add(participant)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Welcome, {name}! You have been registered.',
            'participant_count': event.participant_count
        })
    
    return render_template('register.html', event=event)

# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/event/<code>/participants')
def get_participants(code):
    """Get list of participants for an event"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    participants = [{
        'id': p.id,
        'name': p.name,
        'registered_at': p.registered_at.isoformat()
    } for p in event.participants]
    
    return jsonify({
        'participants': participants,
        'count': len(participants),
        'status': event.status.value
    })

@app.route('/api/event-name/generate')
def generate_name():
    """Generate a random event name"""
    style = request.args.get('style', 'default')
    name = generate_event_name(style)
    return jsonify({'name': name})

@app.route('/api/event-names/suggestions')
def get_suggestions():
    """Get multiple event name suggestions"""
    count = int(request.args.get('count', 5))
    names = get_random_event_names(count)
    return jsonify({'names': names})

# ============================================================================
# Health Check
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})

# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - Page Not Found</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #667eea; }
        </style>
    </head>
    <body>
        <h1>🎅 404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    ''', 404

@app.errorhandler(500)
def server_error(e):
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>500 - Server Error</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #ef4444; }
        </style>
    </head>
    <body>
        <h1>🎄 500 - Server Error</h1>
        <p>Something went wrong on our end.</p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    ''', 500

# ============================================================================
# Initialize Database
# ============================================================================

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_ENV') == 'development')
