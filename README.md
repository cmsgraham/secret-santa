# Secret Santa Application

A production-ready web application for organizing Secret Santa gift exchanges with automatic randomization, email notifications via nameinahat.com mail server, and comprehensive logging.

## 🎯 Features

- 🎲 **Smart Randomization**: Automatically assigns Secret Santa pairs while ensuring no one gets themselves
- 📧 **Dedicated Mail Server**: Uses nameinahat.com mail server for reliable email delivery
- 🗄️ **PostgreSQL Database**: Persistent storage with full audit trails
- 📊 **Comprehensive Logging**: Track all events, assignments, and email deliveries
- 🐳 **Containerized**: Production-ready Docker setup with Docker Compose
- 🔒 **Security**: Rate limiting, security headers, and secure defaults
- 📈 **Scalable**: Horizontal scaling ready with load balancer support
- 🔍 **Monitoring**: Health checks and status endpoints
- ☁️ **Cloud Ready**: Deployable on AWS, GCP, Azure, or any container platform

## 🚀 Quick Start (Production)

```bash
# Clone and start
git clone <your-repo>
cd secret_santa

# Configure SMTP credentials for nameinahat.com mail server
cp .env.example .env
# Edit .env with SMTP settings from mailserver/.mail-credentials

./start.sh
```

The start script will:
- Set up environment configuration
- Build and deploy the containerized stack
- Start PostgreSQL database, Redis, and web app

**Access Points:**
- 🌐 **Web App**: http://localhost:5000
- 🔍 **Health Check**: http://localhost:5000/health

## 📧 Mail Server

This application uses a dedicated nameinahat.com mail server. See `/mailserver/README.md` for mail server documentation.

### SMTP Configuration:
- Server: 172.233.171.101
- Port: 2587
- TLS: Enabled
- Username: secretsanta@nameinahat.com

## 🛠️ Development Setup

```bash
# Clone the repository
git clone <your-repo>
cd secret_santa

# Development with Docker
docker-compose up -d

# OR Development with local Python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Flask App     │    │   PostgreSQL    │
│  (Load Balancer)│───▶│  (Secret Santa) │───▶│   (Database)    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       ▼                       
         │              ┌─────────────────┐              
         │              │     MailHog     │              
         └──────────────│   (SMTP Server) │              
                        │                 │              
                        └─────────────────┘              
```

### Infrastructure Components:

- **Flask Application**: Python web server handling Secret Santa logic
- **PostgreSQL**: Database storing events, assignments, and email logs
- **MailHog**: SMTP server for email delivery (development) or external SMTP (production)
- **Redis**: Cache and session storage (ready for background tasks)
- **Nginx**: Reverse proxy with rate limiting and security headers

## 📊 Database Schema

### Tables:
- **secret_santa_events**: Event metadata and status tracking
- **assignments**: Secret Santa giver-receiver pairs
- **email_logs**: Complete audit trail of all sent emails

### Key Features:
- UUID primary keys for security
- Comprehensive indexing for performance
- Audit trails with timestamps
- Email delivery status tracking

## How It Works

1. **Input**: Enter participant phone numbers with country codes (minimum 2)
2. **Validation**: System validates all phone number formats
3. **Assignment**: Randomly assigns Secret Santa pairs ensuring no self-assignments
4. **Notification**: Sends personalized WhatsApp messages to each participant with their assignment
5. **Complete**: All participants receive their Secret Santa assignments via WhatsApp!

## Project Structure

```
secret_santa/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── templates/
│   └── index.html     # Main web interface
├── static/
│   ├── styles.css     # CSS styling
│   └── script.js      # Frontend JavaScript
└── README.md          # This file
```

## WhatsApp Message Template

Each participant receives a WhatsApp message like this:

```
🎄 Ho Ho Ho! 🎅

Dear Participant,

You've been assigned as the Secret Santa for: *[Secret Person]*

Remember:
- Keep it a secret! 🤫
- Be thoughtful with your gift choice
- Have fun spreading holiday cheer! 🎁

Happy Holidays!
The Secret Santa Organizer

Event ID: [Event ID]
```

## Security Features

- **No Data Storage**: Email credentials are never stored
- **App Passwords**: Uses secure Gmail App Passwords instead of regular passwords
- **Input Validation**: Validates all email addresses before processing
- **Error Handling**: Graceful error handling for email sending failures

## Troubleshooting

**WhatsApp messages not delivered?**
- Verify your WhatsApp Business API credentials are correct
- Check phone numbers are in international format (+country code)
- Ensure your Meta app has proper permissions
- Verify you haven't exceeded message rate limits

**Getting "Invalid phone number" errors?**
- Ensure all phone numbers include country codes (+1, +44, etc.)
- Remove any spaces, dashes, or special characters except +
- Use international format: +1234567890

**API errors?**
- Check your access token is valid and not expired
- Verify your app permissions in Meta Developer Console
- Ensure your Phone Number ID is correct

**Application won't start?**
- Ensure Python virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check that port 5000 is not in use by another application

## Development

To modify or extend the application:

1. **Backend**: Edit `app.py` for server-side logic
2. **Frontend**: Modify files in `templates/` and `static/`
3. **Styling**: Update `static/styles.css`
4. **JavaScript**: Modify `static/script.js`

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

🎄 **Happy Holidays and enjoy your Secret Santa exchange!** 🎁