# Microsoft Integration - Deployment Guide

## Quick Start

### 1. Environment Variables

Add to your `.env` or environment configuration:

```bash
# Microsoft OAuth Credentials (Required)
MSCLIENTID=your-microsoft-client-id
MSCLIENTSECRET=your-microsoft-client-secret
MSTENANTID=your-microsoft-tenant-id
REDIRECT_URI=https://faraday-ai.onrender.com/api/v1/auth/microsoft/callback

# Token Encryption (Recommended)
TOKEN_ENCRYPTION_KEY=<generate-using-python-code-below>
```

### 2. Generate Encryption Key

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Use this as TOKEN_ENCRYPTION_KEY
```

### 3. Database Migration

Run the migration to create token tables:

```bash
# If using Alembic
alembic upgrade head

# Or manually run the SQL from alembic/versions/001_add_microsoft_oauth_tokens.py
```

### 4. Verify Installation

Check health endpoint:

```bash
curl http://localhost:8000/api/v1/health/microsoft/
```

## Production Checklist

### Security
- [x] Token encryption enabled
- [x] Rate limiting configured
- [x] Input validation implemented
- [x] Error handling comprehensive
- [ ] SSL/TLS certificates configured
- [ ] Security headers configured
- [ ] CORS properly configured

### Database
- [ ] Migration run successfully
- [ ] Indexes created
- [ ] Foreign keys configured
- [ ] Backup strategy in place

### Monitoring
- [ ] Health checks configured
- [ ] Logging configured
- [ ] Metrics collection set up
- [ ] Alerts configured

### Testing
- [ ] Integration tests passing
- [ ] OAuth flow tested
- [ ] Calendar endpoints tested
- [ ] Error scenarios tested

## API Endpoints

### Authentication

#### Main System
- `GET /api/v1/auth/microsoft/` - Initiate OAuth login
- `GET /api/v1/auth/microsoft/callback` - OAuth callback
- `GET /api/v1/auth/microsoft/user` - Get user info

#### Beta System
- `GET /api/v1/beta/auth/microsoft/` - Initiate OAuth login
- `GET /api/v1/beta/auth/microsoft/callback` - OAuth callback
- `GET /api/v1/beta/auth/microsoft/user` - Get user info

### Calendar

#### Main System
- `GET /api/v1/integration/microsoft/calendar/` - Get calendar info
- `GET /api/v1/integration/microsoft/calendar/events` - Get events
- `POST /api/v1/integration/microsoft/calendar/events` - Create event
- `PUT /api/v1/integration/microsoft/calendar/events/{event_id}` - Update event
- `DELETE /api/v1/integration/microsoft/calendar/events/{event_id}` - Delete event

#### Beta System
- `GET /api/v1/beta/integration/microsoft/calendar/` - Get calendar info
- `GET /api/v1/beta/integration/microsoft/calendar/events` - Get events
- `POST /api/v1/beta/integration/microsoft/calendar/events` - Create event
- `PUT /api/v1/beta/integration/microsoft/calendar/events/{event_id}` - Update event
- `DELETE /api/v1/beta/integration/microsoft/calendar/events/{event_id}` - Delete event

### Health & Monitoring
- `GET /api/v1/health/microsoft/` - Health check
- `GET /api/v1/health/microsoft/tokens` - Token statistics

## Rate Limits

| Endpoint | Limit | Period |
|----------|-------|--------|
| OAuth Initiate | 10 requests | 1 minute |
| OAuth Callback | 20 requests | 1 hour |
| User Info | 100 requests | 1 minute |
| Calendar Info | 100 requests | 1 minute |
| Calendar Events | 200 requests | 1 minute |
| Create Event | 50 requests | 1 minute |
| Update Event | 50 requests | 1 minute |
| Delete Event | 50 requests | 1 minute |

## Troubleshooting

### Common Issues

1. **"Microsoft Graph service not configured"**
   - Verify environment variables are set
   - Check credentials are correct
   - Verify REDIRECT_URI matches Azure AD configuration

2. **"Token encryption failed"**
   - Verify TOKEN_ENCRYPTION_KEY is set
   - Check key format (should be 44 bytes base64)
   - Review logs for encryption errors

3. **"Rate limit exceeded"**
   - Check rate limit configuration
   - Review request patterns
   - Consider increasing limits if needed

4. **"Failed to refresh token"**
   - Check Microsoft Graph API status
   - Verify refresh token is valid
   - Review token expiration times

## Support

For issues or questions:
1. Check health endpoint: `/api/v1/health/microsoft/`
2. Review logs for error details
3. Check token statistics: `/api/v1/health/microsoft/tokens`
4. Verify Microsoft Graph API status

