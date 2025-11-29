# DNS Records for nameinahat.com Mail Server

Add these DNS records in your GoDaddy DNS management panel for **nameinahat.com**

## Server IP Address
**172.233.171.101**

---

## Required DNS Records

### 1. MX Record (Mail Exchange)
**Priority: 10**
```
Type: MX
Name: @
Value: mail.nameinahat.com
Priority: 10
TTL: 3600 (or 1 hour)
```

### 2. A Record for Mail Server
```
Type: A
Name: mail
Value: 172.233.171.101
TTL: 3600 (or 1 hour)
```

### 3. SPF Record (Sender Policy Framework)
```
Type: TXT
Name: @
Value: v=spf1 ip4:172.233.171.101 a:mail.nameinahat.com ~all
TTL: 3600 (or 1 hour)
```

**Explanation:**
- `v=spf1` - SPF version 1
- `ip4:172.233.171.101` - Allow sending from this IP
- `a:mail.nameinahat.com` - Allow sending from the A record of mail.nameinahat.com
- `~all` - Soft fail for all other servers (recommended for initial setup)

### 4. DKIM Record (DomainKeys Identified Mail)
```
Type: TXT
Name: mail._domainkey
Value: v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu8Qq3zPDEUMCxUjFyTjAMAmUvJ3+n5jPT1oWh9T4wVF2ytcpvIW9ofWYrsvIg8NwrqFCXSDkiWlchupuocfZ0N8k2y86cZ/iUO6ZJqJARJFnGkEwqMPYDg375qMKah2qsusZqDWMcKpOJaat0K/dsspUhoV5Pm5vmbrvNj/0RtZdZU5iunxpWv6FXrFqlOdI0qj9tcvkVeLbSltCBKXm3EuhSzEUDn65vflXvuGlm+DDg7EpJH4BlRGNKamS5rVN4l/0+FejpSiGYWWZb3x7xELdbV9P6AzujYlt1ixzvWLQn7FWxyU1qPyt5kMxjKi0gTJ/RK2AIREoNKN3yFvh2wIDAQAB
TTL: 3600 (or 1 hour)
```

**Note:** If GoDaddy has a character limit for TXT records, you may need to split the DKIM value into multiple strings in quotes. Some DNS providers accept it like this:
```
"v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu8Qq3zPDEUMCxUjFyTjAMAmUvJ3+n5jPT1oWh9T4wVF2ytcpvIW9ofWYrsvIg8NwrqFCXSDkiWlchupuocfZ0N8k2y86cZ/iUO6ZJqJARJFnGkEwqMPYDg375qMKah2qsusZqDWMcKpOJaat0K/dsspUhoV5Pm5vmbrvNj/0RtZdZU5iunxpWv6FXrFqlOdI0qj9tcvkVeLbSltCBKXm3EuhSzEUDn65vflXvuGlm+DDg7EpJH4BlRGNKamS5rVN4l/0+FejpSiGYWWZb3x7xELdbV9P6AzujYlt1ixzvWLQn7FWxyU1qPyt5kMxjKi0gTJ/RK2AIREoNKN3yFvh2wIDAQAB"
```

### 5. DMARC Record (Domain-based Message Authentication)
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:postmaster@nameinahat.com; ruf=mailto:postmaster@nameinahat.com; fo=1; adkim=r; aspf=r
TTL: 3600 (or 1 hour)
```

**Explanation:**
- `v=DMARC1` - DMARC version 1
- `p=none` - Policy: monitor only (start with this, can change to `quarantine` or `reject` later)
- `rua=mailto:postmaster@nameinahat.com` - Aggregate reports sent here
- `ruf=mailto:postmaster@nameinahat.com` - Forensic reports sent here
- `fo=1` - Generate reports for any authentication failure
- `adkim=r` - Relaxed DKIM alignment
- `aspf=r` - Relaxed SPF alignment

### 6. Reverse DNS (PTR Record) - Optional but Highly Recommended
**This must be configured through your hosting provider (Linode), not GoDaddy**

Contact Linode support or use their DNS manager to set:
```
PTR Record for 172.233.171.101 → mail.nameinahat.com
```

---

## Website DNS Records (Secret Santa Application)

### 7. A Record for Website Root
```
Type: A
Name: @
Value: 172.233.171.101
TTL: 3600 (or 1 hour)
```
This makes **nameinahat.com** point to your server where the Secret Santa app runs.

### 8. A Record for WWW Subdomain
```
Type: A
Name: www
Value: 172.233.171.101
TTL: 3600 (or 1 hour)
```
This makes **www.nameinahat.com** point to your server.

### 9. CNAME for Secret Santa Subdomain (Alternative Option)
If you prefer to use a subdomain like **secretsanta.nameinahat.com**:
```
Type: A
Name: secretsanta
Value: 172.233.171.101
TTL: 3600 (or 1 hour)
```

**Note:** Currently the Secret Santa app runs on port 5000. You'll need to either:
- Set up a reverse proxy (nginx) to serve on port 80/443
- Access it via: http://nameinahat.com:5000 (after DNS propagates)
- Or configure nginx to handle SSL and route traffic properly

---

## Step-by-Step Instructions for GoDaddy

1. **Log in to GoDaddy**
   - Go to https://www.godaddy.com
   - Sign in to your account

2. **Navigate to DNS Management**
   - Go to "My Products"
   - Find "nameinahat.com" domain
   - Click "DNS" or "Manage DNS"

3. **Add Each Record**
   - Click "Add" or "Add Record"
   - Select the record type (A, MX, TXT)
   - Fill in the Name and Value fields as shown above
   - Set TTL (Time To Live)
   - Click "Save"

4. **Wait for DNS Propagation**
   - DNS changes can take 1-48 hours to propagate globally
   - Usually happens within 1-4 hours
   - You can check propagation at: https://dnschecker.org

---

## Verification Commands

After adding the records and waiting for propagation, verify them:

### Check MX Record
```bash
dig MX nameinahat.com +short
```
Expected: `10 mail.nameinahat.com.`

### Check A Record
```bash
dig A mail.nameinahat.com +short
```
Expected: `172.233.171.101`

### Check SPF Record
```bash
dig TXT nameinahat.com +short | grep spf
```
Expected: `"v=spf1 ip4:172.233.171.101 a:mail.nameinahat.com ~all"`

### Check DKIM Record
```bash
dig TXT mail._domainkey.nameinahat.com +short
```
Expected: Should show the DKIM public key

### Check DMARC Record
```bash
dig TXT _dmarc.nameinahat.com +short
```
Expected: `"v=DMARC1; p=none; rua=mailto:postmaster@nameinahat.com..."`

### Check Website A Records
```bash
dig A nameinahat.com +short
```
Expected: `172.233.171.101`

```bash
dig A www.nameinahat.com +short
```
Expected: `172.233.171.101`

---

## Testing Email Delivery

Once DNS records are propagated, test with:

### 1. Mail Tester
Send an email to a generated address at: https://www.mail-tester.com
This will give you a score out of 10 and show any issues.

### 2. Manual Test
```bash
curl -X POST http://172.233.171.101:5000/assign \
  -H "Content-Type: application/json" \
  -d '{"event_name":"DNS Test","organizer_email":"your-email@gmail.com","emails":"your-email@gmail.com\ntest@example.com"}'
```

---

## Current Status

- ✅ Mail server is running and operational
- ✅ DKIM signing is configured
- ✅ Successfully delivering to Gmail (tested)
- ✅ Secret Santa app is running on port 5000
- ⏳ DNS records need to be added (this document)
- ⏳ Reverse DNS (PTR) recommended but optional
- ⏳ Nginx reverse proxy recommended for production (port 80/443)

## Accessing the Secret Santa Website

**After DNS propagation:**
- Direct access: http://nameinahat.com:5000
- With www: http://www.nameinahat.com:5000
- Current IP access: http://172.233.171.101:5000

**For production (recommended):**
Set up nginx as a reverse proxy to:
- Serve on standard ports 80 (HTTP) and 443 (HTTPS)
- Handle SSL/TLS certificates (Let's Encrypt)
- Remove the need for :5000 port in URLs
- Enable access via: https://nameinahat.com

## Notes

- **Without these DNS records**: Emails will still be sent but may be marked as spam
- **With these DNS records**: Email deliverability and reputation will improve significantly
- **Start with monitoring**: DMARC policy is set to `p=none` to monitor without blocking
- **After 2-4 weeks**: Review DMARC reports and consider changing to `p=quarantine` or `p=reject`

---

## Support

If you encounter issues:
1. Use the verification commands above to check DNS propagation
2. Check mail server logs: `docker logs nameinahat-mailserver`
3. Test with mail-tester.com for detailed deliverability analysis
