# Roosh Backend Application

Quick start guide for running this Django REST API locally with Docker (recommended) or directly with Python.

## Prerequisites
- Docker Desktop 4.x (or Docker Engine + Docker Compose v2)
- Optional for local (non‑Docker) dev: Python 3.12, MySQL 8.0

## 1) Create your .env file
Use the provided example and fill in the variables that apply to you.

```bash
cp .env.example .env
```

Minimum you will need for Docker setup (example values):

```
# Django
DEBUG=1
DJANGO_SECRET=change-me
ALLOWED_HOSTS=*

# Database (MySQL) – must match docker-compose defaults
DB_NAME=roosh
DB_USER=roosh
DB_PASS=roosh
DB_HOST=database
DB_PORT=3306

# Security
API_KEY=dev-secret-key  # used by ApiKeyMiddleware (header: X-API-Key)
# CORS_ALLOWED_ORIGINS=https://your-frontend.example.com
```

Notes:
- API requests must include header `X-API-Key: <your API_KEY>` (see core/middleware.py) except OPTIONS preflight.
- If you want to restrict CORS, set `CORS_ALLOWED_ORIGINS` to a comma‑separated list of allowed origins.

## 2) Create the shared Docker network (first time only)
This compose file expects an external network called `roosh-shared-network`.

```bash
docker network create roosh-shared-network || true
```

## 3) Start the stack with Docker
From the project root:

```bash
docker compose -f docker-roosh-api/docker-compose.yml up --build
```

This will start:
- MySQL 8.0 (service name `database`, port 3306 exposed)
- Django app (service name `web`, port 8000 exposed)

The first run will install dependencies and then start the app via the entrypoint.

## 4) Apply database migrations
Open a new terminal while containers are running and run:

```bash
docker compose -f docker-roosh-api/docker-compose.yml exec web python manage.py migrate
```

(Optional) Load/create initial data as needed, or create a superuser if you later add Django admin.

## 5) Verify the API is up
Health endpoint:

```bash
curl -H "X-API-Key: $API_KEY" http://localhost:8000/v1/health/
```

You should see a JSON response and HTTP 200.

## Local development without Docker (optional)
If you prefer to run directly on your machine:

1) Install system dependencies for `mysqlclient` (varies per OS). On Debian/Ubuntu: `sudo apt-get install build-essential default-libmysqlclient-dev pkg-config`.
2) Create and export the same environment variables as in `.env` (you can `pip install python-dotenv` or export manually).
3) Ensure a local MySQL 8.0 is running with a database and user that match `DB_*` settings. For local dev you can set `DB_HOST=127.0.0.1`.
4) Install Python deps using the same requirements as the container:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r docker-roosh-api/web/requirements.txt
```

5) Run migrations and start the dev server:

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Configuration reference
All configurable values live in `.env` and are read in `app/settings.py`.
- DEBUG: `1` or `0`
- DJANGO_SECRET: Secret key for Django
- ALLOWED_HOSTS: Comma‑separated list; `*` for all
- DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT: MySQL connection
- API_KEY: Required to access endpoints (header `X-API-Key` or query `api_key`)
- CORS_ALLOWED_ORIGINS: Comma‑separated list of origins. If not set, all origins are allowed.

### Email (Postmark)
To enable booking emails via Postmark, add the following variables to your `.env`:

```
# Postmark
POSTMARK_API_TOKEN=your-postmark-server-token
POSTMARK_FROM=no-reply@your-domain.tld  # verified sender in Postmark

# Templates:
POSTMARK_BOOKING_CONFIRMATION_TEMPLATE_ID=1234567   # numeric template ID or alias for confirmation
POSTMARK_BOOKING_CANCELLATION_TEMPLATE_ID=2345678   # numeric template ID or alias for cancellation
```

Behavior:
- After a booking is successfully created (`POST /v1/createbooking/`), the server posts to Postmark's `email/withTemplate` endpoint using `POSTMARK_BOOKING_CONFIRMATION_TEMPLATE_ID`.
- The confirmation `TemplateModel` includes: `subject`, `email`, `booking_id`, `reseller_name`, `start_date`, `end_date`, `parking_type`, `CURRENT_YEAR`.
- After a booking is cancelled (`POST /v1/cancelbooking/<booking_id>/`), the server posts a cancellation email using `POSTMARK_BOOKING_CANCELLATION_TEMPLATE_ID`.
- The cancellation `TemplateModel` includes: `subject`, `customer_email`, `booking_id`, `reseller_name`, `CURRENT_YEAR`.
- Email send failures are logged but do not affect the API responses.

## Useful commands
- Start/stop Docker: `docker compose -f docker-roosh-api/docker-compose.yml up -d` / `down`
- Tail logs: `docker compose -f docker-roosh-api/docker-compose.yml logs -f web`
- Run manage.py inside container: `docker compose -f docker-roosh-api/docker-compose.yml exec web python manage.py <cmd>`

## API reference

### Cancel booking (soft delete)
- Method: `POST`
- Path: `/v1/cancelbooking/<booking_id>/`
- Description: Sets the booking's `status` to `2` (Cancelled) without deleting the record.
- Response 200 OK:
```
{
  "status": "ok",
  "data": {
    "booking_id": 123,
    "status": 2
  }
}
```
- Response 404 when booking not found:
```
{
  "status": "error",
  "data": "Booking not found"
}
```
- Notes:
  - The operation is idempotent. Calling it multiple times on the same booking will keep status `2`.

## Troubleshooting
- Database not ready: the `web` service waits for the `database` healthcheck. Give it a moment or check logs: `docker compose -f docker-roosh-api/docker-compose.yml logs -f database`.
- Access denied: ensure your requests include the correct `X-API-Key` header.
- CORS errors in browser: set `CORS_ALLOWED_ORIGINS` to include your frontend origin, or leave it empty to allow all during development.
