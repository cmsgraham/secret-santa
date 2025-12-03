#!/usr/bin/env python
"""
Migration script to add missing columns to users and participants tables
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_v2 import app, db
from models import User

def migrate():
    """Run migration"""
    with app.app_context():
        try:
            from sqlalchemy import text
            
            print("🔄 Running database migrations...")
            print()
            
            # Check and add columns to users table
            print("📋 Checking users table...")
            inspector_query = "SELECT column_name FROM information_schema.columns WHERE table_name='users'"
            result = db.session.execute(text(inspector_query))
            users_columns = {row[0] for row in result}
            
            if 'unsubscribe_token' not in users_columns:
                print("  ➕ Adding unsubscribe_token column to users...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN unsubscribe_token VARCHAR(64) UNIQUE"))
                db.session.commit()
            else:
                print("  ✓ unsubscribe_token already exists")
            
            if 'email_opt_out' not in users_columns:
                print("  ➕ Adding email_opt_out column to users...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN email_opt_out BOOLEAN DEFAULT FALSE"))
                db.session.commit()
            else:
                print("  ✓ email_opt_out already exists")
            
            # Check and add columns to participants table
            print()
            print("📋 Checking participants table...")
            inspector_query = "SELECT column_name FROM information_schema.columns WHERE table_name='participants'"
            result = db.session.execute(text(inspector_query))
            participants_columns = {row[0] for row in result}
            
            if 'gift_links' not in participants_columns:
                print("  ➕ Adding gift_links column to participants...")
                db.session.execute(text("ALTER TABLE participants ADD COLUMN gift_links TEXT"))
                db.session.commit()
            else:
                print("  ✓ gift_links already exists")
            
            if 'preferred_language' not in participants_columns:
                print("  ➕ Adding preferred_language column to participants...")
                db.session.execute(text("ALTER TABLE participants ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'"))
                db.session.commit()
            else:
                print("  ✓ preferred_language already exists")
            
            print()
            print("✅ All migrations completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration error: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate()
