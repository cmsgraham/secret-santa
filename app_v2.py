"""
Secret Santa Application - Multi-Event Architecture
Flask application for organizing multiple Secret Santa gift exchanges
"""
import os
import secrets
import random
import io
import base64
import logging
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

# Configure logging
logger = logging.getLogger(__name__)
import qrcode

from models import Base, User, Event, Participant, Assignment, AuthToken, EventStatus, FeedPost, FeedComment, FeedLike
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
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 2592000  # 30 days in seconds
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

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
        
        # Connect with timeout to prevent hanging
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
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

def generate_qr_code_base64(data):
    """Generate a QR code and return it as base64 encoded image"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert image to base64
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return None

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
# Session Management
# ============================================================================

@app.before_request
def make_session_permanent():
    """Make sessions permanent to keep them alive"""
    session.permanent = True

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
        
        # Validate email
        try:
            validated = validate_email(email)
            email = validated.normalized
        except EmailNotValidError:
            return jsonify({'success': False, 'error': 'Invalid email address'}), 400
        
        # Create or get user (use email prefix as default name)
        user = create_or_get_user(email, email.split('@')[0])
        
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
def create_event():
    """Create a new Secret Santa event"""
    # Check if coming from participant dashboard with authentication
    participant_email = session.get('participant_email')
    from_dashboard = False
    
    # If not logged in as organizer but has participant_email, auto-create user account
    if 'user_id' not in session and participant_email:
        # Get or create user from participant email
        # Try to get name from a recent participant record
        participant = Participant.query.filter_by(email=participant_email).first()
        if participant:
            # Auto-create/get user account without magic link
            user = create_or_get_user(participant_email, participant.name)
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            from_dashboard = True
    
    # Require login for creating events
    if 'user_id' not in session:
        flash('Please log in to create an event', 'warning')
        return redirect(url_for('login', next=request.url))
    
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
    user_email = session.get('user_email', '')
    user_name = session.get('user_name', '')
    return render_template('create_event.html', 
                         suggestions=suggestions,
                         user_email=user_email,
                         user_name=user_name,
                         from_dashboard=from_dashboard or bool(participant_email))

# ============================================================================
# Routes - Event Management
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Unified dashboard showing all events (created and participating)"""
    user = get_current_user()
    
    # If user not found in database (stale session), redirect to login
    if not user:
        session.clear()
        flash('Your session has expired. Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    # Get events where user is the organizer
    created_events = Event.query.filter_by(organizer_id=user.id).order_by(Event.created_at.desc()).all()
    
    # Get events where user is a participant
    participant_events = Participant.query.filter_by(email=user.email).all()
    
    # Create a set of event IDs where user is participating
    participating_event_ids = {p.event_id for p in participant_events}
    
    # Prepare created events with participation status
    created_events_data = []
    for event in created_events:
        participant = None
        for p in participant_events:
            if p.event_id == event.id:
                participant = p
                break
        
        created_events_data.append({
            'event': event,
            'is_participating': event.id in participating_event_ids,
            'participant': participant,
            'member_url': url_for('member_page', code=event.code, participant_id=participant.id) if participant else None
        })
    
    # Prepare participating events data (exclude ones they created)
    participating_events = []
    for p in participant_events:
        event = p.event
        # Skip if already in created_events (avoid duplicates)
        if event.organizer_id != user.id:
            participating_events.append({
                'event': event,
                'participant': p,
                'member_url': url_for('member_page', code=event.code, participant_id=p.id)
            })
    
    return render_template('dashboard.html', 
                         created_events=created_events_data,
                         participating_events=participating_events,
                         user=user)

@app.route('/event/<code>/manage')
@login_required
def manage_event(code):
    """Event management page for organizers"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id']:
        flash('You do not have permission to manage this event', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate QR code for registration link
    registration_url = request.host_url.rstrip('/') + url_for('register_participant', code=code)
    qr_code = generate_qr_code_base64(registration_url)
    
    return render_template('manage_event.html', event=event, qr_code=qr_code, registration_url=registration_url)

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

@app.route('/event/<code>/toggle-guessing', methods=['POST'])
@login_required
def toggle_guessing(code):
    """Toggle the guessing phase for participants"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    if event.organizer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Can only enable guessing if draw is completed
    if not event.guessing_enabled and event.status != EventStatus.DRAW_COMPLETED:
        return jsonify({
            'success': False, 
            'error': 'Can only enable guessing after the draw is completed'
        }), 400
    
    event.guessing_enabled = not event.guessing_enabled
    db.session.commit()
    
    status = 'enabled' if event.guessing_enabled else 'disabled'
    return jsonify({'success': True, 'message': f'Guessing phase {status}'})

@app.route('/event/<code>/delete', methods=['POST'])
@login_required
def delete_event(code):
    """Delete a closed event"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    # Check authorization
    if event.organizer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Only allow deleting closed events
    if event.status != EventStatus.EVENT_CLOSED:
        return jsonify({
            'success': False, 
            'error': 'Only closed events can be deleted'
        }), 400
    
    # Delete all related data (cascade will handle participants, assignments, etc.)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Event deleted successfully'})

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
        
        # Store participant_id and email in session for member page access
        session['participant_id'] = participant.id
        session['participant_email'] = participant.email
        
        # Generate member page URL
        member_url = url_for('member_page', code=event.code, participant_id=participant.id, _external=True)
        
        return jsonify({
            'success': True,
            'message': f'Welcome, {name}! You have been registered.',
            'participant_count': event.participant_count,
            'member_url': member_url,
            'participant_id': participant.id
        })
    
    return render_template('register.html', event=event)

@app.route('/participant/dashboard', methods=['GET', 'POST'])
def participant_dashboard():
    """Redirect to unified dashboard - kept for backwards compatibility"""
    # If user is already logged in via user_id, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    # Check if participant is authenticated via participant_email
    participant_email = session.get('participant_email')
    
    if not participant_email:
        # Handle magic link request
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            
            # Validate email
            try:
                validated = validate_email(email)
                email = validated.normalized
            except EmailNotValidError:
                return jsonify({'success': False, 'error': 'Invalid email address'}), 400
            
            # Check if this email exists as a participant
            participants = Participant.query.filter_by(email=email).all()
            if not participants:
                return jsonify({'success': False, 'error': 'No events found for this email address'}), 404
            
            # Get participant name from first registration
            participant_name = participants[0].name
            
            # Create or get user for this email
            user = create_or_get_user(email, participant_name)
            
            # Create magic link token
            token = create_magic_link_token(user)
            
            # Send magic link email for dashboard access
            magic_link = url_for('verify_magic_link', token=token, _external=True)
            subject = "🎄 Your Secret Santa Dashboard Login Link"
            body = f"""
Hi {participant_name}!

Click the link below to access your Secret Santa dashboard:

{magic_link}

This link will expire in 1 hour.

From your dashboard, you can:
- View all Secret Santa events (created and participating)
- Manage your gift preferences and hints
- Create new Secret Santa events

Happy gifting! 🎁
            """
            
            if send_email(email, subject, body):
                return jsonify({
                    'success': True,
                    'message': 'Check your email for the login link!'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send login email'
                }), 500
        
        return render_template('participant_login.html')
    
    # Participant is authenticated via participant_email, log them in as user
    user = User.query.filter_by(email=participant_email).first()
    if user:
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session.pop('participant_email', None)  # Remove old session key
        session.pop('participant_id', None)
    
    return redirect(url_for('dashboard'))

@app.route('/participant/logout')
def participant_logout():
    """Logout participant from dashboard"""
    session.pop('participant_email', None)
    session.pop('participant_id', None)
    return redirect(url_for('participant_dashboard'))

@app.route('/participant/auth/verify/<token>')
def verify_participant_magic_link(token):
    """Verify magic link token - redirects to unified dashboard"""
    return verify_magic_link(token)

@app.route('/event/<code>/member/<participant_id>', methods=['GET', 'POST'])
def member_page(code, participant_id):
    """Member landing page for participants to manage their info"""
    event = Event.query.filter_by(code=code).first_or_404()
    participant = Participant.query.filter_by(id=participant_id, event_id=event.id).first_or_404()
    
    # Check authentication: must be the participant themselves ONLY
    # They must have either:
    # 1. participant_id in session (directly registered and stored)
    # 2. participant_email in session that matches this participant
    # 3. user_email in session that matches this participant (unified auth)
    is_own_page = (
        str(session.get('participant_id')) == str(participant_id) or 
        session.get('participant_email') == participant.email or
        session.get('user_email') == participant.email
    )
    
    # If not authenticated, redirect to participant dashboard login
    # No direct email verification on this page to prevent organizers from accessing
    if not is_own_page:
        flash('Please log in through the participant dashboard to access your member page.', 'warning')
        return redirect(url_for('participant_dashboard'))
    
    # User is authenticated, proceed with normal member page logic
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'save_hints':
            participant.hints = data.get('hints', '').strip()[:1000]  # Limit to 1000 chars
            db.session.commit()
            return jsonify({'success': True, 'message': 'Hints saved successfully'})
        
        elif action == 'save_preferences':
            participant.gift_preferences = data.get('gift_preferences', '').strip()[:2000]  # Limit to 2000 chars
            db.session.commit()
            return jsonify({'success': True, 'message': 'Preferences saved successfully'})
        
        elif action == 'submit_guess':
            if not event.guessing_enabled:
                return jsonify({'success': False, 'error': 'Guessing is not enabled yet'}), 400
            
            if participant.guessed_secret_santa_id:
                return jsonify({'success': False, 'error': 'You have already submitted a guess'}), 400
            
            guess_id = data.get('guess')
            if not guess_id or guess_id == participant.id:
                return jsonify({'success': False, 'error': 'Invalid guess'}), 400
            
            participant.guessed_secret_santa_id = guess_id
            participant.guessed_at = datetime.now(timezone.utc)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Guess submitted successfully'})
        
        elif action == 'update_profile_picture':
            profile_picture = data.get('profile_picture', '').strip()
            if profile_picture and len(profile_picture) <= 500:  # Validate length
                participant.profile_picture = profile_picture
                db.session.commit()
                return jsonify({'success': True, 'message': 'Profile picture updated successfully'})
            return jsonify({'success': False, 'error': 'Invalid profile picture'}), 400
        
        elif action == 'update_nickname':
            nickname = data.get('nickname', '').strip()
            if nickname and len(nickname) <= 100:  # Validate length
                participant.nickname = nickname
                db.session.commit()
                return jsonify({'success': True, 'message': 'Nickname updated successfully'})
            return jsonify({'success': False, 'error': 'Invalid nickname'}), 400
        
        return jsonify({'success': False, 'error': 'Invalid action'}), 400
    
    # GET request - load the member page
    assignment = None
    receiving_assignment = None
    
    if event.status in [EventStatus.DRAW_COMPLETED, EventStatus.EVENT_CLOSED]:
        # Get who this participant is giving to
        assignment = Assignment.query.filter_by(giver_id=participant.id).first()
        # Get who is giving to this participant (their Secret Santa)
        receiving_assignment = Assignment.query.filter_by(receiver_id=participant.id).first()
    
    return render_template('member.html', 
                         event=event, 
                         participant=participant,
                         assignment=assignment,
                         receiving_assignment=receiving_assignment)

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

@app.route('/event/<code>/join', methods=['POST'])
@login_required
def join_own_event(code):
    """Allow organizer to join their own event automatically"""
    event = Event.query.filter_by(code=code).first_or_404()
    user = get_current_user()
    
    # Check if user is the organizer
    if event.organizer_id != user.id:
        return jsonify({'success': False, 'error': 'Only the organizer can auto-join'}), 403
    
    # Check if registration is open
    if event.status != EventStatus.REGISTRATION_OPEN:
        return jsonify({'success': False, 'error': 'Registration is closed'}), 400
    
    # Check if already registered
    existing = Participant.query.filter_by(event_id=event.id, email=user.email).first()
    if existing:
        return jsonify({
            'success': False, 
            'error': 'Already registered',
            'member_url': url_for('member_page', code=event.code, participant_id=existing.id)
        }), 400
    
    # Create participant using user's information
    participant = Participant(
        event_id=event.id,
        name=user.name,
        nickname=user.name,  # Default nickname to their name
        email=user.email
    )
    db.session.add(participant)
    db.session.commit()
    
    # Store participant info in session for member page access
    session['participant_id'] = participant.id
    session['participant_email'] = participant.email
    
    # Generate member page URL
    member_url = url_for('member_page', code=event.code, participant_id=participant.id)
    
    return jsonify({
        'success': True,
        'message': f'Successfully joined {event.name}!',
        'member_url': member_url,
        'participant_id': participant.id
    })

@app.route('/event/<code>/participant/<participant_id>/remove', methods=['POST'])
@login_required
def remove_participant(code, participant_id):
    """Remove a participant from an event"""
    event = Event.query.filter_by(code=code).first_or_404()
    participant = Participant.query.filter_by(id=participant_id, event_id=event.id).first_or_404()
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Only the organizer can remove participants'}), 403
    
    # Check if draw has been completed
    if event.status != EventStatus.REGISTRATION_OPEN:
        return jsonify({'success': False, 'error': 'Cannot remove participants after draw is completed'}), 400
    
    participant_name = participant.name
    db.session.delete(participant)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'{participant_name} has been removed from the event'
    })

# ============================================================================
# Feed (Santa's Secret Wall)
# ============================================================================

@app.route('/event/<code>/feed', methods=['GET', 'POST'])
def feed(code):
    """Santa's Secret Wall - Anonymous feed for event participants"""
    event = Event.query.filter_by(code=code).first_or_404()
    
    # Get all participants in the event
    members = event.participants
    
    # Handle POST - create new feed post
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash('Post cannot be empty', 'error')
            return redirect(url_for('feed', code=code))
        
        # Get the current participant from session - try multiple sources
        participant_id = session.get('participant_id')
        participant_email = session.get('participant_email')
        user_email = session.get('user_email')  # Organizer auth fallback
        
        print(f"DEBUG: Feed POST attempt for event {code}")
        print(f"DEBUG: participant_id={participant_id}, participant_email={participant_email}, user_email={user_email}")
        print(f"DEBUG: Full session keys: {list(session.keys())}")
        
        # Try to find participant by ID first, then by email (participant_email), then by user_email
        participant = None
        if participant_id:
            participant = Participant.query.get(participant_id)
        elif participant_email:
            participant = Participant.query.filter_by(email=participant_email, event_id=event.id).first()
        elif user_email:
            # Check if the organizer is also a participant in this event
            participant = Participant.query.filter_by(email=user_email, event_id=event.id).first()
        
        if not participant:
            flash('You must be logged in to post', 'warning')
            return redirect(url_for('feed', code=code))
        
        if participant.event_id != event.id:
            flash('Invalid participant', 'error')
            return redirect(url_for('feed', code=code))
        
        # Update session with participant_id if it wasn't there
        if 'participant_id' not in session:
            session['participant_id'] = participant.id
        if 'participant_email' not in session:
            session['participant_email'] = participant.email
        
        # Create and save the post
        post = FeedPost(
            event_id=event.id,
            participant_id=participant.id,
            nickname=participant.nickname or participant.name,
            content=content
        )
        db.session.add(post)
        db.session.commit()
        
        flash('Post shared! 🎉', 'success')
        return redirect(url_for('feed', code=code))
    
    # Retrieve all posts for this event with likes and comments
    posts = FeedPost.query.filter_by(event_id=event.id).order_by(FeedPost.created_at.desc()).all()
    
    # Get current participant for checking if they've liked posts
    current_participant_id = session.get('participant_id')
    
    # Prepare post data with like status
    posts_data = []
    for post in posts:
        like_count = len(post.likes)
        user_has_liked = any(like.participant_id == current_participant_id for like in post.likes) if current_participant_id else False
        comment_count = len(post.comments)
        posts_data.append({
            'post': post,
            'like_count': like_count,
            'user_has_liked': user_has_liked,
            'comment_count': comment_count,
            'comments': sorted(post.comments, key=lambda c: c.created_at)
        })
    
    # Prepare hints data with engagement stats
    hints_data = []
    for member in members:
        if member.hints:
            # Count likes for this hint (we'll use a pseudo-id based on participant)
            hint_likes = db.session.query(FeedLike).filter(
                FeedLike.post_id == f"hint_{member.id}"
            ).count()
            hint_comments = db.session.query(FeedComment).filter(
                FeedComment.post_id == f"hint_{member.id}"
            ).count()
            
            user_has_liked_hint = False
            if current_participant_id:
                user_has_liked_hint = db.session.query(FeedLike).filter_by(
                    post_id=f"hint_{member.id}",
                    participant_id=current_participant_id
                ).first() is not None
            
            hint_comments_list = db.session.query(FeedComment).filter(
                FeedComment.post_id == f"hint_{member.id}"
            ).order_by(FeedComment.created_at).all()
            
            hints_data.append({
                'participant': member,
                'content': member.hints,
                'like_count': hint_likes,
                'user_has_liked': user_has_liked_hint,
                'comment_count': hint_comments,
                'comments': hint_comments_list,
                'type': 'hint'
            })
    
    # Prepare gift ideas data with engagement stats
    ideas_data = []
    for member in members:
        if member.gift_preferences:
            # Count likes for this gift idea
            idea_likes = db.session.query(FeedLike).filter(
                FeedLike.post_id == f"idea_{member.id}"
            ).count()
            idea_comments = db.session.query(FeedComment).filter(
                FeedComment.post_id == f"idea_{member.id}"
            ).count()
            
            user_has_liked_idea = False
            if current_participant_id:
                user_has_liked_idea = db.session.query(FeedLike).filter_by(
                    post_id=f"idea_{member.id}",
                    participant_id=current_participant_id
                ).first() is not None
            
            idea_comments_list = db.session.query(FeedComment).filter(
                FeedComment.post_id == f"idea_{member.id}"
            ).order_by(FeedComment.created_at).all()
            
            ideas_data.append({
                'participant': member,
                'content': member.gift_preferences,
                'like_count': idea_likes,
                'user_has_liked': user_has_liked_idea,
                'comment_count': idea_comments,
                'comments': idea_comments_list,
                'type': 'idea'
            })
    
    # Return feed page
    return render_template('feed.html', event=event, members=members, posts_data=posts_data, hints_data=hints_data, ideas_data=ideas_data)

@app.route('/feed/post/<post_id>/like', methods=['POST'])
def like_post(post_id):
    """Like or unlike a feed post"""
    post = FeedPost.query.get_or_404(post_id)
    participant_id = session.get('participant_id')
    
    if not participant_id:
        return {'error': 'Not logged in'}, 401
    
    participant = Participant.query.get(participant_id)
    if not participant or participant.event_id != post.event_id:
        return {'error': 'Invalid participant'}, 403
    
    # Check if already liked
    existing_like = FeedLike.query.filter_by(post_id=post_id, participant_id=participant_id).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        db.session.commit()
        return {'liked': False, 'like_count': len(post.likes) - 1}
    else:
        # Like
        like = FeedLike(post_id=post_id, participant_id=participant_id)
        db.session.add(like)
        db.session.commit()
        return {'liked': True, 'like_count': len(post.likes)}

@app.route('/feed/wall/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    """Add a comment to a feed post"""
    post = FeedPost.query.get_or_404(post_id)
    
    # Try to get current participant with fallbacks
    current_participant_id = session.get('participant_id')
    participant_email = session.get('participant_email')
    user_email = session.get('user_email')
    
    current_participant = None
    if current_participant_id:
        found = Participant.query.get(current_participant_id)
        # Only use if they're in the same event as the target
        if found and found.event_id == post.event_id:
            current_participant = found
    
    if not current_participant and participant_email:
        current_participant = Participant.query.filter_by(email=participant_email, event_id=post.event_id).first()
    
    if not current_participant and user_email:
        current_participant = Participant.query.filter_by(email=user_email, event_id=post.event_id).first()
    
    if not current_participant:
        flash('You must be logged in to comment', 'warning')
        return redirect(url_for('feed', code=post.event.code))
    
    if current_participant.event_id != post.event_id:
        flash('Invalid participant', 'error')
        return redirect(url_for('feed', code=post.event.code))
    
    # Update session with participant info if needed
    if 'participant_id' not in session:
        session['participant_id'] = current_participant.id
    if 'participant_email' not in session:
        session['participant_email'] = current_participant.email
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('feed', code=post.event.code))
    
    comment = FeedComment(
        post_id=post_id,
        participant_id=current_participant.id,
        nickname=current_participant.nickname or current_participant.name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added! 💬', 'success')
    return redirect(url_for('feed', code=post.event.code))

@app.route('/feed/hint/<participant_id>/like', methods=['POST'])
def like_hint(participant_id):
    """Like or unlike a hint"""
    try:
        print(f"DEBUG like_hint: participant_id={participant_id}, session={dict(session)}")
        participant = Participant.query.get_or_404(participant_id)
        print(f"DEBUG like_hint: Target participant found: {participant.id}, event_id={participant.event_id}")
        
        # Try to get current participant with fallbacks
        current_participant_id = session.get('participant_id')
        participant_email = session.get('participant_email')
        user_email = session.get('user_email')
        
        print(f"DEBUG like_hint: current_participant_id={current_participant_id}, participant_email={participant_email}, user_email={user_email}")
        
        current_participant = None
        if current_participant_id:
            found = Participant.query.get(current_participant_id)
            # Only use if they're in the same event as the target
            if found and found.event_id == participant.event_id:
                current_participant = found
                print(f"DEBUG like_hint: Looked up by participant_id in correct event, found={current_participant is not None}")
            else:
                print(f"DEBUG like_hint: participant_id found but wrong event or not found")
        
        if not current_participant and participant_email:
            current_participant = Participant.query.filter_by(email=participant_email, event_id=participant.event_id).first()
            print(f"DEBUG like_hint: Looked up by participant_email in event {participant.event_id}, found={current_participant is not None}")
        
        if not current_participant and user_email:
            current_participant = Participant.query.filter_by(email=user_email, event_id=participant.event_id).first()
            print(f"DEBUG like_hint: Looked up by user_email in event {participant.event_id}, found={current_participant is not None}")
        
        print(f"DEBUG like_hint: current_participant={current_participant}")
        
        if not current_participant:
            return jsonify({'error': 'Not logged in'}), 401
        
        # Update session with participant info if needed
        if 'participant_id' not in session:
            session['participant_id'] = current_participant.id
        if 'participant_email' not in session:
            session['participant_email'] = current_participant.email
        
        pseudo_post_id = f"hint_{participant_id}"
        
        # Check if already liked
        existing_like = FeedLike.query.filter_by(post_id=pseudo_post_id, participant_id=current_participant.id).first()
        
        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()
            like_count = FeedLike.query.filter_by(post_id=pseudo_post_id).count()
            return jsonify({'liked': False, 'like_count': like_count})
        else:
            like = FeedLike(post_id=pseudo_post_id, participant_id=current_participant.id)
            db.session.add(like)
            db.session.commit()
            like_count = FeedLike.query.filter_by(post_id=pseudo_post_id).count()
            return jsonify({'liked': True, 'like_count': like_count})
    except Exception as e:
        print(f"Error in like_hint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Server error'}), 500

@app.route('/feed/idea/<participant_id>/like', methods=['POST'])
def like_idea(participant_id):
    """Like or unlike a gift idea"""
    try:
        print(f"DEBUG like_idea: participant_id={participant_id}, session={dict(session)}")
        participant = Participant.query.get_or_404(participant_id)
        print(f"DEBUG like_idea: Target participant found: {participant.id}, event_id={participant.event_id}")
        
        # Try to get current participant with fallbacks
        current_participant_id = session.get('participant_id')
        participant_email = session.get('participant_email')
        user_email = session.get('user_email')
        
        print(f"DEBUG like_idea: current_participant_id={current_participant_id}, participant_email={participant_email}, user_email={user_email}")
        
        current_participant = None
        if current_participant_id:
            found = Participant.query.get(current_participant_id)
            # Only use if they're in the same event as the target
            if found and found.event_id == participant.event_id:
                current_participant = found
                print(f"DEBUG like_idea: Looked up by participant_id in correct event, found={current_participant is not None}")
            else:
                print(f"DEBUG like_idea: participant_id found but wrong event or not found")
        
        if not current_participant and participant_email:
            current_participant = Participant.query.filter_by(email=participant_email, event_id=participant.event_id).first()
            print(f"DEBUG like_idea: Looked up by participant_email in event {participant.event_id}, found={current_participant is not None}")
        
        if not current_participant and user_email:
            current_participant = Participant.query.filter_by(email=user_email, event_id=participant.event_id).first()
            print(f"DEBUG like_idea: Looked up by user_email in event {participant.event_id}, found={current_participant is not None}")
        
        print(f"DEBUG like_idea: current_participant={current_participant}")
        
        if not current_participant:
            return jsonify({'error': 'Not logged in'}), 401
        
        # Update session with participant info if needed
        if 'participant_id' not in session:
            session['participant_id'] = current_participant.id
        if 'participant_email' not in session:
            session['participant_email'] = current_participant.email
        
        pseudo_post_id = f"idea_{participant_id}"
        
        # Check if already liked
        existing_like = FeedLike.query.filter_by(post_id=pseudo_post_id, participant_id=current_participant.id).first()
        
        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()
            like_count = FeedLike.query.filter_by(post_id=pseudo_post_id).count()
            return jsonify({'liked': False, 'like_count': like_count})
        else:
            like = FeedLike(post_id=pseudo_post_id, participant_id=current_participant.id)
            db.session.add(like)
            db.session.commit()
            like_count = FeedLike.query.filter_by(post_id=pseudo_post_id).count()
            return jsonify({'liked': True, 'like_count': like_count})
    except Exception as e:
        print(f"Error in like_idea: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Server error'}), 500

@app.route('/feed/hint/<participant_id>/comment', methods=['POST'])
def comment_hint(participant_id):
    """Add a comment to a hint"""
    participant = Participant.query.get_or_404(participant_id)
    
    # Try to get current participant with fallbacks
    current_participant_id = session.get('participant_id')
    participant_email = session.get('participant_email')
    user_email = session.get('user_email')
    
    current_participant = None
    if current_participant_id:
        found = Participant.query.get(current_participant_id)
        # Only use if they're in the same event as the target
        if found and found.event_id == participant.event_id:
            current_participant = found
    
    if not current_participant and participant_email:
        current_participant = Participant.query.filter_by(email=participant_email, event_id=participant.event_id).first()
    
    if not current_participant and user_email:
        current_participant = Participant.query.filter_by(email=user_email, event_id=participant.event_id).first()
    
    if not current_participant:
        flash('You must be logged in to comment', 'warning')
        return redirect(url_for('feed', code=participant.event.code))
    
    if current_participant.event_id != participant.event_id:
        flash('Invalid participant', 'error')
        return redirect(url_for('feed', code=participant.event.code))
    
    # Update session with participant info if needed
    if 'participant_id' not in session:
        session['participant_id'] = current_participant.id
    if 'participant_email' not in session:
        session['participant_email'] = current_participant.email
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('feed', code=participant.event.code))
    
    pseudo_post_id = f"hint_{participant_id}"
    
    comment = FeedComment(
        post_id=pseudo_post_id,
        participant_id=current_participant.id,
        nickname=current_participant.nickname or current_participant.name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added! 💬', 'success')
    return redirect(url_for('feed', code=participant.event.code))

@app.route('/feed/idea/<participant_id>/comment', methods=['POST'])
def comment_idea(participant_id):
    """Add a comment to a gift idea"""
    participant = Participant.query.get_or_404(participant_id)
    
    # Try to get current participant with fallbacks
    current_participant_id = session.get('participant_id')
    participant_email = session.get('participant_email')
    user_email = session.get('user_email')
    
    current_participant = None
    if current_participant_id:
        found = Participant.query.get(current_participant_id)
        # Only use if they're in the same event as the target
        if found and found.event_id == participant.event_id:
            current_participant = found
    
    if not current_participant and participant_email:
        current_participant = Participant.query.filter_by(email=participant_email, event_id=participant.event_id).first()
    
    if not current_participant and user_email:
        current_participant = Participant.query.filter_by(email=user_email, event_id=participant.event_id).first()
    
    if not current_participant:
        flash('You must be logged in to comment', 'warning')
        return redirect(url_for('feed', code=participant.event.code))
    
    if current_participant.event_id != participant.event_id:
        flash('Invalid participant', 'error')
        return redirect(url_for('feed', code=participant.event.code))
    
    # Update session with participant info if needed
    if 'participant_id' not in session:
        session['participant_id'] = current_participant.id
    if 'participant_email' not in session:
        session['participant_email'] = current_participant.email
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('feed', code=participant.event.code))
    
    pseudo_post_id = f"idea_{participant_id}"
    
    comment = FeedComment(
        post_id=pseudo_post_id,
        participant_id=current_participant.id,
        nickname=current_participant.nickname or current_participant.name,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added! 💬', 'success')
    return redirect(url_for('feed', code=participant.event.code))

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
