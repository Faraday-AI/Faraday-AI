"""
Query Optimization Utilities

This module provides utilities for optimizing database queries,
including batch operations, pagination, and performance monitoring.
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic, Union, Tuple
from sqlalchemy.orm import Session, Query, joinedload, selectinload
from sqlalchemy import desc, and_, or_, func
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime, timedelta
from functools import wraps
import time
from prometheus_client import Counter, Histogram, Gauge
import json
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import hashlib
from sqlalchemy.sql import text, select, func, and_, or_, not_, case
from sqlalchemy.schema import Index, CreateIndex, DropIndex, ForeignKey
from sqlalchemy.dialects import postgresql
import psutil
import numpy as np
from collections import deque, defaultdict
import statistics
from typing import Set, Callable
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
import asyncio
import weakref
import concurrent.futures
from functools import partial, lru_cache
from contextlib import contextmanager
import re
import pickle
import zlib
from .monitoring import (
    QUERY_OPTIMIZATION, QUERY_PLAN_ANALYSIS, QUERY_CACHE_EFFICIENCY,
    QUERY_RESOURCE_USAGE, QUERY_STABILITY, QUERY_PERFORMANCE,
    QUERY_ADAPTIVE, QUERY_PATTERN, QUERY_MATERIALIZED, QUERY_INDEX,
    QUERY_PARALLEL, QUERY_STATISTICS, QUERY_ERRORS
)

logger = logging.getLogger(__name__)
T = TypeVar('T')

class QueryType(Enum):
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    BATCH = "batch"

class FilterOperator(Enum):
    EQ = "eq"  # Equal
    NE = "ne"  # Not equal
    GT = "gt"  # Greater than
    LT = "lt"  # Less than
    GTE = "gte"  # Greater than or equal
    LTE = "lte"  # Less than or equal
    LIKE = "like"  # Like
    IN = "in"  # In list
    NOT_IN = "not_in"  # Not in list
    IS_NULL = "is_null"  # Is null
    IS_NOT_NULL = "is_not_null"  # Is not null

class QueryPlan(Enum):
    SEQUENTIAL = "sequential"
    INDEX_SCAN = "index_scan"
    TABLE_SCAN = "table_scan"
    NESTED_LOOP = "nested_loop"
    HASH_JOIN = "hash_join"
    MERGE_JOIN = "merge_join"
    PARALLEL = "parallel"
    MATERIALIZED = "materialized"

class AdaptiveStrategy(Enum):
    CACHE = "cache"
    BATCH = "batch"
    PARALLEL = "parallel"
    INDEX = "index"
    JOIN = "join"
    MATERIALIZE = "materialize"
    REWRITE = "rewrite"
    HINT = "hint"

class QueryPattern(Enum):
    SIMPLE_SELECT = "simple_select"
    COMPLEX_JOIN = "complex_join"
    AGGREGATION = "aggregation"
    SUBQUERY = "subquery"
    RECURSIVE = "recursive"
    ANALYTICAL = "analytical"
    TRANSACTIONAL = "transactional"
    BATCH = "batch"

class CacheStrategy(Enum):
    NONE = "none"
    MEMORY = "memory"
    DISK = "disk"
    HYBRID = "hybrid"

class QueryHint(Enum):
    NONE = "none"
    INDEX = "index"
    JOIN = "join"
    MATERIALIZE = "materialize"
    PARALLEL = "parallel"
    CACHE = "cache"
    BATCH = "batch"
    OPTIMIZE = "optimize"

class IndexType(Enum):
    BTREE = "btree"
    HASH = "hash"
    GIST = "gist"
    GIN = "gin"
    BRIN = "brin"
    SPGIST = "spgist"
    BLOOM = "bloom"
    RUM = "rum"

class ParallelStrategy(Enum):
    NONE = "none"
    PARTITION = "partition"
    SHARD = "shard"
    PIPELINE = "pipeline"
    HYBRID = "hybrid"
    STREAM = "stream"
    BATCH = "batch"
    WORKER = "worker"

class StatisticsType(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    CARDINALITY = "cardinality"
    FREQUENCY = "frequency"
    PATTERN = "pattern"
    PERFORMANCE = "performance"

class BatchStrategy(Enum):
    NONE = "none"
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    DYNAMIC = "dynamic"

class ErrorStrategy(Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    DEGRADE = "degrade"
    ABORT = "abort"

@dataclass
class QueryStats:
    execution_time: float
    row_count: int
    complexity_score: float
    cache_hit: bool
    error: Optional[str] = None

@dataclass
class QueryPlanAnalysis:
    plan_type: QueryPlan
    estimated_rows: int
    actual_rows: int
    execution_time: float
    memory_usage: int
    index_usage: bool
    join_strategy: Optional[str]
    optimization_score: float
    complexity_score: float
    stability_score: float
    resource_efficiency: float
    recommended_strategy: AdaptiveStrategy

@dataclass
class MaterializedView:
    name: str
    query: str
    refresh_interval: int
    last_refresh: datetime
    is_valid: bool
    size_bytes: int
    access_count: int
    last_accessed: datetime
    optimization_score: float
    refresh_strategy: str

@dataclass
class IndexRecommendation:
    table: str
    columns: List[str]
    type: IndexType
    benefit_score: float
    size_estimate: int
    last_used: datetime
    usage_count: int
    creation_cost: float
    maintenance_cost: float
    recommended_priority: int

@dataclass
class QueryProfile:
    query_hash: str
    execution_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    last_execution: datetime
    parameters: Dict[str, Any]
    index_usage: Dict[str, int]
    resource_usage: Dict[str, float]
    optimization_history: List[float]
    stability_metrics: Dict[str, float]

@dataclass
class QueryPartition:
    start: int
    end: int
    size: int
    estimated_rows: int
    complexity: float
    resource_requirements: Dict[str, float]
    execution_priority: int
    worker_assignment: Optional[int]

@dataclass
class StatisticsAnalysis:
    type: StatisticsType
    table: str
    columns: List[str]
    correlation: float
    distinct_values: int
    null_fraction: float
    most_common_values: List[Any]
    histogram_bounds: List[Any]
    last_analyzed: datetime
    update_frequency: int
    confidence_score: float
    optimization_potential: float

@dataclass
class ResultCache:
    key: str
    data: Any
    size: int
    created: datetime
    expires: datetime
    hits: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)

@dataclass
class BatchProfile:
    size: int
    success_rate: float
    avg_time: float
    error_rate: float
    last_processed: datetime
    total_processed: int = 0
    total_errors: int = 0

@dataclass
class ErrorProfile:
    type: str
    count: int
    last_occurred: datetime
    resolution: ErrorStrategy
    retry_count: int = 0
    success_rate: float = 0.0

class QueryOptimizer(Generic[T]):
    def __init__(
        self,
        db: Session,
        model_class: T,
        cache_manager: Optional[Any] = None,
        max_batch_size: int = 1000,
        query_timeout: int = 30,
        enable_monitoring: bool = True,
        adaptive_optimization: bool = True,
        max_concurrent_queries: int = 10,
        memory_threshold: float = 0.8,
        enable_materialized_views: bool = True,
        max_materialized_views: int = 10,
        cache_strategy: CacheStrategy = CacheStrategy.HYBRID,
        enable_query_hints: bool = True,
        enable_index_recommendations: bool = True,
        statistics_collection_interval: int = 3600,
        enable_parallelization: bool = True,
        max_parallel_workers: int = 4,
        enable_advanced_statistics: bool = True,
        statistics_analysis_interval: int = 86400,
        result_cache_size: int = 1000,
        result_cache_ttl: int = 3600,
        enable_adaptive_batching: bool = True,
        max_retries: int = 3,
        error_handling_strategy: ErrorStrategy = ErrorStrategy.RETRY,
        stability_threshold: float = 0.9,
        resource_efficiency_threshold: float = 0.8,
        optimization_interval: int = 300,
        pattern_detection_interval: int = 600,
        plan_analysis_interval: int = 900,
        view_refresh_interval: int = 3600,
        index_maintenance_interval: int = 86400,
        statistics_update_interval: int = 7200,
        performance_monitoring_interval: int = 60,
        resource_monitoring_interval: int = 30,
        stability_monitoring_interval: int = 300,
        efficiency_monitoring_interval: int = 600
    ):
        """
        Initialize the query optimizer with enhanced features.
        
        Args:
            db: SQLAlchemy database session
            model_class: SQLAlchemy model class
            cache_manager: Optional cache manager instance
            max_batch_size: Maximum batch size for operations
            query_timeout: Query timeout in seconds
            enable_monitoring: Whether to enable performance monitoring
            adaptive_optimization: Whether to enable adaptive optimization
            max_concurrent_queries: Maximum number of concurrent queries
            memory_threshold: Memory usage threshold for optimization (0.0 to 1.0)
            enable_materialized_views: Whether to enable materialized views
            max_materialized_views: Maximum number of materialized views
            cache_strategy: Cache strategy to use
            enable_query_hints: Whether to enable query hints
            enable_index_recommendations: Whether to enable index recommendations
            statistics_collection_interval: Interval for collecting statistics in seconds
            enable_parallelization: Whether to enable query parallelization
            max_parallel_workers: Maximum number of parallel workers
            enable_advanced_statistics: Whether to enable advanced statistics
            statistics_analysis_interval: Interval for analyzing statistics in seconds
            result_cache_size: Maximum number of cached results
            result_cache_ttl: Time-to-live for cached results in seconds
            enable_adaptive_batching: Whether to enable adaptive batch processing
            max_retries: Maximum number of retries for failed operations
            error_handling_strategy: Strategy for handling errors
            stability_threshold: Threshold for query stability (0.0 to 1.0)
            resource_efficiency_threshold: Threshold for resource efficiency (0.0 to 1.0)
            optimization_interval: Interval for running optimizations in seconds
            pattern_detection_interval: Interval for detecting patterns in seconds
            plan_analysis_interval: Interval for analyzing query plans in seconds
            view_refresh_interval: Interval for refreshing materialized views in seconds
            index_maintenance_interval: Interval for maintaining indexes in seconds
            statistics_update_interval: Interval for updating statistics in seconds
            performance_monitoring_interval: Interval for monitoring performance in seconds
            resource_monitoring_interval: Interval for monitoring resources in seconds
            stability_monitoring_interval: Interval for monitoring stability in seconds
            efficiency_monitoring_interval: Interval for monitoring efficiency in seconds
        """
        self.db = db
        self.model_class = model_class
        self.cache_manager = cache_manager
        self.max_batch_size = max_batch_size
        self.query_timeout = query_timeout
        self.enable_monitoring = enable_monitoring
        self.adaptive_optimization = adaptive_optimization
        self.max_concurrent_queries = max_concurrent_queries
        self.memory_threshold = memory_threshold
        self.enable_materialized_views = enable_materialized_views
        self.max_materialized_views = max_materialized_views
        self.cache_strategy = cache_strategy
        self.enable_query_hints = enable_query_hints
        self.enable_index_recommendations = enable_index_recommendations
        self.statistics_collection_interval = statistics_collection_interval
        self.enable_parallelization = enable_parallelization
        self.max_parallel_workers = max_parallel_workers
        self.enable_advanced_statistics = enable_advanced_statistics
        self.statistics_analysis_interval = statistics_analysis_interval
        self.result_cache_size = result_cache_size
        self.result_cache_ttl = result_cache_ttl
        self.enable_adaptive_batching = enable_adaptive_batching
        self.max_retries = max_retries
        self.error_handling_strategy = error_handling_strategy
        self.stability_threshold = stability_threshold
        self.resource_efficiency_threshold = resource_efficiency_threshold
        self.optimization_interval = optimization_interval
        self.pattern_detection_interval = pattern_detection_interval
        self.plan_analysis_interval = plan_analysis_interval
        self.view_refresh_interval = view_refresh_interval
        self.index_maintenance_interval = index_maintenance_interval
        self.statistics_update_interval = statistics_update_interval
        self.performance_monitoring_interval = performance_monitoring_interval
        self.resource_monitoring_interval = resource_monitoring_interval
        self.stability_monitoring_interval = stability_monitoring_interval
        self.efficiency_monitoring_interval = efficiency_monitoring_interval
        self._query_cache = {}
        self._cache_lock = threading.Lock()
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0,
            'optimizations': 0,
            'stability_score': 1.0,
            'efficiency_score': 1.0
        }
        self._concurrent_queries = 0
        self._query_history = deque(maxlen=1000)
        self._plan_cache = {}
        self._adaptive_decisions = {}
        self._memory_monitor = threading.Thread(target=self._monitor_memory, daemon=True)
        self._memory_monitor.start()
        self._materialized_views: Dict[str, MaterializedView] = {}
        self._query_patterns: Dict[str, int] = {}
        self._view_refresh_lock = threading.Lock()
        self._pattern_detector = threading.Thread(target=self._detect_patterns, daemon=True)
        self._pattern_detector.start()
        self._query_profiles: Dict[str, QueryProfile] = {}
        self._index_recommendations: Dict[str, IndexRecommendation] = {}
        self._statistics_collector = threading.Thread(target=self._collect_statistics, daemon=True)
        self._statistics_collector.start()
        self._statistics_analysis: Dict[str, StatisticsAnalysis] = {}
        self._parallel_executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_workers)
        self._statistics_analyzer = threading.Thread(target=self._analyze_statistics, daemon=True)
        self._statistics_analyzer.start()
        self._optimizer = threading.Thread(target=self._run_optimizations, daemon=True)
        self._optimizer.start()
        self._stability_monitor = threading.Thread(target=self._monitor_stability, daemon=True)
        self._stability_monitor.start()
        self._efficiency_monitor = threading.Thread(target=self._monitor_efficiency, daemon=True)
        self._efficiency_monitor.start()
        self._performance_monitor = threading.Thread(target=self._monitor_performance, daemon=True)
        self._performance_monitor.start()
        self._resource_monitor = threading.Thread(target=self._monitor_resources, daemon=True)
        self._resource_monitor.start()
        self._result_cache: Dict[str, ResultCache] = {}
        self._batch_profiles: Dict[str, BatchProfile] = {}
        self._error_profiles: Dict[str, ErrorProfile] = {}
        self._cache_lock = threading.Lock()
        self._batch_lock = threading.Lock()
        self._error_lock = threading.Lock()

    @staticmethod
    def _measure_query(operation: str) -> Callable:
        """Decorator to measure query performance."""
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                start_time = time.time()
                try:
                    result = func(self, *args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if self.enable_monitoring:
                        QUERY_OPTIMIZATION.labels(operation=operation).observe(execution_time)
                        QUERY_OPTIMIZATION.labels(operation=operation, status='success').inc()
                    
                    return result
                except Exception as e:
                    if self.enable_monitoring:
                        QUERY_OPTIMIZATION.labels(operation=operation, status='error').inc()
                    raise
            return wrapper
        return decorator

    def _apply_filters(
        self,
        query: Query,
        filters: Dict[str, Dict[str, Any]]
    ) -> Query:
        """Apply advanced filters to a query."""
        filter_conditions = []
        
        for field, conditions in filters.items():
            if not hasattr(self.model_class, field):
                continue
                
            column = getattr(self.model_class, field)
            
            for operator, value in conditions.items():
                try:
                    op = FilterOperator(operator)
                    if op == FilterOperator.EQ:
                        filter_conditions.append(column == value)
                    elif op == FilterOperator.NE:
                        filter_conditions.append(column != value)
                    elif op == FilterOperator.GT:
                        filter_conditions.append(column > value)
                    elif op == FilterOperator.LT:
                        filter_conditions.append(column < value)
                    elif op == FilterOperator.GTE:
                        filter_conditions.append(column >= value)
                    elif op == FilterOperator.LTE:
                        filter_conditions.append(column <= value)
                    elif op == FilterOperator.LIKE:
                        filter_conditions.append(column.like(value))
                    elif op == FilterOperator.IN:
                        filter_conditions.append(column.in_(value))
                    elif op == FilterOperator.NOT_IN:
                        filter_conditions.append(~column.in_(value))
                    elif op == FilterOperator.IS_NULL:
                        filter_conditions.append(column.is_(None))
                    elif op == FilterOperator.IS_NOT_NULL:
                        filter_conditions.append(column.isnot(None))
                except ValueError:
                    logger.warning(f"Invalid filter operator: {operator}")
                    continue
        
        if filter_conditions:
            query = query.filter(and_(*filter_conditions))
        
        return query

    @_measure_query('paginate')
    def paginate(
        self,
        query: Query,
        page: int = 1,
        per_page: int = 20,
        order_by: Optional[str] = None,
        desc_order: bool = False,
        cache_ttl: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Enhanced pagination with caching and performance monitoring.
        
        Args:
            query: SQLAlchemy query to paginate
            page: Page number (1-based)
            per_page: Items per page
            order_by: Column to order by
            desc_order: Whether to order in descending order
            cache_ttl: Optional cache TTL in seconds
            
        Returns:
            Dictionary containing paginated results and metadata
        """
        try:
            # Check cache if enabled
            cache_key = None
            if self.cache_manager and cache_ttl:
                cache_key = f"paginate:{self._get_cache_key(query)}:{page}:{per_page}"
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    QUERY_CACHE_EFFICIENCY.labels(type='hit').inc()
                    return cached_result
                QUERY_CACHE_EFFICIENCY.labels(type='miss').inc()

            # Apply ordering if specified
            if order_by:
                column = getattr(self.model_class, order_by)
                query = query.order_by(desc(column) if desc_order else column)

            # Calculate total count
            total = query.count()

            # Calculate pagination
            total_pages = (total + per_page - 1) // per_page
            page = max(1, min(page, total_pages))
            offset = (page - 1) * per_page

            # Get paginated results
            items = query.offset(offset).limit(per_page).all()

            result = {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }

            # Cache result if enabled
            if cache_key and self.cache_manager:
                self.cache_manager.set(cache_key, result, ttl=cache_ttl)

            return result
        except SQLAlchemyError as e:
            logger.error(f"Pagination failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during pagination: {e}")
            raise

    @_measure_query('batch_operation')
    def batch_operation(
        self,
        items: List[Any],
        operation: str,
        batch_size: int = 100,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Enhanced batch operations with parallel processing and progress tracking.
        
        Args:
            items: List of items to process
            operation: Operation to perform ('insert', 'update', 'delete')
            batch_size: Number of items to process in each batch
            parallel: Whether to process batches in parallel
            
        Returns:
            Dictionary containing operation results
        """
        try:
            results = {
                'total': len(items),
                'processed': 0,
                'success': 0,
                'failed': 0,
                'errors': [],
                'start_time': datetime.utcnow(),
                'batches': []
            }

            def process_batch(batch: List[Any]) -> Dict[str, Any]:
                batch_result = {
                    'size': len(batch),
                    'success': 0,
                    'failed': 0,
                    'error': None
                }
                
                try:
                    if operation == 'insert':
                        self.db.bulk_save_objects(batch)
                    elif operation == 'update':
                        for item in batch:
                            self.db.merge(item)
                    elif operation == 'delete':
                        for item in batch:
                            self.db.delete(item)
                    else:
                        raise ValueError(f"Invalid operation: {operation}")

                    self.db.commit()
                    batch_result['success'] = len(batch)
                except Exception as e:
                    self.db.rollback()
                    batch_result['failed'] = len(batch)
                    batch_result['error'] = str(e)
                
                return batch_result

            if parallel:
                futures = []
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    futures.append(self._thread_pool.submit(process_batch, batch))
                
                for future in futures:
                    batch_result = future.result()
                    results['batches'].append(batch_result)
                    results['success'] += batch_result['success']
                    results['failed'] += batch_result['failed']
                    if batch_result['error']:
                        results['errors'].append(batch_result['error'])
                    results['processed'] += batch_result['size']
            else:
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    batch_result = process_batch(batch)
                    results['batches'].append(batch_result)
                    results['success'] += batch_result['success']
                    results['failed'] += batch_result['failed']
                    if batch_result['error']:
                        results['errors'].append(batch_result['error'])
                    results['processed'] += batch_result['size']

            results['end_time'] = datetime.utcnow()
            results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
            
            return results
        except Exception as e:
            logger.error(f"Batch operation failed: {e}")
            raise

    def _monitor_memory(self):
        """Monitor system memory usage for adaptive optimization."""
        while True:
            try:
                memory_percent = psutil.Process().memory_percent()
                if memory_percent > self.memory_threshold:
                    self._adjust_optimization_strategy('memory', memory_percent)
                time.sleep(60)
            except Exception as e:
                logger.error(f"Memory monitoring failed: {e}")
                time.sleep(300)

    def _adjust_optimization_strategy(self, reason: str, value: float):
        """Adjust optimization strategy based on system conditions."""
        if not self.adaptive_optimization:
            return

        adjustments = {
            'memory': {
                'batch_size': max(100, int(self.max_batch_size * 0.5)),
                'concurrent_queries': max(2, int(self.max_concurrent_queries * 0.5))
            },
            'performance': {
                'batch_size': min(2000, int(self.max_batch_size * 1.5)),
                'concurrent_queries': min(20, int(self.max_concurrent_queries * 1.5))
            }
        }

        if reason in adjustments:
            for key, value in adjustments[reason].items():
                setattr(self, key, value)
                QUERY_ADAPTIVE.labels(type=f"{reason}_{key}").inc()

    def _analyze_query_plan(self, query: Query) -> QueryPlanAnalysis:
        """Analyze and optimize query execution plan."""
        try:
            # Get query plan from database
            plan = self.db.execute(text(f"EXPLAIN ANALYZE {str(query.statement)}")).fetchall()
            
            # Parse plan information
            plan_type = self._determine_plan_type(plan)
            estimated_rows = self._extract_estimated_rows(plan)
            actual_rows = self._extract_actual_rows(plan)
            execution_time = self._extract_execution_time(plan)
            
            # Calculate optimization score
            score = self._calculate_optimization_score(
                plan_type,
                estimated_rows,
                actual_rows,
                execution_time
            )
            
            # Update metrics
            QUERY_PLAN_ANALYSIS.labels(type=plan_type.value).set(score)
            
            return QueryPlanAnalysis(
                plan_type=plan_type,
                estimated_rows=estimated_rows,
                actual_rows=actual_rows,
                execution_time=execution_time,
                memory_usage=psutil.Process().memory_info().rss,
                index_usage=self._check_index_usage(plan),
                join_strategy=self._determine_join_strategy(plan),
                optimization_score=score,
                complexity_score=self._calculate_complexity_score(plan_type, estimated_rows, actual_rows, execution_time),
                stability_score=self._calculate_stability_score(),
                resource_efficiency=self._calculate_resource_efficiency(plan_type, estimated_rows, actual_rows, execution_time)
            )
        except Exception as e:
            logger.error(f"Query plan analysis failed: {e}")
            return None

    def _determine_plan_type(self, plan: List[Any]) -> QueryPlan:
        """Determine the type of query execution plan."""
        plan_text = str(plan).lower()
        
        if "index scan" in plan_text:
            return QueryPlan.INDEX_SCAN
        elif "table scan" in plan_text:
            return QueryPlan.TABLE_SCAN
        elif "nested loop" in plan_text:
            return QueryPlan.NESTED_LOOP
        elif "hash join" in plan_text:
            return QueryPlan.HASH_JOIN
        elif "merge join" in plan_text:
            return QueryPlan.MERGE_JOIN
        else:
            return QueryPlan.SEQUENTIAL

    def _calculate_optimization_score(
        self,
        plan_type: QueryPlan,
        estimated_rows: int,
        actual_rows: int,
        execution_time: float
    ) -> float:
        """Calculate query optimization score."""
        # Base score on plan type
        plan_scores = {
            QueryPlan.INDEX_SCAN: 0.9,
            QueryPlan.HASH_JOIN: 0.8,
            QueryPlan.MERGE_JOIN: 0.7,
            QueryPlan.NESTED_LOOP: 0.6,
            QueryPlan.TABLE_SCAN: 0.4,
            QueryPlan.SEQUENTIAL: 0.3
        }
        
        # Adjust score based on row estimation accuracy
        row_accuracy = 1 - abs(estimated_rows - actual_rows) / max(1, actual_rows)
        
        # Adjust score based on execution time (normalized)
        time_score = 1 - min(1, execution_time / 1000)  # Assuming 1s as max
        
        # Combine scores
        return (plan_scores[plan_type] * 0.4 + 
                row_accuracy * 0.3 + 
                time_score * 0.3)

    def _optimize_query_plan(self, query: Query, analysis: QueryPlanAnalysis) -> Query:
        """Optimize query based on plan analysis."""
        if not analysis or analysis.optimization_score > 0.8:
            return query

        optimizations = {
            QueryPlan.TABLE_SCAN: self._optimize_table_scan,
            QueryPlan.NESTED_LOOP: self._optimize_nested_loop,
            QueryPlan.SEQUENTIAL: self._optimize_sequential
        }

        optimizer = optimizations.get(analysis.plan_type)
        if optimizer:
            return optimizer(query, analysis)
        
        return query

    def _optimize_table_scan(self, query: Query, analysis: QueryPlanAnalysis) -> Query:
        """Optimize table scan queries."""
        # Add appropriate indexes
        # This is a placeholder - actual implementation would depend on your schema
        return query

    def _optimize_nested_loop(self, query: Query, analysis: QueryPlanAnalysis) -> Query:
        """Optimize nested loop joins."""
        # Convert to hash join if possible
        # This is a placeholder - actual implementation would depend on your schema
        return query

    def _optimize_sequential(self, query: Query, analysis: QueryPlanAnalysis) -> Query:
        """Optimize sequential queries."""
        # Add parallel processing if possible
        # This is a placeholder - actual implementation would depend on your schema
        return query

    def _detect_patterns(self):
        """Detect and analyze query patterns."""
        while True:
            try:
                # Analyze recent queries for patterns
                recent_queries = list(self._query_history)[-100:]  # Last 100 queries
                patterns = self._analyze_query_patterns(recent_queries)
                
                # Update pattern statistics
                for pattern, count in patterns.items():
                    self._query_patterns[pattern] = count
                    QUERY_PATTERN.labels(pattern=pattern).set(count)
                
                # Adjust optimization strategy based on patterns
                self._adjust_strategy_based_on_patterns(patterns)
                
                time.sleep(self.pattern_detection_interval)
            except Exception as e:
                logger.error(f"Pattern detection failed: {e}")
                time.sleep(self.pattern_detection_interval * 2)

    def _analyze_query_patterns(self, queries: List[Query]) -> Dict[str, int]:
        """Analyze queries for common patterns."""
        patterns = {
            QueryPattern.SIMPLE_SELECT: 0,
            QueryPattern.COMPLEX_JOIN: 0,
            QueryPattern.AGGREGATION: 0,
            QueryPattern.SUBQUERY: 0,
            QueryPattern.RECURSIVE: 0
        }
        
        for query in queries:
            query_str = str(query.statement).lower()
            
            if "join" in query_str and query_str.count("join") > 2:
                patterns[QueryPattern.COMPLEX_JOIN] += 1
            elif "select" in query_str and "from" in query_str and not any(op in query_str for op in ["join", "group", "having"]):
                patterns[QueryPattern.SIMPLE_SELECT] += 1
            elif any(op in query_str for op in ["group by", "having", "sum(", "count(", "avg("]):
                patterns[QueryPattern.AGGREGATION] += 1
            elif "select" in query_str and query_str.count("select") > 1:
                patterns[QueryPattern.SUBQUERY] += 1
            elif "with recursive" in query_str:
                patterns[QueryPattern.RECURSIVE] += 1
        
        return patterns

    def _adjust_strategy_based_on_patterns(self, patterns: Dict[str, int]):
        """Adjust optimization strategy based on detected patterns."""
        total_queries = sum(patterns.values())
        if total_queries == 0:
            return

        # Adjust cache strategy based on patterns
        if patterns[QueryPattern.SIMPLE_SELECT] / total_queries > 0.7:
            self.cache_strategy = CacheStrategy.SIMPLE
        elif patterns[QueryPattern.COMPLEX_JOIN] / total_queries > 0.5:
            self.cache_strategy = CacheStrategy.COMPLEX
        elif patterns[QueryPattern.AGGREGATION] / total_queries > 0.3:
            self.cache_strategy = CacheStrategy.MATERIALIZED

        # Enable/disable materialized views based on patterns
        if patterns[QueryPattern.AGGREGATION] / total_queries > 0.2:
            self.enable_materialized_views = True
        else:
            self.enable_materialized_views = False

    def _create_materialized_view(self, name: str, query: str, refresh_interval: int = 3600) -> bool:
        """Create a materialized view for frequently accessed data."""
        if not self.enable_materialized_views or len(self._materialized_views) >= self.max_materialized_views:
            return False

        try:
            # Create the materialized view
            self.db.execute(text(f"""
                CREATE MATERIALIZED VIEW IF NOT EXISTS {name} AS
                {query}
            """))
            
            # Create index on the view
            self.db.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{name} ON {name} (id)
            """))
            
            # Store view metadata
            self._materialized_views[name] = MaterializedView(
                name=name,
                query=query,
                refresh_interval=refresh_interval,
                last_refresh=datetime.utcnow(),
                is_valid=True,
                size_bytes=0,
                access_count=0,
                last_accessed=datetime.utcnow(),
                optimization_score=0.0,
                refresh_strategy="manual"
            )
            
            QUERY_MATERIALIZED.labels(operation='create').inc()
            return True
        except Exception as e:
            logger.error(f"Failed to create materialized view {name}: {e}")
            return False

    def _refresh_materialized_view(self, name: str) -> bool:
        """Refresh a materialized view."""
        if name not in self._materialized_views:
            return False

        try:
            with self._view_refresh_lock:
                view = self._materialized_views[name]
                if datetime.utcnow() - view.last_refresh < timedelta(seconds=view.refresh_interval):
                    return True

                # Refresh the view
                self.db.execute(text(f"""
                    REFRESH MATERIALIZED VIEW CONCURRENTLY {name}
                """))
                
                # Update metadata
                view.last_refresh = datetime.utcnow()
                view.is_valid = True
                view.access_count += 1
                view.last_accessed = datetime.utcnow()
                
                QUERY_MATERIALIZED.labels(operation='refresh').inc()
                return True
        except Exception as e:
            logger.error(f"Failed to refresh materialized view {name}: {e}")
            return False

    def _rewrite_query(self, query: Query) -> Optional[Query]:
        """Rewrite query for better performance."""
        try:
            query_str = str(query.statement).lower()
            
            # Check for materialized view usage
            for view_name, view in self._materialized_views.items():
                if view.is_valid and view.query.lower() in query_str:
                    # Rewrite query to use materialized view
                    rewritten = text(f"""
                        SELECT * FROM {view_name}
                        WHERE {query_str.split('where')[1] if 'where' in query_str else '1=1'}
                    """)
                    QUERY_OPTIMIZATION.labels(type='materialized_view').inc()
                    return self.db.query(self.model_class).from_statement(rewritten)
            
            # Check for common subquery patterns
            if 'select' in query_str and query_str.count('select') > 1:
                # Rewrite correlated subqueries
                rewritten = self._rewrite_correlated_subquery(query)
                if rewritten:
                    QUERY_OPTIMIZATION.labels(type='subquery').inc()
                    return rewritten
            
            # Check for complex joins
            if 'join' in query_str and query_str.count('join') > 2:
                # Rewrite complex joins
                rewritten = self._rewrite_complex_join(query)
                if rewritten:
                    QUERY_OPTIMIZATION.labels(type='join').inc()
                    return rewritten
            
            return None
        except Exception as e:
            logger.error(f"Query rewrite failed: {e}")
            return None

    def _rewrite_correlated_subquery(self, query: Query) -> Optional[Query]:
        """Rewrite correlated subqueries to joins."""
        # This is a placeholder - actual implementation would depend on your schema
        return None

    def _rewrite_complex_join(self, query: Query) -> Optional[Query]:
        """Rewrite complex joins for better performance."""
        # This is a placeholder - actual implementation would depend on your schema
        return None

    def _collect_statistics(self):
        """Collect and analyze query statistics."""
        while True:
            try:
                # Collect index usage statistics
                self._collect_index_statistics()
                
                # Collect query profiles
                self._collect_query_profiles()
                
                # Generate index recommendations
                if self.enable_index_recommendations:
                    self._generate_index_recommendations()
                
                time.sleep(self.statistics_collection_interval)
            except Exception as e:
                logger.error(f"Statistics collection failed: {e}")
                time.sleep(self.statistics_collection_interval * 2)

    def _collect_index_statistics(self):
        """Collect index usage statistics from the database."""
        try:
            # Get index usage statistics
            stats = self.db.execute(text("""
                SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes
            """)).fetchall()
            
            for stat in stats:
                index_name = f"{stat.schemaname}.{stat.tablename}.{stat.indexname}"
                usage = stat.idx_scan + stat.idx_tup_read + stat.idx_tup_fetch
                QUERY_INDEX.labels(index=index_name).set(usage)
                
                # Update index recommendations
                if index_name in self._index_recommendations:
                    self._index_recommendations[index_name].usage_count = usage
                    self._index_recommendations[index_name].last_used = datetime.utcnow()
        except Exception as e:
            logger.error(f"Failed to collect index statistics: {e}")

    def _collect_query_profiles(self):
        """Collect and analyze query execution profiles."""
        try:
            # Get query execution statistics
            stats = self.db.execute(text("""
                SELECT query, calls, total_time, min_time, max_time, mean_time, stddev_time
                FROM pg_stat_statements
                WHERE query != '<insufficient privilege>'
            """)).fetchall()
            
            for stat in stats:
                query_hash = hashlib.md5(stat.query.encode()).hexdigest()
                
                if query_hash in self._query_profiles:
                    profile = self._query_profiles[query_hash]
                    profile.execution_count += stat.calls
                    profile.total_time += stat.total_time
                    profile.avg_time = stat.mean_time
                    profile.min_time = min(profile.min_time, stat.min_time)
                    profile.max_time = max(profile.max_time, stat.max_time)
                    profile.std_dev = stat.stddev_time
                    profile.last_execution = datetime.utcnow()
                else:
                    self._query_profiles[query_hash] = QueryProfile(
                        query_hash=query_hash,
                        execution_count=stat.calls,
                        total_time=stat.total_time,
                        avg_time=stat.mean_time,
                        min_time=stat.min_time,
                        max_time=stat.max_time,
                        std_dev=stat.stddev_time,
                        last_execution=datetime.utcnow()
                    )
                
                # Update metrics
                QUERY_STATISTICS.labels(metric='executions').observe(stat.calls)
                QUERY_STATISTICS.labels(metric='total_time').observe(stat.total_time)
                QUERY_STATISTICS.labels(metric='avg_time').observe(stat.mean_time)
        except Exception as e:
            logger.error(f"Failed to collect query profiles: {e}")

    def _generate_index_recommendations(self):
        """Generate index recommendations based on query patterns."""
        try:
            # Analyze slow queries
            slow_queries = [
                profile for profile in self._query_profiles.values()
                if profile.avg_time > 100  # Queries taking more than 100ms
            ]
            
            for profile in slow_queries:
                # Extract table and column information
                table, columns = self._extract_table_columns(profile)
                if not table or not columns:
                    continue
                
                # Calculate benefit score
                benefit_score = self._calculate_index_benefit(profile, table, columns)
                if benefit_score < 0.5:  # Only recommend if benefit is significant
                    continue
                
                # Create recommendation
                index_name = f"idx_{table}_{'_'.join(columns)}"
                if index_name not in self._index_recommendations:
                    self._index_recommendations[index_name] = IndexRecommendation(
                        table=table,
                        columns=columns,
                        type=IndexType.BTREE,  # Default to B-tree
                        benefit_score=benefit_score,
                        size_estimate=self._estimate_index_size(table, columns),
                        last_used=datetime.utcnow(),
                        usage_count=0,
                        creation_cost=0.0,
                        maintenance_cost=0.0,
                        recommended_priority=0
                    )
                    QUERY_INDEX.labels(type='new').inc()
        except Exception as e:
            logger.error(f"Failed to generate index recommendations: {e}")

    def _extract_table_columns(self, profile: QueryProfile) -> Tuple[Optional[str], List[str]]:
        """Extract table and column information from query profile."""
        # This is a placeholder - actual implementation would depend on your schema
        return None, []

    def _calculate_index_benefit(self, profile: QueryProfile, table: str, columns: List[str]) -> float:
        """Calculate the potential benefit of creating an index."""
        try:
            # Get current execution time
            current_time = profile.avg_time
            
            # Estimate execution time with index
            estimated_time = self._estimate_indexed_query_time(profile, table, columns)
            
            # Calculate benefit score
            if current_time == 0:
                return 0.0
            return 1 - (estimated_time / current_time)
        except Exception as e:
            logger.error(f"Failed to calculate index benefit: {e}")
            return 0.0

    def _estimate_indexed_query_time(self, profile: QueryProfile, table: str, columns: List[str]) -> float:
        """Estimate query execution time with the proposed index."""
        # This is a placeholder - actual implementation would depend on your schema
        return profile.avg_time * 0.5  # Assume 50% improvement

    def _estimate_index_size(self, table: str, columns: List[str]) -> int:
        """Estimate the size of the proposed index."""
        try:
            # Get table statistics
            stats = self.db.execute(text(f"""
                SELECT reltuples, relpages
                FROM pg_class
                WHERE relname = '{table}'
            """)).fetchone()
            
            if stats:
                # Rough estimate: 20% of table size
                return int(stats.relpages * 0.2 * 8192)  # 8192 bytes per page
            return 0
        except Exception as e:
            logger.error(f"Failed to estimate index size: {e}")
            return 0

    def _apply_query_hints(self, query: Query) -> Query:
        """Apply query hints for better performance."""
        if not self.enable_query_hints:
            return query

        try:
            query_str = str(query.statement).lower()
            
            # Check for index hint opportunities
            if 'where' in query_str and not any(hint in query_str for hint in ['index', 'use index']):
                # Add index hint
                query = query.with_hint(self.model_class, 'USE INDEX (idx_primary)')
                QUERY_OPTIMIZATION.labels(type='index').inc()
            
            # Check for join hint opportunities
            if 'join' in query_str and not any(hint in query_str for hint in ['hash', 'merge', 'nestloop']):
                # Add join hint
                query = query.with_hint(self.model_class, 'HASH JOIN')
                QUERY_OPTIMIZATION.labels(type='join').inc()
            
            return query
        except Exception as e:
            logger.error(f"Failed to apply query hints: {e}")
            return query

    def _analyze_statistics(self):
        """Analyze advanced database statistics."""
        while True:
            try:
                # Collect basic statistics
                self._collect_basic_statistics()
                
                # Analyze column correlations
                if self.enable_advanced_statistics:
                    self._analyze_column_correlations()
                
                # Analyze data distributions
                self._analyze_distributions()
                
                # Update cardinality estimates
                self._update_cardinality_estimates()
                
                time.sleep(self.statistics_analysis_interval)
            except Exception as e:
                logger.error(f"Statistics analysis failed: {e}")
                time.sleep(self.statistics_analysis_interval * 2)

    def _collect_basic_statistics(self):
        """Collect basic table and column statistics."""
        try:
            # Get table statistics
            stats = self.db.execute(text("""
                SELECT schemaname, tablename, attname, null_frac, avg_width, n_distinct,
                       most_common_vals, most_common_freqs, histogram_bounds
                FROM pg_stats
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            """)).fetchall()
            
            for stat in stats:
                table_key = f"{stat.schemaname}.{stat.tablename}"
                if table_key not in self._statistics_analysis:
                    self._statistics_analysis[table_key] = StatisticsAnalysis(
                        type=StatisticsType.BASIC,
                        table=stat.tablename,
                        columns=[stat.attname],
                        correlation=0.0,
                        distinct_values=stat.n_distinct,
                        null_fraction=stat.null_frac,
                        most_common_values=stat.most_common_vals,
                        histogram_bounds=stat.histogram_bounds,
                        last_analyzed=datetime.utcnow()
                    )
                else:
                    analysis = self._statistics_analysis[table_key]
                    analysis.columns.append(stat.attname)
                    analysis.distinct_values = max(analysis.distinct_values, stat.n_distinct)
                    analysis.null_fraction = max(analysis.null_fraction, stat.null_frac)
                
                QUERY_STATISTICS.labels(type='basic').inc()
        except Exception as e:
            logger.error(f"Failed to collect basic statistics: {e}")

    def _analyze_column_correlations(self):
        """Analyze correlations between columns."""
        try:
            for table_key, analysis in self._statistics_analysis.items():
                if len(analysis.columns) < 2:
                    continue
                
                # Get correlation statistics
                correlations = self.db.execute(text(f"""
                    SELECT attname, correlation
                    FROM pg_stats
                    WHERE schemaname = '{table_key.split('.')[0]}'
                    AND tablename = '{table_key.split('.')[1]}'
                    AND correlation IS NOT NULL
                """)).fetchall()
                
                if correlations:
                    analysis.correlation = max(corr.correlation for corr in correlations)
                    analysis.type = StatisticsType.CORRELATION
                    QUERY_STATISTICS.labels(type='correlation').inc()
        except Exception as e:
            logger.error(f"Failed to analyze column correlations: {e}")

    def _analyze_distributions(self):
        """Analyze data distributions for better query planning."""
        try:
            for table_key, analysis in self._statistics_analysis.items():
                # Get distribution statistics
                distribution = self.db.execute(text(f"""
                    SELECT histogram_bounds, most_common_vals, most_common_freqs
                    FROM pg_stats
                    WHERE schemaname = '{table_key.split('.')[0]}'
                    AND tablename = '{table_key.split('.')[1]}'
                """)).fetchall()
                
                if distribution:
                    analysis.histogram_bounds = distribution[0].histogram_bounds
                    analysis.most_common_values = distribution[0].most_common_vals
                    analysis.type = StatisticsType.DISTRIBUTION
                    QUERY_STATISTICS.labels(type='distribution').inc()
        except Exception as e:
            logger.error(f"Failed to analyze distributions: {e}")

    def _update_cardinality_estimates(self):
        """Update cardinality estimates for better query planning."""
        try:
            for table_key, analysis in self._statistics_analysis.items():
                # Get cardinality statistics
                cardinality = self.db.execute(text(f"""
                    SELECT reltuples, relpages
                    FROM pg_class
                    WHERE relname = '{analysis.table}'
                """)).fetchone()
                
                if cardinality:
                    analysis.distinct_values = cardinality.reltuples
                    analysis.type = StatisticsType.CARDINALITY
                    QUERY_STATISTICS.labels(type='cardinality').inc()
        except Exception as e:
            logger.error(f"Failed to update cardinality estimates: {e}")

    def _partition_query(self, query: Query, partition_size: int = 1000) -> List[QueryPartition]:
        """Partition a query for parallel execution."""
        try:
            # Get total row count
            total_count = query.count()
            
            # Calculate number of partitions
            num_partitions = min(
                self.max_parallel_workers,
                (total_count + partition_size - 1) // partition_size
            )
            
            partitions = []
            for i in range(num_partitions):
                start = i * partition_size
                end = min((i + 1) * partition_size, total_count)
                size = end - start
                
                # Estimate complexity for this partition
                complexity = self._estimate_partition_complexity(query, start, end)
                
                partitions.append(QueryPartition(
                    start=start,
                    end=end,
                    size=size,
                    estimated_rows=size,
                    complexity=complexity
                ))
            
            return partitions
        except Exception as e:
            logger.error(f"Failed to partition query: {e}")
            return []

    def _estimate_partition_complexity(self, query: Query, start: int, end: int) -> float:
        """Estimate the complexity of a query partition."""
        try:
            # Get query components
            query_str = str(query.statement).lower()
            
            # Calculate base complexity
            complexity = 1.0
            
            # Adjust for joins
            if 'join' in query_str:
                complexity *= 1.5
            
            # Adjust for subqueries
            if 'select' in query_str and query_str.count('select') > 1:
                complexity *= 1.2
            
            # Adjust for aggregations
            if any(op in query_str for op in ['group by', 'having', 'sum(', 'count(', 'avg(']):
                complexity *= 1.3
            
            # Adjust for partition size
            partition_ratio = (end - start) / query.count()
            complexity *= partition_ratio
            
            return complexity
        except Exception as e:
            logger.error(f"Failed to estimate partition complexity: {e}")
            return 1.0

    def _execute_parallel(self, query: Query, strategy: ParallelStrategy = ParallelStrategy.PARTITION) -> List[Any]:
        """Execute a query in parallel."""
        if not self.enable_parallelization:
            return query.all()

        try:
            # Partition the query
            partitions = self._partition_query(query)
            if not partitions:
                return query.all()

            # Execute partitions in parallel
            futures = []
            for partition in partitions:
                # Create partition query
                partition_query = query.offset(partition.start).limit(partition.size)
                
                # Submit for execution
                future = self._parallel_executor.submit(partition_query.all)
                futures.append(future)
            
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception as e:
                    logger.error(f"Parallel execution failed: {e}")
            
            QUERY_PARALLEL.labels(type=strategy.value).inc()
            return results
        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            return query.all()

    def _monitor_stability(self):
        """Monitor query stability and adjust strategies accordingly."""
        while True:
            try:
                # Calculate stability score
                stability_score = self._calculate_stability_score()
                self._stats['stability_score'] = stability_score
                QUERY_STABILITY.labels(metric='score').set(stability_score)
                
                # Adjust strategies based on stability
                if stability_score < self.stability_threshold:
                    self._adjust_strategies_for_stability()
                
                time.sleep(self.stability_monitoring_interval)
            except Exception as e:
                logger.error(f"Stability monitoring failed: {e}")
                time.sleep(self.stability_monitoring_interval * 2)

    def _monitor_efficiency(self):
        """Monitor resource efficiency and optimize accordingly."""
        while True:
            try:
                # Calculate efficiency score
                efficiency_score = self._calculate_efficiency_score()
                self._stats['efficiency_score'] = efficiency_score
                QUERY_RESOURCE_USAGE.labels(type='overall').set(efficiency_score)
                
                # Optimize resource usage
                if efficiency_score < self.resource_efficiency_threshold:
                    self._optimize_resource_usage()
                
                time.sleep(self.efficiency_monitoring_interval)
            except Exception as e:
                logger.error(f"Efficiency monitoring failed: {e}")
                time.sleep(self.efficiency_monitoring_interval * 2)

    def _monitor_performance(self):
        """Monitor query performance and adjust optimizations."""
        while True:
            try:
                # Analyze performance metrics
                self._analyze_performance_metrics()
                
                # Adjust optimization strategies
                self._adjust_optimization_strategies()
                
                time.sleep(self.performance_monitoring_interval)
            except Exception as e:
                logger.error(f"Performance monitoring failed: {e}")
                time.sleep(self.performance_monitoring_interval * 2)

    def _monitor_resources(self):
        """Monitor system resources and adjust accordingly."""
        while True:
            try:
                # Monitor CPU usage
                cpu_percent = psutil.cpu_percent()
                QUERY_RESOURCE_USAGE.labels(type='cpu').set(cpu_percent)
                
                # Monitor memory usage
                memory_percent = psutil.Process().memory_percent()
                QUERY_RESOURCE_USAGE.labels(type='memory').set(memory_percent)
                
                # Monitor disk usage
                disk_percent = psutil.disk_usage('/').percent
                QUERY_RESOURCE_USAGE.labels(type='disk').set(disk_percent)
                
                # Adjust resource allocation
                self._adjust_resource_allocation(cpu_percent, memory_percent, disk_percent)
                
                time.sleep(self.resource_monitoring_interval)
            except Exception as e:
                logger.error(f"Resource monitoring failed: {e}")
                time.sleep(self.resource_monitoring_interval * 2)

    def _calculate_stability_score(self) -> float:
        """Calculate overall query stability score."""
        try:
            # Get recent query history
            recent_queries = list(self._query_history)[-100:]
            if not recent_queries:
                return 1.0
            
            # Calculate stability metrics
            execution_times = [q.execution_time for q in recent_queries if hasattr(q, 'execution_time')]
            if not execution_times:
                return 1.0
            
            # Calculate coefficient of variation
            mean_time = statistics.mean(execution_times)
            std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            cv = std_dev / mean_time if mean_time > 0 else 0
            
            # Calculate stability score (lower CV = higher stability)
            stability_score = 1 - min(1, cv)
            
            return stability_score
        except Exception as e:
            logger.error(f"Failed to calculate stability score: {e}")
            return 1.0

    def _calculate_efficiency_score(self) -> float:
        """Calculate resource efficiency score."""
        try:
            # Get resource usage metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.Process().memory_percent()
            disk_percent = psutil.disk_usage('/').percent
            
            # Calculate efficiency scores for each resource
            cpu_efficiency = 1 - (cpu_percent / 100)
            memory_efficiency = 1 - (memory_percent / 100)
            disk_efficiency = 1 - (disk_percent / 100)
            
            # Calculate weighted average
            efficiency_score = (
                cpu_efficiency * 0.4 +
                memory_efficiency * 0.4 +
                disk_efficiency * 0.2
            )
            
            return efficiency_score
        except Exception as e:
            logger.error(f"Failed to calculate efficiency score: {e}")
            return 1.0

    def _analyze_performance_metrics(self):
        """Analyze query performance metrics and adjust strategies."""
        try:
            # Get recent query profiles
            recent_profiles = list(self._query_profiles.values())[-100:]
            if not recent_profiles:
                return
            
            # Calculate performance metrics
            avg_execution_time = statistics.mean(p.avg_time for p in recent_profiles)
            max_execution_time = max(p.max_time for p in recent_profiles)
            min_execution_time = min(p.min_time for p in recent_profiles)
            std_dev_time = statistics.stdev(p.avg_time for p in recent_profiles) if len(recent_profiles) > 1 else 0
            
            # Update metrics
            QUERY_STATISTICS.labels(metric='avg_time').observe(avg_execution_time)
            QUERY_STATISTICS.labels(metric='max_time').observe(max_execution_time)
            QUERY_STATISTICS.labels(metric='min_time').observe(min_execution_time)
            QUERY_STATISTICS.labels(metric='std_dev').observe(std_dev_time)
            
            # Adjust optimization strategies based on performance
            if avg_execution_time > 1.0:  # More than 1 second
                self._increase_optimization_aggressiveness()
            elif avg_execution_time < 0.1:  # Less than 100ms
                self._decrease_optimization_aggressiveness()
        except Exception as e:
            logger.error(f"Failed to analyze performance metrics: {e}")

    def _adjust_resource_allocation(self, cpu_percent: float, memory_percent: float, disk_percent: float):
        """Adjust resource allocation based on current usage."""
        try:
            # Adjust thread pool size based on CPU usage
            if cpu_percent > 80:
                self._thread_pool._max_workers = max(2, self._thread_pool._max_workers - 1)
            elif cpu_percent < 20:
                self._thread_pool._max_workers = min(self.max_parallel_workers, self._thread_pool._max_workers + 1)
            
            # Adjust cache size based on memory usage
            if memory_percent > 80:
                self.result_cache_size = max(100, self.result_cache_size // 2)
            elif memory_percent < 20:
                self.result_cache_size = min(10000, self.result_cache_size * 2)
            
            # Adjust batch size based on disk usage
            if disk_percent > 80:
                self.max_batch_size = max(100, self.max_batch_size // 2)
            elif disk_percent < 20:
                self.max_batch_size = min(10000, self.max_batch_size * 2)
        except Exception as e:
            logger.error(f"Failed to adjust resource allocation: {e}")

    def _adjust_strategies_for_stability(self):
        """Adjust optimization strategies to improve stability."""
        try:
            # Reduce parallelization
            self.max_parallel_workers = max(2, self.max_parallel_workers - 1)
            
            # Increase batch size
            self.max_batch_size = min(10000, self.max_batch_size * 2)
            
            # Disable aggressive optimizations
            self.enable_query_hints = False
            self.enable_rewrite = False
            
            # Increase cache TTL
            self.result_cache_ttl = min(86400, self.result_cache_ttl * 2)
            
            # Log strategy adjustment
            logger.info("Adjusted optimization strategies for improved stability")
        except Exception as e:
            logger.error(f"Failed to adjust strategies for stability: {e}")

    def _optimize_resource_usage(self):
        """Optimize resource usage based on current efficiency."""
        try:
            # Clean up old cache entries
            self._cleanup_cache()
            
            # Refresh materialized views
            self._refresh_materialized_views()
            
            # Update statistics
            self._update_statistics()
            
            # Optimize indexes
            self._optimize_indexes()
            
            # Log optimization
            logger.info("Optimized resource usage")
        except Exception as e:
            logger.error(f"Failed to optimize resource usage: {e}")

    def _increase_optimization_aggressiveness(self):
        """Increase optimization aggressiveness for better performance."""
        try:
            # Enable more aggressive optimizations
            self.enable_query_hints = True
            self.enable_rewrite = True
            self.enable_parallelization = True
            
            # Increase parallel workers
            self.max_parallel_workers = min(20, self.max_parallel_workers + 2)
            
            # Reduce batch size
            self.max_batch_size = max(100, self.max_batch_size // 2)
            
            # Decrease cache TTL
            self.result_cache_ttl = max(60, self.result_cache_ttl // 2)
            
            # Log strategy adjustment
            logger.info("Increased optimization aggressiveness")
        except Exception as e:
            logger.error(f"Failed to increase optimization aggressiveness: {e}")

    def _decrease_optimization_aggressiveness(self):
        """Decrease optimization aggressiveness to reduce overhead."""
        try:
            # Disable aggressive optimizations
            self.enable_query_hints = False
            self.enable_rewrite = False
            self.enable_parallelization = False
            
            # Reduce parallel workers
            self.max_parallel_workers = max(2, self.max_parallel_workers - 2)
            
            # Increase batch size
            self.max_batch_size = min(10000, self.max_batch_size * 2)
            
            # Increase cache TTL
            self.result_cache_ttl = min(86400, self.result_cache_ttl * 2)
            
            # Log strategy adjustment
            logger.info("Decreased optimization aggressiveness")
        except Exception as e:
            logger.error(f"Failed to decrease optimization aggressiveness: {e}")

    def _cleanup_cache(self):
        """Clean up old cache entries."""
        try:
            with self._cache_lock:
                current_time = datetime.utcnow()
                expired_keys = [
                    key for key, cache in self._result_cache.items()
                    if current_time > cache.expires
                ]
                for key in expired_keys:
                    del self._result_cache[key]
                QUERY_RESOURCE_USAGE.labels(type='cleanup').inc(len(expired_keys))
        except Exception as e:
            logger.error(f"Failed to cleanup cache: {e}")

    def _refresh_materialized_views(self):
        """Refresh materialized views based on usage patterns."""
        try:
            with self._view_refresh_lock:
                current_time = datetime.utcnow()
                for view in self._materialized_views.values():
                    if current_time - view.last_refresh > timedelta(seconds=view.refresh_interval):
                        self._refresh_materialized_view(view.name)
        except Exception as e:
            logger.error(f"Failed to refresh materialized views: {e}")

    def _update_statistics(self):
        """Update database statistics for better query planning."""
        try:
            # Update table statistics
            self.db.execute(text("ANALYZE"))
            
            # Update index statistics
            self.db.execute(text("""
                SELECT schemaname, tablename, indexname
                FROM pg_indexes
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            """))
            
            # Log update
            logger.info("Updated database statistics")
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")

    def _optimize_indexes(self):
        """Optimize database indexes based on usage patterns."""
        try:
            # Get index usage statistics
            stats = self.db.execute(text("""
                SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes
            """)).fetchall()
            
            # Analyze and optimize indexes
            for stat in stats:
                usage = stat.idx_scan + stat.idx_tup_read + stat.idx_tup_fetch
                if usage == 0:  # Unused index
                    self.db.execute(text(f"""
                        DROP INDEX IF EXISTS {stat.schemaname}.{stat.indexname}
                    """))
        except Exception as e:
            logger.error(f"Failed to optimize indexes: {e}")

    def _run_optimizations(self):
        """Run periodic optimizations."""
        while True:
            try:
                # Run optimizations based on intervals
                current_time = datetime.utcnow()
                
                # Run pattern detection
                if current_time.second % self.pattern_detection_interval == 0:
                    self._detect_patterns()
                
                # Run plan analysis
                if current_time.second % self.plan_analysis_interval == 0:
                    self._analyze_query_plans()
                
                # Run view refresh
                if current_time.second % self.view_refresh_interval == 0:
                    self._refresh_materialized_views()
                
                # Run index maintenance
                if current_time.second % self.index_maintenance_interval == 0:
                    self._optimize_indexes()
                
                # Run statistics update
                if current_time.second % self.statistics_update_interval == 0:
                    self._update_statistics()
                
                time.sleep(1)
            except Exception as e:
                logger.error(f"Optimization run failed: {e}")
                time.sleep(60)

    def _analyze_query_plans(self):
        """Analyze and optimize query plans."""
        try:
            # Get recent queries
            recent_queries = list(self._query_history)[-100:]
            
            # Analyze each query
            for query in recent_queries:
                plan_analysis = self._analyze_query_plan(query)
                if plan_analysis and plan_analysis.optimization_score < 0.8:
                    self._optimize_query_plan(query, plan_analysis)
        except Exception as e:
            logger.error(f"Failed to analyze query plans: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced query optimizer statistics."""
        stats = {
            'total_queries': self._stats['total_queries'],
            'cache_hits': self._stats['cache_hits'],
            'cache_misses': self._stats['cache_misses'],
            'cache_hit_ratio': self._stats['cache_hits'] / max(1, self._stats['total_queries']),
            'errors': self._stats['errors'],
            'optimizations': self._stats['optimizations'],
            'stability_score': self._stats['stability_score'],
            'efficiency_score': self._stats['efficiency_score']
        }
        
        # Add plan analysis statistics
        plan_stats = {
            'plan_types': {},
            'average_optimization_score': 0.0,
            'memory_usage': psutil.Process().memory_info().rss,
            'concurrent_queries': self._concurrent_queries
        }
        
        # Calculate plan type distribution
        plan_types = [analysis.plan_type for analysis in self._query_history if analysis]
        if plan_types:
            for plan_type in QueryPlan:
                plan_stats['plan_types'][plan_type.value] = plan_types.count(plan_type) / len(plan_types)
            
            # Calculate average optimization score
            scores = [analysis.optimization_score for analysis in self._query_history if analysis]
            if scores:
                plan_stats['average_optimization_score'] = statistics.mean(scores)
        
        stats.update(plan_stats)
        
        # Add materialized view statistics
        view_stats = {
            'materialized_views': len(self._materialized_views),
            'valid_views': sum(1 for v in self._materialized_views.values() if v.is_valid),
            'total_view_size': sum(v.size_bytes for v in self._materialized_views.values())
        }
        
        # Add pattern detection statistics
        pattern_stats = {
            'detected_patterns': self._query_patterns,
            'cache_strategy': self.cache_strategy.value
        }
        
        stats.update(view_stats)
        stats.update(pattern_stats)
        
        # Add index recommendation statistics
        index_stats = {
            'recommendations': len(self._index_recommendations),
            'active_recommendations': sum(1 for r in self._index_recommendations.values() if r.usage_count > 0),
            'total_index_size': sum(r.size_estimate for r in self._index_recommendations.values())
        }
        
        # Add query profile statistics
        profile_stats = {
            'profiled_queries': len(self._query_profiles),
            'slow_queries': sum(1 for p in self._query_profiles.values() if p.avg_time > 100),
            'total_executions': sum(p.execution_count for p in self._query_profiles.values())
        }
        
        stats.update(index_stats)
        stats.update(profile_stats)
        
        # Add parallel execution statistics
        parallel_stats = {
            'parallel_queries': sum(1 for _ in self._parallel_executor._threads),
            'max_parallel_workers': self.max_parallel_workers,
            'active_workers': len(self._parallel_executor._threads)
        }
        
        # Add statistics analysis information
        analysis_stats = {
            'analyzed_tables': len(self._statistics_analysis),
            'advanced_statistics': sum(1 for a in self._statistics_analysis.values() 
                                     if a.type != StatisticsType.BASIC),
            'total_correlations': sum(1 for a in self._statistics_analysis.values() 
                                    if a.type == StatisticsType.CORRELATION)
        }
        
        stats.update(parallel_stats)
        stats.update(analysis_stats)
        
        # Add cache statistics
        cache_stats = {
            'cache_size': len(self._result_cache),
            'cache_hits': sum(cache.hits for cache in self._result_cache.values()),
            'cache_memory_usage': sum(cache.size for cache in self._result_cache.values())
        }
        
        # Add batch processing statistics
        batch_stats = {
            'total_batches': len(self._batch_profiles),
            'successful_batches': sum(1 for p in self._batch_profiles.values() if p.success_rate > 0.9),
            'average_batch_size': statistics.mean(p.size for p in self._batch_profiles.values()) if self._batch_profiles else 0
        }
        
        # Add error handling statistics
        error_stats = {
            'total_errors': sum(p.count for p in self._error_profiles.values()),
            'error_types': len(self._error_profiles),
            'retry_success_rate': statistics.mean(p.success_rate for p in self._error_profiles.values()) if self._error_profiles else 0
        }
        
        stats.update(cache_stats)
        stats.update(batch_stats)
        stats.update(error_stats)
        return stats 