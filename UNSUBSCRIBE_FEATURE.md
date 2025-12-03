# Email Unsubscribe Feature - RFC 8058 Implementation

## Overview

The Secret Santa application now includes professional email unsubscribe functionality that appears directly in Gmail, Outlook, and other email clients—just like major platforms such as Amazon, GitHub, and Slack.

## How It Works

### 1. **One-Click Unsubscribe (Gmail/Outlook)**

When users receive emails, they'll see an "Unsubscribe" link in the email client's header:

```
Gmail:  [List Unsubscribe +]  (appears at the top of the email)
Outlook: [Unsubscribe] button (appears in the message header)
```

This is achieved through **RFC 8058** email headers that are automatically added to every email:

```
List-Unsubscribe: <https://nameinahat.com/unsubscribe/TOKEN>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

### 2. **How Users Are Unsubscribed**

When a user clicks the unsubscribe button:
- Their `email_opt_out` flag is set to `True` in the database
- No more emails will be sent to them
- They see a confirmation page
- They can resubscribe at any time

### 3. **Email Format**

All emails are now sent as:
- **Plain text version** - includes unsubscribe links
- **HTML version** - includes styled footer with Unsubscribe and Manage Preferences links

Both versions are included for maximum compatibility across email clients.

## Technical Implementation

### Unsubscribe Token Generation

Every user automatically gets a unique unsubscribe token:
```python
unsubscribe_token = SHA256(user_id + random_hex)
```

This token is:
- Unique per user
- Stored in the database
- Used in unsubscribe/resubscribe links
- 64 characters long

### Email Sending Flow

```
1. User created/logged in
   ↓
2. ensure_user_has_unsubscribe_token() called
   ↓
3. Email sent with RFC 8058 headers
   ↓
4. User sees "Unsubscribe" in email client
   ↓
5. User can click to unsubscribe OR resubscribe
```

### Database Fields

```python
User model:
  - unsubscribe_token: VARCHAR(64) - unique token for links
  - email_opt_out: BOOLEAN - whether user opted out (default: False)
```

## Routes

### Unsubscribe Route
```
GET/POST /unsubscribe/<token>
- GET: Shows confirmation page
- POST: Sets email_opt_out = True, shows success
```

### Resubscribe Route
```
GET/POST /resubscribe/<token>
- GET: Shows resubscribe confirmation page
- POST: Sets email_opt_out = False, shows success
```

## Email Header Examples

### Before (No RFC 8058)
```
From: secretsanta@nameinahat.com
To: user@example.com
Subject: Your Secret Santa Assignment
```
❌ No unsubscribe button in Gmail/Outlook

### After (RFC 8058 Compliant)
```
From: secretsanta@nameinahat.com
To: user@example.com
Subject: Your Secret Santa Assignment
List-Unsubscribe: <https://nameinahat.com/unsubscribe/abc123def456...>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
Content-Type: multipart/alternative
```

✅ Unsubscribe button appears in Gmail/Outlook header

## User Experience

### Unsubscribing
1. User receives email
2. Clicks "Unsubscribe" in email client header
3. Sees confirmation page
4. Confirms they want to unsubscribe
5. Gets success message: "✅ You have been unsubscribed!"
6. No more emails received

### Resubscribing
1. User navigates to resubscribe link (from email footer or settings)
2. Sees resubscribe confirmation page
3. Confirms they want to resubscribe
4. Gets success message: "✅ You have been resubscribed!"
5. Receives Secret Santa emails again

## Benefits

✅ **Professional** - Matches Gmail/Outlook standards
✅ **One-click** - Users don't need to verify via email
✅ **Compliant** - Follows RFC 8058 standard
✅ **User-friendly** - Clear, intuitive process
✅ **Trackable** - App knows when users unsubscribe
✅ **Recoverable** - Users can resubscribe anytime

## Email Client Support

| Client | Unsubscribe Display | Support |
|--------|-------------------|---------|
| Gmail | Header button | ✅ Full support |
| Outlook | Header button | ✅ Full support |
| Apple Mail | Link in footer | ✅ Full support |
| Thunderbird | Link in header | ✅ Full support |
| Spam checkers | Recognized as legitimate | ✅ Improves deliverability |

## Code Changes

### Updated Files
- `app_v2.py` - Enhanced `send_email()` function with RFC 8058 headers
- `templates/resubscribe.html` - New resubscribe confirmation page

### Key Functions
- `generate_unsubscribe_token()` - Creates unique tokens
- `ensure_user_has_unsubscribe_token()` - Ensures every user has a token
- `send_email()` - Sends emails with RFC 8058 headers and multipart content
- `unsubscribe()` route - Handles unsubscribe flow
- `resubscribe()` route - Handles resubscribe flow

## Testing

To test the unsubscribe feature:

1. **Send test email:**
   ```python
   from app_v2 import send_email
   send_email('test@example.com', 'Test Subject', 'Test body', user_id='user-id')
   ```

2. **Check email headers:**
   - Look for "List-Unsubscribe" header
   - Should contain full HTTPS URL with token

3. **Test unsubscribe link:**
   - Click the unsubscribe link
   - Should see confirmation page
   - Database should have `email_opt_out = True`

4. **Test resubscribe link:**
   - Click the resubscribe link
   - Should see resubscribe page
   - Database should have `email_opt_out = False`

## Deployment Status

✅ **Live in Production**
- Deployed to: `https://nameinahat.com`
- All emails now include RFC 8058 headers
- Users can unsubscribe via their email client
- Database migration applied: columns added to production

## References

- [RFC 8058 - Clarifications for RFC 5545 Compliance](https://tools.ietf.org/html/rfc8058)
- [Gmail - Add a "List-Unsubscribe" email header](https://support.google.com/a/answer/6254652)
- [Mailgun - Email Unsubscribe Headers](https://documentation.mailgun.com/en/latest/user_manual.html#mailing-lists)
- [List-Unsubscribe Header Best Practices](https://returnable.gitbook.io/deliverability/email-list-unsubscribe-best-practices)
