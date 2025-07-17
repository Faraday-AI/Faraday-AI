"""
Dashboard Services Package

This package contains various services used by the dashboard core functionality.
"""

from .cache_manager import CacheManager
from .query_optimizer import QueryOptimizer
from .monitoring import MonitoringService
from .safety_service import SafetyService
from .avatar_service import AvatarService
from .load_balancer_service import LoadBalancerService
from .adaptive_rate_limiter import AdaptiveRateLimiter
from .notification_rate_limiter import NotificationRateLimiter
from .notification_write_through import NotificationWriteThrough
from .notification_cache_warmer import NotificationCacheWarmer
from .notification_shard_manager import NotificationShardManager
from .notification_cache_coordinator import NotificationCacheCoordinator
from .notification_batch_optimizer import NotificationBatchOptimizer
from .notification_cache_service import NotificationCacheService
from .notification_monitor_service import NotificationMonitorService
from .notification_queue_service import NotificationQueueService
from .real_time_notification_service import RealTimeNotificationService
from .optimization_monitoring_service import OptimizationMonitoringService
from .analytics_service import AnalyticsService
from .dashboard_service import DashboardService
from .resource_sharing_service import ResourceSharingService
from .core_sharing_service import CoreSharingService
from .cross_org_optimization_service import CrossOrgOptimizationService
from .predictive_access_service import PredictiveAccessService
from .smart_sharing_patterns_service import SmartSharingPatternsService
from .resource_sharing_performance_service import ResourceSharingPerformanceService
from .resource_sharing_cache_service import ResourceSharingCacheService
from .resource_optimization_service import ResourceOptimizationService
from .organization_analytics_service import OrganizationAnalyticsService
from .organization_service import OrganizationService
from .gpt_manager_service import GPTManagerService
from .access_control_service import AccessControlService
from .user_preferences_service import UserPreferencesService
from .tool_registry_service import ToolRegistryService
from .gpt_function_service import GPTFunctionService
from .gpt_coordination_service import GPTCoordinationService
from .security_service import SecurityService
from .monitoring_service import MonitoringService
from .notification_service import NotificationService
from .gpt_context_service import GPTContextService
from .compatibility_service import CompatibilityService
from .recommendation_service import RecommendationService

class DashboardServices:
    """Namespace class for all dashboard services."""
    CacheManager = CacheManager
    QueryOptimizer = QueryOptimizer
    MonitoringService = MonitoringService
    SafetyService = SafetyService
    AvatarService = AvatarService
    LoadBalancerService = LoadBalancerService
    AdaptiveRateLimiter = AdaptiveRateLimiter
    NotificationRateLimiter = NotificationRateLimiter
    NotificationWriteThrough = NotificationWriteThrough
    NotificationCacheWarmer = NotificationCacheWarmer
    NotificationShardManager = NotificationShardManager
    NotificationCacheCoordinator = NotificationCacheCoordinator
    NotificationBatchOptimizer = NotificationBatchOptimizer
    NotificationCacheService = NotificationCacheService
    NotificationMonitorService = NotificationMonitorService
    NotificationQueueService = NotificationQueueService
    RealTimeNotificationService = RealTimeNotificationService
    OptimizationMonitoringService = OptimizationMonitoringService
    AnalyticsService = AnalyticsService
    DashboardService = DashboardService
    ResourceSharingService = ResourceSharingService
    CoreSharingService = CoreSharingService
    CrossOrgOptimizationService = CrossOrgOptimizationService
    PredictiveAccessService = PredictiveAccessService
    SmartSharingPatternsService = SmartSharingPatternsService
    ResourceSharingPerformanceService = ResourceSharingPerformanceService
    ResourceSharingCacheService = ResourceSharingCacheService
    ResourceOptimizationService = ResourceOptimizationService
    OrganizationAnalyticsService = OrganizationAnalyticsService
    OrganizationService = OrganizationService
    GPTManagerService = GPTManagerService
    AccessControlService = AccessControlService
    UserPreferencesService = UserPreferencesService
    ToolRegistryService = ToolRegistryService
    GPTFunctionService = GPTFunctionService
    GPTCoordinationService = GPTCoordinationService
    SecurityService = SecurityService
    NotificationService = NotificationService
    GPTContextService = GPTContextService
    CompatibilityService = CompatibilityService
    RecommendationService = RecommendationService

    @classmethod
    def get_all_services(cls):
        """Get all service classes."""
        return [
            cls.CacheManager,
            cls.QueryOptimizer,
            cls.MonitoringService,
            cls.SafetyService,
            cls.AvatarService,
            cls.LoadBalancerService,
            cls.AdaptiveRateLimiter,
            cls.NotificationRateLimiter,
            cls.NotificationWriteThrough,
            cls.NotificationCacheWarmer,
            cls.NotificationShardManager,
            cls.NotificationCacheCoordinator,
            cls.NotificationBatchOptimizer,
            cls.NotificationCacheService,
            cls.NotificationMonitorService,
            cls.NotificationQueueService,
            cls.RealTimeNotificationService,
            cls.OptimizationMonitoringService,
            cls.AnalyticsService,
            cls.DashboardService,
            cls.ResourceSharingService,
            cls.CoreSharingService,
            cls.CrossOrgOptimizationService,
            cls.PredictiveAccessService,
            cls.SmartSharingPatternsService,
            cls.ResourceSharingPerformanceService,
            cls.ResourceSharingCacheService,
            cls.ResourceOptimizationService,
            cls.OrganizationAnalyticsService,
            cls.OrganizationService,
            cls.GPTManagerService,
            cls.AccessControlService,
            cls.UserPreferencesService,
            cls.ToolRegistryService,
            cls.GPTFunctionService,
            cls.GPTCoordinationService,
            cls.SecurityService,
            cls.NotificationService,
            cls.GPTContextService,
            cls.CompatibilityService,
            cls.RecommendationService
        ]

__all__ = [
    'DashboardServices',
    'CacheManager',
    'QueryOptimizer',
    'MonitoringService',
    'SafetyService',
    'AvatarService',
    'LoadBalancerService',
    'AdaptiveRateLimiter',
    'NotificationRateLimiter',
    'NotificationWriteThrough',
    'NotificationCacheWarmer',
    'NotificationShardManager',
    'NotificationCacheCoordinator',
    'NotificationBatchOptimizer',
    'NotificationCacheService',
    'NotificationMonitorService',
    'NotificationQueueService',
    'RealTimeNotificationService',
    'OptimizationMonitoringService',
    'AnalyticsService',
    'DashboardService',
    'ResourceSharingService',
    'CoreSharingService',
    'CrossOrgOptimizationService',
    'PredictiveAccessService',
    'SmartSharingPatternsService',
    'ResourceSharingPerformanceService',
    'ResourceSharingCacheService',
    'ResourceOptimizationService',
    'OrganizationAnalyticsService',
    'OrganizationService',
    'GPTManagerService',
    'AccessControlService',
    'UserPreferencesService',
    'ToolRegistryService',
    'GPTFunctionService',
    'GPTCoordinationService',
    'SecurityService',
    'NotificationService',
    'GPTContextService',
    'CompatibilityService',
    'RecommendationService'
] 