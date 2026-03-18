# Task Manager REST API

A production-ready REST API built with **FastAPI**, **PostgreSQL**, and **JWT Authentication**. Demonstrates clean code architecture, async endpoints, pagination, soft-delete patterns, and full test coverage.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (async) |
| Database | PostgreSQL + SQLAlchemy ORM |
| Auth | JWT (access + refresh tokens) via `python-jose` |
| Password Hashing | bcrypt via `passlib` |
| Containerisation | Docker + docker-compose |
| Testing | pytest + pytest-cov (25+ tests, ~85% coverage) |
| API Docs | Auto-generated OpenAPI / Swagger UI |

## Features

- **JWT Authentication** — Register, login, token refresh
- **Full CRUD** for tasks with ownership isolation
- **Pagination & Filtering** — filter by status/priority, paginate results
- **Soft Delete** — tasks are flagged `is_deleted`, never hard-deleted
- **Input Validation** — Pydantic v2 schemas with strict typing
- **Secure by design** — bcrypt hashing, bearer token auth, no cross-user data leakage
- **Dockerised** — one command to run the full stack

## Quick Start

### With Docker (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/task-manager-api.git
cd task-manager-api
docker-compose up --build
```

API will be live at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:password@localhost:5432/taskdb
export SECRET_KEY=your-secret-key

# Run
uvicorn main:app --reload
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login → get JWT tokens |
| POST | `/auth/refresh` | Refresh access token |

### Tasks (require `Authorization: Bearer <token>`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/` | Create task |
| GET | `/tasks/` | List tasks (paginated, filterable) |
| GET | `/tasks/{id}` | Get task by ID |
| PATCH | `/tasks/{id}` | Partial update |
| DELETE | `/tasks/{id}` | Soft delete |

### Query Parameters for GET /tasks/
- `page` (int, default: 1)
- `page_size` (int, default: 10, max: 100)
- `status` — `todo` | `in_progress` | `done`
- `priority` — `low` | `medium` | `high`

## Example Usage

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","username":"yourname","password":"secret"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=yourname&password=secret"

# Create task
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Ship the feature","priority":"high","status":"in_progress"}'

# List with filter
curl "http://localhost:8000/tasks/?status=in_progress&page=1&page_size=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Running Tests

```bash
# All tests with coverage report
pytest tests/ -v --cov=. --cov-report=term-missing

# Tests use SQLite (no PostgreSQL needed for testing)
```

## Project Structure

```
task-manager-api/
├── main.py           # FastAPI app, router registration, lifespan
├── database.py       # SQLAlchemy engine, session, Base
├── models.py         # ORM models: User, Task (with enums)
├── schemas.py        # Pydantic v2 schemas for request/response
├── auth_utils.py     # JWT creation/decode, password hashing
├── routers/
│   ├── auth.py       # /auth/register, /auth/login, /auth/refresh
│   └── tasks.py      # Full CRUD for /tasks/
├── tests/
│   └── test_api.py   # 25+ tests covering all endpoints
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Key Design Decisions

- **Soft delete over hard delete** — preserves data integrity for audit trails
- **Refresh tokens** — access tokens expire in 30min; refresh tokens last 7 days
- **Ownership isolation** — all task queries filter by `owner_id`, preventing data leakage between users
- **Partial updates with PATCH** — only provided fields are updated via `model_dump(exclude_unset=True)`
- **SQLite for tests** — no external DB needed to run the test suite

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `SECRET_KEY` | (dev default) | JWT signing key — **change in production** |

---

Built by [Kamali Rajasekaran](https://linkedin.com/in/kamali-rajasekaran) · Backend Engineer
