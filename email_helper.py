#!/usr/bin/env python3
"""
Flask helper module for email blacklist/whitelist integration
Provides functions to check email deliverability before sending
"""

import os
import sys
from pathlib import Path

# Add current directory to path to import email_blacklist_management
sys.path.insert(0, os.path.dirname(__file__))

from email_blacklist_management import EmailBlacklistManager

class FlaskEmailHelper:
    """Helper class to integrate email blacklist/whitelist with Flask"""
    
    def __init__(self, db_path: str = "email_blacklist.db"):
        """Initialize the email helper"""
        self.manager = EmailBlacklistManager(db_path)
    
    def should_send_email(self, email: str, force: bool = False) -> bool:
        """
        Determine if an email should be sent
        
        Args:
            email: Email address to check
            force: If True, ignore blacklist for whitelisted emails
        
        Returns:
            True if email should be sent, False otherwise
        """
        # Check whitelist first
        import sqlite3
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        
        # If whitelisted, always send
        cursor.execute('SELECT * FROM email_whitelist WHERE email = ?', (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return True
        
        # If blacklisted and not whitelisted, don't send (unless forced)
        cursor.execute('SELECT * FROM email_blacklist WHERE email = ?', (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return force
        
        conn.close()
        return True
    
    def mark_bounce(self, email: str, bounce_type: str = "soft"):
        """
        Record a bounce for an email address
        
        Args:
            email: Email address that bounced
            bounce_type: 'soft' or 'hard' bounce
        """
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        
        # Check if already in blacklist
        cursor.execute('SELECT * FROM email_blacklist WHERE email = ?', (email.lower(),))
        entry = cursor.fetchone()
        
        if entry:
            # Update bounce count
            cursor.execute(
                'UPDATE email_blacklist SET bounce_count = bounce_count + 1, last_bounce = CURRENT_TIMESTAMP WHERE email = ?',
                (email.lower(),)
            )
        else:
            # Add to blacklist
            cursor.execute(
                'INSERT INTO email_blacklist (email, blacklist_type, reason, bounce_count, last_bounce) VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)',
                (email.lower(), bounce_type, f'{bounce_type.capitalize()} bounce')
            )
        
        conn.commit()
        conn.close()
    
    def get_email_status(self, email: str) -> dict:
        """
        Get complete status of an email
        
        Returns:
            Dict with is_blacklisted, is_whitelisted, bounce_count, etc.
        """
        import sqlite3
        
        status = {
            'email': email,
            'is_blacklisted': False,
            'is_whitelisted': False,
            'bounce_count': 0,
            'last_bounce': None,
            'blacklist_reason': None,
            'whitelist_notes': None,
            'should_send': True
        }
        
        conn = sqlite3.connect(self.manager.db_path)
        cursor = conn.cursor()
        
        # Check whitelist
        cursor.execute('SELECT * FROM email_whitelist WHERE email = ?', (email.lower(),))
        whitelist_entry = cursor.fetchone()
        if whitelist_entry:
            status['is_whitelisted'] = True
            status['whitelist_notes'] = whitelist_entry[3]
            status['should_send'] = True
        
        # Check blacklist
        cursor.execute('SELECT * FROM email_blacklist WHERE email = ?', (email.lower(),))
        blacklist_entry = cursor.fetchone()
        if blacklist_entry:
            status['is_blacklisted'] = True
            status['bounce_count'] = blacklist_entry[5]
            status['last_bounce'] = blacklist_entry[6]
            status['blacklist_reason'] = blacklist_entry[3]
            status['should_send'] = False  # Unless whitelisted
        
        conn.close()
        return status


# Flask integration utilities

def check_email_before_send(email: str, app: any = None, force: bool = False) -> bool:
    """
    Check if email should be sent before calling mail.send()
    
    Usage in Flask:
        from email_helper import check_email_before_send
        
        if check_email_before_send(recipient_email):
            mail.send(msg)
    """
    helper = FlaskEmailHelper()
    return helper.should_send_email(email, force=force)


def record_email_bounce(email: str, bounce_type: str = "soft") -> None:
    """
    Record an email bounce in the system
    
    Usage in Flask:
        @app.errorhandler(smtplib.SMTPRecipientsRefused)
        def handle_smtp_error(error):
            record_email_bounce(recipient_email, 'hard')
    """
    helper = FlaskEmailHelper()
    helper.mark_bounce(email, bounce_type)


def get_email_status_check(email: str) -> dict:
    """
    Get status of an email for debugging/checking
    
    Usage in Flask route:
        @app.route('/admin/email-status/<email>')
        def email_status(email):
            status = get_email_status_check(email)
            return jsonify(status)
    """
    helper = FlaskEmailHelper()
    return helper.get_email_status(email)


if __name__ == '__main__':
    # Simple test
    helper = FlaskEmailHelper()
    
    print("Testing Flask Email Helper")
    print("=" * 50)
    
    # Test email
    test_email = "test@example.com"
    
    print(f"\n1. Check if should send to {test_email}:")
    print(f"   Result: {helper.should_send_email(test_email)}")
    
    print(f"\n2. Get status for {test_email}:")
    status = helper.get_email_status(test_email)
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print(f"\n3. Mark as bounced:")
    helper.mark_bounce(test_email, "hard")
    
    print(f"\n4. Check status after bounce:")
    status = helper.get_email_status(test_email)
    print(f"   Should send: {status['should_send']}")
    print(f"   Bounces: {status['bounce_count']}")
