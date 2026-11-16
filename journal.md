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

## 2026-11-13 — Session 2: Part 1 (accounts and authentication)

### What was asked
Make the changes needed to finish Part 1 (register, login, profile), record them here, and don't push anything.

### Decisions
- **Sessions:** a signed JWT (HS256, `python-jose`) stored in an `HttpOnly` cookie named `session`, valid for 7 days. `SameSite=Lax` works because `localhost:3000` and `localhost:8080` count as the same site. `Secure` is off for local HTTP and should be turned on for HTTPS.
- **Register also signs the user in**, since the frontend goes straight to `/app` afterwards.
- **Emails are lowercased** before saving and when signing in.
- **Login failures are deliberately vague:** a wrong password and an unknown email both return 401 "Invalid email or password", and both take about the same time (an unknown email is checked against a dummy hash).
- **Validation:** name is 1–100 characters and can't be blank; password is at least 8 characters and at most 72 **bytes** (bcrypt ignores anything past 72 bytes, and accented or non-Latin characters take more than one byte each). The fake-data tool's generated passwords meet this.
- **`GET /v1/profile` also returns `id`**, because the fake-data tool reads it.
- No logout endpoint yet, since the frontend has no logout button.
- `schema.sql` is unchanged; Part 1 only needs the existing `users` table.

### Changes made (`backend/`)
| File | Change |
|---|---|
| `app/config.py` | **New.** Loads `.env` once and holds all settings. `JWT_SECRET` is required; the app won't start without it. |
| `app/database.py` | Added a `db_cursor()` helper that commits on success, rolls back on error, and always closes the connection. |
| `app/security.py` | Added session token create/read and `set_session_cookie()`. `verify_password()` now handles a missing user safely. |
| `app/deps.py` | **New.** `get_current_user` reads the session cookie and loads the user, or returns 401 "Not signed in". |
| `app/errors.py` | **New.** Every error, including FastAPI's validation errors and unexpected crashes, now returns `{ "error": true, "message": "..." }`. Raw database errors are logged instead of sent to the browser. Crashes are caught in a middleware placed inside CORS, so 500 responses still carry CORS headers and the frontend can read them. |
| `app/routes/auth.py` | Register: validation, lowercased email, `ON CONFLICT` so two sign-ups with the same email at the same moment give a 400 instead of a 500, and sets the cookie. **New** `POST /v1/auth/login`. |
| `app/routes/profile.py` | **New.** `GET /v1/profile` returns `{ id, name, email }`. |
| `app/main.py` | Registers the error handlers and the profile router. The CORS origin now comes from config. |
| `.env.example` | Added `JWT_SECRET` and `FRONTEND_ORIGIN`. |

This also fixes these issues from Session 1: the error format mismatch, no session handling, register not signing in, connections left open after errors, raw DB errors sent to the client, the duplicate-email race, emails not lowercased, and the duplicate `load_dotenv()`.

### Testing
- Postgres isn't installed on this machine, so the flow was tested over real HTTP against a running server, with the database replaced by an in-memory stand-in. **15/15 checks passed:**
  - register → 201, sets an HttpOnly cookie; profile works right away
  - duplicate email (any case) → 400; bad email, short password or blank name → 422; all with `{error, message}`
  - profile with no cookie or a bad cookie → 401
  - wrong password and unknown email → the same 401
  - login works with any email case; logging in as someone else switches the session
  - CORS allows `localhost:3000` with credentials
- (Expanded to 21 checks after the self-review below.)
- **Not yet tested against real Postgres or in the browser.** The test script lives outside the repo and isn't committed.

### Self-review (same session)
A second pass over the Part 1 code found and fixed:
1. **500 errors were unreadable by the frontend.** Starlette runs a catch-all `exception_handler(Exception)` outside every middleware, including CORS, so the browser would block the response and the UI would show "Failed to fetch". Replaced it with a middleware that sits inside CORS.
2. **The password limit counted characters, not bytes.** 40 accented characters (80 bytes) passed the 72-character limit and would have been silently cut short by bcrypt. It's now checked in bytes.
3. **Messages read "name: Value error, Name can't be blank".** The `Value error, ` prefix is now stripped.
4. Malformed JSON returned a message starting with a character position (e.g. "7: JSON decode error"); the position is now dropped.
5. HTTP errors now keep their headers (e.g. `Allow` on a 405).

Added 6 tests for these (the cleaned-up messages, the multi-byte password limit, 72 ASCII characters still accepted, malformed JSON, and a simulated database crash returning a generic 500 with CORS headers and no database details). **21/21 checks pass.**

### To run it
1. Install and start Postgres, then create the database and load `backend/schema.sql`.
2. Copy `backend/.env.example` to `backend/.env`, then fill in the DB settings and a `JWT_SECRET`.
3. From `backend/`: `source .venv/bin/activate && python -m app.main`.

### Status summary
| Item | Status |
|---|---|
| Part 1: register, login, profile | Done (tested against an in-memory stand-in for the database) |
| Part 2: friends add/list | Not started |

### Not done
- Nothing committed or pushed.

---

## 2026-11-15 — Session 3: Part 2 (friends network)

### What was asked
Plan Part 2, re-check the plan, then build it. No testing for now, and don't push.

### Decisions
- **Storage:** a `friendships` table that stores each friendship as two rows (A→B and B→A), so the network query only follows one direction. The primary key `(user_id, friend_id)` prevents duplicates and covers every lookup. A `CHECK` blocks self-friending, and `ON DELETE CASCADE` removes friendships with a deleted user.
- **Network query:** three plain steps (`d1`, `d2`, `d3`), each with `DISTINCT`, instead of a recursive query. Recursive queries revisit the same people repeatedly in a dense network like the fake data.
  - `MIN(degree)` keeps each person at their closest degree.
  - `WHERE id <> me` removes the user, who always shows up at 2nd degree as their friends' friend.
- **Adding a friend:**
  - Both rows are written in one `INSERT … ON CONFLICT DO NOTHING`, so a friendship is never half-written.
  - Re-adding an existing friend, from either side, returns **200**. The fake-data tool sends many duplicate and reverse adds.
  - The self-check compares user ids rather than emails, so a differently-cased email is still caught.
  - Unknown email → 404 "No user with that email". This reveals whether an email is registered, which is acceptable because the friends list already shows emails.
- **Route path:** the list route is `""`, not `"/"`, so `/v1/friends` doesn't get redirected (a redirected cross-origin request can lose the cookie).

### Changes made (`backend/`)
| File | Change |
|---|---|
| `schema.sql` | Added the `friendships` table. Both tables now use `CREATE TABLE IF NOT EXISTS`, so the file can be re-run safely. |
| `app/routes/friends.py` | **New.** `GET /v1/friends` returns `[{name, email, degree: '1st' \| '2nd' \| '3rd'}]` sorted by degree, then name. `POST /v1/friends/add` takes `{friendEmail}`. Both require a signed-in user. |
| `app/main.py` | Registered the friends router at `/v1/friends`. |

### Testing
- **Not tested, as agreed.** The only check: the app loads, and all five `/v1` routes are registered.
- The network query **has not been run against Postgres.** Worth trying before relying on it: the README's Bob → Sarah → Rachel → Sam → Jack example, and the frontend's "Insert Fake Data" button.

### To run it
If the database was already created from the old `schema.sql`, re-run `backend/schema.sql`; only the new `friendships` table will be added.

### Status summary
| Item | Status |
|---|---|
| Part 1: register, login, profile | Done (tested against an in-memory stand-in for the database) |
| Part 2: friends add/list | Built, not tested |

### Not done
- Nothing pushed. `main` is ahead of `origin/main`.

---
