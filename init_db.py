#!/usr/bin/env python3
"""
Database initialization script for Secret Santa multi-event application.
Run this script to create all database tables.

Usage:
    python init_db.py
"""

import os
from sqlalchemy import create_engine
from models import Base, User, Event, Participant, Assignment, AuthToken

def init_database():
    """Initialize the database by creating all tables."""
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql://secret_santa:password@db:5432/secret_santa_db')
    
    print(f"📡 Connecting to database: {database_url}")
    engine = create_engine(database_url)
    
    print("🗄️  Dropping existing tables...")
    Base.metadata.drop_all(engine)
    
    print("📊 Creating new tables...")
    Base.metadata.create_all(engine)
    
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
