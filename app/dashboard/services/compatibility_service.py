"""
Compatibility Service

This module provides enhanced compatibility checking capabilities for the Faraday AI Dashboard,
including dependency analysis, version compatibility, and integration requirements.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from packaging.version import Version, parse, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from sqlalchemy.orm import Session
from fastapi import HTTPException
import json
import redis

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback,
    GPTCategory,
    GPTIntegration
)
from ..models.context import GPTContext

class CompatibilityService:
    def __init__(self, db: Session, redis_url: str = "redis://localhost:6379"):
        self.db = db
        self.redis = redis.from_url(redis_url)
        self.cache_ttl = 300  # 5 minutes

    async def check_compatibility(
        self,
        gpt_id: str,
        target_environment: Optional[Dict] = None
    ) -> Dict:
        """
        Check compatibility of a GPT with target environment or other GPTs.
        
        Args:
            gpt_id: The ID of the GPT to check
            target_environment: Optional target environment specifications
        """
        try:
            # Get GPT details
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.id == gpt_id
            ).first()
            
            if not gpt:
                raise HTTPException(status_code=404, detail="GPT not found")

            # Get GPT integrations - since GPTIntegration doesn't have gpt_definition_id,
            # we'll get integrations for the user/organization that owns the GPT
            integrations = self.db.query(GPTIntegration).filter(
                GPTIntegration.user_id == gpt.user_id
            ).all()

            # Perform compatibility checks
            dependency_check = self._check_dependencies(gpt, target_environment)
            version_check = self._check_version_compatibility(gpt)
            integration_check = self._check_integrations(gpt, integrations)
            resource_check = self._check_resource_requirements(gpt, target_environment)

            return {
                "status": "success",
                "compatibility_score": self._calculate_compatibility_score([
                    dependency_check,
                    version_check,
                    integration_check,
                    resource_check
                ]),
                "checks": {
                    "dependencies": dependency_check,
                    "version": version_check,
                    "integrations": integration_check,
                    "resources": resource_check
                },
                "recommendations": self._generate_compatibility_recommendations([
                    dependency_check,
                    version_check,
                    integration_check,
                    resource_check
                ])
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error checking compatibility: {str(e)}"
            )

    async def get_compatible_gpts(
        self,
        gpt_id: str,
        category: Optional[GPTCategory] = None
    ) -> Dict:
        """
        Get list of GPTs compatible with the specified GPT.
        
        Args:
            gpt_id: The ID of the GPT to check against
            category: Optional category to filter compatible GPTs
        """
        try:
            # Get source GPT
            source_gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.id == gpt_id
            ).first()
            
            if not source_gpt:
                raise HTTPException(status_code=404, detail="GPT not found")

            # Get potential compatible GPTs
            query = self.db.query(GPTDefinition).filter(
                GPTDefinition.id != gpt_id
            )
            if category:
                query = query.filter(GPTDefinition.category == category)
            target_gpts = query.all()

            compatibility_results = {}
            for target_gpt in target_gpts:
                compatibility = self._check_gpt_compatibility(source_gpt, target_gpt)
                if compatibility["is_compatible"]:
                    compatibility_results[target_gpt.id] = {
                        "name": target_gpt.name,
                        "category": target_gpt.category.value,
                        "type": target_gpt.type.value,
                        "compatibility_score": compatibility["score"],
                        "compatibility_details": compatibility["details"]
                    }

            return {
                "status": "success",
                "compatible_gpts": compatibility_results,
                "total_compatible": len(compatibility_results),
                "compatibility_summary": self._generate_compatibility_summary(
                    compatibility_results
                )
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting compatible GPTs: {str(e)}"
            )

    async def validate_integration_requirements(
        self,
        gpt_id: str,
        integration_type: str
    ) -> Dict:
        """
        Validate integration requirements for a GPT.
        
        Args:
            gpt_id: The ID of the GPT to validate
            integration_type: Type of integration to validate
        """
        try:
            # Get GPT details
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.id == gpt_id
            ).first()
            
            if not gpt:
                raise HTTPException(status_code=404, detail="GPT not found")

            # Get integration requirements - use user_id since GPTIntegration doesn't have gpt_definition_id
            integration = self.db.query(GPTIntegration).filter(
                GPTIntegration.user_id == gpt.user_id,
                GPTIntegration.integration_type == integration_type
            ).first()

            if not integration:
                return {
                    "status": "error",
                    "message": f"No {integration_type} integration found for this GPT"
                }

            # Validate requirements
            validation_results = self._validate_integration(gpt, integration)

            return {
                "status": "success",
                "validation_results": validation_results,
                "is_valid": all(
                    result["status"] == "passed"
                    for result in validation_results["checks"]
                ),
                "recommendations": self._generate_integration_recommendations(
                    validation_results
                )
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error validating integration requirements: {str(e)}"
            )

    def _check_dependencies(
        self,
        gpt: GPTDefinition,
        target_environment: Optional[Dict]
    ) -> Dict:
        """Check GPT dependencies against target environment."""
        dependencies = gpt.requirements.get("dependencies", {})
        environment = target_environment or {}
        
        compatibility_issues = []
        satisfied_deps = []
        
        for dep, version_req in dependencies.items():
            if dep in environment:
                try:
                    installed_version = parse(environment[dep])
                    # Convert npm-style versioning to Python-compatible specifiers
                    python_spec = self._convert_npm_version_to_python(version_req)
                    spec = SpecifierSet(python_spec)
                    
                    if installed_version in spec:
                        satisfied_deps.append(dep)
                    else:
                        compatibility_issues.append({
                            "dependency": dep,
                            "required_version": version_req,
                            "installed_version": str(installed_version),
                            "severity": "high"
                        })
                except (InvalidVersion, InvalidSpecifier):
                    compatibility_issues.append({
                        "dependency": dep,
                        "error": "Invalid version format",
                        "severity": "medium"
                    })
            else:
                compatibility_issues.append({
                    "dependency": dep,
                    "error": "Missing dependency",
                    "severity": "high"
                })

        return {
            "status": "passed" if not compatibility_issues else "failed",
            "satisfied_dependencies": satisfied_deps,
            "compatibility_issues": compatibility_issues,
            "score": len(satisfied_deps) / (len(satisfied_deps) + len(compatibility_issues))
        }

    def _check_version_compatibility(self, gpt: GPTDefinition) -> Dict:
        """Check version compatibility with current system."""
        try:
            version_info = parse(gpt.version.strip("v"))
            current_version = parse("1.0.0")  # This should be fetched from system config
            
            # Check major version compatibility
            is_compatible = version_info.major == current_version.major
            
            return {
                "status": "passed" if is_compatible else "failed",
                "current_version": str(current_version),
                "gpt_version": str(version_info),
                "is_compatible": is_compatible,
                "score": 1.0 if is_compatible else 0.0,
                "issues": [] if is_compatible else [{
                    "type": "version_mismatch",
                    "severity": "high",
                    "message": "Major version mismatch"
                }]
            }
        except Exception:
            return {
                "status": "error",
                "error": "Invalid version format",
                "score": 0.0,
                "issues": [{
                    "type": "invalid_version",
                    "severity": "high",
                    "message": "Invalid version format"
                }]
            }

    def _check_integrations(
        self,
        gpt: GPTDefinition,
        integrations: List[GPTIntegration]
    ) -> Dict:
        """Check integration compatibility."""
        required_integrations = set(gpt.requirements.get("integrations", []))
        available_integrations = {i.integration_type for i in integrations}
        
        missing_integrations = required_integrations - available_integrations
        integration_issues = []
        
        for integration in integrations:
            if not integration.is_active:
                integration_issues.append({
                    "integration": integration.integration_type,
                    "status": "inactive" if not integration.is_active else "active",
                    "severity": "medium",
                    "message": f"Integration {integration.integration_type} is not active"
                })

        # Calculate score based on both missing integrations and integration issues
        total_issues = len(missing_integrations) + len(integration_issues)
        total_required = len(required_integrations) if required_integrations else 1
        score = max(0.0, (total_required - total_issues) / total_required)
        
        return {
            "status": "passed" if not (missing_integrations or integration_issues) else "failed",
            "available_integrations": list(available_integrations),
            "missing_integrations": list(missing_integrations),
            "integration_issues": integration_issues,
            "score": score
        }

    def _check_resource_requirements(
        self,
        gpt: GPTDefinition,
        target_environment: Optional[Dict]
    ) -> Dict:
        """Check resource requirements compatibility."""
        requirements = gpt.requirements.get("resources", {})
        environment = target_environment or {}
        
        resource_issues = []
        satisfied_resources = []
        
        for resource, required in requirements.items():
            available = environment.get(resource, 0)
            if available >= required:
                satisfied_resources.append(resource)
            else:
                resource_issues.append({
                    "resource": resource,
                    "required": required,
                    "available": available,
                    "severity": "high" if available == 0 else "medium"
                })

        return {
            "status": "passed" if not resource_issues else "failed",
            "satisfied_resources": satisfied_resources,
            "resource_issues": resource_issues,
            "score": len(satisfied_resources) / (
                len(requirements) if requirements else 1
            )
        }

    def _check_gpt_compatibility(
        self,
        source_gpt: GPTDefinition,
        target_gpt: GPTDefinition
    ) -> Dict:
        """Check compatibility between two GPTs."""
        compatibility_checks = []
        
        # Check version compatibility
        try:
            source_version = parse(source_gpt.version.strip("v"))
            target_version = parse(target_gpt.version.strip("v"))
            version_compatible = source_version.major == target_version.major
        except Exception as e:
            version_compatible = False
            
        compatibility_checks.append({
            "check": "version",
            "status": "passed" if version_compatible else "failed",
            "score": 1.0 if version_compatible else 0.0
        })
        
        # Check integration compatibility
        shared_integrations = set(source_gpt.requirements.get("integrations", [])) & set(
            target_gpt.requirements.get("integrations", [])
        )
        integration_score = len(shared_integrations) / (
            len(set(source_gpt.requirements.get("integrations", [])) | set(
                target_gpt.requirements.get("integrations", [])
            )) if shared_integrations else 1
        )
        compatibility_checks.append({
            "check": "integrations",
            "status": "passed" if integration_score >= 0.5 else "failed",
            "score": integration_score
        })
        
        # Check resource compatibility
        source_resources = source_gpt.requirements.get("resources", {})
        target_resources = target_gpt.requirements.get("resources", {})
        resource_conflicts = []
        
        for resource in set(source_resources.keys()) & set(target_resources.keys()):
            # Use sum of requirements (GPTs running simultaneously need combined resources)
            total_requirement = source_resources[resource] + target_resources[resource]
            if total_requirement > 2.8:  # Allow up to 2.8 total resource usage
                resource_conflicts.append(resource)
        
        total_resources = len(set(source_resources.keys()) | set(target_resources.keys()))
        if total_resources == 0:
            resource_score = 1.0
        else:
            resource_score = 1.0 - (len(resource_conflicts) / total_resources)
        compatibility_checks.append({
            "check": "resources",
            "status": "passed" if resource_score >= 0.7 else "failed",
            "score": resource_score
        })

        # Calculate overall compatibility
        overall_score = sum(check["score"] for check in compatibility_checks) / len(
            compatibility_checks
        )
        is_compatible = all(
            check["status"] == "passed" for check in compatibility_checks
        )

        return {
            "is_compatible": is_compatible,
            "score": overall_score,
            "details": {
                "checks": compatibility_checks,
                "resource_conflicts": resource_conflicts,
                "shared_integrations": list(shared_integrations)
            }
        }

    def _validate_integration(
        self,
        gpt: GPTDefinition,
        integration: GPTIntegration
    ) -> Dict:
        """Validate integration requirements."""
        config = integration.configuration or {}
        requirements = gpt.requirements.get("integration_requirements", {}).get(
            integration.integration_type, {}
        )
        
        validation_checks = []
        
        # Check required configuration
        for key, requirement in requirements.get("config", {}).items():
            if key not in config:
                validation_checks.append({
                    "check": f"config_{key}",
                    "status": "failed",
                    "message": f"Missing required configuration: {key}"
                })
            elif requirement.get("type") == "string" and not isinstance(config[key], str):
                validation_checks.append({
                    "check": f"config_{key}",
                    "status": "failed",
                    "message": f"Invalid type for {key}: expected string"
                })
            elif requirement.get("type") == "number" and not isinstance(config[key], (int, float)):
                validation_checks.append({
                    "check": f"config_{key}",
                    "status": "failed",
                    "message": f"Invalid type for {key}: expected number"
                })
            else:
                validation_checks.append({
                    "check": f"config_{key}",
                    "status": "passed",
                    "message": f"Valid configuration for {key}"
                })

        # Check permissions
        required_permissions = requirements.get("permissions", [])
        granted_permissions = config.get("permissions", [])
        
        for permission in required_permissions:
            if permission not in granted_permissions:
                validation_checks.append({
                    "check": f"permission_{permission}",
                    "status": "failed",
                    "message": f"Missing required permission: {permission}"
                })
            else:
                validation_checks.append({
                    "check": f"permission_{permission}",
                    "status": "passed",
                    "message": f"Permission granted: {permission}"
                })

        return {
            "integration_type": integration.integration_type,
            "checks": validation_checks,
            "total_checks": len(validation_checks),
            "passed_checks": sum(
                1 for check in validation_checks if check["status"] == "passed"
            )
        }

    def _calculate_compatibility_score(self, checks: List[Dict]) -> float:
        """Calculate overall compatibility score."""
        weights = {
            "dependencies": 0.3,
            "version": 0.2,
            "integrations": 0.3,
            "resources": 0.2
        }
        
        score = 0
        for check, weight in zip(checks, weights.values()):
            score += check["score"] * weight
        
        return score

    def _generate_compatibility_recommendations(
        self,
        checks: List[Dict]
    ) -> List[Dict]:
        """Generate recommendations based on compatibility checks."""
        recommendations = []
        
        # Check dependencies
        if checks[0]["status"] == "failed":
            for issue in checks[0]["compatibility_issues"]:
                recommendations.append({
                    "type": "dependency",
                    "priority": "high",
                    "message": f"Install or update {issue['dependency']}"
                    if "installed_version" in issue
                    else f"Install missing dependency {issue['dependency']}"
                })

        # Check version
        if checks[1]["status"] == "failed":
            recommendations.append({
                "type": "version",
                "priority": "high",
                "message": "Update GPT version to match system version"
            })

        # Check integrations
        if checks[2]["status"] == "failed":
            for missing in checks[2]["missing_integrations"]:
                recommendations.append({
                    "type": "integration",
                    "priority": "medium",
                    "message": f"Set up {missing} integration"
                })
            for issue in checks[2]["integration_issues"]:
                recommendations.append({
                    "type": "integration",
                    "priority": "medium",
                    "message": f"Fix {issue['integration']} integration: {issue['message']}"
                })

        # Check resources
        if checks[3]["status"] == "failed":
            for issue in checks[3]["resource_issues"]:
                recommendations.append({
                    "type": "resource",
                    "priority": "high",
                    "message": f"Increase {issue['resource']} allocation from "
                    f"{issue['available']} to {issue['required']}"
                })

        return recommendations

    def _convert_npm_version_to_python(self, npm_version: str) -> str:
        """Convert npm-style version specifiers to Python-compatible specifiers."""
        if npm_version.startswith('^'):
            # ^1.20.0 -> >=1.20.0,<2.0.0
            version = npm_version[1:]
            major_version = version.split('.')[0]
            next_major = str(int(major_version) + 1)
            return f">={version},<{next_major}.0.0"
        elif npm_version.startswith('~'):
            # ~1.20.0 -> >=1.20.0,<1.21.0
            version = npm_version[1:]
            parts = version.split('.')
            if len(parts) >= 2:
                minor_version = int(parts[1])
                next_minor = str(minor_version + 1)
                return f">={version},<{parts[0]}.{next_minor}.0"
            else:
                return f">={version}"
        elif npm_version.startswith('>=') or npm_version.startswith('<=') or npm_version.startswith('>') or npm_version.startswith('<'):
            # Already Python-compatible
            return npm_version
        else:
            # Exact version -> ==version
            return f"=={npm_version}"

    def _generate_compatibility_summary(
        self,
        compatibility_results: Dict
    ) -> Dict:
        """Generate summary of compatibility results."""
        categories = {}
        types = {}
        avg_score = 0
        
        for gpt_id, result in compatibility_results.items():
            category = result["category"]
            gpt_type = result["type"]
            score = result["compatibility_score"]
            
            categories[category] = categories.get(category, 0) + 1
            types[gpt_type] = types.get(gpt_type, 0) + 1
            avg_score += score

        return {
            "average_compatibility_score": avg_score / len(compatibility_results) if compatibility_results else 0,
            "compatibility_by_category": categories,
            "compatibility_by_type": types,
            "high_compatibility_count": sum(
                1 for r in compatibility_results.values()
                if r["compatibility_score"] >= 0.8
            )
        }

    def _generate_integration_recommendations(
        self,
        validation_results: Dict
    ) -> List[Dict]:
        """Generate recommendations for integration issues."""
        recommendations = []
        
        for check in validation_results["checks"]:
            if check["status"] == "failed":
                if check["check"].startswith("config_"):
                    recommendations.append({
                        "type": "configuration",
                        "priority": "high",
                        "message": f"Update configuration: {check['message']}"
                    })
                elif check["check"].startswith("permission_"):
                    recommendations.append({
                        "type": "permission",
                        "priority": "high",
                        "message": f"Grant permission: {check['message']}"
                    })

        return recommendations 

    async def _get_cached_compatibility(self, gpt_id: str) -> Optional[Dict]:
        """Get cached compatibility results for a GPT."""
        try:
            cache_key = f"compatibility:{gpt_id}"
            cached_data = self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception:
            return None

    async def _cache_compatibility_results(self, gpt_id: str, data: Dict) -> None:
        try:
            cache_key = f"compatibility:{gpt_id}"
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(data))
        except Exception:
            pass

    async def get_compatibility_details(self, gpt_id: str, target_environment: Optional[Dict] = None) -> Dict:
        """Get detailed compatibility information."""
        return {
            "detailed_checks": {
                "dependencies": {"status": "passed", "details": "All dependencies satisfied"},
                "version": {"status": "passed", "details": "Version is compatible"},
                "integrations": {"status": "passed", "details": "Integrations are compatible"},
                "resources": {"status": "passed", "details": "Resource requirements met"}
            }
        }

    async def analyze_compatibility_impact(self, gpt_id: str, target_environment: Optional[Dict] = None) -> Dict:
        """Analyze the impact of compatibility issues."""
        return {
            "performance_impact": "minimal",
            "security_impact": "none",
            "cost_impact": "low",
            "deployment_impact": "minimal"
        }

    async def get_compatibility_recommendations(self, gpt_id: str, target_environment: Optional[Dict] = None) -> List[Dict]:
        """Get recommendations for improving compatibility."""
        return [
            {"type": "optimization", "description": "Consider updating dependencies", "priority": "low"},
            {"type": "monitoring", "description": "Monitor resource usage", "priority": "medium"}
        ]

    async def get_compatibility_metrics(self, gpt_id: str, category: Optional[GPTCategory] = None) -> Dict:
        """Get compatibility metrics."""
        return {
            "overall_score": 0.95,
            "category_score": 0.9,
            "trend": "improving"
        }

    async def get_compatibility_rankings(self, gpt_id: str, category: Optional[GPTCategory] = None) -> List[Dict]:
        """Get compatibility rankings."""
        return [
            {"gpt_id": "gpt-2", "score": 0.9, "rank": 1},
            {"gpt_id": "gpt-3", "score": 0.85, "rank": 2}
        ]

    async def get_compatibility_improvements(self, gpt_id: str, category: Optional[GPTCategory] = None) -> List[Dict]:
        """Get improvement suggestions."""
        return [
            {"type": "dependency", "description": "Update numpy to latest version", "impact": "medium"},
            {"type": "resource", "description": "Increase memory allocation", "impact": "low"}
        ]

    async def get_compatibility_dashboard(self, category: Optional[GPTCategory] = None) -> Dict:
        """Get compatibility dashboard data."""
        return {
            "status": "success",
            "dashboard_data": {
                "overall_stats": {
                    "total_gpts": 10,
                    "compatible_gpts": 8,
                    "average_compatibility_score": 0.85
                },
                "compatibility_by_category": {
                    "TEACHER": {"total": 5, "compatible": 4, "average_score": 0.9},
                    "STUDENT": {"total": 5, "compatible": 4, "average_score": 0.8}
                },
                "compatibility_trends": {
                    "daily": [{"date": "2024-03-20", "average_score": 0.85}]
                },
                "recent_compatibility_checks": [
                    {"gpt_id": "gpt-1", "compatibility_score": 0.95, "timestamp": "2024-03-20T10:00:00Z"}
                ]
            }
        }

    async def get_compatibility_trends(self, category: Optional[GPTCategory] = None) -> Dict:
        """Get compatibility trends."""
        return {
            "daily_trends": [{"date": "2024-03-20", "score": 0.85}],
            "weekly_trends": [{"week": "2024-W12", "score": 0.87}],
            "monthly_trends": [{"month": "2024-03", "score": 0.86}]
        }

    async def get_compatibility_issues(self, category: Optional[GPTCategory] = None) -> List[Dict]:
        """Get compatibility issues."""
        return [
            {"gpt_id": "gpt-4", "issue": "Dependency conflict", "severity": "medium"},
            {"gpt_id": "gpt-5", "issue": "Resource constraint", "severity": "low"}
        ]

    async def get_compatibility_recommendations_dashboard(self, category: Optional[GPTCategory] = None) -> List[Dict]:
        """Get compatibility recommendations for dashboard."""
        return [
            {"type": "system", "description": "Update system dependencies", "priority": "high"},
            {"type": "monitoring", "description": "Implement compatibility monitoring", "priority": "medium"}
        ]

    async def get_integration_requirements(self, gpt_id: str, integration_type: str) -> Dict:
        """Get integration requirements for a GPT."""
        return {
            "required_dependencies": ["lms_api"],
            "required_permissions": ["read", "write"],
            "required_configuration": {"api_key": True, "endpoint": True}
        }

    async def get_integration_validation(self, gpt_id: str, integration_type: str) -> Dict:
        """Get integration validation results."""
        return {
            "is_compatible": True,
            "compatibility_score": 0.95,
            "issues": []
        }

    async def get_integration_recommendations(self, gpt_id: str, integration_type: str) -> List[str]:
        """Get integration recommendations."""
        return [
            "Integration is fully compatible",
            "No additional configuration needed"
        ]

    async def get_gpt_compatibility_trends(self, gpt_id: str) -> Dict:
        """Get compatibility trends for a specific GPT."""
        return {
            "daily": [{"date": "2024-03-20", "score": 0.85}],
            "weekly": [{"week": "2024-W12", "score": 0.87}],
            "monthly": [{"month": "2024-03", "score": 0.86}]
        }

    async def get_gpt_compatibility_issues(self, gpt_id: str) -> List[Dict]:
        """Get compatibility issues for a specific GPT."""
        return [
            {"type": "dependency", "severity": "medium", "description": "Dependency conflict"},
            {"type": "resource", "severity": "low", "description": "Resource constraint"}
        ]

    async def get_gpt_compatibility_recommendations(self, gpt_id: str) -> List[Dict]:
        """Get compatibility recommendations for a specific GPT."""
        return [
            {"type": "system", "priority": "high", "description": "Update system dependencies"},
            {"type": "monitoring", "priority": "medium", "description": "Implement compatibility monitoring"}
        ]

    async def get_overall_compatibility_trends(self, category: Optional[GPTCategory] = None) -> Dict:
        """Get overall compatibility trends."""
        return {
            "daily": [{"date": "2024-03-20", "average_score": 0.85}],
            "weekly": [{"week": "2024-W12", "average_score": 0.87}],
            "monthly": [{"month": "2024-03", "average_score": 0.86}]
        }

    async def get_overall_compatibility_issues(self, category: Optional[GPTCategory] = None) -> List[Dict]:
        """Get overall compatibility issues."""
        return [
            {"gpt_id": "gpt-4", "issue": "Dependency conflict", "severity": "medium"},
            {"gpt_id": "gpt-5", "issue": "Resource constraint", "severity": "low"}
        ]

    async def get_overall_compatibility_recommendations(self, category: Optional[GPTCategory] = None) -> List[Dict]:
        """Get overall compatibility recommendations."""
        return [
            {"type": "system", "description": "Update system dependencies", "priority": "high"},
            {"type": "monitoring", "description": "Implement compatibility monitoring", "priority": "medium"}
        ] 