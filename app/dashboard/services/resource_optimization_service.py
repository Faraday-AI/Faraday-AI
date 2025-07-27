"""
Resource Optimization Service

This module provides AI-driven resource optimization capabilities for organizations
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from fastapi import HTTPException

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback,
    GPTCategory
)
from ..models.context import GPTContext
from .analytics_service import AnalyticsService
from ..models.organization_models import (
    Organization,
    OrganizationResource,
    OrganizationMember
)

class ResourceOptimizationService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    async def optimize_resources(
        self,
        gpt_id: str,
        optimization_target: str
    ) -> Dict[str, Any]:
        """Optimize resources for a specific GPT."""
        try:
            # Get GPT definition
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.id == gpt_id
            ).first()
            
            if not gpt:
                raise HTTPException(
                    status_code=404,
                    detail=f"GPT {gpt_id} not found"
                )

            # Get usage predictions
            usage_prediction = await self._get_gpt_usage_prediction(gpt_id)
            
            # Get performance trends
            performance_trends = await self._get_gpt_performance_trends(gpt_id)
            
            # Calculate optimization plan
            optimization_plan = self._calculate_optimization_plan(
                usage_prediction,
                performance_trends,
                optimization_target
            )
            
            # Generate scaling recommendations
            scaling_recommendations = self._generate_scaling_recommendations(
                optimization_plan,
                usage_prediction["predictions"]
            )
            
            # Estimate improvements
            estimated_improvements = self._estimate_improvements(
                optimization_plan,
                performance_trends
            )

            return {
                "status": "success",
                "optimization_plan": optimization_plan,
                "scaling_recommendations": scaling_recommendations,
                "estimated_improvements": estimated_improvements
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing resources: {str(e)}"
            )

    async def get_optimization_history(
        self,
        org_id: str,
        time_range: str = "30d"
    ) -> List[Dict[str, Any]]:
        """Get historical optimization data and results."""
        try:
            # Convert time range to timedelta
            time_delta = self._parse_time_range(time_range)
            start_time = datetime.utcnow() - time_delta

            # Get historical optimization records
            # This would typically come from a dedicated table
            # For now, we'll simulate the data
            history = await self._simulate_optimization_history(org_id, start_time)

            return history

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving optimization history: {str(e)}"
            )

    async def predict_resource_needs(
        self,
        org_id: str,
        prediction_window: str = "7d"
    ) -> Dict[str, Any]:
        """Predict future resource needs using AI models."""
        try:
            # Get historical resource usage data
            usage_data = await self._get_historical_usage(org_id)

            # Generate predictions
            predictions = await self._generate_resource_predictions(
                usage_data,
                prediction_window
            )

            # Generate confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(
                predictions
            )

            # Generate recommendations based on predictions
            recommendations = await self._generate_predictive_recommendations(
                predictions,
                confidence_intervals
            )

            return {
                "predictions": predictions,
                "confidence_intervals": confidence_intervals,
                "recommendations": recommendations
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error predicting resource needs: {str(e)}"
            )

    async def get_optimization_dashboard(
        self,
        time_window: str = "24h",
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get optimization dashboard data."""
        try:
            # Get all GPTs
            query = self.db.query(GPTDefinition)
            if category:
                query = query.filter(GPTDefinition.category == category)
            
            gpts = query.all()
            
            dashboard_data = {
                "status": "success",
                "total_gpts": len(gpts),
                "optimization_summary": {
                    "high_priority": 0,
                    "medium_priority": 0,
                    "low_priority": 0
                },
                "resource_utilization": {
                    "average_cpu": 0.75,
                    "average_memory": 0.65,
                    "peak_usage": 0.85
                },
                "cost_analysis": {
                    "total_cost": 1000.0,
                    "potential_savings": 150.0,
                    "optimization_opportunities": 5
                },
                "performance_metrics": {
                    "average_response_time": 1.2,
                    "success_rate": 0.95,
                    "error_rate": 0.05
                }
            }
            
            return dashboard_data

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting optimization dashboard: {str(e)}"
            )

    async def _analyze_resource_utilization(
        self,
        resources: List[OrganizationResource]
    ) -> Dict[str, Any]:
        """Analyze current resource utilization patterns."""
        utilization = {
            "by_type": {},
            "by_status": {},
            "efficiency_scores": {},
            "bottlenecks": [],
            "underutilized": []
        }

        # Group resources by type
        for resource in resources:
            # Calculate utilization metrics
            resource_metrics = await self._calculate_resource_metrics(resource)
            
            # Update utilization data
            if resource.resource_type not in utilization["by_type"]:
                utilization["by_type"][resource.resource_type] = []
            utilization["by_type"][resource.resource_type].append(resource_metrics)
            
            # Track status
            if resource.status not in utilization["by_status"]:
                utilization["by_status"][resource.status] = 0
            utilization["by_status"][resource.status] += 1
            
            # Calculate efficiency score
            efficiency_score = await self._calculate_efficiency_score(resource)
            utilization["efficiency_scores"][resource.id] = efficiency_score
            
            # Identify bottlenecks and underutilization
            if efficiency_score < 0.3:
                utilization["underutilized"].append(resource.id)
            elif efficiency_score > 0.9:
                utilization["bottlenecks"].append(resource.id)

        return utilization

    async def _generate_optimization_recommendations(
        self,
        resources: List[OrganizationResource],
        utilization: Dict[str, Any],
        optimization_type: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate AI-driven optimization recommendations."""
        recommendations = []

        # Process based on optimization type
        if optimization_type == "cost":
            recommendations.extend(
                await self._generate_cost_optimization_recommendations(
                    resources,
                    utilization,
                    constraints
                )
            )
        elif optimization_type == "performance":
            recommendations.extend(
                await self._generate_performance_optimization_recommendations(
                    resources,
                    utilization,
                    constraints
                )
            )
        elif optimization_type == "efficiency":
            recommendations.extend(
                await self._generate_efficiency_optimization_recommendations(
                    resources,
                    utilization,
                    constraints
                )
            )

        return recommendations

    async def _calculate_optimization_impact(
        self,
        resources: List[OrganizationResource],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate potential impact of optimization recommendations."""
        impact = {
            "cost_savings": 0.0,
            "performance_improvement": 0.0,
            "efficiency_gain": 0.0,
            "resource_reduction": 0,
            "bottleneck_reduction": 0,
            "risks": []
        }

        for recommendation in recommendations:
            # Calculate various impact metrics
            if recommendation.get("type") == "cost_optimization":
                impact["cost_savings"] += recommendation.get("estimated_savings", 0)
            elif recommendation.get("type") == "performance_optimization":
                impact["performance_improvement"] += recommendation.get("estimated_improvement", 0)
            elif recommendation.get("type") == "efficiency_optimization":
                impact["efficiency_gain"] += recommendation.get("estimated_efficiency_gain", 0)

            # Track resource changes
            if recommendation.get("action") == "remove":
                impact["resource_reduction"] += 1
            elif recommendation.get("action") == "scale_down":
                impact["resource_reduction"] += 0.5

            # Track bottleneck reduction
            if recommendation.get("addresses_bottleneck"):
                impact["bottleneck_reduction"] += 1

            # Track potential risks
            if "risks" in recommendation:
                impact["risks"].extend(recommendation["risks"])

        return impact

    async def _generate_implementation_plan(
        self,
        recommendations: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a phased implementation plan for recommendations."""
        # Sort recommendations by priority and impact
        prioritized_recommendations = sorted(
            recommendations,
            key=lambda x: (x.get("priority", 0), x.get("impact", 0)),
            reverse=True
        )

        # Generate implementation phases
        phases = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }

        for recommendation in prioritized_recommendations:
            # Determine phase based on complexity and dependencies
            phase = self._determine_implementation_phase(
                recommendation,
                constraints
            )
            phases[phase].append(recommendation)

        return {
            "phases": phases,
            "timeline": self._generate_implementation_timeline(phases),
            "dependencies": self._identify_implementation_dependencies(phases),
            "risks": self._assess_implementation_risks(phases)
        }

    def _parse_time_range(self, time_range: str) -> timedelta:
        """Convert time range string to timedelta."""
        try:
            value = int(time_range[:-1])
            unit = time_range[-1].lower()
            
            if unit == "h":
                return timedelta(hours=value)
            elif unit == "d":
                return timedelta(days=value)
            elif unit == "w":
                return timedelta(weeks=value)
            elif unit == "m":
                return timedelta(days=value * 30)
            else:
                raise ValueError(f"Invalid time unit: {unit}")
        except Exception as e:
            raise ValueError(f"Invalid time range format: {time_range}")

    async def _calculate_resource_metrics(
        self,
        resource: OrganizationResource
    ) -> Dict[str, Any]:
        """Calculate detailed metrics for a resource."""
        return {
            "id": resource.id,
            "type": resource.resource_type,
            "status": resource.status,
            "utilization": await self._calculate_utilization_rate(resource),
            "efficiency": await self._calculate_efficiency_score(resource),
            "cost": await self._calculate_resource_cost(resource),
            "performance": await self._calculate_performance_metrics(resource)
        }

    async def _calculate_utilization_rate(
        self,
        resource: OrganizationResource
    ) -> float:
        """Calculate resource utilization rate."""
        # This would typically involve analyzing usage logs and metrics
        # For now, return a simulated value
        return np.random.uniform(0.3, 0.9)

    async def _calculate_efficiency_score(
        self,
        resource: OrganizationResource
    ) -> float:
        """Calculate resource efficiency score."""
        # This would typically involve analyzing performance metrics
        # For now, return a simulated value
        return np.random.uniform(0.4, 0.95)

    async def _calculate_resource_cost(
        self,
        resource: OrganizationResource
    ) -> Dict[str, float]:
        """Calculate resource cost metrics."""
        # This would typically involve analyzing billing data
        # For now, return simulated values
        return {
            "hourly_cost": np.random.uniform(0.5, 5.0),
            "monthly_cost": np.random.uniform(100, 1000),
            "cost_per_use": np.random.uniform(0.1, 1.0)
        }

    async def _calculate_performance_metrics(
        self,
        resource: OrganizationResource
    ) -> Dict[str, Any]:
        """Calculate resource performance metrics."""
        # This would typically involve analyzing performance logs
        # For now, return simulated values
        return {
            "response_time": np.random.uniform(50, 200),
            "error_rate": np.random.uniform(0.001, 0.01),
            "availability": np.random.uniform(0.99, 0.9999)
        }

    def _determine_implementation_phase(
        self,
        recommendation: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """Determine implementation phase for a recommendation."""
        priority = recommendation.get("priority", 0)
        complexity = recommendation.get("complexity", 0)
        dependencies = recommendation.get("dependencies", [])

        if priority > 8 and complexity < 5 and not dependencies:
            return "immediate"
        elif priority > 5 or (complexity < 7 and len(dependencies) < 3):
            return "short_term"
        else:
            return "long_term"

    def _generate_implementation_timeline(
        self,
        phases: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Generate timeline for implementation phases."""
        return {
            "immediate": {
                "start": datetime.utcnow(),
                "end": datetime.utcnow() + timedelta(days=7),
                "duration": "1 week"
            },
            "short_term": {
                "start": datetime.utcnow() + timedelta(days=7),
                "end": datetime.utcnow() + timedelta(days=30),
                "duration": "3 weeks"
            },
            "long_term": {
                "start": datetime.utcnow() + timedelta(days=30),
                "end": datetime.utcnow() + timedelta(days=90),
                "duration": "2 months"
            }
        }

    def _identify_implementation_dependencies(
        self,
        phases: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Identify dependencies between implementation phases."""
        dependencies = []
        all_recommendations = []
        
        # Collect all recommendations
        for phase, recommendations in phases.items():
            for rec in recommendations:
                all_recommendations.append({
                    "id": rec.get("id"),
                    "phase": phase,
                    "dependencies": rec.get("dependencies", [])
                })

        # Map dependencies
        for rec in all_recommendations:
            for dep_id in rec["dependencies"]:
                dep = next((r for r in all_recommendations if r["id"] == dep_id), None)
                if dep:
                    dependencies.append({
                        "from": dep_id,
                        "to": rec["id"],
                        "type": "required",
                        "phases": [dep["phase"], rec["phase"]]
                    })

        return dependencies

    def _assess_implementation_risks(
        self,
        phases: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Assess risks for implementation phases."""
        risks = []
        
        for phase, recommendations in phases.items():
            phase_risks = self._identify_phase_risks(phase, recommendations)
            risks.extend(phase_risks)

        return risks

    def _identify_phase_risks(
        self,
        phase: str,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify risks for a specific implementation phase."""
        risks = []
        
        # Analyze concurrent changes
        if len(recommendations) > 5:
            risks.append({
                "phase": phase,
                "type": "concurrent_changes",
                "severity": "medium",
                "description": "High number of concurrent changes may impact stability",
                "mitigation": "Consider splitting changes into smaller batches"
            })

        # Analyze resource dependencies
        resource_changes = sum(1 for r in recommendations if r.get("action") in ["remove", "modify"])
        if resource_changes > 3:
            risks.append({
                "phase": phase,
                "type": "resource_dependency",
                "severity": "high",
                "description": "Multiple resource changes may have cascading effects",
                "mitigation": "Implement changes sequentially with validation steps"
            })

        return risks

    async def get_resource_allocation_plan(
        self,
        time_window: str = "24h",
        category: Optional[str] = None
    ) -> Dict:
        """
        Get resource allocation plan for GPTs.
        
        Args:
            time_window: Time window for planning
            category: Optional category to filter GPTs
        """
        try:
            # Get all relevant GPTs
            query = self.db.query(GPTDefinition)
            if category:
                query = query.filter(GPTDefinition.category == category)
            gpts = query.all()

            allocation_plan = {}
            total_resources = 0
            peak_demands = []

            for gpt in gpts:
                # Get resource predictions
                prediction = await self.analytics_service.predict_resource_usage(gpt.id)
                if prediction["status"] == "success":
                    peak_demand = prediction["predictions"]["predicted_peak_usage"]
                    peak_demands.append((gpt.id, peak_demand))
                    total_resources += peak_demand

            if not peak_demands:
                return {
                    "status": "error",
                    "message": "No resource usage data available"
                }

            # Calculate optimal allocations
            allocations = self._calculate_resource_allocations(
                peak_demands,
                total_resources
            )

            return {
                "status": "success",
                "allocations": allocations,
                "total_resources": total_resources,
                "optimization_opportunities": self._identify_optimization_opportunities(
                    allocations,
                    peak_demands
                )
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating resource allocation plan: {str(e)}"
            )

    async def get_scaling_recommendations(
        self,
        gpt_id: str,
        forecast_window: str = "7d"
    ) -> Dict:
        """
        Get scaling recommendations for a GPT.
        
        Args:
            gpt_id: The ID of the GPT
            forecast_window: Window for forecasting resource needs
        """
        try:
            # Get usage predictions and performance trends
            prediction = await self.analytics_service.predict_resource_usage(gpt_id)
            if prediction["status"] != "success":
                return {
                    "status": "error",
                    "message": "Insufficient usage data for recommendations"
                }

            # Analyze scaling needs
            scaling_analysis = self._analyze_scaling_needs(
                prediction["predictions"],
                prediction["confidence_score"]
            )

            return {
                "status": "success",
                "current_utilization": prediction["predictions"]["predicted_peak_usage"],
                "scaling_recommendations": scaling_analysis["recommendations"],
                "trigger_points": scaling_analysis["trigger_points"],
                "cost_impact": self._estimate_cost_impact(scaling_analysis)
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating scaling recommendations: {str(e)}"
            )

    def _calculate_optimization_plan(
        self,
        usage_prediction: Dict,
        performance_trends: Dict,
        optimization_target: str
    ) -> Dict:
        """Calculate optimal resource allocation plan."""
        current_usage = usage_prediction["predictions"]["predicted_peak_usage"]
        growth_trend = usage_prediction["predictions"]["growth_trend"]
        
        # Base resource needs
        base_allocation = current_usage * 1.2  # 20% buffer
        
        # Adjust based on optimization target
        if optimization_target == "performance":
            # Prioritize performance with higher buffer
            allocation = base_allocation * 1.3
            buffer_strategy = "aggressive"
        elif optimization_target == "efficiency":
            # Minimize resource usage
            allocation = base_allocation * 1.1
            buffer_strategy = "minimal"
        else:  # balanced
            allocation = base_allocation * 1.2
            buffer_strategy = "moderate"

        return {
            "recommended_allocation": float(allocation),
            "buffer_strategy": buffer_strategy,
            "scaling_threshold": float(current_usage * 0.8),
            "growth_adjusted_allocation": float(allocation * (1 + growth_trend))
        }

    def _generate_scaling_recommendations(
        self,
        optimization_plan: Dict,
        predictions: Dict
    ) -> List[Dict]:
        """Generate scaling recommendations based on optimization plan."""
        recommendations = []
        
        # Check if current allocation needs immediate adjustment
        if predictions["predicted_peak_usage"] > optimization_plan["scaling_threshold"]:
            recommendations.append({
                "type": "immediate_scaling",
                "priority": "high",
                "target_allocation": optimization_plan["recommended_allocation"],
                "reason": "Current usage approaching threshold"
            })

        # Plan for future scaling
        if predictions["growth_trend"] > 0:
            recommendations.append({
                "type": "planned_scaling",
                "priority": "medium",
                "target_allocation": optimization_plan["growth_adjusted_allocation"],
                "timeline": "within 7 days",
                "reason": "Anticipated growth in usage"
            })

        return recommendations

    def _estimate_improvements(
        self,
        optimization_plan: Dict,
        performance_trends: Dict
    ) -> Dict:
        """Estimate improvements from optimization."""
        current_performance = performance_trends.get("performance_score", 0)
        
        # Estimate improvement factors
        response_time_improvement = 0.1  # 10% improvement
        reliability_improvement = 0.05   # 5% improvement
        
        return {
            "estimated_performance_score": min(
                current_performance * (1 + response_time_improvement),
                1.0
            ),
            "response_time_improvement": response_time_improvement,
            "reliability_improvement": reliability_improvement,
            "cost_efficiency_impact": self._calculate_efficiency_impact(optimization_plan)
        }

    def _calculate_resource_allocations(
        self,
        peak_demands: List[Tuple[str, float]],
        total_resources: float
    ) -> Dict[str, Dict]:
        """Calculate optimal resource allocations."""
        allocations = {}
        
        # Sort by peak demand
        peak_demands.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate proportional allocations
        for gpt_id, peak_demand in peak_demands:
            proportion = peak_demand / total_resources
            allocations[gpt_id] = {
                "base_allocation": float(peak_demand),
                "recommended_allocation": float(peak_demand * 1.2),  # 20% buffer
                "proportion": float(proportion),
                "scaling_limits": {
                    "min": float(peak_demand * 0.8),
                    "max": float(peak_demand * 1.5)
                }
            }

        return allocations

    def _identify_optimization_opportunities(
        self,
        allocations: Dict,
        peak_demands: List[Tuple[str, float]]
    ) -> List[Dict]:
        """Identify resource optimization opportunities."""
        opportunities = []
        
        # Analyze allocation efficiency
        total_allocated = sum(a["recommended_allocation"] for a in allocations.values())
        total_peak = sum(demand for _, demand in peak_demands)
        
        if total_allocated > total_peak * 1.3:  # More than 30% buffer
            opportunities.append({
                "type": "over_allocation",
                "severity": "medium",
                "potential_savings": float(total_allocated - (total_peak * 1.2)),
                "recommendation": "Consider reducing allocation buffers"
            })

        # Identify underutilized resources
        for gpt_id, allocation in allocations.items():
            peak = next(demand for id_, demand in peak_demands if id_ == gpt_id)
            if peak < allocation["base_allocation"] * 0.6:  # Less than 60% utilization
                opportunities.append({
                    "type": "underutilization",
                    "gpt_id": gpt_id,
                    "severity": "high",
                    "current_utilization": float(peak / allocation["base_allocation"]),
                    "recommendation": "Reduce resource allocation"
                })

        return opportunities

    def _analyze_scaling_needs(
        self,
        predictions: Dict,
        confidence_score: float
    ) -> Dict:
        """Analyze scaling needs based on predictions."""
        peak_usage = predictions["predicted_peak_usage"]
        growth_trend = predictions["growth_trend"]
        
        recommendations = []
        trigger_points = []
        
        # Immediate scaling needs
        if peak_usage > 0.8:  # 80% utilization
            recommendations.append({
                "type": "vertical_scaling",
                "urgency": "high",
                "scale_factor": 1.5,
                "reason": "High current utilization"
            })
            trigger_points.append({
                "metric": "utilization",
                "threshold": 0.8,
                "action": "scale_up",
                "scale_factor": 1.5
            })

        # Growth-based scaling
        if growth_trend > 0.1:  # 10% growth trend
            recommendations.append({
                "type": "predictive_scaling",
                "urgency": "medium",
                "scale_factor": 1 + growth_trend,
                "timeline": "7 days",
                "reason": "Anticipated growth"
            })
            trigger_points.append({
                "metric": "growth_rate",
                "threshold": 0.1,
                "action": "plan_scaling",
                "scale_factor": 1 + growth_trend
            })

        return {
            "recommendations": recommendations,
            "trigger_points": trigger_points,
            "confidence_level": confidence_score
        }

    def _estimate_cost_impact(self, scaling_analysis: Dict) -> Dict:
        """Estimate cost impact of scaling recommendations."""
        total_impact = 0
        cost_breakdown = []
        
        for rec in scaling_analysis["recommendations"]:
            scale_factor = rec["scale_factor"]
            # Simplified cost calculation
            cost_increase = (scale_factor - 1) * 100  # Base cost unit of 100
            
            total_impact += cost_increase
            cost_breakdown.append({
                "type": rec["type"],
                "cost_increase": float(cost_increase),
                "timeline": rec.get("timeline", "immediate")
            })

        return {
            "total_cost_impact": float(total_impact),
            "breakdown": cost_breakdown,
            "optimization_potential": self._calculate_optimization_potential(
                total_impact,
                scaling_analysis
            )
        }

    def _calculate_efficiency_impact(self, optimization_plan: Dict) -> Dict:
        """Calculate efficiency impact of optimization plan."""
        current_allocation = optimization_plan["scaling_threshold"]
        recommended_allocation = optimization_plan["recommended_allocation"]
        
        # Calculate efficiency metrics
        resource_efficiency = current_allocation / recommended_allocation
        cost_efficiency = 1 - (recommended_allocation - current_allocation) / current_allocation
        
        return {
            "resource_efficiency": float(resource_efficiency),
            "cost_efficiency": float(cost_efficiency),
            "optimization_ratio": float(recommended_allocation / current_allocation)
        }

    def _calculate_optimization_potential(
        self,
        total_cost: float,
        scaling_analysis: Dict
    ) -> Dict:
        """Calculate potential for cost optimization."""
        confidence = scaling_analysis["confidence_level"]
        
        # Adjust savings potential based on confidence
        base_savings = total_cost * 0.2  # Assume 20% potential savings
        adjusted_savings = base_savings * confidence
        
        return {
            "potential_savings": float(adjusted_savings),
            "confidence_level": float(confidence),
            "optimization_methods": [
                {
                    "method": "resource_scheduling",
                    "savings_potential": float(adjusted_savings * 0.4)
                },
                {
                    "method": "capacity_optimization",
                    "savings_potential": float(adjusted_savings * 0.6)
                }
            ]
        } 

    async def optimize_resources_org(
        self,
        org_id: str,
        optimization_type: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Optimize organization resources using AI-driven analysis."""
        try:
            # Get organization resources
            resources = self.db.query(OrganizationResource).filter(
                OrganizationResource.organization_id == org_id,
                OrganizationResource.status == "active"
            ).all()

            if not resources:
                raise HTTPException(
                    status_code=404,
                    detail="No active resources found for optimization"
                )

            # Analyze current resource utilization
            utilization = await self._analyze_resource_utilization(resources)

            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                resources,
                utilization,
                optimization_type,
                constraints
            )

            # Calculate potential impact
            impact = await self._calculate_optimization_impact(
                resources,
                recommendations
            )

            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(
                recommendations,
                constraints
            )

            return {
                "current_state": utilization,
                "recommendations": recommendations,
                "impact": impact,
                "implementation_plan": implementation_plan
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing resources: {str(e)}"
            )

    async def _get_gpt_usage_prediction(self, gpt_id: str) -> Dict[str, Any]:
        """Get usage prediction for a GPT."""
        # Placeholder implementation
        return {
            "current_usage": 0.75,
            "predicted_usage": 0.85,
            "confidence": 0.8,
            "trend": "increasing"
        }

    async def _get_gpt_performance_trends(self, gpt_id: str) -> Dict[str, Any]:
        """Get performance trends for a GPT."""
        # Placeholder implementation
        return {
            "response_time": {"trend": "stable", "value": 1.2},
            "success_rate": {"trend": "improving", "value": 0.95},
            "error_rate": {"trend": "stable", "value": 0.05}
        } 