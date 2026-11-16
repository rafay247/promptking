# Todo App

A fast, minimal todo list app built with React and Firebase — create, complete, and organize tasks with real-time sync and optional multi-device login via Firebase Auth.

```markdown
# Todo App

A fast, minimal todo list app built with React and Firebase — create, complete, and organize tasks with real-time sync across devices.

## Features

- ✅ Create, edit, complete, and delete todos
- 🔄 Real-time sync via Firestore (changes appear instantly across tabs/devices)
- 🔐 User authentication (sign up / log in) with Firebase Auth
- 🗂️ Per-user task lists — each account only sees its own todos
- 📱 Responsive UI, works on desktop and mobile

## Tech Stack

- **React** (Vite)
- **Firebase** — Firestore (database) + Firebase Auth (authentication)
- **Firebase Hosting** for deployment

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- A free [Firebase](https://console.firebase.google.com/) project with **Firestore** and **Authentication** (Email/Password provider) enabled

### 1. Clone and install

```bash
git clone https://github.com/[your-username]/[your-repo].git
cd [your-repo]
npm install
```

### 2. Configure Firebase

Create a `.env.local` file in the project root with your Firebase project's web config (Project Settings → General → Your apps → SDK setup):

```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

> `.env.local` is gitignored by default — never commit real keys.

### 3. Run locally

```bash
npm run dev
```

App runs at `http://localhost:5173`.

## Scripts

| Command           | Description                      |
|--------------------|----------------------------------|
| `npm run dev`      | Start local dev server           |
| `npm run build`    | Build for production             |
| `npm run preview`  | Preview the production build     |

## Project Structure

```
src/
├── components/     # UI components (TodoItem, TodoList, AddTodo, etc.)
├── firebase.js     # Firebase app initialization
├── hooks/          # Custom hooks (e.g. useAuth, useTodos)
├── App.jsx
└── main.jsx
```

## Firestore Data Model

```
todos (collection)
└── {todoId}
    ├── text: string
    ├── completed: boolean
    ├── userId: string       // owner's Firebase Auth UID
    └── createdAt: timestamp
```

Recommended Firestore security rule — restrict reads/writes to the owning user:

```js
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /todos/{todoId} {
      allow read, update, delete: if request.auth != null && request.auth.uid == resource.data.userId;
      allow create: if request.auth != null && request.auth.uid == request.resource.data.userId;
    }
  }
}
```

## Deployment

```bash
npm run build
firebase deploy
```

(Requires `firebase init hosting` to be run once, with the build output directory set to `dist`.)

## License

MIT
```

Assumed: Vite as the build tool (modern default over Create React App), Firestore for storage, Email/Password auth, and MIT license — swap these if your stack differs.
