import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
import redis.asyncio as redis
from fastapi import Request, HTTPException
import ipaddress
import re
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityService:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns = {
            # Critical patterns - immediate block after 2 attempts
            'critical': [
                r'\.env$',
                r'\.git/',
                r'config\.',
                r'\.sql$',
                r'backup\.sql$',
                r'db_backup\.sql$',
                r'database\.sql$',
                r'dump\.sql$',
                r'phpinfo\.php$',
                r'admin\.php$',
                r'shell\.php$',
                r'eval\.php$'
            ],
            # High risk patterns - block after 5 attempts
            'high': [
                r'wp-admin',
                r'administrator',
                r'\.htaccess$',
                r'\.ssh/',
                r'id_rsa',
                r'\.DS_Store$',
                r'\.log$',
                r'error\.log$',
                r'debug\.log$',
                r'access\.log$'
            ],
            # Medium risk patterns - block after 10 attempts
            'medium': [
                r'\.php$',
                r'\.aspx$',
                r'\.jsp$',
                r'\.yaml$',
                r'\.json$',
                r'backup',
                r'config',
                r'settings',
                r'setup',
                r'install'
            ],
            # Low risk patterns - monitor only
            'low': [
                r'test',
                r'demo',
                r'sample',
                r'temp',
                r'old',
                r'new'
            ]
        }
        
        # Add malicious user agent patterns
        self.malicious_user_agents = [
            r'curl',
            r'wget',
            r'nmap',
            r'sqlmap',
            r'nikto',
            r'nikto',
            r'gobuster',
            r'dirbuster',
            r'hydra',
            r'burpsuite',
            r'arachni',
            r'zap',
            r'wpscan',
            r'joomscan',
            r'droopescan',
            r'nikto',
            r'nikto',
            r'nikto',
            r'nikto',
            r'nikto'
        ]
        
        # Add known malicious IP ranges (simplified)
        self.malicious_ip_ranges = [
            "1.0.0.0/24",  # Example range
            "2.0.0.0/24",  # Example range
            "3.0.0.0/24"   # Example range
        ]
        
        # Request size limits (in bytes)
        self.request_limits = {
            'headers': 8192,      # 8KB for headers
            'body': 1048576,      # 1MB for body
            'url': 2048,          # 2KB for URL
            'query': 1024         # 1KB for query string
        }
        
        self.rate_limits = {
            'default': {'requests': 100, 'window': 60},  # 100 requests per minute
            'suspicious': {'requests': 10, 'window': 60},  # 10 requests per minute for suspicious patterns
            'critical': {'requests': 2, 'window': 60},    # 2 requests per minute for critical patterns
            'blocked': {'requests': 0, 'window': 60}      # No requests allowed for blocked IPs
        }
        
        self.threat_thresholds = {
            ThreatLevel.CRITICAL: 2,   # Block after 2 attempts
            ThreatLevel.HIGH: 5,       # Block after 5 attempts
            ThreatLevel.MEDIUM: 10,    # Block after 10 attempts
            ThreatLevel.LOW: 50        # Block after 50 attempts
        }
        
        self.cleanup_task = None
        self.monitoring_task = None

    async def initialize(self):
        """Initialize the security service"""
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_blocks())
        self.monitoring_task = asyncio.create_task(self._monitor_threats())
        await self._load_blocked_ips()

    async def cleanup(self):
        """Cleanup resources"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

    async def _load_blocked_ips(self):
        """Load blocked IPs from Redis"""
        blocked_ips = await self.redis_client.smembers('blocked_ips')
        self.blocked_ips = {ip.decode('utf-8') for ip in blocked_ips}

    async def _cleanup_expired_blocks(self):
        """Cleanup expired IP blocks"""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_ips = set()
                
                for ip in self.blocked_ips:
                    block_info = await self.redis_client.hgetall(f'ip_block:{ip}')
                    if block_info:
                        block_time = datetime.fromisoformat(block_info[b'block_time'].decode('utf-8'))
                        if current_time - block_time > timedelta(hours=24):
                            expired_ips.add(ip)
                
                for ip in expired_ips:
                    await self.unblock_ip(ip)
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)

    async def _monitor_threats(self):
        """Monitor and analyze threats"""
        while True:
            try:
                # Get all suspicious requests in the last hour
                keys = await self.redis_client.keys('suspicious:*')
                current_time = datetime.utcnow()
                
                for key in keys:
                    ip = key.decode('utf-8').split(':')[1]
                    threat_level = await self._assess_threat_level(ip)
                    
                    if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]:
                        await self.block_ip(ip, f"High threat level detected: {threat_level.value}")
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in threat monitoring: {e}")
                await asyncio.sleep(60)

    async def _assess_threat_level(self, ip: str) -> ThreatLevel:
        """Assess threat level for an IP"""
        # Get request history
        key = f'suspicious:{ip}'
        history = await self.redis_client.hgetall(key)
        
        if not history:
            return ThreatLevel.LOW
            
        count = int(history.get(b'count', 0))
        patterns = history.get(b'patterns', b'').decode('utf-8').split(',')
        
        # Check for critical patterns
        if any(re.search(pattern, p) for pattern in self.suspicious_patterns['critical'] for p in patterns):
            return ThreatLevel.CRITICAL
            
        # Check for high risk patterns
        if any(re.search(pattern, p) for pattern in self.suspicious_patterns['high'] for p in patterns):
            return ThreatLevel.HIGH
            
        # Check request frequency
        if count >= self.threat_thresholds[ThreatLevel.HIGH]:
            return ThreatLevel.HIGH
        elif count >= self.threat_thresholds[ThreatLevel.MEDIUM]:
            return ThreatLevel.MEDIUM
            
        return ThreatLevel.LOW

    async def check_request(self, request: Request) -> bool:
        """Check if a request should be allowed"""
        client_ip = request.client.host
        path = request.url.path
        
        # Check if IP is blocked
        if await self.is_ip_blocked(client_ip):
            raise HTTPException(status_code=403, detail="IP address blocked")
        
        # Check request size limits
        await self._check_request_size(request)
        
        # Check user agent
        if self._is_malicious_user_agent(request.headers.get('user-agent', '')):
            await self.track_suspicious_request(client_ip, path, ThreatLevel.HIGH)
        
        # Check IP range
        if self._is_malicious_ip_range(client_ip):
            await self.track_suspicious_request(client_ip, path, ThreatLevel.MEDIUM)
        
        # Check for suspicious patterns
        threat_level = self._check_threat_level(path)
        if threat_level != ThreatLevel.LOW:
            await self.track_suspicious_request(client_ip, path, threat_level)
            
            # Apply appropriate rate limit based on threat level
            rate_limit_category = threat_level.value if threat_level == ThreatLevel.CRITICAL else 'suspicious'
            if not await self.check_rate_limit(client_ip, path, rate_limit_category):
                raise HTTPException(status_code=429, detail=f"{threat_level.value.capitalize()} risk activity detected")
        
        # Check general rate limit
        if not await self.check_rate_limit(client_ip, path):
            raise HTTPException(status_code=429, detail="Too many requests")
        
        return True

    def _check_threat_level(self, path: str) -> ThreatLevel:
        """Check threat level of a request path"""
        for pattern in self.suspicious_patterns['critical']:
            if re.search(pattern, path):
                return ThreatLevel.CRITICAL
                
        for pattern in self.suspicious_patterns['high']:
            if re.search(pattern, path):
                return ThreatLevel.HIGH
                
        for pattern in self.suspicious_patterns['medium']:
            if re.search(pattern, path):
                return ThreatLevel.MEDIUM
                
        for pattern in self.suspicious_patterns['low']:
            if re.search(pattern, path):
                return ThreatLevel.LOW
                
        return ThreatLevel.LOW

    async def track_suspicious_request(self, ip: str, path: str, threat_level: ThreatLevel):
        """Track suspicious requests with threat levels"""
        key = f'suspicious:{ip}'
        
        # Update request count
        count = await self.redis_client.hincrby(key, 'count', 1)
        
        # Update pattern history
        patterns = await self.redis_client.hget(key, 'patterns')
        pattern_list = patterns.decode('utf-8').split(',') if patterns else []
        pattern_list.append(path)
        await self.redis_client.hset(key, 'patterns', ','.join(pattern_list[-10:]))  # Keep last 10 patterns
        
        # Set expiration
        await self.redis_client.expire(key, 3600)  # Expire after 1 hour
        
        # Check if threshold exceeded
        threshold = self.threat_thresholds[threat_level]
        if count >= threshold:
            await self.block_ip(ip, f"Exceeded {threat_level.value} threat threshold")

    async def check_rate_limit(self, ip: str, path: str, category: str = 'default') -> bool:
        """Check if a request is within rate limits"""
        limit = self.rate_limits[category]
        key = f'ratelimit:{category}:{ip}'
        
        # Get current count
        count = await self.redis_client.incr(key)
        if count == 1:  # First request, set expiration
            await self.redis_client.expire(key, limit['window'])
        
        return count <= limit['requests']

    async def block_ip(self, ip: str, reason: str):
        """Block an IP address"""
        if not await self.is_ip_blocked(ip):
            self.blocked_ips.add(ip)
            await self.redis_client.sadd('blocked_ips', ip)
            await self.redis_client.hset(
                f'ip_block:{ip}',
                mapping={
                    'block_time': datetime.utcnow().isoformat(),
                    'reason': reason
                }
            )
            logger.warning(f"Blocked IP {ip}: {reason}")

    async def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        if await self.is_ip_blocked(ip):
            self.blocked_ips.remove(ip)
            await self.redis_client.srem('blocked_ips', ip)
            await self.redis_client.delete(f'ip_block:{ip}')
            logger.info(f"Unblocked IP {ip}")

    async def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked"""
        return ip in self.blocked_ips

    async def get_blocked_ips(self) -> List[Dict[str, str]]:
        """Get list of blocked IPs with reasons"""
        blocked = []
        for ip in self.blocked_ips:
            info = await self.redis_client.hgetall(f'ip_block:{ip}')
            if info:
                blocked.append({
                    'ip': ip,
                    'block_time': info[b'block_time'].decode('utf-8'),
                    'reason': info[b'reason'].decode('utf-8')
                })
        return blocked

    async def get_security_metrics(self) -> Dict:
        """Get security metrics"""
        metrics = await super().get_security_metrics()
        metrics.update({
            'malicious_user_agents': await self._get_malicious_user_agent_count(),
            'malicious_ip_ranges': await self._get_malicious_ip_range_count(),
            'request_size_violations': await self._get_request_size_violations()
        })
        return metrics

    async def _get_suspicious_request_count(self) -> int:
        """Get count of suspicious requests in the last hour"""
        keys = await self.redis_client.keys('suspicious:*')
        count = 0
        for key in keys:
            count += int(await self.redis_client.hget(key, 'count') or 0)
        return count

    async def _get_rate_limit_violations(self) -> int:
        """Get count of rate limit violations"""
        keys = await self.redis_client.keys('ratelimit:*')
        violations = 0
        for key in keys:
            count = int(await self.redis_client.get(key) or 0)
            category = key.decode('utf-8').split(':')[1]
            limit = self.rate_limits[category]['requests']
            if count > limit:
                violations += 1
        return violations

    async def _get_malicious_user_agent_count(self) -> int:
        """Get count of requests with malicious user agents"""
        return len(await self.redis_client.keys('malicious_ua:*'))

    async def _get_malicious_ip_range_count(self) -> int:
        """Get count of requests from malicious IP ranges"""
        return len(await self.redis_client.keys('malicious_ip:*'))

    async def _get_request_size_violations(self) -> int:
        """Get count of request size violations"""
        return len(await self.redis_client.keys('size_violation:*'))

    async def _check_request_size(self, request: Request):
        """Check request size limits"""
        # Check headers size
        headers_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if headers_size > self.request_limits['headers']:
            raise HTTPException(status_code=413, detail="Request headers too large")
        
        # Check URL size
        url_size = len(str(request.url))
        if url_size > self.request_limits['url']:
            raise HTTPException(status_code=414, detail="URL too long")
        
        # Check query string size
        query_size = len(str(request.query_params))
        if query_size > self.request_limits['query']:
            raise HTTPException(status_code=414, detail="Query string too long")
        
        # Check body size (if present)
        if request.method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
            if len(body) > self.request_limits['body']:
                raise HTTPException(status_code=413, detail="Request body too large")

    def _is_malicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent matches known malicious patterns"""
        if not user_agent:
            return False
        return any(re.search(pattern, user_agent.lower()) for pattern in self.malicious_user_agents)

    def _is_malicious_ip_range(self, ip: str) -> bool:
        """Check if IP is in known malicious ranges"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in ipaddress.ip_network(range_) for range_ in self.malicious_ip_ranges)
        except ValueError:
            return False 