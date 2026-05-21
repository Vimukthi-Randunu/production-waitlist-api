# Production Waitlist API

A production-grade waitlist API built with FastAPI and PostgreSQL — the kind of backend deployed before a product launch to collect and manage email signups. Runs on real HTTPS, a real domain, and a full CI/CD pipeline with staging, approval gate, health checks, and automatic rollback.

**Live demo:**  Live URLs are available on request. Environments are spun up on demand to demonstrate.  Contact: wkvp.randunu@gmail.com

---

## What This Is

Businesses need a waitlist before they launch. This API is what sits behind that waitlist page — collecting emails, preventing duplicates, letting the team view signups, and removing bad entries. It is production ready, containerized, and deployed through a pipeline that treats staging and production as completely separate environments.

---

## Architecture

```
Internet
    │
    ▼
Nginx container (port 80 → redirect to HTTPS, port 443 → SSL termination)
    │  internal Docker network
    ▼
FastAPI + Uvicorn container (port 8000, not publicly exposed)
    │  internal Docker network
    ▼
PostgreSQL container (port 5432, not publicly exposed)
```

Nginx is the only container exposed to the internet. It terminates SSL, redirects HTTP to HTTPS, and forwards requests internally to FastAPI by container name. PostgreSQL is never reachable from outside the Docker network.

SSL certificates are issued by Let's Encrypt via Certbot and stored on the EC2 host filesystem. Nginx reads them through a Docker volume mount. Auto-renewal is handled by a Certbot scheduled task on the host.

---

## Pipeline

```
Push to main
      │
      ▼
   test
   pytest runs on GitHub runner
   pipeline stops here if tests fail
      │
      ▼
   build-and-push
   Docker image built and tagged with commit SHA
   pushed to Docker Hub
      │
      ▼
   deploy-staging
   SSHs into staging EC2
   writes .env from GitHub secrets
   git pull, docker compose pull, docker compose up
      │
      ▼
   health-check-staging
   curl -f http://staging-ip/health
   pipeline stops here if staging is unhealthy
   production is never touched
      │
      ▼
   deploy-production  ← manual approval gate
   SSHs into production EC2
   same deploy process as staging
   saves current SHA before deploying for rollback
      │
      ▼
   health-check-production
   curl -f https://demo.radianceits.com/health
   rolls back to previous SHA if unhealthy
```

Pull requests to main run tests only — no deployment. Full pipeline runs on merge to main.

---

## Environments

| | Staging | Production |
|---|---|---|
| Protocol | HTTP | HTTPS |
| Domain | Raw EC2 IP | demo.radianceits.com |
| SSL | None | Let's Encrypt |
| Deployment | Automatic | Manual approval gate |
| Secrets | Isolated GitHub environment | Isolated GitHub environment |

Staging and production are completely isolated. Separate EC2 instances, separate GitHub environment secrets, separate SSH keys. A broken staging deploy cannot affect production users.

---

## API Endpoints

**Public**

| Method | Endpoint | Description |
|---|---|---|
| POST | /waitlist | Submit an email to the waitlist |
| GET | /waitlist/{id} | Check a signup by ID |
| GET | /health | Health check for the pipeline |

**Admin — protected by API key**

| Method | Endpoint | Description |
|---|---|---|
| GET | /admin/waitlist | View all waitlist entries |
| DELETE | /admin/waitlist/{id} | Remove an entry |

Admin endpoints require the header `X-API-Key: your-api-key`. The API key is never hardcoded — it is injected at runtime from GitHub secrets.

---

## Database Schema

**Table: waitlist_entries**

| Column | Type | Notes |
|---|---|---|
| id | integer | primary key, auto increment |
| email | string | unique, not null |
| signed_up_at | timestamp | auto set on creation |
| is_confirmed | boolean | default false |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python 3.13, FastAPI, Uvicorn |
| Database | PostgreSQL 15 |
| Reverse proxy | Nginx |
| SSL | Let's Encrypt, Certbot |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Registry | Docker Hub |
| Infrastructure | AWS EC2 Ubuntu 24.04 |
| Environments | GitHub Environments with approval gates |
| Domain | Route 53, radianceits.com |

---

## Key Infrastructure Decisions

**SHA tagging over latest**
Every image pushed to Docker Hub is tagged with the exact Git commit SHA. This means every deployment is permanently addressable and rollback means redeploying a specific previous SHA — not guessing what latest was pointing at.

**Nginx as reverse proxy**
FastAPI runs on port 8000 inside the Docker network and is never exposed publicly. Nginx sits in front on ports 80 and 443, handles SSL termination, and redirects all HTTP traffic to HTTPS. This is the standard production architecture for any web backend.

**Certbot on host, not in container**
Certbot runs directly on the EC2 host and writes certificates to `/etc/letsencrypt`. Nginx reads them through a Docker volume mount. This is simpler to manage and easier to debug than a containerized Certbot approach, and auto-renewal works reliably through the host OS scheduler.

**Separate nginx configs per environment**
`nginx/nginx.conf` — HTTP only, used by staging. `nginx/nginx.prod.conf` — HTTPS with SSL, used by production. The production deploy job copies the production config into place before starting containers. Staging never sees HTTPS config and cannot fail due to missing certificates.

**Database retry on startup**
FastAPI retries the PostgreSQL connection up to 10 times with 3 second intervals on startup. This solves the container startup ordering problem — Docker Compose starts containers roughly simultaneously and PostgreSQL needs a few seconds to finish initializing before it can accept connections.

**Cost management**
Both EC2 instances are terminated after the project is demonstrated and AMI snapshots are saved. The Elastic IP is released at the same time. Docker Hub images and Route 53 DNS records are kept. When a live demo is needed the environment is relaunched from the saved AMI in minutes.

---

## Running Locally

```bash
git clone https://github.com/Vimukthi-Randunu/production-waitlist-api.git
cd production-waitlist-api
```

Create a `.env` file:

```
POSTGRES_USER=waitlist_user
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=waitlist_db
API_KEY=yourapikey
IMAGE_TAG=latest
```

Start the containers:

```bash
docker compose up --build
```

API is available at `http://localhost:80`

Run tests:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

*Built by Vimukthi Randunu — [radianceits.com](https://radianceits.com)*
