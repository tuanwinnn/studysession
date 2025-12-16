from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between users and sessions
session_members = db.Table(
    'session_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),   # FK to User
    db.Column('session_id', db.Integer, db.ForeignKey('study_session.id'), primary_key=True)  # FK to StudySession
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # user ID
    username = db.Column(db.String(80), unique=True, nullable=False)  # unique username
    email = db.Column(db.String(120), unique=True, nullable=False)  # unique email
    password_hash = db.Column(db.String(128))  # hashed password
    
    # Sessions this user has joined (many-to-many)
    joined_sessions = db.relationship(
        'StudySession',
        secondary=session_members, 
        backref=db.backref('members', lazy='dynamic')
    )
    # Sessions this user has created (one-to-many)
    created_sessions = db.relationship(
        'StudySession',
        backref='creator', 
        foreign_keys='StudySession.creator_id',
        lazy='dynamic'
    )
    
    def set_password(self, password):
        """Hash and store the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check a plaintext password against the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # session ID
    title = db.Column(db.String(200), nullable=False)  # session title
    date = db.Column(db.DateTime, nullable=False)  # when the session happens
    time = db.Column(db.String(20), nullable=False)  # human-readable time range
    location = db.Column(db.String(200), nullable=False)  # session location
    topic = db.Column(db.String(100))  # optional topic
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # creator user FK
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # when record was created
    
    # Recurring Session fields
    is_recurring = db.Column(db.Boolean, default=False)  # is this a recurring session
    recurrence_interval = db.Column(db.String(20))  # weekly, biweekly, monthly, etc.
    parent_id = db.Column(db.Integer, db.ForeignKey('study_session.id'))  # parent session FK for recurrence

    def get_participant_count(self):
        """Number of users in this session"""
        return self.members.count()
    
    def is_past(self):
        """Check if the session date has passed"""
        return self.date.date() < datetime.utcnow().date()
        
    def __repr__(self):
        return f'<StudySession {self.title}>'

class SessionComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # comment ID
    content = db.Column(db.Text, nullable=False)  # comment text
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # when comment was made

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # commenter
    sesssion_id = db.Column(db.Integer, db.ForeignKey('study_session.id'), nullable=False)  # session commented on

    user = db.relationship('User', backref='comments')  # relationship to User
    session = db.relationship('StudySession', backref='comments')  # relationship to StudySession
