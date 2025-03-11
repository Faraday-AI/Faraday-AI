from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings, DistrictRole

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_district_email(email: str) -> bool:
    """Verify email belongs to district domain."""
    return any(email.endswith(f"@{domain}") for domain in settings.district_email_domains)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token for district staff."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        if not verify_district_email(email):
            raise HTTPException(status_code=401, detail="Email domain not authorized")
    except JWTError:
        raise credentials_exception
    
    return payload

def verify_role(required_roles: list[DistrictRole]):
    """Decorator to verify user has required role."""
    async def role_checker(user: Dict[str, Any] = Depends(get_current_user)):
        if user.get("role") not in [role.value for role in required_roles]:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to perform this action"
            )
        return user
    return role_checker

# Role-based security dependencies
require_pe_staff = verify_role([DistrictRole.PE_STAFF, DistrictRole.ADMIN])
require_health_staff = verify_role([DistrictRole.HEALTH_STAFF, DistrictRole.ADMIN])
require_admin = verify_role([DistrictRole.ADMIN]) 