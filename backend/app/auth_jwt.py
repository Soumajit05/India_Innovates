"""
JWT-based authentication and authorization.
Replaces simple API key auth with industry-standard JWT tokens.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthenticationCredentials

logger = logging.getLogger(__name__)

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
http_bearer = HTTPBearer()


class Token:
    """JWT token models."""
    
    def __init__(self, access_token: str, token_type: str = "bearer", refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token


class TokenPayload:
    """JWT token payload."""
    
    def __init__(self, sub: str, scopes: list = None, exp: datetime = None, iat: datetime = None):
        self.subject = sub  # User ID
        self.scopes = scopes or []
        self.exp = exp
        self.iat = iat
    
    @property
    def permissions(self):
        """Extract permissions from scopes."""
        scope_map = {
            "read": ["dashboard", "query", "alerts"],
            "write": ["feedback", "scenarios"],
            "admin": ["ingestion", "settings", "users"]
        }
        perms = []
        for scope in self.scopes:
            perms.extend(scope_map.get(scope, []))
        return perms


class JWTAuthenticator:
    """JWT token generation and validation."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        subject: str,
        scopes: list = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            subject: User ID or identifier
            scopes: List of permission scopes (e.g., ["read", "write"])
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        now = datetime.utcnow()
        expire = now + expires_delta
        
        payload = {
            "sub": subject,
            "scopes": scopes or ["read"],
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
        }
        
        encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """Create long-lived refresh token."""
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        now = datetime.utcnow()
        expire = now + expires_delta
        
        payload = {
            "sub": subject,
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
        }
        
        encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenPayload:
        """
        Verify and decode JWT token.
        
        Args:
            token: OAuth2 token string
            
        Returns:
            TokenPayload with decoded claims
            
        Raises:
            HTTPException if token invalid
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            subject: str = payload.get("sub")
            if subject is None:
                raise credentials_exception
            
            scopes = payload.get("scopes", [])
            exp = datetime.fromtimestamp(payload.get("exp"))
            iat = datetime.fromtimestamp(payload.get("iat"))
            
            return TokenPayload(
                sub=subject,
                scopes=scopes,
                exp=exp,
                iat=iat
            )
        except JWTError:
            raise credentials_exception


# ============================================================================
# DEPENDENCY INJECTORS FOR FASTAPI
# ============================================================================

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """FastAPI dependency to extract current user from token."""
    return JWTAuthenticator.verify_token(token)


def require_permission(permission: str):
    """Factory to create permission-checking dependency."""
    async def check_permission(current_user: TokenPayload = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return check_permission


async def api_key_auth(credentials: HTTPAuthenticationCredentials = Depends(http_bearer)) -> Dict:
    """
    Legacy API key authentication (backward compat).
    Accepts simple bearer token as API key.
    """
    valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
    if credentials.credentials not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return {"api_key": credentials.credentials}
