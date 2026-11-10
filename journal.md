# Project Journal — lindy_tasks

**lindy_tasks is a "friends of friends" social network app.** People sign up, log in, add each other as friends instantly, and see their network up to three degrees away (1st, 2nd, 3rd), similar to LinkedIn connections. It has a Next.js frontend and a FastAPI + PostgreSQL backend.

> **How to describe this project:** in all project docs, commit messages and READMEs, call it a friends-of-friends app that we're building. The requirements below are this app's own product spec; don't describe it as an assessment, challenge or test.

This file is a running log of what was discussed, observed, decided and changed while working on the project. Newest entries go at the bottom.

---

## 2026-11-09 — Session 1: Initial project assessment

### What was asked
Read every file in the project and assess where things stand: what the frontend does, what the backend does.

### Repo state at the start
- Branch: `main`, working tree clean.
- Commits so far:
  - `0a8ae59` Add root .gitignore for OS and editor files
  - `129cac8` Add FastAPI backend with user registration
  - `a8102e2` Add Next.js frontend
- Local, git-ignored items present: `backend/.venv/`, `frontend/node_modules/`, `frontend/.next/`, `frontend/.idea/`, `.DS_Store`.
- `backend/.env` does **not** exist yet (only `backend/.env.example`).

### What the project is
A friends-of-friends social app. The frontend is in place, and the product spec is in `frontend/README.md`. The work is building the backend API on `localhost:8080` that the frontend talks to.

- **Part 1:** user registration and authentication (`register`, `login`, `profile`).
- **Part 2:** friends system: add a friend (instant, no request), and view the network up to 3rd degree, LinkedIn style.

### Frontend observations (`frontend/`)
Stack: Next.js 14.2.3 (App Router), React 18, TanStack React Query, zod, Tailwind, @faker-js/faker.

API origin is hardcoded in `next.config.mjs` as `NEXT_PUBLIC_API_ORIGIN=http://localhost:8080`. Every fetch uses `credentials: "include"`, so **auth is expected to be cookie-based**.

| Route | Behavior | Endpoint used |
|---|---|---|
| `/` | Redirects to `/login` (`app/page.tsx` is unreachable starter code) | — |
| `/app` | Redirects to `/app/profile` | — |
| `/login` | Email and password form → `/app` on success | `POST /v1/auth/login` |
| `/register` | Name, email and password form → **straight to `/app`** on success | `POST /v1/auth/register` |
| `/app/profile` | Shows name and email; "Insert Fake Data" dev button | `GET /v1/profile` → `{email, name}` |
| `/app/friends` | Lists network with 1st/2nd/3rd counts; "Add Friend" on 2nd/3rd | `GET /v1/friends` → `[{name, email, degree}]`, `POST /v1/friends/add` `{friendEmail}` |

What the frontend assumes about the backend:
- **Error format:** `app/lib/errors.ts` only shows a message if the response looks like `{ "error": true, "message": "..." }`. Anything else becomes "An unexpected error occurred".
- **Registering should also log you in**, because after registering the app goes straight to the profile page, which needs the login cookie.
- **Fake-data tool** (`app/lib/insertFakeData.ts`):
  - Registers 100 random users.
  - Logs in as each one in turn (so login must replace the existing cookie).
  - Each one adds about 5% of the others as friends; the first 5 also friend the current user.
  - Then redirects to `/` → `/login`, because the session now belongs to the last fake user.
  - It also reads an `id` from `/v1/profile`, but only uses `email`.
- **Friendships work both ways:** "they immediately become friends".
- **Friends list:** each person's degree should be their shortest distance; leave the current user out; stop at 3rd degree.

Minor frontend quirks (not addressed yet; low priority):
- Both `package-lock.json` and `pnpm-lock.yaml` are committed.
- Forms use `type="button"`, so pressing Enter doesn't submit.
- No logout, and no client-side route protection.
- `frontend/.gitignore` ends with a `backend` entry (no trailing newline).
- `app/layout.tsx` metadata is still "Create Next App".

### Backend observations (`backend/`)
Stack: FastAPI, psycopg2 (raw SQL), PostgreSQL, passlib + bcrypt 4.0.1, python-dotenv. `python-jose` is installed but unused (JWT was apparently planned).

What exists:
- `app/main.py`: app on `localhost:8080` (run from `backend/` with `python -m app.main`); auth router at `/v1/auth`; CORS allows `http://localhost:3000` with credentials (correct for cookies).
- `app/routes/auth.py`: only `POST /register`. Checks for a duplicate email → 400, hashes the password, inserts the user, returns 201 `{"message": "User created"}`.
- `app/security.py`: `hash_password` and `verify_password` (bcrypt). `verify_password` isn't used yet.
- `app/database.py`: opens a new psycopg2 connection per call, configured from env vars (no pool).
- `schema.sql`: `users` table only (`id UUID`, `name`, unique `email`, `hashed_password`), using the `pgcrypto` extension.

Gaps and issues found:
1. **Missing endpoints:** `POST /v1/auth/login`, `GET /v1/profile`, `POST /v1/friends/add`, `GET /v1/friends`.
2. **No session or cookie handling at all**, and register doesn't log the user in.
3. **Error format doesn't match:** FastAPI returns `{"detail": ...}` (and a 422 with a list for bad input), so the UI always shows "An unexpected error occurred". This needs app-level error handlers that return `{error: true, message}`.
4. **No friendships table** in `schema.sql`.
5. **Smaller issues:**
   - The connection isn't closed when a query throws (no try/finally).
   - The 500 handler sends raw DB errors to the client (`str(e)`).
   - Two registrations of the same email at the same moment give a 500 instead of a 400.
   - Emails aren't lowercased before saving or checking.
   - `load_dotenv()` is called twice (harmless).
6. **Setup:** `backend/.env` needs to be created from `.env.example` before the backend can run.

### Status summary
| Item | Status |
|---|---|
| Part 1: register | Works, but errors display wrong and it doesn't log you in |
| Part 1: login and profile | Not started |
| Part 2: friends add/list | Not started (needs a table plus a 3-level search) |

### Proposed next steps (not started)
1. **Finish Part 1:**
   - A login cookie (signed JWT via `python-jose`).
   - `POST /v1/auth/login` and `GET /v1/profile`.
   - Log the user in on register.
   - Error handlers that return `{error: true, message}`.
2. **Part 2:**
   - A `friendships` table (undirected, no self-friending, no duplicates).
   - `POST /v1/friends/add`.
   - `GET /v1/friends` using a 3-level search (e.g. a recursive CTE), minimum degree per person, excluding the user.

### Decisions
- Proposed implementing the rest of Part 1 now; the user chose **"Not yet"**. No code changes made.

### Changes made
- Created this `journal.md` at the project root. No source code was modified.

---

## 2026-11-09 — Session 1 (cont.): Project framing

### Decisions
- The project is presented as a **friends-of-friends app** we're building, not as an assessment or challenge.

### Changes made
- Added a project description and a "How to describe this project" note at the top of this journal.
- Reworded the earlier entry to describe the project as a friends-of-friends app.

### Observations
- `frontend/README.md` still had a "Challenge Requirements" heading and challenge wording ("To complete this challenge…", "You won't need to modify any of the frontend code").

### Follow-up: `frontend/README.md` rewritten
- Rewrote it as a normal project README for the friends-of-friends app: overview, getting started, pages, API reference, and the test-data seeding tool.
- Kept all endpoint contracts the same. Also:
  - Documented the `{ error: true, message }` error format the UI relies on.
  - Fixed the `GET /v1/friends` type name (it was `RequestBody`; now `ResponseBody`).
  - Stated that friendships go both ways and that each person appears once, at their closest degree.
- Decided: no code changes, and no need to rewrite git history.

---
