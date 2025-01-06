# Online Debate Platform

## Overview

The **Online Debate Platform** is a Django-based platform that empowers users to create, participate in, and manage debates in an intuitive and collaborative environment. Designed to encourage critical thinking and engagement, this platform provides dynamic debate creation, voting on arguments, and a gamified user leveling system.

---

## Features

### For End Users:
- **Debate Participation**: Create, join, or participate in debates with other users.
- **Arguments & Voting**: Express your point of view and vote on the best arguments.
- **User Accounts**:
  - Register, log in, and manage accounts.
  - Gamified leveling with experience points (`XP`) and user leaderboards.

### For Administrators:
- Manage debates and categories via the Django Admin panel.
- Update or moderate debate statuses (`Scheduled`, `Ongoing`, `Finished`, `Canceled`).

### API Features:
- RESTful API endpoints for debates, users, votes, and categories.
- Token-based authentication with throttling for secure usage.
- Swagger and ReDoc documentation for API testing and exploration.

---

## Key Technologies

- **Backend**: Django 5.x, Django REST Framework, Celery (for task handling)
- **Authentication**: Simple JWT for securing API endpoints
- **Frontend**: Django Templates for rendering HTML
- **Database**: SQLite for development, production-compatible with PostgreSQL
- **Caching**: Redis for caching and background task support
- **API Documentation**: Swagger UI and ReDoc via drf-spectacular
- **Task Queue**: Redis as the broker for Celery background jobs

---

## Installation

### Prerequisites
Make sure the following is installed:
- Python 3.9+
- Redis (for Celery tasks and caching)
- pip (Python package manager)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/GigaDarchia/DjangoDebatePlatform.git
   cd DjangoDebatePlatform
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start Redis:
   ```bash
   redis-server
   ```
5. Start celery worker:
    ```bash
   celery -A debatePlatform worker --loglevel=info
    ```
6. Start celery beat:
    ```bash
    celery -A debatePlatform beat --loglevel=info
    ```
7. Run the server:
   ```bash
   python manage.py runserver
   ```

---

## Usage

### Web Application
- Access the platform through `http://127.0.0.1:8000/`.
- Register a user or log in with admin credentials.
- Explore features like debate listing, creating arguments, and voting.

### REST API
- Access API endpoints at `/api/`.
- View API documentation at:
  - Swagger: `/api/swagger/`
  - ReDoc: `/api/schema/redoc/`

---
