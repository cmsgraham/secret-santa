# 📧 Email Management Tools - Quick Reference

## What This Solves

**Problem**: Your emails are being blacklisted and rejected by recipient servers.

**Solution**: A set of tools to check email deliverability, manage blacklists, and whitelist legitimate addresses.

## Files Created

1. **`email_blacklist_management.py`** (Main Python script)
   - Core email blacklist/whitelist management
   - Email deliverability checking
   - DNSBL status checking
   - DNS record validation (SPF, DKIM, DMARC)

2. **`email_management.sh`** (Shell wrapper)
   - Easy-to-use command-line interface
   - Colored output for readability
   - Error handling and help messages

3. **`EMAIL_MANAGEMENT_GUIDE.md`** (Full documentation)
   - Comprehensive usage guide
   - Troubleshooting section
   - Integration examples

4. **`email_blacklist.db`** (Auto-created SQLite database)
   - Stores blacklisted emails
   - Tracks whitelisted addresses
   - Records DNSBL check history

## Quick Start

### Check an Email

```bash
./email_management.sh check user@example.com
```

This will:
- ✅ Validate email format
- ✅ Check if it's whitelisted
- ✅ Check if it's blacklisted
- ✅ Verify DNSBL status
- ✅ Check DNS records

### Whitelist an Email

```bash
./email_management.sh whitelist user@example.com "Customer email"
```

### Blacklist an Email

```bash
./email_management.sh blacklist spam@example.com "Hard bounce"
```

### View Lists

```bash
# Show blacklisted emails
./email_management.sh list

# Show whitelisted emails
./email_management.sh whitelist-list
```

### Generate Report

```bash
./email_management.sh report
```

## Common Issues & Solutions

### "Email is blacklisted: Hard bounce"

**Cause**: Email doesn't exist or is invalid
**Solution**:
1. Verify the email address is correct
2. If valid, whitelist it: `./email_management.sh whitelist user@example.com`
3. Check mail server logs for bounce reason

### "Domain is listed in DNSBL"

**Cause**: Your mail server IP reputation is poor
**Solution**:
1. Check mail server logs for configuration issues
2. Ensure SPF/DKIM/DMARC records are configured
3. Review bounce rates
4. Contact mail server provider about delisting

### "Missing SPF/DKIM/DMARC"

**Cause**: DNS records not configured
**Solution**:
1. Add SPF record: `v=spf1 include:mail.nameinahat.com ~all`
2. Configure DKIM with mail provider
3. Add DMARC record: `v=DMARC1; p=quarantine; rua=mailto:dmarc@nameinahat.com`

## Database Location

The email management database is stored in:
```
/Users/cmadriga/secret_santa/email_blacklist.db
```

## Integration with Python Code

```python
from email_blacklist_management import EmailBlacklistManager

manager = EmailBlacklistManager()

# Check if email should be sent
results = manager.check_email_deliverability('user@example.com')

if results['is_whitelisted']:
    # Send email - whitelisted
    send_email(user_email)
elif results['is_blacklisted'] and not results['is_whitelisted']:
    # Skip - blacklisted and not whitelisted
    log_skipped_email(user_email)
else:
    # Normal send
    send_email(user_email)
```

## Optional: Full Feature Set

Install these for complete DNSBL and DNS checking:

```bash
pip3 install --user dnspython email-validator python-dotenv
```

## Commands Reference

| Command | Usage | Purpose |
|---------|-------|---------|
| `check` | `check <email>` | Check email deliverability |
| `whitelist` | `whitelist <email> [notes]` | Add to whitelist |
| `blacklist` | `blacklist <email> [reason]` | Add to blacklist |
| `list` | `list` | Show blacklisted emails |
| `whitelist-list` | `whitelist-list` | Show whitelisted emails |
| `report` | `report` | Generate status report |

## Next Steps

1. **For immediate use**:
   ```bash
   ./email_management.sh check cristian.madrigal@gmail.com
   ./email_management.sh whitelist cristian.madrigal@gmail.com "Valid customer"
   ```

2. **For deployment**:
   - Copy scripts to production server
   - Set up cron job for weekly reports
   - Integrate with Flask app if needed

3. **For monitoring**:
   - Run `report` command weekly
   - Check mail server logs regularly
   - Review bounce patterns

## Support

See `EMAIL_MANAGEMENT_GUIDE.md` for:
- Detailed troubleshooting
- Advanced usage
- Database management
- Integration examples
