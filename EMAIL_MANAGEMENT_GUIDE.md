# Email Blacklist/Whitelist Management Guide

## Overview

The Email Blacklist/Whitelist Management tools help you monitor and manage email deliverability issues. This is especially useful when emails from your mail server are being rejected or blocked by recipient mail servers.

## Problem: Blacklisted Emails

Email addresses can be blacklisted for several reasons:
- **Bounce backs**: Multiple failed delivery attempts
- **Spam complaints**: Recipients marking emails as spam
- **DNS issues**: Missing or misconfigured SPF/DKIM/DMARC records
- **Server reputation**: Your mail server IP is listed in DNS Blacklist (DNSBL)
- **Invalid addresses**: Non-existent or inactive email accounts

## Solution: Tools

We provide two tools for email management:

1. **Python Script** (`email_blacklist_management.py`) - Core functionality
2. **Shell Script** (`email_management.sh`) - Easy-to-use wrapper

## Installation

### Dependencies

```bash
# Install required Python packages
pip3 install dnspython email-validator python-dotenv
```

### Setup

The scripts use an SQLite database (`email_blacklist.db`) that is automatically created on first run.

## Quick Start

### Check Email Deliverability

```bash
./email_management.sh check user@example.com
```

This checks:
- ✅ Email format validity
- ✅ Whitelist status
- ✅ Blacklist status
- ✅ DNSBL (DNS Blacklist) status
- ✅ DNS records (SPF, DKIM, DMARC)
- ✅ SMTP connectivity

**Example Output:**
```
📧 Checking deliverability for: user@example.com
  ✅ Email format is valid
  ❌ Email is blacklisted: Hard bounce (bounces: 3)
  🔍 Checking DNSBL for domain: example.com
    📧 Domain MX: mail.example.com
    🌐 MX IP: 192.0.2.1
    ✅ Domain is not listed in common DNSBLs
  SPF: ✅ Present
  DKIM: ⚠️  Requires selector
  DMARC: ✅ Present

============================================================
📋 DELIVERABILITY SUMMARY
============================================================
Email: user@example.com
Valid format: ✅ Yes
Whitelisted: ❌ No
Blacklisted: ⚠️  Yes
DNSBL listed: ✅ No

💡 Recommendations:
  • Consider whitelisting this email if it's valid
  • Check bounce reason and mail server logs
```

### Whitelist an Email

Whitelisting allows emails to bypass blacklist checks and be sent normally.

```bash
# Basic whitelist
./email_management.sh whitelist user@example.com

# With notes
./email_management.sh whitelist user@example.com "Customer - valid address"
```

### Blacklist an Email

Manually blacklist emails that should not receive messages.

```bash
# Basic blacklist
./email_management.sh blacklist invalid@example.com

# With reason
./email_management.sh blacklist invalid@example.com "Invalid address - multiple bounces"
```

### View Lists

```bash
# List blacklisted emails
./email_management.sh list

# List whitelisted emails
./email_management.sh whitelist-list
```

### Generate Report

Get a complete overview of email status.

```bash
./email_management.sh report
```

**Example Report:**
```
============================================================
📊 EMAIL BLACKLIST/WHITELIST REPORT
============================================================

📧 Statistics:
  • Blacklisted emails: 5
  • Whitelisted emails: 3
  • Previously whitelisted: 0

⚠️  Current Blacklisted Emails:
  • invalid@example.com       - Hard bounce (bounces: 5)
  • noreply@test.com          - Soft bounce (bounces: 2)
  • admin@oldomain.com        - Spam complaint (bounces: 1)

✅ Whitelisted Emails:
  • cristian.madrigal@gmail.com  - Valid customer
  • manager@company.com          - Employee
  • support@partner.org          - Business partner
```

## Understanding DNSBL (DNS Blacklist)

DNSBL lists maintain IP addresses of mail servers known to send spam. If your mail server's IP is listed, recipients will reject your emails.

### Common DNSBLs Checked

1. **Spamhaus**
   - zen.spamhaus.org
   - dyna.spamhaus.org
   - pbl.spamhaus.org
   - blacklist.spamhaus.org

2. **Other Lists**
   - aspews.ext.sorbs.net (Sorbs)
   - b.barracudacentral.org (Barracuda)

### If Your Server is DNSBL Listed

1. **Identify the issue**: Run `check` command for any domain email
2. **Check mail server logs** for spam/configuration issues
3. **Review bounce rates** - high bounces indicate reputation issues
4. **Fix DNS records** - ensure SPF/DKIM/DMARC are configured
5. **Request delisting** - contact the DNSBL provider for removal

## Checking Mail Server Configuration

The `check` command automatically validates:

### SPF (Sender Policy Framework)
- Specifies which mail servers can send email for your domain
- **Missing SPF**: Increases spam likelihood

### DKIM (DomainKeys Identified Mail)
- Cryptographically signs your emails
- **Missing DKIM**: Harder to verify email authenticity

### DMARC (Domain-based Message Authentication)
- Sets policy for handling authentication failures
- **Missing DMARC**: Allows email spoofing

### Fix DNS Records

Add these TXT records to your domain:

```
# SPF Record
v=spf1 include:mail.nameinahat.com ~all

# DMARC Record
v=DMARC1; p=quarantine; rua=mailto:dmarc@nameinahat.com

# DKIM
(Consult your mail hosting provider for DKIM selector and public key)
```

## Integration with Application

### Database Schema

The tool uses SQLite with three tables:

#### email_blacklist
- Tracks blacklisted email addresses
- Stores bounce counts and dates
- Records whitelist status

#### email_whitelist
- Stores whitelisted emails
- Allows notes for each entry

#### dnsbl_checks
- Maintains history of DNSBL checks
- Tracks which lists have checked an email

### Using in Code

```python
from email_blacklist_management import EmailBlacklistManager

manager = EmailBlacklistManager()

# Check if email is deliverable
results = manager.check_email_deliverability('user@example.com')
if results['is_whitelisted']:
    # Send email without restrictions
    pass
elif results['is_blacklisted']:
    # Handle blacklisted email
    pass
```

## Troubleshooting

### Script Won't Run

**Problem**: `command not found: python3`
**Solution**: Install Python 3.7+ and try again

**Problem**: `ModuleNotFoundError: No module named 'dns'`
**Solution**: Run `pip3 install dnspython`

### Email Shows as Blacklisted but Should Be Valid

1. Check the bounce reason - may be temporary
2. Verify email is actually deliverable
3. Whitelist if it's a known good address

### Server DNSBL Listed

1. Check mail server logs for configuration issues
2. Review bounce rates - look for patterns
3. Contact your hosting provider
4. Request delisting from DNSBL providers

## Best Practices

1. **Regular Monitoring**
   - Run `report` command weekly
   - Monitor bounce rates in mail server logs

2. **Proactive Whitelisting**
   - Whitelist trusted partners and customers
   - Reduce friction in email delivery

3. **Handle Bounces**
   - Monitor soft bounces (temporary failures)
   - Investigate hard bounces (permanent failures)

4. **Maintain DNS Records**
   - Ensure SPF/DKIM/DMARC are configured
   - Update records when mail server changes

5. **Blacklist Cleanup**
   - Periodically review blacklisted emails
   - Remove entries for addresses that have been fixed

## Advanced Usage

### Batch Operations

```bash
# Check multiple emails
for email in user1@example.com user2@example.com user3@example.com; do
    ./email_management.sh check "$email"
done

# Whitelist from file
while IFS= read -r email; do
    ./email_management.sh whitelist "$email"
done < whitelist.txt
```

### Integration with Cron

```bash
# Daily email report
0 9 * * * /path/to/email_management.sh report > /var/log/email_report.log

# Weekly whitelist check
0 10 * * 1 /path/to/email_management.sh list > /var/log/blacklist_check.log
```

## Database Management

### View Database

```bash
# Connect to SQLite
sqlite3 email_blacklist.db

# View blacklisted emails
SELECT email, reason, bounce_count FROM email_blacklist;

# View whitelisted emails
SELECT email, notes FROM email_whitelist;
```

### Reset Database

```bash
# Backup current database
cp email_blacklist.db email_blacklist.db.backup

# Remove old database (script will recreate)
rm email_blacklist.db
```

## Support

For issues or questions:

1. Check mail server logs: `/var/log/mail.log` or `/var/log/postfix/`
2. Review DNSBL status at: https://mxtoolbox.com/
3. Test DNS records with: https://www.dmarcian.com/
4. Contact mail hosting support for DNSBL delisting

## Related Documentation

- [Mail Server Configuration](../MAILSERVER_MIGRATION.md)
- [HTTPS Deployment](../HTTPS_DEPLOYMENT.md)
- [Security Advisory](../SECURITY_ADVISORY.md)
