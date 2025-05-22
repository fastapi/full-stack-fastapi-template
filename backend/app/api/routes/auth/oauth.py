from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.db import get_db
from app.models import User
from app.schemas.auth import OAuthProvider, OAuthTokenRequest, SSOProvider, SSORequest

router = APIRouter(prefix="/oauth")

# OAuth providers configuration
OAUTH_PROVIDERS = {
    OAuthProvider.GOOGLE: {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    OAuthProvider.MICROSOFT: {
        "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/oidc/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
}

def get_oauth_redirect_url(provider: OAuthProvider) -> str:
    """Generate OAuth redirect URL for the given provider."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )
    
    provider_config = OAUTH_PROVIDERS[provider]
    redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/oauth/{provider}/callback"
    
    # TODO: Generate state parameter for CSRF protection
    state = ""
    
    # Build authorization URL
    from urllib.parse import urlencode
    params = {
        "client_id": getattr(settings, f"{provider.upper()}_CLIENT_ID"),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(provider_config["scopes"]),
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    return f"{provider_config['authorization_url']}?{urlencode(params)}"

@router.get("/{provider}")
async def oauth_login(
    provider: OAuthProvider,
    redirect_uri: str,
):
    """
    Initiate OAuth login flow.
    """
    # Store redirect_uri in session or state parameter
    # For now, we'll pass it as a query parameter to the OAuth provider
    try:
        auth_url = get_oauth_redirect_url(provider)
        return {"authorization_url": f"{auth_url}&redirect_uri={redirect_uri}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initiating OAuth flow",
        ) from e

@router.get("/{provider}/callback")
async def oauth_callback(
    provider: OAuthProvider,
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    OAuth callback endpoint.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}",
        )
    
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )
    
    # TODO: Verify state parameter
    
    try:
        # Exchange authorization code for access token
        provider_config = OAUTH_PROVIDERS[provider]
        token_data = await exchange_code_for_token(provider, code, provider_config)
        
        # Get user info from provider
        user_info = await get_user_info(provider, token_data["access_token"], provider_config)
        
        # Find or create user
        user = await get_or_create_user_from_oauth(db, provider, user_info)
        
        # Generate JWT tokens
        tokens = security.generate_token_response(str(user.id))
        
        # TODO: Store refresh token in database
        
        # Redirect to frontend with tokens
        # In production, use secure, http-only cookies
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error during OAuth callback: {str(e)}",
        )

async def exchange_code_for_token(provider: OAuthProvider, code: str, provider_config: Dict) -> Dict:
    """Exchange authorization code for access token."""
    # TODO: Implement token exchange
    # This will make a POST request to the provider's token endpoint
    # with the authorization code and client credentials
    return {}

async def get_user_info(provider: OAuthProvider, access_token: str, provider_config: Dict) -> Dict:
    """Get user info from OAuth provider."""
    # TODO: Implement user info retrieval
    # This will make a GET request to the provider's userinfo endpoint
    # with the access token
    return {}

async def get_or_create_user_from_oauth(db: Session, provider: OAuthProvider, user_info: Dict) -> User:
    """Find or create a user from OAuth user info."""
    # TODO: Implement user lookup/creation
    # This will find an existing user by email or create a new one
    # and update the SSO provider information
    return User()  # Placeholder

# SSO Endpoints
@router.post("/sso/{provider}")
async def sso_login(
    provider: SSOProvider,
    sso_request: SSORequest,
):
    """
    Initiate SSO login flow for SAML or OIDC.
    """
    if provider == SSOProvider.SAML:
        # TODO: Implement SAML SSO
        pass
    elif provider == SSOProvider.OIDC:
        # TODO: Implement OIDC SSO
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported SSO provider: {provider}",
        )
    
    return {"message": "SSO flow initiated"}
