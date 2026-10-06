# IPD Dev Environment

Everything runs in Docker, so you don't need Node or Postgres installed locally.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

Check that Docker works:

```bash
docker --version
docker compose version
```

## First-time setup

```bash
git clone <repo-url>
cd <repo-folder>
cp .env.example .env
```

Open `.env` and set `POSTGRES_PASSWORD` to any value you like. The `.env` file is git-ignored, so it stays on your machine.

## Start the stack

Run all compose commands from the repo root (the folder containing `docker-compose.yml`).

```bash
docker compose up --build
```

Add `-d` to run in the background. The first run takes a few minutes while images download and dependencies install.

Check that everything is healthy:

```bash
docker compose ps
```

## Developing

- **Frontend:** edit files in `src/frontend/`. Changes hot-reload in the browser, no rebuild needed.
- **Database:** SQL files in `src/data/init/` run automatically, in alphabetical order, the first time the database is created.

### Adding a frontend dependency

Add it inside the container so `package.json` and the lockfile stay in sync, then rebuild:

```bash
docker compose exec frontend npm install <package>
docker compose up --build frontend
```

Commit the updated `package.json` and `package-lock.json`.

## Common commands

| Command | What it does |
|---------|--------------|
| `docker compose up -d` | Start everything in the background |
| `docker compose logs -f <service>` | Follow a service's logs (`db`, `frontend`) |
| `docker compose down` | Stop and remove containers (**keeps** database data) |
| `docker compose down -v` | Stop and remove containers **and delete the database** |
| `docker compose up --build` | Rebuild images, then start |

## Project layout

```
src/
├── computation/   # solvers (not containerized yet)
├── data/          # database init scripts
├── frontend/      # React + Vite app
└── simulation/    # simulation code (not containerized yet)
```