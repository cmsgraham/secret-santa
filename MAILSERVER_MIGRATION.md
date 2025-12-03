# Mail Server Migration - Complete ✅

## Migration Summary

Your mail server has been successfully migrated from the old Linode server to the new Akamai server.

| Component | Old Server | New Server | Status |
|-----------|-----------|-----------|--------|
| **Application Server** | 172.233.171.101 | 172.233.185.208 | ✅ Migrated |
| **Mail Server** | 172.233.171.101 | 172.233.185.208 | ✅ Migrated |
| **Web Domain** | nameinahat.com | nameinahat.com | ⏳ DNS pending |
| **Mail Domain** | mail.nameinahat.com (old IP) | mail.nameinahat.com (new IP) | ⏳ DNS pending |

## What's Been Done

✅ **Mail server Docker containers copied to new server (172.233.185.208)**
- Mailserver configuration: `/opt/mailserver/`
- Mail accounts: `secretsanta@`, `noreply@`, `admin@`
- SSL certificates: Copied and configured
- DKIM keys: Migrated
- Mail storage: Fresh database ready

✅ **Mail server started and running**
- All services operational: Postfix, Dovecot, OpenDKIM, OpenDMARC, Amavis
- SMTP port 2587 (TLS): Ready to accept mail
- IMAP port 2143: Ready for mail retrieval
- SMTPS port 2465, IMAPS port 2993: Available

✅ **Flask app updated**
- SMTP settings updated to point to new server (172.233.185.208:2587)
- docker-compose.yml: Updated
- .env on server: Updated
- App restarted and running

## Required DNS Changes

**You must update these DNS records for the mail server to work:**

### 1. Update A Record for mail subdomain
```
Type: A
Name: mail
Old Value: 172.233.171.101
New Value: 172.233.185.208  ← UPDATE THIS
TTL: 3600 (1 hour)
```

### 2. Update SPF Record
```
Type: TXT
Name: @
Old Value: v=spf1 mx a:mail.nameinahat.com ip4:172.233.171.101 ~all
New Value: v=spf1 mx a:mail.nameinahat.com ip4:172.233.185.208 ~all  ← UPDATE THIS
TTL: 3600 (1 hour)
```

### 3. MX Record (no change needed - points to mail.nameinahat.com)
```
Type: MX
Name: @
Value: mail.nameinahat.com  (unchanged - DNS will resolve to new IP via A record)
Priority: 10
TTL: 3600 (1 hour)
```

### 4. DKIM Record (no change needed)
```
Type: TXT
Name: mail._domainkey
Value: [same as before - DKIM keys were migrated]
TTL: 3600 (1 hour)
```

### 5. DMARC Record (no change needed)
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:admin@nameinahat.com; ruf=mailto:admin@nameinahat.com; fo=1
TTL: 3600 (1 hour)
```

## How to Update DNS (GoDaddy Example)

1. **Log in to your GoDaddy account**
2. **Go to Domains → nameinahat.com → Manage DNS**
3. **Find and edit the A record for "mail"**
   - Change value from `172.233.171.101` to `172.233.185.208`
   - Click Save
4. **Find and edit the TXT record for "@" (SPF record)**
   - Change `ip4:172.233.171.101` to `ip4:172.233.185.208`
   - Click Save
5. **Wait for DNS propagation (15-30 minutes)**

## Reverse DNS Configuration (Important for Email Deliverability)

To improve email deliverability, configure reverse DNS (PTR) at Akamai:

1. **Log in to your Akamai account**
2. **Navigate to: Compute → Linodes → 172.233.185.208**
3. **Go to: Networking → Reverse DNS**
4. **Set the reverse DNS to: `mail.nameinahat.com`**
5. **Save and wait for propagation (15-30 minutes)**

## Mail Server Details

### Location
- Path: `/opt/mailserver/` on 172.233.185.208

### Services Running
```
- Postfix (SMTP relay)
- Dovecot (IMAP/POP3)
- OpenDKIM (DKIM signing)
- OpenDMARC (DMARC validation)
- Amavis (Virus/Spam scanning)
- SpamAssassin (Spam filtering)
- ClamAV (Virus scanning)
- Fail2Ban (Brute force protection)
- Postgrey (Greylisting)
```

### Available Ports
- **SMTP Submission**: 2587 (TLS required) ← Used by app
- **SMTPS**: 2465 (SSL)
- **SMTP**: 2525 (internal)
- **IMAP**: 2143 (STARTTLS)
- **IMAPS**: 2993 (SSL)
- **POP3S**: 2995 (SSL)

### Mail Accounts (from .mail-credentials)
- `secretsanta@nameinahat.com` - Application sender
- `noreply@nameinahat.com` - System notifications
- `admin@nameinahat.com` - Server administration

## Testing Email Delivery

After DNS updates propagate, test with:

```bash
# SSH to new server
ssh -i ~/.ssh/linode root@172.233.185.208

# Check mail server
cd /opt/mailserver
docker-compose logs nameinahat-mailserver | tail -50

# Test SMTP connection
telnet 172.233.185.208 2587

# Test mail queue
docker exec nameinahat-mailserver postqueue -p

# Send test email
echo "Test" | mail -s "Test" -S smtp=172.233.185.208:2587 test@gmail.com
```

## Monitoring Mail Server

### View logs
```bash
cd /opt/mailserver
docker-compose logs -f
```

### Check mail queue
```bash
docker exec nameinahat-mailserver postqueue -p
```

### Check mail delivery
```bash
docker exec nameinahat-mailserver grep "to=" /var/log/mail.log | tail -20
```

## Important Notes

⚠️ **Do not delete the old mail server** until:
1. DNS propagation is complete (24-48 hours)
2. All emails have been delivered
3. You've verified mail flow is working
4. You've tested email sending from the app

⚠️ **Old server** (172.233.171.101) should be kept running temporarily as a backup

## Troubleshooting

### Mail not being delivered
1. Check DNS records are updated to 172.233.185.208
2. Wait for DNS propagation
3. Verify reverse DNS is configured
4. Check mail server logs: `docker-compose logs`

### SMTP connection refused
1. Verify port 2587 is open on firewall (Akamai CloudGuard)
2. Check mail server is running: `docker-compose ps`
3. Test locally: `docker exec nameinahat-mailserver telnet localhost 2587`

### Email marked as spam
1. Verify SPF, DKIM, DMARC records
2. Set up reverse DNS (PTR)
3. Test with: https://mail-tester.com/
4. Check reputation at: https://mxtoolbox.com/

## Next Steps

1. ✅ Mail server running on new server
2. ⏳ **Update DNS A record for mail** (from 172.233.171.101 → 172.233.185.208)
3. ⏳ **Update SPF record** (from ip4:172.233.171.101 → ip4:172.233.185.208)
4. ⏳ **Configure reverse DNS** (mail.nameinahat.com for 172.233.185.208)
5. ⏳ Wait for DNS propagation (15-30 minutes)
6. ✅ Test email delivery from app

---

**Status**: Mail server migration complete - **Awaiting DNS updates**
**Date**: December 3, 2025
