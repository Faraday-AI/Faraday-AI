from fastapi import Request, HTTPException, status
from datetime import timedelta

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
RATE_LIMIT_REQUESTS = 100  # Maximum requests per window

async def add_rate_limiting(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Get current request count
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
    else:
        current = int(current)
        if current >= RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        redis_client.incr(key)
    
    response = await call_next(request)
    return response 