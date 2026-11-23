from langgraph_sdk.auth import is_studio_user, Auth
auth = Auth()
print("Auth initialized")
def is_valid_key(api_key: str) -> bool:
    is_valid = True # your API key validation logic
    return is_valid

@auth.authenticate # (1)!
async def authenticate(headers: dict) -> Auth.types.MinimalUserDict:
    token = headers.get(b"authorization")
    print(f"Token: {token}")
    api_key = headers.get(b"x-api-key")
    if not api_key or not is_valid_key(api_key):
        raise Auth.exceptions.HTTPException(status_code=401, detail="Invalid API key")

    # Fetch user-specific tokens from your secret store
    # user_tokens = await fetch_user_tokens(api_key)

    return { 
        "identity": api_key,  #  fetch user ID from LangSmith
        "github_token" : "github_token",
        "jira_token" : "jira_token",
        # ... custom fields/secrets here
    }

@auth.on
async def add_owner(
    ctx: Auth.types.AuthContext,
    value: dict  # The payload being sent to this access method
) -> dict:  # Returns a filter dict that restricts access to resources
    if is_studio_user(ctx.user):
        print("Studio user")
        return {}

    filters = {"owner": ctx.user.identity}
    metadata = value.setdefault("metadata", {})
    metadata.update(filters)
    return filters