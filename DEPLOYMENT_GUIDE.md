# Production Deployment Guide - Multilingual Update

This document explains how to deploy the multilingual update to your production Secret Santa server.

## ⚠️ Important: Database Migration Required

The new multilingual feature adds two new columns to the PostgreSQL database:
- `users.preferred_language` 
- `participants.preferred_language`

### Option 1: Automatic Database Initialization (Fresh Database)

If you're starting with a fresh database, the columns will be created automatically:

```bash
# Run on your production server
docker-compose up -d db
sleep 5
docker-compose run app python init_db.py
```

### Option 2: Migrate Existing Database

If you have an existing database with data, use the migration script:

```bash
# Run on your production server
docker-compose exec db psql -U secret_santa -d secret_santa_db -f /docker-entrypoint-initdb.d/add_language_columns.sql

# OR use the Python migration script:
docker-compose exec app python migrate_add_language_support.py
```

### Option 3: Manual SQL Migration

Connect directly to PostgreSQL and run:

```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL;

ALTER TABLE participants 
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL;

-- Optional: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_preferred_language ON users(preferred_language);
CREATE INDEX IF NOT EXISTS idx_participants_preferred_language ON participants(preferred_language);
```

## 🚀 Deployment Steps

### Step 1: Pull Latest Code

```bash
cd /path/to/secret_santa
git pull origin main
```

### Step 2: Apply Database Migration

Choose one of the migration options above based on your database state.

### Step 3: Rebuild Docker Image

```bash
docker-compose down
docker-compose up -d --build
```

### Step 4: Verify Deployment

```bash
# Check if app is running
curl http://localhost:5000/health

# Check if language selector appears on login page
curl http://localhost:5000/login | grep -c "language-selector"
```

## ✨ New Features

After deployment, users will see:

1. **Language Selector** on all pages (login, register, home, dashboard, etc.)
2. **6 Language Options:**
   - English
   - Español (México)
   - Español (Costa Rica)
   - Español (Colombia)
   - Español (Argentina)
   - Español (España)

3. **Automatic Language Persistence:**
   - Language preference saved to user profile in database
   - Persists across sessions and devices
   - Falls back to Accept-Language header for new users

## 📋 Files Changed

New files added:
- `i18n.py` - Translation system core
- `jinja_i18n.py` - Jinja2 template integration
- `language_selector.py` - Language metadata
- `templates/components/language_selector.html` - Language selector component
- `translations/en/messages.json` - English translations
- `translations/es_*/messages.json` - Spanish variant translations
- `migrate_add_language_support.py` - Database migration script
- `add_language_columns.sql` - SQL migration script

Modified files:
- `app_v2.py` - Added language detection middleware and API endpoints
- All template files - Added language selector components
- `models.py` - Added `preferred_language` columns

## 🔧 API Endpoints

### Set Language
```
POST /api/language/set
Content-Type: application/json

{
  "language": "es_CR"
}
```

Response:
```json
{
  "success": true,
  "message": "Language preference updated",
  "language": "es_CR"
}
```

### Get Supported Languages
```
GET /api/languages

Response:
{
  "success": true,
  "languages": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English",
      "flag": "🇺🇸",
      "region": "United States"
    },
    ...
  ],
  "current": "en"
}
```

## 🧪 Testing

After deployment:

1. Visit login page: http://your-server/login
2. Look for language selector in top-right
3. Click selector and choose Spanish variant
4. Page should reload with Spanish translations
5. Log in and verify language persists after login

## 📊 Database Schema Changes

### Users Table
```sql
ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL;
```

### Participants Table
```sql
ALTER TABLE participants ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL;
```

## ⚡ Performance Notes

- Translation files are cached with `@lru_cache` decorator
- Language detection happens before each request via middleware
- Session language takes priority to minimize database queries
- Indexes created on language columns for fast lookups

## 🆘 Troubleshooting

### Language selector not appearing
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
- Check browser console for JavaScript errors
- Verify translation files are present: `translations/en/messages.json`

### Database migration fails
- Verify PostgreSQL is running: `docker-compose ps`
- Check database connection: `docker-compose logs db`
- Manually verify columns exist: `SELECT column_name FROM information_schema.columns WHERE table_name='users';`

### Translations show keys instead of text
- Verify translation files are in `/app/translations/` directory
- Check that locale code is valid (en, es_MX, es_CR, es_CO, es_AR, es_ES)
- Check app logs: `docker-compose logs app`

## ✅ Deployment Checklist

- [ ] Pulled latest code from main branch
- [ ] Database migrated successfully
- [ ] Docker containers rebuilt
- [ ] App container is healthy
- [ ] Language selector visible on login page
- [ ] Can switch between languages
- [ ] Language persists after login
- [ ] No console errors in browser DevTools

## 📞 Support

If you encounter issues:

1. Check application logs: `docker-compose logs app`
2. Check database logs: `docker-compose logs db`
3. Verify environment variables in `.env` file
4. Review migration script output for errors

---

**Deployment Date:** December 2, 2025  
**Branch:** main  
**Commit:** b8fd91d
