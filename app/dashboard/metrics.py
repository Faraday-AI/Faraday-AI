"""
Prometheus Metrics

This module defines Prometheus metrics used throughout the dashboard application.
"""

from prometheus_client import Gauge, Counter, Histogram

# GPT Manager metrics
GPT_TOOL_COUNT = Gauge("gpt_tool_count", "Number of active GPT tools per user", ["user_id"])
GPT_COMMAND_LATENCY = Histogram("gpt_command_latency_seconds", "Latency of GPT command processing")
GPT_COMMAND_COUNT = Counter("gpt_command_count", "Number of GPT commands processed", ["status"])
GPT_TOOL_ERRORS = Counter("gpt_tool_errors", "Number of GPT tool errors", ["tool_name"]) 