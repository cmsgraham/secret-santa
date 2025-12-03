# Email Management Integration Guide

## Summary

Created a complete email blacklist/whitelist management system for the Secret Santa application.

## Problem Solved

When emails are blacklisted by your mail server, they won't be delivered to recipients. This toolkit allows you to:
- ✅ Check which emails are blacklisted
- ✅ Identify why emails are being rejected (bounces, DNSBL, invalid addresses)
- ✅ Whitelist legitimate addresses
- ✅ Monitor email deliverability
- ✅ Track bounce patterns

## Files Created

| File | Purpose | Type |
|------|---------|------|
| `email_blacklist_management.py` | Core blacklist/whitelist management | Python library |
| `email_management.sh` | Command-line interface | Shell script |
| `email_helper.py` | Flask integration helper | Python module |
| `EMAIL_MANAGEMENT_GUIDE.md` | Comprehensive documentation | Documentation |
| `EMAIL_MANAGEMENT_QUICKREF.md` | Quick reference | Documentation |
| `email_blacklist.db` | SQLite database (auto-created) | Database |

## Immediate Usage

### Check an Email

```bash
cd /Users/cmadriga/secret_santa
./email_management.sh check cristian.madrigal@gmail.com
```

### Whitelist an Email

```bash
./email_management.sh whitelist cristian.madrigal@gmail.com "Valid customer"
```

### View Report

```bash
./email_management.sh report
```

## Integration with Flask App

### Option 1: Command-line Check Before Sending

```python
# In app_v2.py or email sending function
import subprocess
import sys

def send_email_safely(recipient_email, subject, body):
    """Send email only if it's not blacklisted"""
    from email_helper import check_email_before_send
    
    # Check if we should send
    if not check_email_before_send(recipient_email):
        print(f"⚠️  Skipping email to {recipient_email} - blacklisted")
        return False
    
    # Send email normally
    try:
        # your email sending code here
        send_email(recipient_email, subject, body)
        return True
    except smtplib.SMTPRecipientsRefused as e:
        # Record bounce
        from email_helper import record_email_bounce
        record_email_bounce(recipient_email, 'hard')
        return False
```

### Option 2: Check Whitelist for VIP Users

```python
def send_event_notification(participant_email):
    """Send event notification with bounce tracking"""
    from email_helper import FlaskEmailHelper
    
    helper = FlaskEmailHelper()
    status = helper.get_email_status(participant_email)
    
    # Log email status
    print(f"Email status for {participant_email}:")
    print(f"  - Blacklisted: {status['is_blacklisted']}")
    print(f"  - Whitelisted: {status['is_whitelisted']}")
    print(f"  - Bounces: {status['bounce_count']}")
    
    # Send if should_send
    if status['should_send']:
        send_email(participant_email, "Your Secret Santa Assignment", "...")
    else:
        logger.warning(f"Email {participant_email} marked for skip - status: {status}")
```

### Option 3: Admin Route to Check Email Status

```python
@app.route('/admin/email-check/<email>', methods=['GET'])
def admin_check_email(email):
    """Admin endpoint to check email status"""
    from email_helper import get_email_status_check
    
    status = get_email_status_check(email)
    return jsonify(status)
```

## Database Structure

The SQLite database tracks three types of information:

### email_blacklist table
```sql
CREATE TABLE email_blacklist (
    email TEXT PRIMARY KEY,
    blacklist_type TEXT,
    reason TEXT,
    listed_date TIMESTAMP,
    bounce_count INTEGER,
    last_bounce TIMESTAMP,
    whitelisted BOOLEAN,
    whitelisted_date TIMESTAMP
);
```

### email_whitelist table
```sql
CREATE TABLE email_whitelist (
    email TEXT PRIMARY KEY,
    whitelisted_date TIMESTAMP,
    notes TEXT
);
```

### dnsbl_checks table
```sql
CREATE TABLE dnsbl_checks (
    email TEXT,
    domain TEXT,
    check_date TIMESTAMP,
    is_listed BOOLEAN,
    dnsbl_list TEXT,
    result TEXT
);
```

## Deployment

### Step 1: Copy Files to Server

```bash
ssh -i ~/.ssh/linode root@172.233.185.208

cd /opt/secret-santa

# Copy files
scp -i ~/.ssh/linode email_blacklist_management.py root@172.233.185.208:/opt/secret-santa/
scp -i ~/.ssh/linode email_helper.py root@172.233.185.208:/opt/secret-santa/
scp -i ~/.ssh/linode email_management.sh root@172.233.185.208:/opt/secret-santa/

# Make executable
chmod +x /opt/secret-santa/email_management.sh
```

### Step 2: Check Email Deliverability

```bash
cd /opt/secret-santa

# Check specific email
python3 email_blacklist_management.py check user@example.com

# View all blacklisted
python3 email_blacklist_management.py list

# Generate report
python3 email_blacklist_management.py report
```

### Step 3: Whitelist Known Good Addresses

```bash
./email_management.sh whitelist cristian.madrigal@gmail.com "Primary contact"
./email_management.sh whitelist support@company.com "Business partner"
```

### Step 4: Set Up Cron Job (Optional)

```bash
# Add to crontab
crontab -e

# Add this line for daily report at 9am
0 9 * * * cd /opt/secret-santa && python3 email_blacklist_management.py report > /var/log/email_report.log 2>&1
```

## Monitoring

### Daily Email Report

```bash
./email_management.sh report
```

Expected output:
```
============================================================
📊 EMAIL BLACKLIST/WHITELIST REPORT
============================================================

📧 Statistics:
  • Blacklisted emails: X
  • Whitelisted emails: Y
  • Previously whitelisted: Z

⚠️  Current Blacklisted Emails:
  • user@example.com     - Hard bounce (bounces: 3)
  • noreply@test.com     - Soft bounce (bounces: 2)

✅ Whitelisted Emails:
  • cristian.madrigal@gmail.com  - Primary contact
```

### Check Specific Email

```bash
./email_management.sh check user@example.com
```

## Troubleshooting

### Q: Email shows as blacklisted, but I know it's valid

**A:** Whitelist it with context:
```bash
./email_management.sh whitelist user@example.com "Customer - re-verified"
```

### Q: How do I check why an email is bouncing?

**A:** Run the check command:
```bash
./email_management.sh check user@example.com
```

It will show:
- Email format validation
- DNSBL status
- DNS records (SPF, DKIM, DMARC)
- Bounce count
- Last bounce date

### Q: Can I integrate this into the Flask app?

**A:** Yes! Use the `email_helper.py` module:
```python
from email_helper import check_email_before_send, record_email_bounce

# Before sending
if check_email_before_send(email):
    send_email(email)

# After bounce
record_email_bounce(email, 'hard')
```

### Q: Where is the database stored?

**A:** It's an SQLite database at:
```
/Users/cmadriga/secret_santa/email_blacklist.db
/opt/secret-santa/email_blacklist.db (on production server)
```

You can view it directly:
```bash
sqlite3 email_blacklist.db
> SELECT * FROM email_whitelist;
> SELECT * FROM email_blacklist;
```

## Advanced: Batch Operations

### Whitelist from CSV

```bash
# Create whitelist.csv with emails
cat whitelist.csv | while IFS= read -r email; do
    ./email_management.sh whitelist "$email"
done
```

### Check Multiple Emails

```bash
for email in user1@example.com user2@example.com user3@example.com; do
    ./email_management.sh check "$email"
done
```

### Export Report to File

```bash
./email_management.sh report > email_report_$(date +%Y%m%d).txt
```

## Best Practices

1. **Run weekly reports** to catch trends
2. **Whitelist VIP addresses** to ensure delivery
3. **Monitor bounce rates** - sudden increases indicate issues
4. **Check DNS records** when adding new domains
5. **Review blacklist regularly** - some bounces are temporary
6. **Document reasons** when whitelisting/blacklisting

## Support & Documentation

- Quick start: `EMAIL_MANAGEMENT_QUICKREF.md`
- Full guide: `EMAIL_MANAGEMENT_GUIDE.md`
- Test email: `./email_management.sh check test@example.com`

## Next Steps

1. ✅ Run a check on the blacklisted email
2. ✅ Whitelist it if it's valid
3. ✅ Check your mail server DNSBL status
4. ✅ Verify SPF/DKIM/DMARC records are configured
5. ✅ Monitor weekly with `report` command
