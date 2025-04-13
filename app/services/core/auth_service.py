from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User
import logging
from openai import OpenAI
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.db = next(get_db())

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = db.query(User).filter(User.email == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a new access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def verify_chatgpt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify the ChatGPT authentication token."""
        try:
            # This would be replaced with actual ChatGPT token verification
            # For now, we're just decoding the JWT
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return None

    async def get_or_create_user(self, email: str, name: str) -> User:
        """Get existing user or create new one in database."""
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                user = User(
                    email=email,
                    name=name,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"Created new user: {email}")
            
            return user
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            self.db.rollback()
            raise

    async def create_session(self, user: User) -> Dict[str, Any]:
        """Create a new session for the user."""
        try:
            # Create session token
            session_data = {
                "sub": str(user.id),
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(days=1)
            }
            session_token = jwt.encode(
                session_data,
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )

            # Update user's last login
            user.last_login = datetime.utcnow()
            self.db.commit()

            return {
                "access_token": session_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name
                }
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            self.db.rollback()
            raise

    async def verify_session(self, token: str) -> Optional[User]:
        """Verify a session token and return the user."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = self.db.query(User).filter(User.id == user_id).first()
                return user
            return None
        except jwt.JWTError as e:
            logger.error(f"Session verification failed: {str(e)}")
            return None

    async def handle_chatgpt_login(self, chatgpt_token: str) -> Dict[str, Any]:
        """Handle login through ChatGPT and create/update local session."""
        try:
            # Verify ChatGPT token
            chatgpt_data = await self.verify_chatgpt_token(chatgpt_token)
            if not chatgpt_data:
                raise ValueError("Invalid ChatGPT token")

            # Get or create user
            user = await self.get_or_create_user(
                email=chatgpt_data["email"],
                name=chatgpt_data.get("name", "")
            )

            # Create session
            session = await self.create_session(user)
            
            logger.info(f"Successful login for user: {user.email}")
            return session
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise

    async def logout(self, user: User) -> bool:
        """Handle user logout."""
        try:
            # Update last logout time
            user.last_logout = datetime.utcnow()
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Logout error: {str(e)}")
            self.db.rollback()
            return False 