from sqlalchemy.orm import validates
from config import db, bcrypt


class User(db.Model):
    """
    User model — handles authentication and owns notes.
    Passwords are never stored in plaintext; bcrypt hash only.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column('password_hash', db.String(128), nullable=False)

    # One user has many notes; deleting user cascades to their notes
    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan', lazy=True)

    @validates('username')
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError('Username cannot be empty.')
        return value.strip()

    # Prevent direct reads of the hashed password
    @property
    def password_hash(self):
        raise AttributeError('Password hash is not readable.')

    @password_hash.setter
    def password_hash(self, plaintext_password):
        """Hash and store password using bcrypt."""
        self._password_hash = bcrypt.generate_password_hash(plaintext_password).decode('utf-8')

    def authenticate(self, plaintext_password):
        """Return True if the given password matches the stored hash."""
        return bcrypt.check_password_hash(self._password_hash, plaintext_password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }

    def __repr__(self):
        return f'<User id={self.id} username={self.username}>'


class Note(db.Model):
    """
    Note model — belongs to a User.
    Each note has a title and content; timestamps are auto-managed.
    """
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Foreign key linking note to its owner
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='notes')

    @validates('title')
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError('Title cannot be empty.')
        return value.strip()

    @validates('content')
    def validate_content(self, key, value):
        if not value or not value.strip():
            raise ValueError('Content cannot be empty.')
        return value.strip()

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
        }

    def __repr__(self):
        return f'<Note id={self.id} title={self.title!r} user_id={self.user_id}>'
