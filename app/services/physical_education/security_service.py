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
from app.services.physical_education import service_integration
from app.models.movement_analysis import MovementAnalysis, MovementPattern

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityService:
    """Comprehensive security service for physical education system."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SecurityService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = None
        self.redis_client = None
        self.student_manager = None
        self.activity_manager = None
        self.assessment_system = None
        
        # Security settings
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
        
        # Security monitoring
        self.security_events = []
        self.access_violations = []
        self.rate_limit_violations = []
        self.threat_assessments = {}
        self.security_metrics = {}

    async def initialize(self):
        """Initialize security service components."""
        try:
            self.db = next(get_db())
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                ssl=settings.REDIS_SSL
            )
            self.student_manager = service_integration.get_service("student_manager")
            self.activity_manager = service_integration.get_service("activity_manager")
            self.assessment_system = service_integration.get_service("assessment_system")
            
            # Initialize security components
            await self._load_blocked_ips()
            asyncio.create_task(self._cleanup_expired_blocks())
            asyncio.create_task(self._monitor_threats())
            
            self.logger.info("Security Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Security Service: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup security service resources."""
        try:
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            # Clear all data
            self.blocked_ips.clear()
            self.suspicious_requests.clear()
            self.rate_limits.clear()
            self.security_events.clear()
            self.access_violations.clear()
            self.rate_limit_violations.clear()
            self.threat_assessments.clear()
            self.security_metrics.clear()
            
            # Reset service references
            self.db = None
            self.redis_client = None
            self.student_manager = None
            self.activity_manager = None
            self.assessment_system = None
            
            self.logger.info("Security Service cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Security Service: {str(e)}")
            raise

    # IP Security Methods
    async def _load_blocked_ips(self):
        """Load blocked IPs from Redis."""
        try:
            if self.redis_client:
                blocked = await self.redis_client.smembers("blocked_ips")
                self.blocked_ips = {ip.decode() if isinstance(ip, bytes) else ip for ip in blocked}
        except redis.RedisError as e:
            self.logger.error(f"Error loading blocked IPs from Redis: {str(e)}")
            raise

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
            except redis.RedisError as e:
                self.logger.error(f"Redis error in cleanup_expired_blocks: {str(e)}")
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"Error in cleanup_expired_blocks: {str(e)}")
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
        try:
            key = f"{ip}:{category}"
            if key not in self.rate_limits:
                self.rate_limits[key] = []
            
            current_time = datetime.utcnow()
            self.rate_limits[key] = [t for t in self.rate_limits[key] 
                                   if current_time - t < timedelta(minutes=1)]
            
            if len(self.rate_limits[key]) >= 100:  # 100 requests per minute
                await self.log_security_event(
                    "rate_limit_exceeded",
                    "system",
                    {"ip": ip, "path": path, "category": category}
                )
                return False
            
            self.rate_limits[key].append(current_time)
            return True
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return False

    async def block_ip(self, ip: str, reason: str):
        """Block an IP address."""
        try:
            self.blocked_ips.add(ip)
            if self.redis_client:
                await self.redis_client.sadd("blocked_ips", ip)
                expiry = datetime.utcnow() + timedelta(hours=24)
                await self.redis_client.hset("block_expiry", ip, expiry.isoformat())
                await self.log_security_event(
                    "ip_blocked",
                    "system",
                    {"ip": ip, "reason": reason}
                )
        except redis.RedisError as e:
            self.logger.error(f"Redis error blocking IP {ip}: {str(e)}")
            raise

    async def unblock_ip(self, ip: str):
        """Unblock an IP address."""
        try:
            self.blocked_ips.discard(ip)
            if self.redis_client:
                await self.redis_client.srem("blocked_ips", ip)
                await self.redis_client.hdel("block_expiry", ip)
                await self.log_security_event(
                    "ip_unblocked",
                    "system",
                    {"ip": ip}
                )
        except redis.RedisError as e:
            self.logger.error(f"Redis error unblocking IP {ip}: {str(e)}")
            raise

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
        """Validate request data against expected fields and types."""
        try:
            if not isinstance(request_data, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Request data must be a dictionary"
                )
            
            # Check for required fields
            missing_fields = [field for field in expected_fields if field not in request_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {', '.join(missing_fields)}"
                )
            
            # Sanitize input data
            sanitized_data = {}
            for field, value in request_data.items():
                sanitized_data[field] = await self.sanitize_input(value, field, db)
            
            return sanitized_data
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Error validating request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error validating request data"
            )

    async def sanitize_input(
        self,
        input_data: Any,
        input_type: str,
        db: Session = Depends(get_db)
    ) -> Any:
        """Sanitize input data based on type."""
        try:
            if input_data is None:
                return None
                
            if isinstance(input_data, str):
                # Remove any potentially dangerous characters
                sanitized = re.sub(r'[<>{}[\]\\]', '', input_data)
                # Trim whitespace
                sanitized = sanitized.strip()
                return sanitized
                
            elif isinstance(input_data, (int, float)):
                return input_data
                
            elif isinstance(input_data, list):
                return [await self.sanitize_input(item, input_type, db) for item in input_data]
                
            elif isinstance(input_data, dict):
                return {
                    k: await self.sanitize_input(v, input_type, db)
                    for k, v in input_data.items()
                }
                
            return input_data
        except Exception as e:
            self.logger.error(f"Error sanitizing input: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input data for field {input_type}"
            )

    # Metrics and Monitoring
    async def get_security_metrics(self) -> Dict:
        """Get security metrics and statistics."""
        try:
            metrics = {
                "suspicious_requests": await self._get_suspicious_request_count(),
                "rate_limit_violations": await self._get_rate_limit_violations(),
                "malicious_user_agents": await self._get_malicious_user_agent_count(),
                "malicious_ip_ranges": await self._get_malicious_ip_range_count(),
                "request_size_violations": await self._get_request_size_violations(),
                "blocked_ips": len(self.blocked_ips),
                "active_threats": len(self.threat_assessments),
                "security_events": len(self.security_events)
            }
            
            if self.redis_client:
                try:
                    metrics["redis_connected"] = await self.redis_client.ping()
                except redis.RedisError:
                    metrics["redis_connected"] = False
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error getting security metrics: {str(e)}")
            return {}

    async def _get_suspicious_request_count(self) -> int:
        """Get count of suspicious requests."""
        try:
            if self.redis_client:
                return int(await self.redis_client.get("suspicious_request_count") or 0)
            return len(self.suspicious_requests)
        except redis.RedisError as e:
            self.logger.error(f"Redis error getting suspicious request count: {str(e)}")
            return len(self.suspicious_requests)

    async def _get_rate_limit_violations(self) -> int:
        """Get count of rate limit violations."""
        try:
            if self.redis_client:
                return int(await self.redis_client.get("rate_limit_violations") or 0)
            return len(self.rate_limit_violations)
        except redis.RedisError as e:
            self.logger.error(f"Redis error getting rate limit violations: {str(e)}")
            return len(self.rate_limit_violations)

    async def _get_malicious_user_agent_count(self) -> int:
        """Get count of malicious user agent detections."""
        try:
            if self.redis_client:
                return int(await self.redis_client.get("malicious_user_agent_count") or 0)
            return len([ua for ua in self.security_events if ua.get("type") == "malicious_user_agent"])
        except redis.RedisError as e:
            self.logger.error(f"Redis error getting malicious user agent count: {str(e)}")
            return 0

    async def _get_malicious_ip_range_count(self) -> int:
        """Get count of malicious IP range detections."""
        try:
            if self.redis_client:
                return int(await self.redis_client.get("malicious_ip_range_count") or 0)
            return len([ip for ip in self.security_events if ip.get("type") == "malicious_ip_range"])
        except redis.RedisError as e:
            self.logger.error(f"Redis error getting malicious IP range count: {str(e)}")
            return 0

    async def _get_request_size_violations(self) -> int:
        """Get count of request size violations."""
        try:
            if self.redis_client:
                return int(await self.redis_client.get("request_size_violations") or 0)
            return len([req for req in self.security_events if req.get("type") == "request_size_violation"])
        except redis.RedisError as e:
            self.logger.error(f"Redis error getting request size violations: {str(e)}")
            return 0

    def _check_request_size(self, request: Request):
        """Check if request size exceeds limits."""
        try:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request entity too large"
                )
        except ValueError as e:
            self.logger.error(f"Error checking request size: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid content length"
            )

    def _is_malicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is malicious."""
        try:
            if not user_agent:
                return False
            return any(agent.lower() in user_agent.lower() for agent in self.malicious_user_agents)
        except Exception as e:
            self.logger.error(f"Error checking malicious user agent: {str(e)}")
            return False

    def _is_malicious_ip_range(self, ip: str) -> bool:
        """Check if IP is in malicious range."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in network for network in self.malicious_ip_ranges)
        except ValueError as e:
            self.logger.error(f"Error checking malicious IP range: {str(e)}")
            return False 