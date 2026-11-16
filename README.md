# Friends of Friends

A small social network I'm building to explore how connection graphs work. You create an account, add friends instantly (no friend requests), see your network up to three degrees away (similar to LinkedIn connections), and log out when you're done:

```
Bob is friends with Sarah, Sarah with Rachel, Rachel with Sam, Sam with Jack.

Bob's network:  Sarah (1st) · Rachel (2nd) · Sam (3rd)
Jack is 4th degree, so he isn't shown.
```

**Stack:** Next.js 14 + React Query + Tailwind on the frontend. FastAPI + PostgreSQL on the backend, with cookie-based sessions.

## Setup

You need **Python 3.10+**, **Node.js 18+** and **PostgreSQL**.

### 1. Database

With Homebrew on macOS:

```bash
brew install postgresql@16
brew services start postgresql@16
createdb lindy_tasks
psql -d lindy_tasks -f backend/schema.sql
```

`schema.sql` is safe to re-run; it only creates tables that don't exist yet.

### 2. Backend (runs on `localhost:8080`)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then fill in `.env`:

- `DB_*`: your Postgres connection details. With Homebrew, `DB_USER` is your macOS username and the password is blank.
- `JWT_SECRET`: required, and the server won't start without it. Generate one with:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

Start the server:

```bash
python -m app.main
```

### 3. Frontend (runs on `localhost:3000`)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and register an account. To fill your network with test data, use the **Insert Fake Data** button on the profile page. It creates 100 random users and connects some of them to you; sign in again afterwards.

## API

| Method | Endpoint | What it does |
|---|---|---|
| `POST` | `/v1/auth/register` | Create an account (`name`, `email`, `password`) and sign in |
| `POST` | `/v1/auth/login` | Sign in (`email`, `password`) |
| `POST` | `/v1/auth/logout` | Sign out (clears the session cookie) |
| `GET` | `/v1/profile` | The signed-in user's `id`, `name` and `email` |
| `POST` | `/v1/friends/add` | Add a friend by `friendEmail` |
| `GET` | `/v1/friends` | Your network: `[{ name, email, degree: "1st" \| "2nd" \| "3rd" }]` |

Errors always come back as `{ "error": true, "message": "..." }`. Full request and response shapes are in [frontend/README.md](frontend/README.md).

## Project structure

```
.
├── backend/              FastAPI server
├── frontend/             Next.js app
├── journal.md            Development log: decisions and changes, session by session
└── .gitignore            Ignores OS and editor files
```

### Backend

| File | What it does |
|---|---|
| `app/main.py` | Creates the FastAPI app, registers routes, error handlers and CORS, and starts the server on port 8080 |
| `app/config.py` | Loads `.env` and holds every setting (database, session secret, frontend origin) |
| `app/database.py` | Opens Postgres connections. `db_cursor()` commits on success, rolls back on error, and always closes the connection |
| `app/security.py` | Password hashing (bcrypt), session tokens (signed JWT), and setting and clearing the session cookie |
| `app/deps.py` | `get_current_user`: reads the session cookie and loads the signed-in user, or returns 401 |
| `app/errors.py` | Turns every error, including validation errors and crashes, into `{ error, message }` |
| `app/routes/auth.py` | Register, login and logout endpoints |
| `app/routes/profile.py` | Profile endpoint |
| `app/routes/friends.py` | Add-friend endpoint and the 3-degree network query |
| `schema.sql` | Database tables: `users`, and `friendships` (each friendship stored in both directions) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for `.env` |

### Frontend

| File | What it does |
|---|---|
| `app/layout.tsx` | Root layout: sets the browser tab title and wraps every page in the React Query provider |
| `app/providers.tsx` | Sets up the React Query client |
| `app/login/page.tsx` | Sign-in form (Enter submits) |
| `app/register/page.tsx` | Sign-up form (Enter submits) |
| `app/app/layout.tsx` | Layout for signed-in pages: checks the session and sends signed-out visitors to `/login`, plus Profile / Friends navigation and the Log out button |
| `app/app/profile/page.tsx` | Shows your name and email, plus the Insert Fake Data button |
| `app/app/friends/page.tsx` | Your network grouped by degree, with an Add Friend button for 2nd and 3rd degree people |
| `app/lib/api.ts` | Shared API helpers: `apiFetch` (sends the cookie, and throws an `ApiError` carrying the HTTP status), `fetchProfile` and `logout` |
| `app/lib/errors.ts` | Pulls the `message` out of API error responses |
| `app/lib/insertFakeData.ts` | Generates 100 fake users and random friendships for testing |
| `app/globals.css` | Global styles (Tailwind) |
| `next.config.mjs` | Redirects (`/` → `/login`, `/app` → `/app/profile`) and the backend URL |
| `tailwind.config.ts`, `postcss.config.mjs` | Tailwind setup |
| `tsconfig.json`, `.eslintrc.json` | TypeScript and lint config |
| `package.json` | Dependencies and scripts (`dev`, `build`, `start`, `lint`) |
