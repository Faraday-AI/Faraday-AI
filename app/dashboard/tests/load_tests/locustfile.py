"""
Load testing script for the compatibility service using Locust.
"""

from locust import HttpUser, task, between
import random
import json

class CompatibilityUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Initialize test data."""
        self.gpt_ids = [f"gpt-{i}" for i in range(1, 6)]
        self.categories = ["TEACHER", "STUDENT", "ADMIN"]
        self.integration_types = ["lms", "analytics", "assessment"]
        self.target_environment = {
            "numpy": "1.21.0",
            "pandas": "1.3.2",
            "memory": 4.0,
            "cpu": 2.0
        }
    
    @task(3)
    def check_compatibility(self):
        """Test compatibility check endpoint."""
        gpt_id = random.choice(self.gpt_ids)
        self.client.post(
            f"/compatibility/check/{gpt_id}",
            json={"target_environment": self.target_environment}
        )
    
    @task(2)
    def get_compatible_gpts(self):
        """Test getting compatible GPTs endpoint."""
        gpt_id = random.choice(self.gpt_ids)
        category = random.choice(self.categories)
        self.client.get(
            f"/compatibility/compatible/{gpt_id}",
            params={"category": category}
        )
    
    @task(2)
    def validate_integration(self):
        """Test integration validation endpoint."""
        gpt_id = random.choice(self.gpt_ids)
        integration_type = random.choice(self.integration_types)
        self.client.post(
            f"/compatibility/validate-integration",
            json={
                "gpt_id": gpt_id,
                "integration_type": integration_type
            }
        )
    
    @task(1)
    def get_dashboard(self):
        """Test dashboard endpoint."""
        category = random.choice(self.categories)
        self.client.get(
            "/compatibility/dashboard",
            params={"category": category}
        )

class HighLoadUser(CompatibilityUser):
    """User class for high-load scenarios."""
    wait_time = between(0.1, 0.5)  # Aggressive timing
    
    @task(5)
    def rapid_compatibility_checks(self):
        """Rapid compatibility checks."""
        for _ in range(3):
            gpt_id = random.choice(self.gpt_ids)
            self.client.post(
                f"/compatibility/check/{gpt_id}",
                json={"target_environment": self.target_environment}
            )
    
    @task(3)
    def bulk_integration_validation(self):
        """Bulk integration validation."""
        gpt_id = random.choice(self.gpt_ids)
        for integration_type in self.integration_types:
            self.client.post(
                f"/compatibility/validate-integration",
                json={
                    "gpt_id": gpt_id,
                    "integration_type": integration_type
                }
            )

class CacheTestUser(CompatibilityUser):
    """User class for testing cache effectiveness."""
    wait_time = between(0.5, 1.5)
    
    def on_start(self):
        super().on_start()
        self.cached_gpt_id = "gpt-1"  # Use same GPT ID to test caching
    
    @task(4)
    def test_cache_hit(self):
        """Test cache hit rate."""
        self.client.post(
            f"/compatibility/check/{self.cached_gpt_id}",
            json={"target_environment": self.target_environment}
        )
    
    @task(1)
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        # First request should cache
        self.client.post(
            f"/compatibility/check/{self.cached_gpt_id}",
            json={"target_environment": self.target_environment}
        )
        # Modified environment to force cache invalidation
        modified_env = dict(self.target_environment)
        modified_env["memory"] = 8.0
        self.client.post(
            f"/compatibility/check/{self.cached_gpt_id}",
            json={"target_environment": modified_env}
        ) 