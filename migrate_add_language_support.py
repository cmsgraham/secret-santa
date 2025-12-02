#!/usr/bin/env python3
"""
Migration script to add multilingual support columns to existing database.
This script adds the preferred_language columns to users and participants tables.

Usage:
    python migrate_add_language_support.py

This is safe to run multiple times - it uses IF NOT EXISTS to avoid errors.
"""

import os
import sys
from sqlalchemy import text, inspect
from sqlalchemy import create_engine

def migrate_database():
    """Migrate the database to add language support columns."""
    
    # Get database URL from environment
    database_url = os.getenv(
        'DATABASE_URL', 
        'postgresql://secret_santa:password@db:5432/secret_santa_db'
    )
    
    print(f"📡 Connecting to database: {database_url}")
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            inspector = inspect(engine)
            
            users_columns = [col['name'] for col in inspector.get_columns('users')]
            participants_columns = [col['name'] for col in inspector.get_columns('participants')]
            
            print("\n📊 Checking existing columns...")
            print(f"  users table: {len(users_columns)} columns")
            print(f"  participants table: {len(participants_columns)} columns")
            
            # Add preferred_language to users if it doesn't exist
            if 'preferred_language' not in users_columns:
                print("\n➕ Adding preferred_language column to users table...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL
                """))
                conn.commit()
                print("   ✅ users.preferred_language added")
            else:
                print("   ✓ users.preferred_language already exists")
            
            # Add preferred_language to participants if it doesn't exist
            if 'preferred_language' not in participants_columns:
                print("\n➕ Adding preferred_language column to participants table...")
                conn.execute(text("""
                    ALTER TABLE participants 
                    ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL
                """))
                conn.commit()
                print("   ✅ participants.preferred_language added")
            else:
                print("   ✓ participants.preferred_language already exists")
            
            # Create indexes for better performance
            print("\n📈 Creating indexes for language lookups...")
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_preferred_language 
                    ON users(preferred_language)
                """))
                print("   ✅ Index on users.preferred_language created")
            except:
                print("   ✓ Index already exists")
            
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_participants_preferred_language 
                    ON participants(preferred_language)
                """))
                print("   ✅ Index on participants.preferred_language created")
            except:
                print("   ✓ Index already exists")
            
            conn.commit()
            
        print("\n✅ Migration completed successfully!")
        print("\n📋 Summary:")
        print("  • Added preferred_language columns to users and participants")
        print("  • Default value: 'en' (English)")
        print("  • Created indexes for language lookups")
        print("  • Database is ready for multilingual support!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("\nPlease check:")
        print("  1. DATABASE_URL is correct")
        print("  2. PostgreSQL is running and accessible")
        print("  3. You have sufficient database permissions")
        return False
    finally:
        engine.dispose()

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
