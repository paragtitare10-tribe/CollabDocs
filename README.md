# CollabDocs

Django REST API for collaborative documents, workspaces, comments, tags, and audit logs.

## Requirements

- Python 3.12 or newer
- Docker with the Docker Compose plugin, or a local PostgreSQL server

## Setup

From the project root, create a virtual environment and install dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file in the project root. These values are used by both Django and `docker-compose.yml`:

```dotenv
POSTGRES_DB=collabdocs
POSTGRES_USER=collabdocs
POSTGRES_PASSWORD=change-this-local-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

For local development, keep `.env` out of version control and use a non-production password.

## Start PostgreSQL

With Docker Compose, start the database from the project root:

```sh
docker compose up -d db
docker compose ps
```

Wait for the database container to report healthy before applying migrations. To use a local PostgreSQL server instead, create the configured database and user and set `POSTGRES_HOST` and `POSTGRES_PORT` to that server.

## Apply Migrations

Apply all checked-in database migrations:

```sh
python manage.py migrate
```

When you change a model, create migration files and then apply them:

```sh
python manage.py makemigrations
python manage.py migrate
```

## Run the Server

Start Django's development server:

```sh
python manage.py runserver
```

The API is then available at `http://127.0.0.1:8000/api/`. The Django admin is at `http://127.0.0.1:8000/admin/`.

Stop the database container when finished with:

```sh
docker compose down
```

The named Docker volume preserves PostgreSQL data. To remove the volume and its data as well, use `docker compose down -v` only when you intend to delete the local database.
