from fastmcp.server.auth import AccessToken, TokenVerifier
from fastapi import HTTPException
from auth.jwt import decode_access_token

class CustomTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            user_data = await decode_access_token(token)
        except HTTPException as error:
            if error.status_code != 401:
                raise
            return None

        subject = user_data.get("sub")
        if not subject:
            return None

        # scopes = ["read", "write"] if user_data.get("role") == "admin" else ["read"]
        return AccessToken(
            token=token,
            client_id=str(user_data.get("user_id") or subject),
            scopes=user_data.get("scopes", ["read"]),
            expires_at=user_data.get("exp"),
            subject=subject,
            claims=user_data,
        )