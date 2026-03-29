from flask import request, session
from flask_restful import Api, Resource

from config import app, db
from models import User, Note

api = Api(app)


# ─── Helper ────────────────────────────────────────────────────────────────────

def current_user():
    """Return the logged-in User or None."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


# ─── Auth Resources ────────────────────────────────────────────────────────────

class Signup(Resource):
    """POST /signup — Create a new account and log in immediately."""

    def post(self):
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return {'error': 'Username and password are required.'}, 422

        if User.query.filter_by(username=username).first():
            return {'error': 'Username is already taken.'}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            return {'error': str(e)}, 422

        session['user_id'] = user.id
        return user.to_dict(), 201


class Login(Resource):
    """POST /login — Authenticate and start a session."""

    def post(self):
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        user = User.query.filter_by(username=username).first()

        if not user or not user.authenticate(password):
            return {'error': 'Invalid username or password.'}, 401

        session['user_id'] = user.id
        return user.to_dict(), 200


class Logout(Resource):
    """DELETE /logout — End the current session."""

    def delete(self):
        if not session.get('user_id'):
            return {'error': 'Not logged in.'}, 401

        session.pop('user_id', None)
        return {}, 204


class CheckSession(Resource):
    """GET /check_session — Return current user if session is active."""

    def get(self):
        user = current_user()
        if user:
            return user.to_dict(), 200
        return {'error': 'Unauthorized. Please log in.'}, 401


# ─── Notes Resources ───────────────────────────────────────────────────────────

class Notes(Resource):
    """
    GET  /notes  — Paginated list of notes for the logged-in user.
    POST /notes  — Create a new note for the logged-in user.
    """

    def get(self):
        user = current_user()
        if not user:
            return {'error': 'Unauthorized. Please log in.'}, 401

        # Pagination params: ?page=1&per_page=10
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        paginated = (
            Note.query
            .filter_by(user_id=user.id)
            .order_by(Note.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            'notes': [note.to_dict() for note in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
        }, 200

    def post(self):
        user = current_user()
        if not user:
            return {'error': 'Unauthorized. Please log in.'}, 401

        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title or not content:
            return {'error': 'Title and content are required.'}, 422

        try:
            note = Note(title=title, content=content, user_id=user.id)
            db.session.add(note)
            db.session.commit()
        except ValueError as e:
            return {'error': str(e)}, 422

        return note.to_dict(), 201


class NoteById(Resource):
    """
    PATCH  /notes/<id> — Update a note (owner only).
    DELETE /notes/<id> — Delete a note (owner only).
    """

    def _get_authorized_note(self, note_id):
        """
        Shared auth + ownership check.
        Returns (user, note) on success or (None, error_response) on failure.
        """
        user = current_user()
        if not user:
            return None, ({'error': 'Unauthorized. Please log in.'}, 401)

        note = Note.query.get(note_id)
        if not note:
            return None, ({'error': 'Note not found.'}, 404)

        if note.user_id != user.id:
            return None, ({'error': 'Forbidden. You do not own this note.'}, 403)

        return note, None

    def patch(self, note_id):
        note, error = self._get_authorized_note(note_id)
        if error:
            return error

        data = request.get_json()

        try:
            if 'title' in data:
                note.title = data['title']
            if 'content' in data:
                note.content = data['content']
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

        return note.to_dict(), 200

    def delete(self, note_id):
        note, error = self._get_authorized_note(note_id)
        if error:
            return error

        db.session.delete(note)
        db.session.commit()
        return {}, 204


# ─── Register Routes ───────────────────────────────────────────────────────────

api.add_resource(Signup,       '/signup')
api.add_resource(Login,        '/login')
api.add_resource(Logout,       '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Notes,        '/notes')
api.add_resource(NoteById,     '/notes/<int:note_id>')


# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(port=5555, debug=True)
