from flask import Flask, render_template, request, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import logging
from email_validator import validate_email, EmailNotValidError
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_dir = os.getenv('LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/secret_santa.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'sqlite:///secret_santa.db'  # Default to SQLite for development
)
# Handle SQLite URL format for development
if DATABASE_URL.startswith('sqlite:///') and not os.path.isabs(DATABASE_URL[10:]):
    # Make SQLite path relative to current directory
    DATABASE_URL = f'sqlite:///{os.path.abspath(DATABASE_URL[10:])}'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class SecretSantaEvent(db.Model):
    __tablename__ = 'secret_santa_events'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False, default="Secret Santa Exchange")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    organizer_email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    participants_count = db.Column(db.Integer, default=0)
    emails_sent = db.Column(db.Integer, default=0)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='event', lazy=True)
    email_logs = db.relationship('EmailLog', backref='event', lazy=True)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.String, db.ForeignKey('secret_santa_events.id'), nullable=False)
    giver_email = db.Column(db.String(255), nullable=False)
    receiver_email = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = db.Column(db.String, db.ForeignKey('secret_santa_events.id'), nullable=False)
    recipient_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # sent, failed
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# WhatsApp API configuration
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')

# SMTP Configuration for nameinahat.com mail server
SMTP_SERVER = os.getenv('SMTP_SERVER', '172.233.171.101')
SMTP_PORT = int(os.getenv('SMTP_PORT', 2587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'secretsanta@nameinahat.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
USE_TLS = os.getenv('USE_TLS', 'true').lower() == 'true'
DEFAULT_SENDER_EMAIL = os.getenv('DEFAULT_SENDER_EMAIL', 'secretsanta@nameinahat.com')

def validate_emails(email_list):
    """Validate email addresses."""
    valid_emails = []
    invalid_emails = []
    
    # Simple email regex
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    for email in email_list:
        email = email.strip()
        if email and email_pattern.match(email):
            valid_emails.append(email)
        elif email:  # Only add to invalid if not empty
            invalid_emails.append(email)
    
    return valid_emails, invalid_emails

def validate_phone_numbers(phone_list):
    """Validate a list of phone numbers."""
    valid_phones = []
    invalid_phones = []
    
    for phone in phone_list:
        phone = phone.strip()
        if not phone:
            continue
        # Remove common formatting characters
        clean_phone = re.sub(r'[^\d+]', '', phone)
        # Basic validation: should start with + and have at least 10 digits
        if re.match(r'^\+\d{10,15}$', clean_phone):
            valid_phones.append(clean_phone)
        else:
            invalid_phones.append(phone)
    
    return valid_phones, invalid_phones

def create_secret_santa_assignments(emails, event_id):
    """Create Secret Santa assignments ensuring no self-assignments."""
    if len(emails) < 2:
        raise ValueError("At least 2 participants are required")
    
    logger.info(f"Creating assignments for event {event_id} with {len(emails)} participants")
    
    # Shuffle the list to randomize
    participants = emails.copy()
    recipients = emails.copy()
    
    # Keep shuffling until we have no self-assignments
    max_attempts = 1000
    attempts = 0
    
    while attempts < max_attempts:
        random.shuffle(recipients)
        # Check if any participant is assigned to themselves
        if all(giver != receiver for giver, receiver in zip(participants, recipients)):
            break
        attempts += 1
    
    if attempts >= max_attempts:
        logger.error(f"Could not create valid assignments for event {event_id} after {max_attempts} attempts")
        raise RuntimeError("Could not create valid assignments after multiple attempts")
    
    # Save assignments to database
    assignments = []
    for giver, receiver in zip(participants, recipients):
        assignment = Assignment(
            event_id=event_id,
            giver_email=giver,
            receiver_email=receiver
        )
        db.session.add(assignment)
        assignments.append((giver, receiver))
    
    db.session.commit()
    logger.info(f"Saved {len(assignments)} assignments for event {event_id}")
    return assignments

def send_email(recipient_email, recipient_name, secret_person, event_id):
    """Send Secret Santa assignment email with logging."""
    email_log = EmailLog(
        event_id=event_id,
        recipient_email=recipient_email,
        subject="🎅 Your Secret Santa Assignment!",
        status='pending'
    )
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = f"Secret Santa <{DEFAULT_SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = "🎅 Your Secret Santa Assignment!"
        
        body = f"""Ho Ho Ho! 🎄

Dear {recipient_name},

You've been assigned as the Secret Santa for: {secret_person}

Remember:
- Keep it a secret! 🤫
- Be thoughtful with your gift choice
- Have fun spreading holiday cheer! 🎁

Happy Holidays!
The Secret Santa Organizer

Event ID: {event_id}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        if USE_TLS:
            server.starttls()
        
        # Authenticate
        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        # Log success
        email_log.status = 'sent'
        db.session.add(email_log)
        db.session.commit()
        
        logger.info(f"Email sent successfully to {recipient_email} for event {event_id}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send email to {recipient_email} for event {event_id}: {error_msg}")
        
        # Log failure
        email_log.status = 'failed'
        email_log.error_message = error_msg
        db.session.add(email_log)
        db.session.commit()
        
        return False

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration."""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/events/<event_id>/status')
def get_event_status(event_id):
    """Get the status of a Secret Santa event."""
    event = SecretSantaEvent.query.get_or_404(event_id)
    assignments = Assignment.query.filter_by(event_id=event_id).all()
    email_logs = EmailLog.query.filter_by(event_id=event_id).all()
    
    return jsonify({
        'event': {
            'id': event.id,
            'name': event.name,
            'status': event.status,
            'created_at': event.created_at.isoformat(),
            'participants_count': event.participants_count,
            'emails_sent': event.emails_sent
        },
        'assignments': len(assignments),
        'email_logs': [{
            'recipient': log.recipient_email,
            'status': log.status,
            'sent_at': log.sent_at.isoformat(),
            'error': log.error_message
        } for log in email_logs]
    })

@app.route('/assign', methods=['POST'])
def assign_secret_santa():
    """Process Secret Santa assignments and send emails."""
    data = request.get_json()
    
    # Get form data
    emails_text = data.get('emails', '')
    sender_email = data.get('sender_email', os.getenv('DEFAULT_SENDER_EMAIL', 'secretsanta@nameinahat.com'))
    event_name = data.get('event_name', 'Secret Santa Exchange')
    
    # Validate inputs
    if not emails_text:
        return jsonify({'success': False, 'error': 'Please provide participant emails'})
    
    # Parse emails (split by newline, comma, or semicolon)
    import re
    email_list = re.split(r'[,;\n]+', emails_text)
    
    # Validate email addresses
    valid_emails, invalid_emails = validate_emails(email_list)
    
    if invalid_emails:
        logger.warning(f"Invalid emails provided: {invalid_emails}")
        return jsonify({
            'success': False, 
            'error': f'Invalid email addresses: {", ".join(invalid_emails)}'
        })
    
    if len(valid_emails) < 2:
        return jsonify({
            'success': False, 
            'error': 'At least 2 valid email addresses are required'
        })
    
    # Create new event
    event = SecretSantaEvent(
        name=event_name,
        organizer_email=sender_email,
        participants_count=len(valid_emails)
    )
    db.session.add(event)
    db.session.commit()
    
    logger.info(f"Created new event {event.id} with {len(valid_emails)} participants")
    
    try:
        # Create Secret Santa assignments
        assignments = create_secret_santa_assignments(valid_emails, event.id)
        
        # Send emails
        success_count = 0
        failed_emails = []
        
        for giver, receiver in assignments:
            # Extract name from email (part before @)
            giver_name = giver.split('@')[0]
            receiver_name = receiver.split('@')[0]
            
            if send_email(giver, giver_name, receiver_name, event.id):
                success_count += 1
            else:
                failed_emails.append(giver)
        
        # Update event status
        event.emails_sent = success_count
        if success_count == len(assignments):
            event.status = 'completed'
        else:
            event.status = 'partial'
        
        db.session.commit()
        
        if success_count == len(assignments):
            logger.info(f"Event {event.id} completed successfully - all {success_count} emails sent")
            return jsonify({
                'success': True,
                'message': f'Secret Santa assignments sent to all {success_count} participants!',
                'event_id': event.id
            })
        else:
            logger.warning(f"Event {event.id} partially completed - {success_count}/{len(assignments)} emails sent")
            return jsonify({
                'success': False,
                'error': f'Failed to send emails to: {", ".join(failed_emails)}',
                'event_id': event.id
            })
    
    except Exception as e:
        logger.error(f"Error processing event {event.id}: {str(e)}")
        event.status = 'failed'
        db.session.commit()
        return jsonify({'success': False, 'error': str(e), 'event_id': event.id})

# Initialize database
def create_tables():
    """Create database tables."""
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")

if __name__ == '__main__':
    # Create logs directory
    log_dir = os.getenv('LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create database tables
    create_tables()
    
    # Run the app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'False').lower() == 'true')