# Microsoft Integration - Production Readiness Guide

## Overview

This document outlines the production-ready features implemented for Microsoft Authentication and Calendar Integration.

## Security Features

### 1. Token Encryption

**Implementation:** `app/services/integration/token_encryption.py`

- All OAuth tokens (access_token, refresh_token, id_token) are encrypted before storing in database
- Uses Fernet symmetric encryption (AES-128 in CBC mode)
- Encryption key can be provided via `TOKEN_ENCRYPTION_KEY` environment variable
- Falls back to deriving key from `JWT_SECRET_KEY` or `SECRET_KEY` if encryption key not provided
- Tokens are automatically decrypted when retrieved from database

**Environment Variable:**
```bash
TOKEN_ENCRYPTION_KEY=<base64-encoded-44-byte-key>
```

**To generate a key:**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Use this as TOKEN_ENCRYPTION_KEY
```

### 2. Rate Limiting

**Implementation:** `app/core/rate_limit.py`

Rate limiting is available for all Microsoft endpoints. Recommended limits:

- **OAuth Initiation:** 10 requests per minute per user
- **OAuth Callback:** 20 requests per hour per IP
- **Calendar Endpoints:** 100 requests per minute per user

### 3. Input Validation

All endpoints use Pydantic models for request validation:
- Email format validation
- Date/time format validation
- Required field validation
- Type checking

### 4. Error Handling

- Comprehensive try-catch blocks
- Detailed error logging
- User-friendly error messages
- Proper HTTP status codes
- No sensitive information in error responses

## Database Security

### Token Storage

- Tokens stored in separate tables: `microsoft_oauth_tokens` and `beta_microsoft_oauth_tokens`
- Encrypted at rest using Fernet encryption
- Unique constraint on user_id/teacher_id prevents duplicate tokens
- Automatic token expiration tracking
- Inactive token marking on refresh failures

### Access Control

- All endpoints require JWT authentication
- User data isolation (users can only access their own tokens)
- Beta system uses separate token table for additional isolation

## Monitoring & Logging

### Logging Levels

- **INFO:** Successful operations, token refreshes
- **WARNING:** Token refresh failures, missing tokens
- **ERROR:** Authentication failures, encryption errors, API errors

### Key Metrics to Monitor

1. **Token Refresh Rate:** Monitor how often tokens are refreshed
2. **Authentication Success Rate:** Track successful vs failed authentications
3. **Calendar API Call Latency:** Monitor Microsoft Graph API response times
4. **Token Storage Errors:** Track encryption/decryption failures

## Health Checks

### Microsoft Integration Health

Check if Microsoft Graph service is properly configured:

```bash
GET /api/v1/health/microsoft
```

Response:
```json
{
  "status": "healthy",
  "service": "microsoft_graph",
  "configured": true,
  "last_check": "2024-01-01T00:00:00Z"
}
```

## Best Practices

### 1. Environment Variables

Required environment variables:
```bash
MSCLIENTID=<your-client-id>
MSCLIENTSECRET=<your-client-secret>
MSTENANTID=<your-tenant-id>
REDIRECT_URI=<your-redirect-uri>
TOKEN_ENCRYPTION_KEY=<optional-encryption-key>
```

### 2. Token Management

- Tokens are automatically refreshed when expired (within 5 minutes of expiration)
- Failed refresh attempts mark tokens as inactive
- Users must re-authenticate if refresh fails

### 3. Error Recovery

- Network errors are retried automatically (via requests library)
- Invalid tokens trigger re-authentication flow
- Database errors are logged and return appropriate HTTP status codes

### 4. Performance

- Token encryption/decryption is fast (< 1ms per operation)
- Database queries are optimized with indexes
- Microsoft Graph API calls are made synchronously (consider async for high-volume)

## Testing

### Test Coverage

Comprehensive test suite in `tests/integration/test_microsoft_integration.py`:

- OAuth flow testing (with mocked Microsoft responses)
- Token storage and retrieval
- Token refresh logic
- Calendar endpoint functionality
- Error handling scenarios

### Running Tests

```bash
# Run all Microsoft integration tests
pytest tests/integration/test_microsoft_integration.py -v

# Run with coverage
pytest tests/integration/test_microsoft_integration.py --cov=app.api.v1.endpoints.microsoft_auth --cov=app.api.v1.endpoints.microsoft_calendar -v
```

## Deployment Checklist

- [ ] Set `TOKEN_ENCRYPTION_KEY` environment variable
- [ ] Verify Microsoft credentials are set correctly
- [ ] Test OAuth flow in staging environment
- [ ] Monitor token refresh rates
- [ ] Set up alerts for authentication failures
- [ ] Configure rate limiting appropriately
- [ ] Review and test error handling
- [ ] Verify database indexes are created
- [ ] Test token encryption/decryption
- [ ] Review security logs

## Troubleshooting

### Common Issues

1. **Token Encryption Errors**
   - Verify `TOKEN_ENCRYPTION_KEY` is set correctly
   - Check that key is 44 bytes when base64 decoded
   - Review logs for encryption initialization errors

2. **Token Refresh Failures**
   - Check Microsoft Graph API status
   - Verify refresh token is valid
   - Review Microsoft tenant configuration

3. **Calendar API Errors**
   - Verify user has granted calendar permissions
   - Check token expiration
   - Review Microsoft Graph API rate limits

## Security Considerations

1. **Token Storage:** Tokens are encrypted at rest, but consider additional security measures:
   - Use database-level encryption
   - Implement token rotation policies
   - Consider using Azure Key Vault for key management

2. **Network Security:**
   - Use HTTPS for all API calls
   - Verify SSL certificates
   - Implement certificate pinning for Microsoft Graph API

3. **Access Control:**
   - Regularly audit token access
   - Implement token revocation
   - Monitor for suspicious activity

## Future Enhancements

1. **Async Support:** Convert Microsoft Graph API calls to async for better performance
2. **Token Rotation:** Implement automatic token rotation
3. **Audit Logging:** Add detailed audit logs for token access
4. **Multi-tenant Support:** Support multiple Microsoft tenants
5. **Webhook Support:** Add webhooks for calendar event changes

