# Testing Guide - Multi-Event Secret Santa

## Local Testing Setup ✅

The application is now running locally with Docker!

### Quick Start

1. **Access the Application**
   - URL: http://localhost:5001
   - Landing page should be visible

2. **Test the Complete Flow**

   **Step 1: Login (Magic Link)**
   - Click "Get Started" or "Organizer Login"
   - Enter your name and email
   - Check your email for the magic link
   - Click the magic link to log in

   **Step 2: Create an Event**
   - After login, you'll see the dashboard
   - Click "Create New Event"
   - Choose a funny auto-generated name or enter custom name
   - Add description (optional)
   - Click "Create Event"

   **Step 3: Share Registration Link**
   - On the event management page, copy the registration link
   - Share with participants (or open in incognito window to test)

   **Step 4: Register Participants**
   - Open the registration link
   - Enter participant name and email
   - Submit (repeat for at least 3 participants)

   **Step 5: Run the Draw**
   - Return to event management page (organizer view)
   - Once minimum participants registered, click "Run Draw"
   - Assignments will be created and emails sent!

   **Step 6: Verify Emails**
   - Check participant email inboxes
   - Each should receive assignment with their recipient's name

### Current Configuration

**Ports:**
- Application: 5001 (changed from 5000 due to macOS Control Center)
- PostgreSQL: 5432
- Redis: 6379

**Docker Services:**
- `app`: Flask application (app_v2.py)
- `db`: PostgreSQL 15
- `redis`: Redis 7

**Email Server:**
- Host: 172.233.171.101:2587
- From: secretsanta@nameinahat.com
- SMTP credentials configured in .env

### Useful Commands

```bash
# View application logs
docker-compose logs app -f

# View all logs
docker-compose logs -f

# Restart application
docker-compose restart app

# Rebuild after code changes
docker-compose up -d --build app

# Stop all containers
docker-compose down

# Reset database
docker-compose exec app python init_db.py

# Access database directly
docker-compose exec db psql -U secret_santa -d secret_santa_db

# Check container status
docker-compose ps
```

### Database Schema

Tables created:
- `users` - Organizers with magic link authentication
- `events` - Events with status, codes, and settings
- `participants` - Event participants with registration info
- `assignments` - Secret Santa pairings (giver → receiver)
- `auth_tokens` - Magic link tokens (1-hour expiration)

### Testing Checklist

- [x] Docker containers running
- [x] Database initialized
- [x] Application accessible at localhost:5001
- [ ] Magic link authentication works
- [ ] Event creation works
- [ ] Event name generator produces funny names
- [ ] Registration link sharing works
- [ ] Participants can register
- [ ] Draw algorithm creates valid assignments
- [ ] Emails are sent successfully
- [ ] State transitions work (open → completed → closed)
- [ ] Reopen/rerun functionality works
- [ ] Authorization prevents non-organizers from managing

### Known Issues

1. **Port 5000 Conflict**: macOS Control Center uses port 5000, changed to 5001
2. **Redis Optional**: App works without Redis for now (sessions in memory)
3. **Email Testing**: Use real email addresses to test SMTP delivery

### Next Steps

1. Complete manual testing of all features
2. Test email delivery to various providers (Gmail, Outlook, etc.)
3. Verify all state transitions
4. Test error handling
5. Push to GitHub
6. Deploy to production server (172.233.171.101)

## Production Deployment

When ready to deploy:

1. **Push to GitHub**
   ```bash
   git push origin new_architecture
   ```

2. **SSH to Production Server**
   ```bash
   ssh root@172.233.171.101
   ```

3. **Pull Latest Code**
   ```bash
   cd /path/to/secret_santa
   git fetch origin
   git checkout new_architecture
   git pull
   ```

4. **Update Production .env**
   - Change `DEBUG=false`
   - Update `APP_URL=http://nameinahat.com` (or https after nginx setup)
   - Ensure strong `SECRET_KEY`

5. **Deploy**
   ```bash
   docker-compose down
   docker-compose up -d --build
   docker-compose exec app python init_db.py
   ```

6. **Test Production**
   - Access http://172.233.171.101:5000 (or configured port)
   - Complete full flow with real email addresses
   - Verify email delivery

7. **Optional: Setup Nginx Reverse Proxy**
   - Configure nginx for port 80/443
   - Setup SSL with Let's Encrypt
   - Enable https://nameinahat.com access

---

## Current Status

✅ **Completed:**
- Multi-event architecture implemented
- Magic link authentication
- Event creation with funny name generator
- Event management dashboard
- Participant registration
- Assignment algorithm
- Email integration
- Docker configuration
- Local testing environment

⏳ **In Progress:**
- Manual testing of complete flow
- Email delivery verification

📋 **Todo:**
- Deploy to production
- Setup nginx reverse proxy
- Configure SSL certificates
- Update DNS if needed

---

## Support

For issues or questions:
1. Check application logs: `docker-compose logs app`
2. Check database: `docker-compose exec db psql -U secret_santa -d secret_santa_db`
3. Verify email server: Test from mailserver container
4. Review code in `app_v2.py`, `models.py`, `event_names.py`
