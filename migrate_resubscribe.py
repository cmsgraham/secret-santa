#!/usr/bin/env python
"""
Migration script to add resubscribe columns to production database
and resubscribe a specific user
"""
import os
import sys
import psycopg2
from psycopg2 import sql

def add_resubscribe_columns():
    """Add unsubscribe_token and email_opt_out columns to users table"""
    
    # Get database connection string from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Parse connection string
    # Format: postgresql://user:password@host:port/database
    try:
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        conn_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
        }
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        sys.exit(1)
    
    try:
        print("🔗 Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("📝 Adding columns to users table...")
        
        # Add unsubscribe_token column
        try:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN unsubscribe_token VARCHAR(64) UNIQUE NULL;
            """)
            print("   ✅ Added unsubscribe_token column")
        except psycopg2.Error as e:
            if 'already exists' in str(e):
                print("   ℹ️  unsubscribe_token column already exists")
            else:
                raise
        
        # Add email_opt_out column
        try:
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN email_opt_out BOOLEAN NOT NULL DEFAULT false;
            """)
            print("   ✅ Added email_opt_out column")
        except psycopg2.Error as e:
            if 'already exists' in str(e):
                print("   ℹ️  email_opt_out column already exists")
            else:
                raise
        
        # Create index on unsubscribe_token
        try:
            cursor.execute("""
                CREATE INDEX idx_users_unsubscribe_token 
                ON users(unsubscribe_token);
            """)
            print("   ✅ Created index on unsubscribe_token")
        except psycopg2.Error as e:
            if 'already exists' in str(e):
                print("   ℹ️  Index already exists")
            else:
                raise
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        return cursor, conn
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)

def resubscribe_user(cursor, conn, email):
    """Resubscribe a specific user by email"""
    
    try:
        print(f"\n🔍 Looking up user: {email}")
        cursor.execute("SELECT id, email, email_opt_out FROM users WHERE email = %s;", (email,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ User not found: {email}")
            return False
        
        user_id, user_email, is_opted_out = result
        print(f"   ✅ Found user: {user_email}")
        print(f"   Current email_opt_out status: {is_opted_out}")
        
        # Update email_opt_out to False
        cursor.execute("UPDATE users SET email_opt_out = false WHERE id = %s;", (user_id,))
        conn.commit()
        
        print(f"   ✅ Updated email_opt_out to false")
        print(f"\n✅ Successfully resubscribed {email}!")
        return True
        
    except Exception as e:
        print(f"❌ Error resubscribing user: {e}")
        return False

if __name__ == '__main__':
    email_to_resubscribe = 'cristian.madrigal@gmail.com'
    
    if len(sys.argv) > 1:
        email_to_resubscribe = sys.argv[1]
    
    print("=" * 70)
    print("Secret Santa - Resubscribe Migration Script")
    print("=" * 70)
    
    # Run migration
    cursor, conn = add_resubscribe_columns()
    
    # Resubscribe user
    success = resubscribe_user(cursor, conn, email_to_resubscribe)
    
    cursor.close()
    conn.close()
    
    sys.exit(0 if success else 1)
