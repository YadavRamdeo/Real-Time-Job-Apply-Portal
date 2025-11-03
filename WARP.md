# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common commands

Backend (Django)
- Create/activate venv (Windows):
  ```
  python -m venv venv
  venv\Scripts\activate
  ```
- Install deps and run migrations:
  ```
  pip install -r requirements.txt
  cd backend
  python manage.py migrate
  ```
- Start dev server (ASGI, Channels enabled):
  ```
  python manage.py runserver
  ```
  Optional (explicit ASGI server):
  ```
  python -m daphne -p 8000 jobportal.asgi:application
  ```
- Create admin user:
  ```
  python manage.py createsuperuser
  ```
- Run backend tests (none present yet, but discovery works):
  ```
  python manage.py test
  ```
  Run a single Django test (example pattern):
  ```
  python manage.py test app_label.tests.TestClass.test_method
  ```

Frontend (React / Create React App)
- Install deps and start:
  ```
  cd frontend
  npm install
  npm start
  ```
- Build production bundle:
  ```
  npm run build
  ```
- Run tests (Jest/RTL):
  ```
  npm test
  ```
  Run a single test file:
  ```
  npm test -- App.test.js
  ```
- Linting: no explicit lint script is defined; CRA surfaces ESLint warnings during `npm start` and `npm test`.

## High-level architecture

- Overall
  - Two-tier app: Django REST API backend (`backend/`) and React SPA frontend (`frontend/`).
  - Authentication: Django REST Framework Token Auth; frontend sends `Authorization: Token <key>` via `src/services/api.js`.
  - Real-time: Django Channels configured with an in-memory channel layer for development; WebSocket URL expected at `ws://localhost:8000/ws/notifications/` (see `frontend/src/config/api.config.js`). No consumers are currently wired; `backend/accounts/routing.py` holds a placeholder.

- Backend (Django)
  - Project: `backend/jobportal/`
    - `settings.py`: DRF + TokenAuth, CORS enabled, SQLite DB, `ASGI_APPLICATION` set, Channels in-memory layer.
    - `urls.py`: mounts app routes under `/api/` prefixes.
    - `asgi.py`: ProtocolTypeRouter for HTTP and WebSocket; routes WebSockets via `accounts.routing.websocket_urlpatterns`.
  - Apps
    - `accounts`: user profile and notifications models; auth endpoints:
      - `POST /api/auth/register/` and `POST /api/auth/login/`
      - `GET /api/accounts/profile/`, `PUT /api/accounts/profile/update/`
    - `resumes`: resume upload/parse and auto-apply flow:
      - `POST /api/resumes/upload/` saves the file, extracts skills/experience, searches external portals, and auto-applies for high matches (>= 60%).
      - `GET /api/resumes/` lists user resumes; `GET/PUT /api/resumes/applications/` and `/api/resumes/applications/<id>/status/` manage applications.
      - Matching logic in `resumes/matching.py`:
        - Uses NLTK + scikit-learn TF-IDF + cosine when available; falls back to token/Jaccard.
    - `jobs`: job listings, live search, and apply:
      - `GET /api/jobs/` active jobs; `GET /api/jobs/<id>/` detail.
      - `GET /api/jobs/search/` aggregates jobs across portals; `GET /api/jobs/matching/<resume_id>/` computes match scores against DB + external results.
      - `POST /api/jobs/apply/<job_id>/` applies with a given resume.
      - Aggregation modules:
        - `jobs/scraper.py`: portal scrapers (Indeed, Naukri, WeWorkRemotely, RemoteOK, Remotive, LinkedIn best-effort) with role filtering and URL de-duplication.
        - `jobs/ats.py`: ATS detectors + API scrapers (Greenhouse, Lever, SmartRecruiters); uses `company_catalog.json` and `company_catalog_urls.txt` if present.
  - Data model highlights
    - `jobs.Company` → `jobs.Job` (FK) → `jobs.JobApplication` (user, resume, status, match_score).
    - `resumes.Resume` stores parsed content, skills, experience.
    - `accounts.Notification` stores per-user notifications (frontend currently polls them; WebSocket path reserved).

- Frontend (React)
  - Bootstrapped with CRA; routing under `src/pages/*` and common components under `src/components/*`.
  - API layer: `src/services/api.js` centralizes endpoints from `src/config/api.config.js`, attaches DRF token, and exposes helpers (`login`, `register`, `getJobs`, `searchLiveJobs`, `uploadResume`, `applyToJob`, etc.).
  - Notifications: `src/components/Notifications.js` polls `GET /api/notifications/` and displays Bootstrap toasts. A `src/services/websocket.js` singleton exists to connect to `WEBSOCKET_URL`, but backend consumers are not implemented yet.

## Notes for future agents working here
- Keep frontend `API_CONFIG` paths in sync with Django routes in `backend/*/urls.py` (notably auth and jobs endpoints already align).
- If enabling real-time notifications, implement Channels consumers and add them to `accounts.routing.websocket_urlpatterns`; consider a Redis channel layer for multi-process usage.
- External job search relies on live HTML/APIs; network failures are handled best-effort with timeouts and de-duplication.
