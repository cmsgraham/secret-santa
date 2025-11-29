"""
Database migration script to add member page features
Adds: hints, gift_preferences, guessed_secret_santa_id, guessed_at to Participant
Adds: guessing_enabled to Event
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///secretsanta.db')
engine = create_engine(DATABASE_URL)

def run_migration():
    """Run the migration to add new columns"""
    with engine.connect() as conn:
        print("Starting migration...")
        
        # Add columns to participants table
        try:
            print("Adding 'hints' column to participants...")
            conn.execute(text("ALTER TABLE participants ADD COLUMN hints TEXT"))
            conn.commit()
            print("✓ Added 'hints' column")
        except Exception as e:
            print(f"  Column 'hints' might already exist: {e}")
        
        try:
            print("Adding 'gift_preferences' column to participants...")
            conn.execute(text("ALTER TABLE participants ADD COLUMN gift_preferences TEXT"))
            conn.commit()
            print("✓ Added 'gift_preferences' column")
        except Exception as e:
            print(f"  Column 'gift_preferences' might already exist: {e}")
        
        try:
            print("Adding 'guessed_secret_santa_id' column to participants...")
            conn.execute(text("ALTER TABLE participants ADD COLUMN guessed_secret_santa_id VARCHAR(36)"))
            conn.commit()
            print("✓ Added 'guessed_secret_santa_id' column")
        except Exception as e:
            print(f"  Column 'guessed_secret_santa_id' might already exist: {e}")
        
        try:
            print("Adding 'guessed_at' column to participants...")
            conn.execute(text("ALTER TABLE participants ADD COLUMN guessed_at TIMESTAMP"))
            conn.commit()
            print("✓ Added 'guessed_at' column")
        except Exception as e:
            print(f"  Column 'guessed_at' might already exist: {e}")
        
        # Add foreign key constraint (PostgreSQL)
        if 'postgresql' in DATABASE_URL:
            try:
                print("Adding foreign key constraint for guessed_secret_santa_id...")
                conn.execute(text(
                    "ALTER TABLE participants ADD CONSTRAINT fk_guessed_secret_santa "
                    "FOREIGN KEY (guessed_secret_santa_id) REFERENCES participants(id)"
                ))
                conn.commit()
                print("✓ Added foreign key constraint")
            except Exception as e:
                print(f"  Foreign key might already exist: {e}")
        
        # Add column to events table
        try:
            print("Adding 'guessing_enabled' column to events...")
            conn.execute(text("ALTER TABLE events ADD COLUMN guessing_enabled BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✓ Added 'guessing_enabled' column")
        except Exception as e:
            print(f"  Column 'guessing_enabled' might already exist: {e}")
        
        print("\n✅ Migration completed successfully!")
        print("\nNew features added:")
        print("  - Participants can add hints about themselves")
        print("  - Participants can add gift preferences and links")
        print("  - Participants can guess their Secret Santa (when enabled)")
        print("  - Organizers can toggle the guessing phase")

if __name__ == '__main__':
    run_migration()
