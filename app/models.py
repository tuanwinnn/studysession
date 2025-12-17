from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Main SQLAlchemy database instance
db = SQLAlchemy()

# Association table for many-to-many relationship between users and study sessions
session_members = db.Table(
    'session_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('session_id', db.Integer, db.ForeignKey('study_session.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Unique username for login/display
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Unique email for contact/login
    email = db.Column(db.String(120), unique=True, nullable=False)
    # Hashed password (never store raw passwords)
    password_hash = db.Column(db.String(128))
    
    # Sessions this user has joined (many-to-many via session_members)
    joined_sessions = db.relationship(
        'StudySession',
        secondary=session_members, 
        backref=db.backref('members', lazy='dynamic')
    )
    # Sessions this user created (one-to-many)
    created_sessions = db.relationship(
        'StudySession',
        backref='creator', 
        foreign_keys='StudySession.creator_id',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class StudySession(db.Model):
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Short title/description of the session
    title = db.Column(db.String(200), nullable=False)
    # Date/time when the session happens
    date = db.Column(db.DateTime, nullable=False)
    # Human-readable time string (e.g., "3:00 PM")
    time = db.Column(db.String(20), nullable=False)
    # Where the session takes place
    location = db.Column(db.String(200), nullable=False)
    # Optional topic or subject focus
    topic = db.Column(db.String(100))
    # User who created this session
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # When the session was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Recurring Session fields
    # Indicates if this session should spawn recurring copies
    is_recurring = db.Column(db.Boolean, default=False)
    # 'weekly', 'biweekly', 'monthly', etc.
    recurrence_interval = db.Column(db.String(20))
    # Optional self-referential link to parent recurring session
    parent_id = db.Column(db.Integer, db.ForeignKey('study_session.id'))

    def get_participant_count(self):
        """Return the number of users who joined this session."""
        return self.members.count()
    
    def is_past(self):
        """Check if the session date is before today's date (UTC-based)."""
        return self.date.date() < datetime.utcnow().date()
        
    def __repr__(self):
        return f'<StudySession {self.title}>'

class SessionComment(db.Model):
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    # Comment text content
    content = db.Column(db.Text, nullable=False)
    # When the comment was created
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Author of the comment
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Session this comment belongs to
    session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'), nullable=False)
    
    # Relationship back to User (user.comments)
    user = db.relationship('User', backref='comments')
    # Relationship back to StudySession (session.comments)
    session = db.relationship('StudySession', backref='comments')
    
    def __repr__(self):
        return f'<Comment by {self.user_id} on session {self.session_id}>'
