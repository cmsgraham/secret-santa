#!/usr/bin/env python3
"""
Database initialization script for Secret Santa multi-event application.
Run this script to create all database tables.

Usage:
    python init_db.py
"""

import os
from models import db, User, Event, Participant, Assignment, AuthToken
from app_v2 import app

def init_database():
    """Initialize the database by creating all tables."""
    with app.app_context():
        print("🗄️  Dropping existing tables...")
        db.drop_all()
        
        print("📊 Creating new tables...")
        db.create_all()
        
        print("✅ Database initialized successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - events")
        print("  - participants")
        print("  - assignments")
        print("  - auth_tokens")
        print("\n🎉 Ready to start the application!")

if __name__ == "__main__":
    init_database()
