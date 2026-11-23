# End-to-End API

A FastAPI application that exposes conversational agents built with LangGraph,
persists selected conversations and graph checkpoints in PostgreSQL, and mounts
an authenticated MCP server for tools used by the chat agent.

> **Prototype notice:** several routes and integrations are incomplete or have
> known security limitations. Read [Security and deployment](#security-and-deployment)
> before exposing this service outside a trusted development environment.

## Contents

- [Requirements](#requirements)
- [Install and run](#install-and-run)
- [Configuration](#configuration)
- [HTTP API](#http-api)
- [Agent designs](#agent-designs)
- [MCP server and client](#mcp-server-and-client)
- [Security and deployment](#security-and-deployment)
- [Known wiring and integration gaps](#known-wiring-and-integration-gaps)

## Requirements

- Python 3.10 or newer
- PostgreSQL
- [Ollama](https://ollama.com/) for the chat model and local embeddings
- API credentials for the external services you plan to use (see
  [Configuration](#configuration))

The configured chat model is `gpt-oss:20b`; the RAG indexes use
`mxbai-embed-large`. The orchestrator also loads the
`Dragneel/ticket-classification-v1` Hugging Face model.

## Install and run

Run these commands from this directory (`ai/End-to-End/API`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create or update a local `.env` file using the variables in
[Configuration](#configuration). Do not commit credentials or tokens.

Prepare a PostgreSQL database and set `DATABASE_URL`. The application creates a
connection pool at startup, and LangGraph's PostgreSQL checkpointer initializes
its own checkpoint tables when a graph first runs. This repository does not
include SQL migrations for the application tables; provision the schema expected
by the user, chat, vendor, and notes database code before using those features.

Start Ollama in a separate terminal and download the models:

```bash
ollama pull gpt-oss:20b
ollama pull mxbai-embed-large
ollama serve
```

Start the API from this directory:

```bash
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Check that the server is responding:

```bash
curl http://127.0.0.1:8000/status
```

Interactive API documentation is available at
<http://127.0.0.1:8000/docs>.

## Configuration

Set values in `.env` or in the process environment. Use real values only in
your local secret store; the placeholders below are not credentials.

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | Logger selection; use `dev` for local development. |
| `DATABASE_URL` | PostgreSQL connection string used by the API and LangGraph checkpoint saver. |
| `JWT_SECRET_KEY` | HS256 signing key. Token creation requires at least 32 bytes. Generate a random value, for example with `python -c 'import secrets; print(secrets.token_urlsafe(48))'`. |
| `MCP_SERVER_URL` | MCP HTTP endpoint, normally `http://127.0.0.1:8000/mcp/` for local development. |
| `AVIATIONSTACK_API_KEY` | AviationStack key used for live flight-status searches. |
| `TAVILY_API_KEY` | Tavily key used for hotel web searches. |
| `DEFAULT_ORIGIN_IATA` | Optional fallback flight origin; defaults to `DAC`. |
| `MONEY_TRANSFER_URL` | Base URL used to construct the transfer link. |
| `MONEY_TRANSFER_CODE` | Code included in the generated transfer URL. Treat it as sensitive. |

Ollama is configured through the `ChatOllama` defaults in the code and is
expected to be available locally. Configure the Ollama host in code or extend
the application configuration if your Ollama server is remote.

## HTTP API

The application exposes the following routes:

| Route | Authentication | Description |
| --- | --- | --- |
| `GET /status` | None | Basic health response and server time. |
| `POST /users/register` | None | Register a user. |
| `POST /users/login` | None | Verify credentials and return an access token. |
| `POST /person-agent` | Bearer access token | Run or resume the name-and-age workflow. |
| `POST /money-agent` | Bearer access token | Run the money-transfer workflow. This path currently also appears in the travel router; see [Known wiring and integration gaps](#known-wiring-and-integration-gaps). |
| `POST /chat-agent` | Bearer access token | Stream a tool-using chat response. |
| `POST /orchestrator-agent` | Bearer access token | Stream a customer-support response. |
| `POST /supervisor-agent` | Bearer access token | Stream a money-transfer conversation using the supervisor workflow. |
| `GET /vendors` | None | List chat vendors. |
| `GET /chats/{vendor_id}` | Bearer access token | List the caller's chats for a vendor. |
| `GET /chat/{id}` | Bearer access token | Retrieve a chat by ID; ownership is not currently checked. |
| `/mcp/` | Bearer access token | MCP server mounted by the FastAPI application. |

Register and log in to obtain an access token:

```bash
curl -X POST http://127.0.0.1:8000/users/register \
  -H 'Content-Type: application/json' \
  -d '{"fname":"Ada","lname":"Lovelace","email":"ada@example.com","password":"choose-a-long-password"}'

curl -X POST http://127.0.0.1:8000/users/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.com","password":"choose-a-long-password"}'
```

Use the returned `access_token` as a bearer token. Agent endpoints stream
Server-Sent Events (SSE), so `curl -N` is useful when trying them manually:

```bash
curl -N -X POST http://127.0.0.1:8000/person-agent \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"query":"start","session_id":"local-demo"}'
```

Agent request bodies use the `Item` model: `query`, `vendor_id`, `session_id`,
and `previous_state_id` are optional. Reuse a session ID to continue a
checkpointer-backed conversation. The person workflow uses an in-memory
checkpointer, so its state does not survive a process restart.

## Agent designs

The graph wiring overview is available in
[`agents/langgraph-graphs.svg`](agents/langgraph-graphs.svg).

| Agent | Design |
| --- | --- |
| **Orchestrator** | Runs an initial support node, retrieves relevant FAQ content, classifies the request, and routes it to the technical, billing, or general handler. Those branches converge on escalation and response nodes. |
| **Supervisor** | A state-driven transfer workflow. It uses `Command` routing to collect and validate amount and currency, ask for explicit confirmation, handle requested changes, and return a configured transfer link after confirmation. |
| **Money** | A second transfer workflow with amount, currency, and confirmation nodes. The supervisor node selects the next step from state; the amount and currency nodes extract and validate user-provided values. Completion returns a transfer link rather than executing a transfer. |
| **Travel** | A linear workflow: search flight status, search hotels, draft an itinerary, then format the final response. Flight searches use AviationStack; hotel searches use Tavily. Ticket prices are not guaranteed by the flight-status API. |
| **Person** | A state router that requests a name and age using LangGraph interrupts, validates each response, and builds a result. Invalid values return to the relevant prompt; a reset request clears the collected state. |
| **Chat** | Calls the local chat model with MCP tools bound. If the model requests a tool, `ToolNode` executes it and control returns to the model; otherwise the graph ends. Conversation checkpoints and chat records use PostgreSQL. |
| **Calendar and email** | A `create_agent` supervisor delegates to calendar and email specialist agents. Calendar tools represent availability/event operations; email uses a send-email tool. This module is not mounted as an HTTP route, and the current tool implementations are stubs that return sample results rather than contacting calendar or email services. |
| **Bank** | `agents/bank/graph.py` is empty and defines no graph. The supervisor workflow is a separate module. |

The **Money** and **Supervisor** workflows are separate graphs with similar
transfer steps but different confirmation behavior. The API currently exposes
both under different paths.

## MCP server and client

`main.py` creates the FastMCP server and mounts its HTTP application at `/mcp/`.
The server registers these tools:

- `list_my_notes` — requires the `read` scope.
- `add_note` and `delete_note` — require the `write` scope.
- `add_tool` — requires the `write` scope.
- `subtract_tool` — currently has no explicit scope check in its handler.

`CustomTokenVerifier` validates the bearer token through the application's JWT
decoder and exposes the token claims and scopes to FastMCP. The chat API passes
the request's access token to `MCPClient`; the client uses `MCP_SERVER_URL` and
`MCPAdapter` to discover MCP tool definitions. The chat graph binds those tools
to the model, and `ToolNode` executes requested tool calls. The MCP server
checks tool scopes for the handlers that call `verify_permissions`.

For local development, the endpoint is normally
`http://127.0.0.1:8000/mcp/`. The chat agent obtains its token from the
authenticated API request. When using `MCPClient` separately, pass a valid
access token to its constructor.

The JWT code currently assigns `read` to non-admin users and `read` plus
`write` to admin users. Confirm the role assigned by your database and do not
assume a newly registered account can call write tools.

## Security and deployment

### Protections present in the code

- Passwords are hashed with `scrypt`; password hash comparisons use
  `hmac.compare_digest`.
- Login issues an HS256 access token with a 60-minute expiry.
- Most agent endpoints require a decoded bearer token.
- MCP uses a token verifier and selected tool handlers check read/write scopes.
- Several user and chat database operations use parameterized SQL.

These controls are a starting point, not a production security review. The
current application has gaps that must be addressed before public deployment:

- **CORS is open:** `main.py` allows every origin, method, and header while also
  allowing credentials. Restrict origins and methods to the deployed clients.
- **TLS is not configured here:** use HTTPS for public API and MCP traffic and
  secure PostgreSQL connections. Do not send bearer tokens over plain HTTP
  outside local development.
- **A separate LangGraph auth hook is a placeholder:** `auth/langgraph.py`
  accepts any non-empty API key, returns example integration fields, and logs
  the authorization header. Replace it with real secret-store validation and
  remove credential logging before using the `langgraph.json` auth configuration.
- **Tokens are logged:** the chat agent prints its MCP token. Remove this and
  review application logs for previously exposed credentials.
- **MCP authorization and data ownership need work:** `subtract_tool` has no
  explicit scope check; note listing is not filtered by caller; note creation
  uses a fixed user ID. Bind records to the authenticated identity and enforce
  authorization for every operation.
- **Chat ownership is incomplete:** `GET /chat/{id}` requires authentication
  but fetches by chat ID without checking that the record belongs to the caller.
- **JWT lifecycle is limited:** login returns an access token; refresh, logout,
  revocation, and token rotation are not implemented. Do not treat the
  `refresh_token` response field as a working refresh flow.
- **Review tool-side effects:** model-selected MCP tools can write or delete
  notes. Add explicit approval and auditing for sensitive operations. The
  transfer workflow returns a URL containing configured values; treat the
  generated URL as sensitive.
- **External data handling:** travel queries are sent to AviationStack and
  Tavily; review their data handling policies before sending user data.
- **Production hardening:** add rate limiting, request-size limits, security
  headers, structured redacted logs, least-privilege database credentials,
  monitoring, and a tested schema migration process.

Never commit `.env`, signing keys, service API keys, database credentials, or
bearer tokens. Rotate any credential that has been logged or exposed.

## Known wiring and integration gaps

- `agents/travel/api.py` registers `POST /money-agent`, the same path used by
  the money API. Since `main.py` registers the money API first, the travel
  endpoint is not available as a distinct route. Give travel its own path
  before relying on it through HTTP.
- The orchestrator classifier maps one label to `blling`, but the route checks
  for `billing`; billing classification may fall through to the general
  handler. Review the label mapping and route condition.
- The calendar/email agent is not registered by `main.py`, and its current
  tools are stubs.
- The bank graph is empty, and `agents/bank/api.py` is not registered by
  `main.py`.
- The MCP note database methods and application SQL schemas should be validated
  against a real test database before enabling note tools.
