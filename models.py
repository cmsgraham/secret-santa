"""
Database models for Secret Santa application
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
import uuid

Base = declarative_base()

class EventStatus(enum.Enum):
    """Event status states"""
    REGISTRATION_OPEN = "registration_open"
    DRAW_COMPLETED = "draw_completed"
    EVENT_CLOSED = "event_closed"

class User(Base):
    """Organizer/User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime)
    
    # Language preference
    preferred_language = Column(String(10), default='en', nullable=False)
    
    # Relationships
    events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"

class Event(Base):
    """Event model for Secret Santa events"""
    __tablename__ = 'events'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), unique=True, nullable=False, index=True)  # Short unique code for URLs
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Organizer
    organizer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    organizer = relationship("User", back_populates="events")
    
    # Event status and dates
    status = Column(Enum(EventStatus), default=EventStatus.REGISTRATION_OPEN, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    draw_date = Column(DateTime)  # When the draw was completed
    closed_at = Column(DateTime)  # When the event was closed
    
    # Settings
    allow_self_assignment = Column(Boolean, default=False)
    min_participants = Column(Integer, default=3)
    max_participants = Column(Integer, default=100)
    guessing_enabled = Column(Boolean, default=False)  # Allow participants to guess their Secret Santa
    default_language = Column(String(10), default='en', nullable=False)  # Default language for event
    
    # Relationships
    participants = relationship("Participant", back_populates="event", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event {self.name} ({self.code})>"
    
    @property
    def participant_count(self):
        return len(self.participants)
    
    @property
    def can_run_draw(self):
        return (
            self.status == EventStatus.REGISTRATION_OPEN and
            self.participant_count >= self.min_participants
        )
    
    @property
    def registration_url(self):
        return f"/event/{self.code}/register"
    
    @property
    def management_url(self):
        return f"/event/{self.code}/manage"

class Participant(Base):
    """Participant in a Secret Santa event"""
    __tablename__ = 'participants'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    
    # Participant details
    name = Column(String(255), nullable=False)
    nickname = Column(String(255))  # Optional fun nickname
    email = Column(String(255), nullable=False)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Member page content
    hints = Column(Text)  # Hints about themselves for others to guess
    gift_preferences = Column(Text)  # Gift ideas, preferences, links
    profile_picture = Column(String(500))  # Icon selection (emoji:🎅) or uploaded image path
    
    # Guessing
    guessed_secret_santa_id = Column(String(36), ForeignKey('participants.id'))  # Their guess of who their Secret Santa is
    guessed_at = Column(DateTime)  # When they made the guess
    
    # Email status
    assignment_email_sent = Column(Boolean, default=False)
    assignment_email_sent_at = Column(DateTime)
    
    # Language preference
    preferred_language = Column(String(10), default='en', nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="participants")
    giving_to = relationship("Assignment", foreign_keys="Assignment.giver_id", back_populates="giver")
    receiving_from = relationship("Assignment", foreign_keys="Assignment.receiver_id", back_populates="receiver")
    guessed_secret_santa = relationship("Participant", remote_side=[id], foreign_keys=[guessed_secret_santa_id])
    feed_posts = relationship("FeedPost", back_populates="participant", cascade="all, delete-orphan")
    feed_comments = relationship("FeedComment", back_populates="participant", cascade="all, delete-orphan")
    feed_likes = relationship("FeedLike", back_populates="participant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Participant {self.name} ({self.email})>"

class Assignment(Base):
    """Secret Santa assignment (who gives to whom)"""
    __tablename__ = 'assignments'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    
    # Assignment relationships
    giver_id = Column(String(36), ForeignKey('participants.id'), nullable=False)
    receiver_id = Column(String(36), ForeignKey('participants.id'), nullable=False)
    
    # Assignment metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    event = relationship("Event", back_populates="assignments")
    giver = relationship("Participant", foreign_keys=[giver_id], back_populates="giving_to")
    receiver = relationship("Participant", foreign_keys=[receiver_id], back_populates="receiving_from")
    
    def __repr__(self):
        return f"<Assignment {self.giver_id} -> {self.receiver_id}>"

class AuthToken(Base):
    """Authentication tokens for magic link login"""
    __tablename__ = 'auth_tokens'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Token metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuthToken for user {self.user_id}>"
    
    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        if self.used:
            return False
        
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        
        # Ensure both datetimes have timezone info for comparison
        if expires.tzinfo is None:
            # If expires_at is naive, assume it's UTC
            expires = expires.replace(tzinfo=timezone.utc)
        
        return now < expires

class FeedPost(Base):
    """Feed post on Santa's Secret Wall"""
    __tablename__ = 'feed_posts'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    participant_id = Column(String(36), ForeignKey('participants.id'), nullable=False)
    
    # Post content
    nickname = Column(String(255), nullable=False)  # Anonymous nickname for display
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    event = relationship("Event", foreign_keys=[event_id])
    participant = relationship("Participant", foreign_keys=[participant_id], back_populates="feed_posts")
    comments = relationship("FeedComment", back_populates="post", cascade="all, delete-orphan", primaryjoin="FeedPost.id==FeedComment.post_id", foreign_keys="[FeedComment.post_id]")
    likes = relationship("FeedLike", back_populates="post", cascade="all, delete-orphan", primaryjoin="FeedPost.id==FeedLike.post_id", foreign_keys="[FeedLike.post_id]")
    
    def __repr__(self):
        return f"<FeedPost {self.nickname} on {self.event_id}>"

class FeedComment(Base):
    """Comment on a feed post"""
    __tablename__ = 'feed_comments'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(100), nullable=False)  # Can be a UUID or pseudo-ID like "hint_<uuid>"
    participant_id = Column(String(36), ForeignKey('participants.id', ondelete='CASCADE'), nullable=False)
    
    # Comment content
    nickname = Column(String(255), nullable=False)  # Anonymous nickname for display
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    post = relationship("FeedPost", back_populates="comments", primaryjoin="FeedPost.id==FeedComment.post_id", foreign_keys=[post_id])
    participant = relationship("Participant", foreign_keys=[participant_id], back_populates="feed_comments")
    
    def __repr__(self):
        return f"<FeedComment {self.nickname} on post {self.post_id}>"

class FeedLike(Base):
    """Like on a feed post"""
    __tablename__ = 'feed_likes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = Column(String(100), nullable=False)  # Can be a UUID or pseudo-ID like "hint_<uuid>"
    participant_id = Column(String(36), ForeignKey('participants.id', ondelete='CASCADE'), nullable=False)
    
    # Like metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    post = relationship("FeedPost", back_populates="likes", primaryjoin="FeedPost.id==FeedLike.post_id", foreign_keys=[post_id])
    participant = relationship("Participant", foreign_keys=[participant_id], back_populates="feed_likes")
    
    def __repr__(self):
        return f"<FeedLike by {self.participant_id} on {self.post_id}>"
