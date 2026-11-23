# 101 Assistant UI

A React and TypeScript single-page application built with Vite. It provides
browser interfaces for the chat, money-transfer, supervisor, and orchestrator
agents exposed by the companion FastAPI service.

## Requirements

- Node.js and npm
- The End-to-End API running at `http://localhost:8000`

The UI sends API requests to the fixed base URL `http://localhost:8000`,
configured in `src/baseService.ts`. If your API runs elsewhere, update
`API_BASE_URL` there before starting or building the UI.

## Install and run

From this directory:

```bash
npm ci
npm run dev
```

Open the local URL printed by Vite (usually
<http://localhost:5173>).

Start the API separately from `../API` and complete its configuration first.
The UI depends on the API for registration, login, agent responses, vendors,
and chat history.

## Pages and usage

| Page | Path | Purpose |
| --- | --- | --- |
| Chat | `/chat` | Select a vendor, chat with the agent, and view saved chat history. |
| Money transfer | `/money` | Stream a conversation with the money-transfer agent. |
| Supervisor | `/supervisor` | Stream a conversation with the supervisor agent. |
| Orchestrator | `/orchestrator` | Stream a customer-support conversation. |
| Login | `/login` | Sign in with an existing account. |
| Register | `/register` | Create an account, then sign in. |

## Component overview

### Application shell

- [`App.tsx`](src/App.tsx) selects a page from the current browser pathname and
  renders the navigation links for Chat, Money transfer, Supervisor, and
  Orchestrator. Unknown paths fall back to Chat.
- [`main.tsx`](src/main.tsx) imports the global stylesheet and mounts `App` in
  the page's `root` element.

### Chat

- [`Chat`](src/components/chat/index.tsx) checks for an access token, loads the
  available vendors, and combines the history panel with the message panel.
- [`ChatHistory`](src/components/chat/history/index.tsx) loads the signed-in
  user's conversation list for the selected vendor.
- [`ChatHistoryItem`](src/components/chat/history/historyItem/index.tsx)
  displays one conversation title, marks the selected item, and reports
  selection to its parent.
- [`ChatMessages`](src/components/chat/messages/index.tsx) displays the
  conversation, sends user messages to the chat API, renders streamed agent
  replies, loads a selected conversation, and starts a fresh session.
- [`Vendor`](src/components/vendor/index.tsx) is the selectable vendor item
  shown above the chat.

### Agent conversation pages

- [`Money`](src/components/money/index.tsx) provides the money-transfer
  conversation, streams responses from the money API, and starts a new session
  when reset.
- [`Supervisor`](src/components/supervisor/index.tsx) provides the supervisor
  conversation with streamed replies and reset behavior.
- [`Orchestrator`](src/components/orchestrator/index.tsx) provides the
  customer-support conversation with streamed replies and reset behavior.

### Account pages

- [`SignInPage`](src/components/user/signIn/index.tsx) submits email and
  password to the login API, stores the returned access token, and redirects to
  Chat.
- [`RegistrationPage`](src/components/user/register/index.tsx) submits a new
  account's name, email, and password and shows a link to sign in after
  successful registration.

### Supporting API modules

- [`service.ts`](src/service.ts) exposes UI-level calls for login, registration,
  chat, agent requests, vendors, and chat history.
- [`baseService.ts`](src/baseService.ts) performs HTTP requests, attaches the
  stored bearer token, handles unauthorized responses, and returns stream
  readers for agent requests.

After login, the access token is stored in browser `localStorage` under
`access_token`. Requests to protected API routes include it as a bearer token.
Agent replies are read as streamed responses; chat history and vendor data are
loaded from the API.

The app uses the browser pathname for page selection rather than a routing
library. Unknown paths display the chat page.

## Available scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the Vite development server. |
| `npm run build` | Run the TypeScript compiler and create a production build in `dist/`. |
| `npm run preview` | Serve the built app locally for a production-preview check. |
| `npm run format` | Format source files under `src/` with Prettier. |
| `npm run format:check` | Check source formatting without changing files. |

Build and preview:

```bash
npm run build
npm run preview
```

## Authentication and deployment notes

The UI checks whether an access token exists before showing protected agent
pages, but the API must validate the token; the browser-side check is not an
authorization boundary. The current implementation stores the bearer token in
`localStorage`, so this prototype should only be deployed with appropriate
transport security and protections against cross-site scripting. For production,
review the API's authentication and deployment guidance as well.

Vite's development server supplies single-page-app fallback behavior for local
navigation. Configure equivalent fallback routing in the production web server
so direct visits to paths such as `/chat` and `/login` serve `index.html`.
