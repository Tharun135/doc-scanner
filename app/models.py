from flask_login import UserMixin
from datetime import datetime
from . import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Stored as bcrypt hash
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_count = db.Column(db.Integer, default=0)

    # Relationship to scan history
    scans = db.relationship('ScanHistory', backref='user', lazy=True,
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class ScanHistory(db.Model):
    __tablename__ = 'scan_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False, default='Untitled Document')
    issue_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    quality_score = db.Column(db.Integer, default=0)  # 0-100
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'issue_count': self.issue_count,
            'word_count': self.word_count,
            'quality_score': self.quality_score,
            'scanned_at': self.scanned_at.strftime('%d %b %Y, %I:%M %p')
        }

    def __repr__(self):
        return f'<ScanHistory user={self.user_id} file={self.filename}>'
