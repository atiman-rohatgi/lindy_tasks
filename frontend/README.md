# Friends of Friends: Frontend

The web client for a friends-of-friends social network. Users create an account, add friends instantly, and see their network up to three degrees away (1st, 2nd and 3rd), similar to LinkedIn connections.

Built with Next.js 14 (App Router), React Query, zod and Tailwind CSS.

## Getting Started

Install the dependencies:

```bash
npm install
```

Start the dev server:

```bash
npm run dev
```

The frontend runs at [http://localhost:3000](http://localhost:3000). It expects the backend API at `http://localhost:8080` (configured in `next.config.mjs`).

## Pages

| Route | Description |
|---|---|
| `/login` | Sign in with email and password |
| `/register` | Create an account (name, email, password) |
| `/app/profile` | The signed-in user's name and email, plus a dev tool to seed test data |
| `/app/friends` | The user's network grouped by degree, with an "Add Friend" button for 2nd and 3rd degree connections |

## API

All endpoints accept and return JSON. Authentication uses a session cookie, so every request is sent with `credentials: "include"`.

### Error format

Failed requests return a non-2xx status with this body. The UI shows `message` to the user:

```ts
type ErrorBody = {
    error: true
    message: string
}
```

### Accounts and authentication

A user has a name, email, password and a list of friends.

#### `POST /v1/auth/register`
Creates a new user account.

Request:
```ts
type RequestBody = {
    name: string
    email: string
    password: string
}
```

Response: any 2xx status.

#### `POST /v1/auth/login`
Signs in to an existing account and sets the session cookie.

Request:
```ts
type RequestBody = {
    email: string
    password: string
}
```

Response: any 2xx status.

#### `GET /v1/profile`
Returns the signed-in user's profile.

Request: none (the session cookie identifies the user).

Response:
```ts
type ResponseBody = {
    email: string
    name: string
}
```

### Friends network

Adding a friend is instant: there are no friend requests. Friendships go both ways.

The friends list includes the user's direct friends plus their 2nd and 3rd degree connections. Each person is listed once, at their closest degree.

Example:
```
Bob is friends with Sarah
Sarah is friends with Rachel
Rachel is friends with Sam
Sam is friends with Jack

Bob's friends list shows:
Sarah (1st)
Rachel (2nd)
Sam (3rd)

Jack isn't shown because he's a 4th degree connection.
```

#### `POST /v1/friends/add`
Adds another user as a friend.

Request:
```ts
type RequestBody = {
    friendEmail: string
}
```

Response: any 2xx status.

#### `GET /v1/friends`
Returns the signed-in user's network.

Request: none.

Response:
```ts
type ResponseBody = {
    name: string
    email: string
    degree: '1st' | '2nd' | '3rd'
}[]
```

## Seeding test data

The "Insert Fake Data" button on the profile page:
1. Registers 100 random users.
2. Signs in as each one and has them add a few random friends.
3. Makes five of them friends with your account.
4. Leaves you signed in as the last generated user, so afterwards you're sent back to the login page. Sign in again to see your network.
