# Productivity Notes API

A secure REST API backend for a personal notes app. Built with Flask, Flask-SQLAlchemy, and session-based authentication. Users can sign up, log in, and manage their own private notes — no one can view or modify another user's data.

---

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy + Flask-Migrate (SQLite)
- Flask-Bcrypt (password hashing)
- Flask-RESTful
- Flask-CORS
- Session-based authentication

---

## Installation

### 1. Clone the repo and install dependencies

```bash
git clone <your-repo-url>
cd productivity-api
pipenv install
pipenv shell
```

### 2. Set up and seed the database

```bash
cd server
flask db init
flask db migrate -m "initial migration"
flask db upgrade
python seed.py
```

---

## Running the App

```bash
cd server
flask run --port=5555
# or
python app.py
```

The API will be available at `http://localhost:5555`.

---

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup` | Register a new user | No |
| POST | `/login` | Log in with username + password | No |
| DELETE | `/logout` | End the current session | Yes |
| GET | `/check_session` | Return current user if logged in | Yes |

### Notes

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/notes` | Get paginated notes for current user | Yes |
| POST | `/notes` | Create a new note | Yes |
| PATCH | `/notes/<id>` | Update a note (owner only) | Yes |
| DELETE | `/notes/<id>` | Delete a note (owner only) | Yes |

### Pagination

The `GET /notes` endpoint supports query params:

```
GET /notes?page=1&per_page=10
```

Response includes: `notes`, `total`, `pages`, `current_page`, `per_page`.

---

## Request / Response Examples

**POST /signup**
```json
{ "username": "rachel", "password": "mypassword" }
→ 201: { "id": 1, "username": "rachel" }
```

**POST /login**
```json
{ "username": "rachel", "password": "mypassword" }
→ 200: { "id": 1, "username": "rachel" }
```

**POST /notes**
```json
{ "title": "My First Note", "content": "Some content here." }
→ 201: { "id": 1, "title": "My First Note", "content": "...", "user_id": 1, ... }
```

**PATCH /notes/1**
```json
{ "title": "Updated Title" }
→ 200: { updated note object }
```

---

## Test Credentials (after seeding)

```
Username: testuser
Password: password123
```
