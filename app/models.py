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

    def __repr__(self):
        return f'<User {self.email}>'
