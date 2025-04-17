import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple, Any
import redis.asyncio as redis
from fastapi import Request, HTTPException, Depends, status
import ipaddress
import re
from enum import Enum
import json
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityService:
    """Comprehensive security service for physical education system."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        self.access_levels = ["student", "teacher", "admin", "health_staff"]
        self.blocked_ips: Set[str] = set()
        self.suspicious_requests: Dict[str, List[datetime]] = {}
        self.rate_limits: Dict[str, Dict[str, List[datetime]]] = {}
        self.malicious_user_agents = {
            "sqlmap", "nikto", "wpscan", "dirbuster", "gobuster",
            "hydra", "metasploit", "nmap", "burpsuite", "zap"
        }
        self.malicious_ip_ranges = {
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16")
        }

    async def initialize(self):
        """Initialize security service components."""
        if self.redis_client:
            await self._load_blocked_ips()
            asyncio.create_task(self._cleanup_expired_blocks())
            asyncio.create_task(self._monitor_threats())

    async def cleanup(self):
        """Cleanup security service resources."""
        if self.redis_client:
            await self.redis_client.close()

    # IP Security Methods
    async def _load_blocked_ips(self):
        """Load blocked IPs from Redis."""
        if self.redis_client:
            blocked = await self.redis_client.smembers("blocked_ips")
            self.blocked_ips = {ip.decode() if isinstance(ip, bytes) else ip for ip in blocked}

    async def _cleanup_expired_blocks(self):
        """Cleanup expired IP blocks."""
        while True:
            try:
                if self.redis_client:
                    current_time = datetime.utcnow()
                    expired_blocks = await self.redis_client.hgetall("block_expiry")
                    for ip, expiry_str in expired_blocks.items():
                        expiry = datetime.fromisoformat(expiry_str.decode())
                        if current_time > expiry:
                            await self.unblock_ip(ip.decode())
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in cleanup_expired_blocks: {e}")
                await asyncio.sleep(60)

    async def _monitor_threats(self):
        """Monitor and assess threats."""
        while True:
            try:
                for ip in list(self.suspicious_requests.keys()):
                    threat_level = await self._assess_threat_level(ip)
                    if threat_level == ThreatLevel.CRITICAL:
                        await self.block_ip(ip, "Critical threat level detected")
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in monitor_threats: {e}")
                await asyncio.sleep(60)

    async def _assess_threat_level(self, ip: str) -> ThreatLevel:
        """Assess threat level for an IP."""
        requests = self.suspicious_requests.get(ip, [])
        recent_requests = [req for req in requests if datetime.utcnow() - req < timedelta(minutes=5)]
        
        if len(recent_requests) > 100:
            return ThreatLevel.CRITICAL
        elif len(recent_requests) > 50:
            return ThreatLevel.HIGH
        elif len(recent_requests) > 20:
            return ThreatLevel.MEDIUM
        return ThreatLevel.LOW

    async def check_request(self, request: Request) -> bool:
        """Check if a request is allowed."""
        client_ip = request.client.host
        if await self.is_ip_blocked(client_ip):
            return False
        
        await self._check_request_size(request)
        if self._is_malicious_user_agent(request.headers.get("user-agent", "")):
            await self.track_suspicious_request(client_ip, request.url.path, ThreatLevel.HIGH)
            return False
        
        if self._is_malicious_ip_range(client_ip):
            await self.track_suspicious_request(client_ip, request.url.path, ThreatLevel.MEDIUM)
        
        return True

    def _check_threat_level(self, path: str) -> ThreatLevel:
        """Determine threat level for a path."""
        sensitive_paths = {
            "/api/admin": ThreatLevel.HIGH,
            "/api/students": ThreatLevel.MEDIUM,
            "/api/teachers": ThreatLevel.MEDIUM
        }
        return sensitive_paths.get(path, ThreatLevel.LOW)

    async def track_suspicious_request(self, ip: str, path: str, threat_level: ThreatLevel):
        """Track suspicious requests."""
        if ip not in self.suspicious_requests:
            self.suspicious_requests[ip] = []
        self.suspicious_requests[ip].append(datetime.utcnow())
        
        if self.redis_client:
            await self.redis_client.hincrby("suspicious_requests", ip, 1)

    async def check_rate_limit(self, ip: str, path: str, category: str = 'default') -> bool:
        """Check rate limiting for requests."""
        key = f"{ip}:{category}"
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        current_time = datetime.utcnow()
        self.rate_limits[key] = [t for t in self.rate_limits[key] 
                               if current_time - t < timedelta(minutes=1)]
        
        if len(self.rate_limits[key]) >= 100:  # 100 requests per minute
            return False
        
        self.rate_limits[key].append(current_time)
        return True

    async def block_ip(self, ip: str, reason: str):
        """Block an IP address."""
        self.blocked_ips.add(ip)
        if self.redis_client:
            await self.redis_client.sadd("blocked_ips", ip)
            expiry = datetime.utcnow() + timedelta(hours=24)
            await self.redis_client.hset("block_expiry", ip, expiry.isoformat())

    async def unblock_ip(self, ip: str):
        """Unblock an IP address."""
        self.blocked_ips.discard(ip)
        if self.redis_client:
            await self.redis_client.srem("blocked_ips", ip)
            await self.redis_client.hdel("block_expiry", ip)

    async def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        return ip in self.blocked_ips

    async def get_blocked_ips(self) -> List[Dict[str, str]]:
        """Get list of blocked IPs with reasons."""
        if self.redis_client:
            blocked = await self.redis_client.smembers("blocked_ips")
            return [{"ip": ip.decode(), "reason": "Blocked by security system"} 
                   for ip in blocked]
        return []

    # User Access Control Methods
    async def validate_access(
        self,
        user_id: str,
        required_level: str,
        db: Session = Depends(get_db)
    ) -> bool:
        """Validate user access level."""
        if required_level not in self.access_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid access level: {required_level}"
            )
        
        # TODO: Implement actual user level check from database
        return True

    async def log_security_event(
        self,
        event_type: str,
        user_id: str,
        details: Dict[str, Any],
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Log a security event."""
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        # TODO: Implement actual logging to database
        return event

    async def validate_request(
        self,
        request_data: Dict[str, Any],
        expected_fields: list,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Validate request data."""
        missing_fields = [field for field in expected_fields 
                         if field not in request_data]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        return request_data

    async def sanitize_input(
        self,
        input_data: Any,
        input_type: str,
        db: Session = Depends(get_db)
    ) -> Any:
        """Sanitize input data."""
        if isinstance(input_data, str):
            # Remove potentially harmful characters
            input_data = re.sub(r'[<>"\']', '', input_data)
        
        return input_data

    # Metrics and Monitoring
    async def get_security_metrics(self) -> Dict:
        """Get security metrics."""
        return {
            "suspicious_requests": await self._get_suspicious_request_count(),
            "rate_limit_violations": await self._get_rate_limit_violations(),
            "malicious_user_agents": await self._get_malicious_user_agent_count(),
            "malicious_ip_ranges": await self._get_malicious_ip_range_count(),
            "request_size_violations": await self._get_request_size_violations()
        }

    async def _get_suspicious_request_count(self) -> int:
        """Get count of suspicious requests."""
        if self.redis_client:
            return await self.redis_client.hlen("suspicious_requests")
        return len(self.suspicious_requests)

    async def _get_rate_limit_violations(self) -> int:
        """Get count of rate limit violations."""
        count = 0
        for requests in self.rate_limits.values():
            if len(requests) >= 100:
                count += 1
        return count

    async def _get_malicious_user_agent_count(self) -> int:
        """Get count of malicious user agents."""
        return len(self.malicious_user_agents)

    async def _get_malicious_ip_range_count(self) -> int:
        """Get count of malicious IP ranges."""
        return len(self.malicious_ip_ranges)

    async def _get_request_size_violations(self) -> int:
        """Get count of request size violations."""
        return 0  # TODO: Implement actual tracking

    def _check_request_size(self, request: Request):
        """Check request size limits."""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request entity too large"
            )

    def _is_malicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is malicious."""
        return any(agent in user_agent.lower() for agent in self.malicious_user_agents)

    def _is_malicious_ip_range(self, ip: str) -> bool:
        """Check if IP is in malicious range."""
        try:
            ip_addr = ipaddress.ip_address(ip)
            return any(ip_addr in network for network in self.malicious_ip_ranges)
        except ValueError:
            return False 