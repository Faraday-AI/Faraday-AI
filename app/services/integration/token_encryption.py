"""
Token Encryption Service for Microsoft OAuth Tokens

Provides secure encryption/decryption of OAuth tokens before storing in database.
Uses Fernet symmetric encryption with key from environment variables.
"""

import os
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class TokenEncryptionService:
    """Service for encrypting and decrypting OAuth tokens."""
    
    _instance = None
    _fernet = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Fernet cipher with encryption key."""
        try:
            # Get encryption key from environment or generate from SECRET_KEY
            encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY")
            
            if not encryption_key:
                # Fallback: derive key from SECRET_KEY if available
                secret_key = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
                if secret_key:
                    # Derive a stable key from SECRET_KEY using PBKDF2
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=b'faraday_token_encryption_salt',  # Fixed salt for consistency
                        iterations=100000,
                        backend=default_backend()
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
                    self._fernet = Fernet(key)
                    logger.info("Token encryption initialized using derived key from SECRET_KEY")
                else:
                    logger.warning("No encryption key available - tokens will be stored in plain text")
                    self._fernet = None
            else:
                # Use provided encryption key
                if len(encryption_key) != 44:  # Fernet keys are 44 bytes when base64 encoded
                    # If not in correct format, try to decode or use as-is
                    try:
                        key = encryption_key.encode() if isinstance(encryption_key, str) else encryption_key
                        self._fernet = Fernet(key)
                    except Exception as e:
                        logger.error(f"Invalid encryption key format: {str(e)}")
                        self._fernet = None
                else:
                    self._fernet = Fernet(encryption_key.encode())
                    logger.info("Token encryption initialized using TOKEN_ENCRYPTION_KEY")
        except Exception as e:
            logger.error(f"Failed to initialize token encryption: {str(e)}")
            self._fernet = None
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a token string.
        
        Args:
            plaintext: The token to encrypt
            
        Returns:
            Encrypted token as base64 string, or original if encryption unavailable
        """
        if not plaintext:
            return plaintext
        
        if not self._fernet:
            logger.warning("Encryption not available - storing token in plain text")
            return plaintext
        
        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt token: {str(e)}")
            # In production, we should fail rather than store plain text
            # For now, return original to prevent breaking existing functionality
            raise ValueError(f"Token encryption failed: {str(e)}")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted token string.
        
        Args:
            ciphertext: The encrypted token
            
        Returns:
            Decrypted token, or original if decryption unavailable
        """
        if not ciphertext:
            return ciphertext
        
        if not self._fernet:
            # If encryption wasn't available, assume plain text
            return ciphertext
        
        try:
            decrypted = self._fernet.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt token: {str(e)}")
            # Try to return as plain text if decryption fails (for backward compatibility)
            # In production, this should raise an error
            return ciphertext


# Singleton instance
_token_encryption_service = None

def get_token_encryption_service() -> TokenEncryptionService:
    """Get the token encryption service instance."""
    global _token_encryption_service
    if _token_encryption_service is None:
        _token_encryption_service = TokenEncryptionService()
    return _token_encryption_service

