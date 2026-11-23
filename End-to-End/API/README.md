# End-to-End API

Environment

1. Create VD: python -m venv .venv
2. Activate VD: . .venv/bin/activate
3. Install from requirements: pip install -r requirements.txt
4. ollama pull llama3
5. ollama serve
6. [Run Ollama with Langchain](https://medium.com/@abonia/ollama-and-langchain-run-llms-locally-900931914a46)

Minimal FastAPI app providing a POST endpoint:

- Endpoint GET/status
- Endpoint: `POST /submit`
- Usage: `uvicorn main:app --reload --port 8000`

Request example:

```json
{ "id": 1, "text": "hello" }
```

Response: echoes the received data under `item`.

## MCP client

The MCP endpoint at `http://localhost:8000/mcp/` requires a bearer token. Get an
access token from `POST /users/login`, then run the client from this directory:

```sh
export MCP_ACCESS_TOKEN="<access_token>"
.venv/bin/python -m mcp_app.mcp_client
```

End-to-End
[GrabDuck](https://www.youtube.com/@GrabDuck/playlists)

[RAG ChromaDB](https://www.youtube.com/watch?v=E4l91XKQSgw)

To Generate RAG
1. Run the command: ollama pull llama3.2
2. Run the command ollama pull mxbai-embed-large
3. 
