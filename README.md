# Simple Social (FastAPI + React)

## Overview
This project is a full-stack social feed app with a FastAPI backend and a React frontend. The backend handles authentication, media uploads, and feed retrieval. The frontend (React) and an optional Streamlit UI consume the same API.

## Backend Highlights
- FastAPI app with async SQLAlchemy (SQLite)
- JWT authentication via fastapi-users
- ImageKit integration for media uploads
- CORS enabled for local development (React on http://localhost:3000)

## Project Structure
- app/            FastAPI app code (routes, auth, models)
- main.py         Uvicorn entrypoint
- frontend-react/ React frontend (Create React App)
- frontend.py     Optional Streamlit frontend
- test_db         SQLite database file

## Backend Setup

### Requirements
- Python 3.12+

### Install Dependencies
Option A (editable install from pyproject.toml):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Option B (uv):

```bash
uv sync
```

### Environment Variables
Create a `.env` file at the project root with the following:

```bash
JWT_SECRET=your_jwt_secret
IMAGEKIT_PRIVATE_KEY=your_imagekit_private_key
```

Notes:
- `JWT_SECRET` is required for authentication.
- `IMAGEKIT_PRIVATE_KEY` is required for `/upload`.
- `app/images.py` loads environment variables using `python-dotenv`.

### Run the Backend

```bash
python main.py
```

Or:

```bash
uvicorn app.app:app --reload
```

The API will be available at `http://localhost:8000`.

## Backend API Overview

Authentication (fastapi-users):
- `POST /auth/register`
- `POST /auth/jwt/login` (form data: `username`, `password`)
- `GET /users/me` (requires `Authorization: Bearer <token>`)

Core features:
- `POST /upload` (form data: `file`, `caption`) - requires auth
- `GET /feed` - requires auth
- `DELETE /posts/{post_id}` - requires auth, owner only

Demo endpoints:
- `GET /posts`
- `GET /posts/{id}`
- `POST /posts`
- `GET /hello-world`

## Frontend (React)

```bash
cd frontend-react
npm install
npm start
```

The React app expects the backend at `http://localhost:8000` (see `frontend-react/src/utils/api.js`).

## Optional Frontend (Streamlit)

```bash
python frontend.py
```

## Notes
- The SQLite database file is stored at `./test_db`. Delete it if you want a clean reset.
