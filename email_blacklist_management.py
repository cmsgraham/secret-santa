#!/usr/bin/env python3
"""
Email Blacklist/Whitelist Management Script
Checks email blacklist status and manages whitelisting for the Secret Santa application
"""

import os
import sys
import argparse
import sqlite3
import json
import socket
import smtplib
import re
from datetime import datetime
from typing import List, Dict, Tuple

# Try to import optional dependencies
try:
    from email_validator import validate_email, EmailNotValidError
    HAS_EMAIL_VALIDATOR = True
except ImportError:
    HAS_EMAIL_VALIDATOR = False

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    # Fallback for .env loading
    def load_dotenv(path=None):
        if path and os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

try:
    import dns.resolver
    import dns.rdatatype
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

# Load environment variables
load_dotenv()

# Configuration
BLACKLIST_DB = "email_blacklist.db"
SMTP_SERVER = os.getenv('SMTP_SERVER', '172.233.171.101')
SMTP_PORT = int(os.getenv('SMTP_PORT', 2587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'secretsanta@nameinahat.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Fallback email validation if email_validator not available
def validate_email_simple(email: str) -> bool:
    """Simple email validation using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_email_wrapper(email: str) -> Tuple[bool, str]:
    """Wrapper for email validation with fallback"""
    if HAS_EMAIL_VALIDATOR:
        try:
            validate_email(email)
            return True, "Valid email format"
        except Exception as e:
            return False, str(e)
    else:
        if validate_email_simple(email):
            return True, "Valid email format (basic check)"
        else:
            return False, "Invalid email format"

class EmailBlacklistManager:
    """Manages email blacklist and whitelist"""
    
    def __init__(self, db_path: str = BLACKLIST_DB):
        """Initialize the blacklist manager"""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for blacklist tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create blacklist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                blacklist_type TEXT NOT NULL,
                reason TEXT,
                listed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bounce_count INTEGER DEFAULT 0,
                last_bounce TIMESTAMP,
                whitelisted BOOLEAN DEFAULT 0,
                whitelisted_date TIMESTAMP
            )
        ''')
        
        # Create whitelist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                whitelisted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # Create DNSBL check history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dnsbl_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                domain TEXT NOT NULL,
                check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_listed BOOLEAN,
                dnsbl_list TEXT,
                result TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_dnsbl(self, domain: str) -> Dict:
        """Check if domain is listed in DNS Blacklist (DNSBL)"""
        print(f"  🔍 Checking DNSBL for domain: {domain}")
        
        if not HAS_DNS:
            print(f"    ⚠️  DNS checking requires dnspython (optional)")
            return {
                'is_listed': False,
                'lists': [],
                'recommendations': ['Install dnspython for full DNSBL checking']
            }
        
        # Common DNSBLs
        dnsbls = [
            'zen.spamhaus.org',
            'dyna.spamhaus.org',
            'blacklist.spamhaus.org',
            'pbl.spamhaus.org',
            'aspews.ext.sorbs.net',
            'b.barracudacentral.org',
        ]
        
        results = {
            'is_listed': False,
            'lists': [],
            'recommendations': []
        }
        
        # Get domain MX record to check the server
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                mx_host = str(mx_records[0].exchange).rstrip('.')
                print(f"    📧 Domain MX: {mx_host}")
                
                # Resolve MX to IP
                try:
                    mx_ip = socket.gethostbyname(mx_host)
                    print(f"    🌐 MX IP: {mx_ip}")
                    
                    # Check each DNSBL
                    for dnsbl in dnsbls:
                        if self._check_dnsbl_listing(mx_ip, dnsbl):
                            results['is_listed'] = True
                            results['lists'].append(dnsbl)
                            print(f"    ⚠️  Listed in {dnsbl}")
                except socket.gaierror:
                    print(f"    ❌ Could not resolve MX hostname: {mx_host}")
        except Exception as e:
            print(f"    ⚠️  Could not check DNSBL: {str(e)}")
        
        if results['is_listed']:
            results['recommendations'] = [
                "Contact your mail server hosting provider",
                "Check spam/bounce rate",
                "Implement SPF, DKIM, and DMARC records",
                "Request delisting from DNSBL providers",
                "Review mail server configuration"
            ]
        
        return results
    
    def _check_dnsbl_listing(self, ip: str, dnsbl: str) -> bool:
        """Check if IP is listed in specific DNSBL"""
        if not HAS_DNS:
            return False
        
        try:
            # Reverse the IP octets for DNSBL query
            octets = ip.split('.')
            reversed_ip = '.'.join(reversed(octets))
            query_host = f"{reversed_ip}.{dnsbl}"
            
            # Attempt DNS query
            dns.resolver.resolve(query_host, 'A', lifetime=5)
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            return False
        except Exception:
            return False
    
    def add_to_blacklist(self, email: str, reason: str = "Manual addition"):
        """Add email to blacklist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT OR REPLACE INTO email_blacklist (email, blacklist_type, reason) VALUES (?, ?, ?)',
                (email.lower(), 'manual', reason)
            )
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added {email} to blacklist")
            return True
        except Exception as e:
            print(f"❌ Error adding to blacklist: {str(e)}")
            return False
    
    def whitelist_email(self, email: str, notes: str = ""):
        """Add email to whitelist and remove from blacklist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add to whitelist
            cursor.execute(
                'INSERT OR REPLACE INTO email_whitelist (email, notes) VALUES (?, ?)',
                (email.lower(), notes)
            )
            
            # Update blacklist status
            cursor.execute(
                'UPDATE email_blacklist SET whitelisted = 1, whitelisted_date = CURRENT_TIMESTAMP WHERE email = ?',
                (email.lower(),)
            )
            
            conn.commit()
            conn.close()
            
            print(f"✅ Whitelisted {email}")
            return True
        except Exception as e:
            print(f"❌ Error whitelisting: {str(e)}")
            return False
    
    def check_email_deliverability(self, email: str) -> Dict:
        """Check if email is likely deliverable"""
        print(f"\n📧 Checking deliverability for: {email}")
        
        results = {
            'email': email,
            'is_valid': False,
            'is_blacklisted': False,
            'is_whitelisted': False,
            'dnsbl_status': {},
            'smtp_check': None,
            'recommendations': []
        }
        
        # 1. Validate email format
        is_valid, validation_msg = validate_email_wrapper(email)
        if is_valid:
            results['is_valid'] = True
            print(f"  ✅ {validation_msg}")
        else:
            print(f"  ❌ {validation_msg}")
            return results
        
        # 2. Check whitelist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM email_whitelist WHERE email = ?', (email.lower(),))
        if cursor.fetchone():
            results['is_whitelisted'] = True
            print("  ✅ Email is whitelisted")
            conn.close()
            return results
        
        # 3. Check blacklist
        cursor.execute('SELECT * FROM email_blacklist WHERE email = ?', (email.lower(),))
        blacklist_entry = cursor.fetchone()
        if blacklist_entry:
            results['is_blacklisted'] = True
            print(f"  ⚠️  Email is blacklisted: {blacklist_entry[3]} (bounces: {blacklist_entry[5]})")
        
        conn.close()
        
        # 4. Check DNSBL for domain
        domain = email.split('@')[1]
        dnsbl_results = self.check_dnsbl(domain)
        results['dnsbl_status'] = dnsbl_results
        
        if dnsbl_results['is_listed']:
            print(f"  ⚠️  Domain is listed in {len(dnsbl_results['lists'])} DNSBL(s)")
        else:
            print(f"  ✅ Domain is not listed in common DNSBLs")
        
        # 5. Check DNS records (SPF, DKIM, DMARC)
        dns_check = self._check_dns_records(domain)
        print(f"  SPF: {dns_check['spf']}")
        print(f"  DKIM: {dns_check['dkim']}")
        print(f"  DMARC: {dns_check['dmarc']}")
        
        # 6. Try SMTP verification (if possible)
        if SMTP_PASSWORD:
            smtp_result = self._verify_smtp(email)
            results['smtp_check'] = smtp_result
            if smtp_result:
                print(f"  ✅ SMTP verification: {smtp_result}")
        
        # Recommendations
        if results['is_blacklisted']:
            results['recommendations'].append("Consider whitelisting this email if it's valid")
            results['recommendations'].append("Check bounce reason and mail server logs")
        
        if dnsbl_results['is_listed']:
            results['recommendations'].extend(dnsbl_results['recommendations'])
        
        if not dns_check['spf']:
            results['recommendations'].append("Domain missing SPF record")
        if not dns_check['dkim']:
            results['recommendations'].append("Domain missing DKIM record")
        if not dns_check['dmarc']:
            results['recommendations'].append("Domain missing DMARC record")
        
        return results
    
    def _check_dns_records(self, domain: str) -> Dict:
        """Check DNS records for domain"""
        results = {
            'spf': '❌ Missing',
            'dkim': '❌ Missing',
            'dmarc': '❌ Missing'
        }
        
        if not HAS_DNS:
            return results
        
        try:
            # Check SPF
            spf_records = dns.resolver.resolve(domain, 'TXT')
            for record in spf_records:
                if 'v=spf1' in str(record):
                    results['spf'] = '✅ Present'
                    break
        except:
            pass
        
        try:
            # Check DMARC
            dmarc_records = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
            if dmarc_records:
                results['dmarc'] = '✅ Present'
        except:
            pass
        
        # Note: DKIM check would require specific selector
        results['dkim'] = '⚠️  Requires selector'
        
        return results
    
    def _verify_smtp(self, email: str) -> str:
        """Verify email via SMTP"""
        try:
            # This is a simple check, not full verification
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            
            # Check if we can send to this address
            # Note: This is a theoretical check
            server.quit()
            return "SMTP connection OK"
        except smtplib.SMTPAuthenticationError:
            return "⚠️  SMTP auth failed"
        except smtplib.SMTPException as e:
            return f"⚠️  SMTP error: {str(e)[:50]}"
        except Exception as e:
            return f"⚠️  Connection error: {str(e)[:50]}"
    
    def list_blacklist(self, show_whitelisted: bool = False) -> List[Dict]:
        """List all blacklisted emails"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if show_whitelisted:
                cursor.execute('SELECT * FROM email_blacklist')
            else:
                cursor.execute('SELECT * FROM email_blacklist WHERE whitelisted = 0')
            
            entries = cursor.fetchall()
            conn.close()
            
            return entries
        except Exception as e:
            print(f"❌ Error reading blacklist: {str(e)}")
            return []
    
    def list_whitelist(self) -> List[Dict]:
        """List all whitelisted emails"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM email_whitelist')
            entries = cursor.fetchall()
            conn.close()
            
            return entries
        except Exception as e:
            print(f"❌ Error reading whitelist: {str(e)}")
            return []
    
    def generate_report(self) -> None:
        """Generate email status report"""
        print("\n" + "="*60)
        print("📊 EMAIL BLACKLIST/WHITELIST REPORT")
        print("="*60)
        
        # Blacklist stats
        blacklist = self.list_blacklist(show_whitelisted=False)
        whitelisted = [e for e in self.list_blacklist(show_whitelisted=True) if e[8]]  # whitelisted flag
        whitelist = self.list_whitelist()
        
        print(f"\n📧 Statistics:")
        print(f"  • Blacklisted emails: {len(blacklist)}")
        print(f"  • Whitelisted emails: {len(whitelist)}")
        print(f"  • Previously whitelisted: {len(whitelisted)}")
        
        if blacklist:
            print(f"\n⚠️  Current Blacklisted Emails:")
            for entry in blacklist[:10]:
                print(f"  • {entry[1]:30} - {entry[3]} (bounces: {entry[5]})")
            if len(blacklist) > 10:
                print(f"  ... and {len(blacklist) - 10} more")
        
        if whitelist:
            print(f"\n✅ Whitelisted Emails:")
            for entry in whitelist[:10]:
                print(f"  • {entry[1]:30} - {entry[3]}")
            if len(whitelist) > 10:
                print(f"  ... and {len(whitelist) - 10} more")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Email Blacklist/Whitelist Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s check user@example.com          # Check email deliverability
  %(prog)s whitelist user@example.com      # Whitelist an email
  %(prog)s blacklist user@example.com      # Blacklist an email
  %(prog)s list                            # List blacklisted emails
  %(prog)s whitelist-list                  # List whitelisted emails
  %(prog)s report                          # Generate report
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check email deliverability')
    check_parser.add_argument('email', help='Email address to check')
    
    # Whitelist command
    whitelist_parser = subparsers.add_parser('whitelist', help='Whitelist an email')
    whitelist_parser.add_argument('email', help='Email address to whitelist')
    whitelist_parser.add_argument('--notes', default='', help='Notes about whitelisting')
    
    # Blacklist command
    blacklist_parser = subparsers.add_parser('blacklist', help='Blacklist an email')
    blacklist_parser.add_argument('email', help='Email address to blacklist')
    blacklist_parser.add_argument('--reason', default='Manual addition', help='Reason for blacklisting')
    
    # List commands
    subparsers.add_parser('list', help='List blacklisted emails')
    subparsers.add_parser('whitelist-list', help='List whitelisted emails')
    
    # Report command
    subparsers.add_parser('report', help='Generate email status report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = EmailBlacklistManager()
    
    if args.command == 'check':
        results = manager.check_email_deliverability(args.email)
        
        print("\n" + "="*60)
        print("📋 DELIVERABILITY SUMMARY")
        print("="*60)
        print(f"Email: {results['email']}")
        print(f"Valid format: {'✅ Yes' if results['is_valid'] else '❌ No'}")
        print(f"Whitelisted: {'✅ Yes' if results['is_whitelisted'] else '❌ No'}")
        print(f"Blacklisted: {'⚠️  Yes' if results['is_blacklisted'] else '✅ No'}")
        print(f"DNSBL listed: {'⚠️  Yes' if results['dnsbl_status']['is_listed'] else '✅ No'}")
        
        if results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
    
    elif args.command == 'whitelist':
        manager.whitelist_email(args.email, args.notes)
    
    elif args.command == 'blacklist':
        manager.add_to_blacklist(args.email, args.reason)
    
    elif args.command == 'list':
        blacklist = manager.list_blacklist()
        if blacklist:
            print("\n📧 Blacklisted Emails:")
            print("-" * 80)
            print(f"{'Email':<40} {'Reason':<20} {'Bounces':<8} {'Date'}")
            print("-" * 80)
            for entry in blacklist:
                email, bl_type, reason, listed_date, bounce_count = entry[1], entry[2], entry[3], entry[4], entry[5]
                print(f"{email:<40} {reason:<20} {bounce_count:<8} {listed_date}")
        else:
            print("✅ No blacklisted emails!")
    
    elif args.command == 'whitelist-list':
        whitelist = manager.list_whitelist()
        if whitelist:
            print("\n✅ Whitelisted Emails:")
            print("-" * 80)
            print(f"{'Email':<40} {'Notes':<30} {'Date'}")
            print("-" * 80)
            for entry in whitelist:
                email, date, notes = entry[1], entry[2], entry[3] or ""
                print(f"{email:<40} {notes:<30} {date}")
        else:
            print("No whitelisted emails!")
    
    elif args.command == 'report':
        manager.generate_report()


if __name__ == '__main__':
    main()
