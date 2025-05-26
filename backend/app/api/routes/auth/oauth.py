from typing import Any, Dict, Optional
import secrets
import json
from datetime import datetime, timedelta, timezone
import base64
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import AnyHttpUrl
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.logging import logger
from app.db import get_db
from app.models import User, OAuthState, OAuthStateCreate
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

def generate_oauth_state(db: Session, provider: str, redirect_uri: str) -> str:
    """
    Generate a secure random state token for CSRF protection and store it in the database.
    
    Args:
        db: Database session
        provider: OAuth provider name
        redirect_uri: The URI to redirect to after authentication
        
    Returns:
        str: A secure random state token
    """
    # Generate a secure random token
    state_token = secrets.token_urlsafe(32)
    
    # Create state record with expiration (10 minutes)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    oauth_state = OAuthState(
        state_token=state_token,
        provider=provider,
        redirect_uri=redirect_uri,
        expires_at=expires_at,
        used=False
    )
    
    db.add(oauth_state)
    db.commit()
    
    # Clean up expired states
    clean_expired_states(db)
    
    return state_token

def verify_oauth_state(db: Session, state_token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an OAuth state token and return its data.
    
    Args:
        db: Database session
        state_token: The state token to verify
        
    Returns:
        Optional[Dict]: The state data if valid, None otherwise
    """
    # Query for the state
    statement = select(OAuthState).where(
        OAuthState.state_token == state_token,
        OAuthState.used == False
    )
    state = db.exec(statement).first()
    
    if not state:
        return None
    
    # Check if state has expired
    if datetime.now(timezone.utc) > state.expires_at:
        # Delete expired state
        db.delete(state)
        db.commit()
        return None
    
    # Mark state as used (one-time use)
    state.used = True
    db.add(state)
    db.commit()
    
    return {
        "provider": state.provider,
        "redirect_uri": state.redirect_uri,
    }

def clean_expired_states(db: Session):
    """Remove expired OAuth states from database."""
    current_time = datetime.now(timezone.utc)
    
    # Find and delete expired states
    statement = select(OAuthState).where(
        OAuthState.expires_at < current_time
    )
    expired_states = db.exec(statement).all()
    
    for state in expired_states:
        db.delete(state)
    
    db.commit()

def get_oauth_redirect_url(db: Session, provider: OAuthProvider, user_redirect_uri: str) -> str:
    """Generate OAuth redirect URL for the given provider."""
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )
    
    provider_config = OAUTH_PROVIDERS[provider]
    redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/oauth/{provider}/callback"
    
    # Generate state parameter for CSRF protection
    state = generate_oauth_state(db, provider.value, user_redirect_uri)
    
    # Build authorization URL
    from urllib.parse import urlencode
    params = {
        "client_id": getattr(settings, f"{provider.upper()}_CLIENT_ID", ""),
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(provider_config["scopes"]),
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    # Remove empty client_id if not configured
    if not params["client_id"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{provider.upper()}_CLIENT_ID not configured",
        )
    
    return f"{provider_config['authorization_url']}?{urlencode(params)}"

@router.get("/{provider}")
async def oauth_login(
    provider: OAuthProvider,
    redirect_uri: str,
    db: Session = Depends(get_db),
):
    """
    Initiate OAuth login flow.
    
    Args:
        provider: OAuth provider (google, microsoft)
        redirect_uri: Where to redirect after successful authentication
        db: Database session
    """
    try:
        auth_url = get_oauth_redirect_url(db, provider, redirect_uri)
        return {"authorization_url": auth_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error initiating OAuth flow: {str(e)}")
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
    
    This endpoint is called by the OAuth provider after user authentication.
    """
    if error:
        logger.error(f"OAuth error from provider: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}",
        )
    
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}",
        )
    
    # Verify state parameter for CSRF protection
    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state parameter",
        )
    
    state_data = verify_oauth_state(db, state)
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )
    
    # Verify provider matches
    if state_data.get("provider") != provider.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State parameter provider mismatch",
        )
    
    try:
        # Exchange authorization code for access token
        provider_config = OAUTH_PROVIDERS[provider]
        redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/oauth/{provider}/callback"
        
        token_data = await exchange_code_for_token(
            provider, code, redirect_uri, provider_config
        )
        
        # Get user info from provider
        user_info = await get_user_info(
            provider, token_data["access_token"], provider_config
        )
        
        # Find or create user
        user = await get_or_create_user_from_oauth(db, provider, user_info)
        
        # Generate JWT tokens
        tokens = security.generate_token_response(user)
        
        # TODO: Store refresh token in database
        
        # Redirect to frontend with tokens
        # Extract the original redirect URI from state
        original_redirect = state_data.get("redirect_uri", f"{settings.FRONTEND_URL}/auth/callback")
        
        # In production, use secure, http-only cookies
        redirect_url = f"{original_redirect}?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Error during OAuth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error during OAuth callback: {str(e)}",
        )

async def exchange_code_for_token(
    provider: OAuthProvider, 
    code: str, 
    redirect_uri: str,
    provider_config: Dict
) -> Dict:
    """Exchange authorization code for access token."""
    async with httpx.AsyncClient() as client:
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": getattr(settings, f"{provider.upper()}_CLIENT_ID", ""),
            "client_secret": getattr(settings, f"{provider.upper()}_CLIENT_SECRET", ""),
        }
        
        # Make request to token endpoint
        response = await client.post(
            provider_config["token_url"],
            data=token_data,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for token"
            )
        
        return response.json()

async def get_user_info(
    provider: OAuthProvider, 
    access_token: str, 
    provider_config: Dict
) -> Dict:
    """Get user info from OAuth provider."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            provider_config["userinfo_url"],
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to get user info: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from OAuth provider"
            )
        
        return response.json()

async def get_or_create_user_from_oauth(
    db: Session, 
    provider: OAuthProvider, 
    user_info: Dict
) -> User:
    """Find or create a user from OAuth user info."""
    # Extract user information based on provider
    if provider == OAuthProvider.GOOGLE:
        email = user_info.get("email")
        full_name = user_info.get("name")
        sub = user_info.get("sub")
        email_verified = user_info.get("email_verified", False)
    elif provider == OAuthProvider.MICROSOFT:
        email = user_info.get("email") or user_info.get("preferred_username")
        full_name = user_info.get("name")
        sub = user_info.get("sub")
        email_verified = user_info.get("email_verified", False)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by OAuth provider"
        )
    
    # Check if user exists by email or SSO sub
    statement = select(User).where(
        (User.email == email) | 
        ((User.sso_provider == provider.value) & (User.sso_sub == sub))
    )
    user = db.exec(statement).first()
    
    if user:
        # Update user information
        user.sso_provider = provider.value
        user.sso_sub = sub
        user.last_login = datetime.now(timezone.utc)
        if not user.email_verified and email_verified:
            user.email_verified = True
            user.is_verified = True
            user.is_active = True
        
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Create new user
        user = User(
            email=email,
            full_name=full_name,
            sso_provider=provider.value,
            sso_sub=sub,
            email_verified=email_verified,
            is_verified=email_verified,
            is_active=email_verified,  # Auto-activate if email is verified by provider
            last_login=datetime.now(timezone.utc),
            hashed_password=None,  # No password for SSO users
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created new user via OAuth: {email}")
    
    return user

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