"""
seed.py — Populate the database with sample users and notes.
Run from the server/ directory:  python seed.py
"""

from faker import Faker
from config import app, db
from models import User, Note

fake = Faker()


def seed_users():
    """Create 5 sample users with known credentials for testing."""
    users = []

    # One predictable test account so you can log in easily
    test_user = User(username='testuser')
    test_user.password_hash = 'password123'
    users.append(test_user)

    # Four randomly-generated users
    for _ in range(4):
        username = fake.unique.user_name()
        user = User(username=username)
        user.password_hash = 'password123'
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    print(f'✓ Seeded {len(users)} users.')
    return users


def seed_notes(users):
    """Create 5–10 notes per user with realistic fake content."""
    notes = []

    for user in users:
        note_count = fake.random_int(min=5, max=10)
        for _ in range(note_count):
            note = Note(
                title=fake.sentence(nb_words=5).rstrip('.'),
                content=fake.paragraph(nb_sentences=4),
                user_id=user.id,
            )
            notes.append(note)

    db.session.add_all(notes)
    db.session.commit()
    print(f'✓ Seeded {len(notes)} notes across {len(users)} users.')


def run():
    with app.app_context():
        print('Clearing existing data...')
        Note.query.delete()
        User.query.delete()
        db.session.commit()

        print('Seeding users...')
        users = seed_users()

        print('Seeding notes...')
        seed_notes(users)

        print('\nDone! Test credentials:')
        print('  Username: testuser')
        print('  Password: password123')


if __name__ == '__main__':
    run()
