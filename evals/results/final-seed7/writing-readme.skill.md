# Todo App

A simple, fast todo list app built with React and Firebase — create, complete, and delete tasks that sync in real time and persist per signed-in user.

```markdown
# Todo App

A simple, fast todo list app built with React and Firebase — create, complete, and delete tasks that sync in real time and persist per signed-in user.

## Features

- Add, edit, complete, and delete todos
- Real-time sync via Firestore (changes reflect instantly across tabs/devices)
- Google sign-in with Firebase Authentication — each user sees only their own todos
- Responsive UI, works on mobile and desktop
- Filter by all / active / completed

## Tech Stack

- **React 18** + **Vite**
- **Firebase** — Authentication (Google provider) and Firestore (database)
- **React Router** (if you have multiple views, e.g. login + app)

## Prerequisites

- Node.js 18+
- A [Firebase project](https://console.firebase.google.com/) with:
  - **Authentication** → Google sign-in provider enabled
  - **Firestore Database** created (start in test mode, then lock down with the rules below)

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/[your-username]/todo-app.git
cd todo-app
npm install
```

### 2. Configure environment variables

Create a `.env` file in the project root (copy `.env.example` if present):

```bash
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

Get these values from Firebase Console → Project Settings → General → Your apps → SDK setup and configuration.

> `.env` is gitignored — never commit real Firebase keys. Vite only exposes variables prefixed with `VITE_` to the client.

### 3. Run locally

```bash
npm run dev
```

App runs at `http://localhost:5173`.

## Available Scripts

| Command           | Description                        |
|-------------------|-------------------------------------|
| `npm run dev`     | Start local dev server with HMR    |
| `npm run build`   | Production build to `dist/`        |
| `npm run preview` | Preview the production build       |
| `npm run lint`    | Run ESLint                         |

## Project Structure

```
src/
├── components/     # TodoList, TodoItem, AddTodo, etc.
├── context/        # Auth context / providers
├── firebase.js     # Firebase app initialization
├── hooks/          # Custom hooks (e.g. useTodos)
├── App.jsx
└── main.jsx
```

## Firestore Security Rules

Each user can only read/write their own todos:

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /todos/{todoId} {
      allow read, update, delete: if request.auth != null && request.auth.uid == resource.data.uid;
      allow create: if request.auth != null && request.auth.uid == request.resource.data.uid;
    }
  }
}
```

## Deployment

Deployed via Firebase Hosting:

```bash
npm run build
firebase login
firebase init hosting   # select your project, set public dir to "dist", configure as SPA: yes
firebase deploy
```

## License

MIT
```

**Assumed:** Vite (not Create React App, which is deprecated) + Firebase Auth with Google sign-in + Firestore for per-user storage, deployed to Firebase Hosting. Replace `[your-username]`, adjust the stack/scripts table, and swap deployment section if you're actually using Vercel/Netlify instead.
