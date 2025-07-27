"""
GPT Coordination Service

This module provides functionality for managing coordination between multiple GPTs
and handling shared context across GPT interactions.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback
)
from ..models.context import GPTContext, ContextInteraction, SharedContext, ContextSummary

class GPTCoordinationService:
    def __init__(self, db: Session):
        self.db = db

    async def initialize_context(
        self,
        user_id: str,
        primary_gpt_id: str,
        context_data: Dict,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """Initialize a new context for GPT coordination."""
        try:
            # Validate GPT subscription
            subscription = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id,
                DashboardGPTSubscription.gpt_definition_id == primary_gpt_id
            ).first()
            
            if not subscription:
                raise HTTPException(
                    status_code=404,
                    detail="GPT subscription not found"
                )

            # Create context
            context = GPTContext(
                id=f"ctx-{uuid.uuid4()}",
                user_id=user_id,
                primary_gpt_id=primary_gpt_id,
                name=name,
                description=description,
                context_data=context_data,
                is_active=True
            )
            
            # Add primary GPT to active GPTs
            context.active_gpts.append(subscription.gpt_definition)
            
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
            
            return {
                "context_id": context.id,
                "primary_gpt": primary_gpt_id,
                "created_at": context.created_at.isoformat(),
                "name": context.name,
                "description": context.description,
                "context_data": context.context_data,
                "active_gpts": [gpt.id for gpt in context.active_gpts]
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error initializing context: {str(e)}"
            )

    async def add_gpt_to_context(
        self,
        context_id: str,
        gpt_id: str,
        role: str
    ) -> Dict:
        """Add a GPT to an existing context."""
        try:
            # Get context and GPT
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id,
                GPTContext.is_active == True
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Active context not found"
                )
            
            gpt = self.db.query(GPTDefinition).filter(
                GPTDefinition.id == gpt_id
            ).first()
            
            if not gpt:
                raise HTTPException(
                    status_code=404,
                    detail="GPT not found"
                )

            # Add GPT to context
            if gpt not in context.active_gpts:
                context.active_gpts.append(gpt)
                
                # Record interaction
                interaction = ContextInteraction(
                    id=f"int-{uuid.uuid4()}",
                    context_id=context_id,
                    gpt_id=gpt_id,
                    interaction_type="join",
                    metadata={"role": role}
                )
                self.db.add(interaction)
            
            self.db.commit()
            
            return {
                "status": "success",
                "context_id": context_id,
                "added_gpt": gpt_id,
                "role": role,
                "active_gpts": [g.id for g in context.active_gpts]
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error adding GPT to context: {str(e)}"
            )

    async def share_context(
        self,
        context_id: str,
        source_gpt_id: str,
        target_gpt_id: str,
        shared_data: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Share context between GPTs."""
        try:
            # Validate context and GPTs
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id,
                GPTContext.is_active == True
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Active context not found"
                )
            
            # Verify both GPTs are in the context
            active_gpt_ids = [g.id for g in context.active_gpts]
            if source_gpt_id not in active_gpt_ids or target_gpt_id not in active_gpt_ids:
                raise HTTPException(
                    status_code=400,
                    detail="Both GPTs must be active in the context"
                )
            
            # Create shared context
            shared_context = SharedContext(
                id=f"sh-{uuid.uuid4()}",
                context_id=context_id,
                source_gpt_id=source_gpt_id,
                target_gpt_id=target_gpt_id,
                shared_data=shared_data,
                metadata=metadata or {}
            )
            
            self.db.add(shared_context)
            
            # Record interaction
            interaction = ContextInteraction(
                id=f"int-{uuid.uuid4()}",
                context_id=context_id,
                gpt_id=source_gpt_id,
                interaction_type="share",
                content=shared_data,
                metadata={
                    "target_gpt": target_gpt_id,
                    **(metadata or {})
                }
            )
            self.db.add(interaction)
            
            self.db.commit()
            self.db.refresh(shared_context)
            
            return {
                "shared_context_id": shared_context.id,
                "context_id": context_id,
                "source_gpt": source_gpt_id,
                "target_gpt": target_gpt_id,
                "shared_at": shared_context.created_at.isoformat(),
                "shared_data": shared_data,
                "metadata": metadata
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error sharing context: {str(e)}"
            )

    async def get_context_history(
        self,
        context_id: str,
        gpt_id: Optional[str] = None,
        interaction_type: Optional[str] = None
    ) -> List[Dict]:
        """Get history of context interactions."""
        try:
            # Build query
            query = self.db.query(ContextInteraction).filter(
                ContextInteraction.context_id == context_id
            )
            
            if gpt_id:
                query = query.filter(ContextInteraction.gpt_id == gpt_id)
            
            if interaction_type:
                query = query.filter(ContextInteraction.interaction_type == interaction_type)
            
            # Get interactions ordered by timestamp
            interactions = query.order_by(ContextInteraction.timestamp).all()
            
            return [{
                "interaction_id": interaction.id,
                "gpt_id": interaction.gpt_id,
                "type": interaction.interaction_type,
                "content": interaction.content,
                "metadata": interaction.metadata,
                "timestamp": interaction.timestamp.isoformat()
            } for interaction in interactions]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving context history: {str(e)}"
            )

    async def update_context(
        self,
        context_id: str,
        gpt_id: str,
        update_data: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Update context with new information."""
        try:
            # Get and validate context
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id,
                GPTContext.is_active == True
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Active context not found"
                )
            
            # Verify GPT is in the context
            if gpt_id not in [g.id for g in context.active_gpts]:
                raise HTTPException(
                    status_code=400,
                    detail="GPT must be active in the context"
                )
            
            # Update context data
            context.context_data.update(update_data)
            context.updated_at = datetime.utcnow()
            
            # Record interaction
            interaction = ContextInteraction(
                id=f"int-{uuid.uuid4()}",
                context_id=context_id,
                gpt_id=gpt_id,
                interaction_type="update",
                content=update_data,
                metadata=metadata or {}
            )
            self.db.add(interaction)
            
            self.db.commit()
            self.db.refresh(context)
            
            return {
                "context_id": context.id,
                "gpt_id": gpt_id,
                "updated_at": context.updated_at.isoformat(),
                "update_data": update_data,
                "context_data": context.context_data,
                "metadata": metadata
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating context: {str(e)}"
            )

    async def close_context(
        self,
        context_id: str,
        summary: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Close a context and store summary."""
        try:
            # Get and validate context
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id,
                GPTContext.is_active == True
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Active context not found"
                )
            
            # Update context status
            context.is_active = False
            context.closed_at = datetime.utcnow()
            
            # Create summary if provided
            if summary:
                context_summary = ContextSummary(
                    id=f"sum-{uuid.uuid4()}",
                    context_id=context_id,
                    summary_type="closure",
                    content=summary,
                    metadata=metadata or {}
                )
                self.db.add(context_summary)
            
            self.db.commit()
            
            return {
                "context_id": context.id,
                "closed_at": context.closed_at.isoformat(),
                "summary": summary,
                "metadata": metadata
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error closing context: {str(e)}"
            )

    async def get_active_contexts(
        self,
        user_id: str,
        gpt_id: Optional[str] = None
    ) -> List[Dict]:
        """Get active contexts for a user."""
        try:
            query = self.db.query(GPTContext).filter(
                GPTContext.user_id == user_id,
                GPTContext.is_active == True
            )
            
            if gpt_id:
                query = query.filter(GPTContext.active_gpts.any(id=gpt_id))
            
            contexts = query.all()
            
            return [
                {
                    "context_id": ctx.id,
                    "primary_gpt": ctx.primary_gpt_id,
                    "created_at": ctx.created_at.isoformat(),
                    "name": ctx.name,
                    "description": ctx.description,
                    "context_data": ctx.context_data,
                    "active_gpts": [gpt.id for gpt in ctx.active_gpts]
                }
                for ctx in contexts
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting active contexts: {str(e)}"
            )

    async def analyze_context(
        self,
        context_id: str,
        include_metrics: bool = True,
        include_patterns: bool = True,
        include_insights: bool = True,
        include_recommendations: bool = True
    ) -> Dict:
        """Analyze a context for insights and patterns."""
        try:
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Context not found"
                )
            
            result = {
                "context_id": context_id,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            if include_metrics:
                result["metrics"] = await self._get_context_metrics(context)
            
            if include_patterns:
                result["patterns"] = await self._analyze_interaction_patterns(context)
            
            if include_insights:
                result["insights"] = await self._generate_context_insights(context)
            
            if include_recommendations:
                result["recommendations"] = await self._generate_optimization_recommendations(context)
            
            return result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing context: {str(e)}"
            )

    async def validate_context(
        self,
        context_id: str,
        validation_type: str,
        validation_params: Optional[Dict] = None
    ) -> Dict:
        """Validate a context against specific criteria."""
        try:
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Context not found"
                )
            
            validation_result = {
                "context_id": context_id,
                "validation_type": validation_type,
                "timestamp": datetime.utcnow().isoformat(),
                "is_valid": True,
                "issues": [],
                "warnings": [],
                "details": {}
            }
            
            if validation_type == "compatibility":
                await self._validate_compatibility(context, validation_result)
            elif validation_type == "integrity":
                await self._validate_integrity(context, validation_result)
            elif validation_type == "performance":
                await self._validate_performance(context, validation_result)
            elif validation_type == "security":
                await self._validate_security(context, validation_result)
            
            return validation_result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error validating context: {str(e)}"
            )

    async def backup_context(
        self,
        context_id: str,
        include_history: bool = True,
        include_shared_data: bool = True
    ) -> Dict:
        """Create a backup of a context."""
        try:
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Context not found"
                )
            
            backup = {
                "id": f"bak-{uuid.uuid4()}",
                "context_id": context_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context_data": context.context_data,
                "metadata": {
                    "name": context.name,
                    "description": context.description,
                    "primary_gpt_id": context.primary_gpt_id,
                    "active_gpts": [gpt.id for gpt in context.active_gpts]
                }
            }
            
            if include_history:
                backup["history"] = await self._get_context_history(context)
            
            if include_shared_data:
                backup["shared_data"] = await self._get_shared_context_data(context)
            
            # Store backup in database
            context_backup = ContextBackup(
                id=backup["id"],
                context_id=context_id,
                backup_data=backup,
                created_at=datetime.utcnow()
            )
            self.db.add(context_backup)
            self.db.commit()
            
            return backup

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating context backup: {str(e)}"
            )

    async def restore_context(
        self,
        backup_id: str,
        restore_options: Optional[Dict] = None
    ) -> Dict:
        """Restore a context from a backup."""
        try:
            backup = self.db.query(ContextBackup).filter(
                ContextBackup.id == backup_id
            ).first()
            
            if not backup:
                raise HTTPException(
                    status_code=404,
                    detail="Backup not found"
                )
            
            # Create new context from backup
            context = GPTContext(
                id=f"ctx-{uuid.uuid4()}",
                user_id=backup.context.user_id,
                primary_gpt_id=backup.backup_data["metadata"]["primary_gpt_id"],
                name=backup.backup_data["metadata"]["name"],
                description=backup.backup_data["metadata"]["description"],
                context_data=backup.backup_data["context_data"],
                is_active=True
            )
            
            # Restore active GPTs
            gpts = self.db.query(GPTDefinition).filter(
                GPTDefinition.id.in_(backup.backup_data["metadata"]["active_gpts"])
            ).all()
            context.active_gpts.extend(gpts)
            
            # Restore history if included and requested
            if "history" in backup.backup_data and restore_options.get("restore_history", True):
                await self._restore_context_history(context, backup.backup_data["history"])
            
            # Restore shared data if included and requested
            if "shared_data" in backup.backup_data and restore_options.get("restore_shared_data", True):
                await self._restore_shared_context_data(context, backup.backup_data["shared_data"])
            
            self.db.add(context)
            self.db.commit()
            
            return {
                "context_id": context.id,
                "backup_id": backup_id,
                "restored_at": datetime.utcnow().isoformat(),
                "restored_data": {
                    "history": "history" in backup.backup_data and restore_options.get("restore_history", True),
                    "shared_data": "shared_data" in backup.backup_data and restore_options.get("restore_shared_data", True)
                }
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error restoring context: {str(e)}"
            )

    async def get_context_templates(
        self,
        category: Optional[str] = None,
        gpt_type: Optional[str] = None
    ) -> List[Dict]:
        """Get available context templates."""
        try:
            query = self.db.query(ContextTemplate)
            
            if category:
                query = query.filter(ContextTemplate.category == category)
            if gpt_type:
                query = query.filter(ContextTemplate.configuration["gpt_type"].astext == gpt_type)
            
            templates = query.all()
            return [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "configuration": template.configuration,
                    "metadata": template.metadata
                }
                for template in templates
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting context templates: {str(e)}"
            )

    async def create_context_template(
        self,
        name: str,
        description: str,
        category: str,
        configuration: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Create a new context template."""
        try:
            template = ContextTemplate(
                id=f"tmpl-{uuid.uuid4()}",
                name=name,
                description=description,
                category=category,
                configuration=configuration,
                metadata=metadata or {}
            )
            
            self.db.add(template)
            self.db.commit()
            
            return {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "configuration": template.configuration,
                "metadata": template.metadata
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating context template: {str(e)}"
            )

    async def create_context_from_template(
        self,
        template_id: str,
        user_id: str,
        context_data: Optional[Dict] = None
    ) -> Dict:
        """Create a new context from a template."""
        try:
            template = self.db.query(ContextTemplate).filter(
                ContextTemplate.id == template_id
            ).first()
            
            if not template:
                raise HTTPException(
                    status_code=404,
                    detail="Template not found"
                )
            
            # Create context using template configuration
            context = GPTContext(
                id=f"ctx-{uuid.uuid4()}",
                user_id=user_id,
                primary_gpt_id=template.configuration["primary_gpt_id"],
                name=template.configuration.get("name", template.name),
                description=template.configuration.get("description", template.description),
                context_data=context_data or template.configuration.get("context_data", {}),
                is_active=True
            )
            
            # Add GPTs specified in template
            gpts = self.db.query(GPTDefinition).filter(
                GPTDefinition.id.in_(template.configuration.get("active_gpts", []))
            ).all()
            context.active_gpts.extend(gpts)
            
            self.db.add(context)
            self.db.commit()
            
            return {
                "context_id": context.id,
                "template_id": template_id,
                "created_at": context.created_at.isoformat(),
                "name": context.name,
                "description": context.description,
                "context_data": context.context_data,
                "active_gpts": [gpt.id for gpt in context.active_gpts]
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating context from template: {str(e)}"
            )

    async def get_context_metrics(
        self,
        context_id: str,
        metric_types: Optional[List[str]] = None,
        time_range: str = "24h",
        include_trends: bool = False,
        include_breakdown: bool = False
    ) -> Dict:
        """Get performance metrics for a context."""
        try:
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Context not found"
                )
            
            metrics = {
                "context_id": context_id,
                "timestamp": datetime.utcnow().isoformat(),
                "time_range": time_range
            }
            
            # Get base metrics
            base_metrics = await self._get_context_metrics(context, time_range)
            metrics.update(base_metrics)
            
            # Filter metrics if types specified
            if metric_types:
                metrics = {k: v for k, v in metrics.items() if k in metric_types}
            
            # Add trends if requested
            if include_trends:
                metrics["trends"] = await self._get_metric_trends(context, time_range)
            
            # Add breakdown if requested
            if include_breakdown:
                metrics["breakdown"] = await self._get_metric_breakdown(context, time_range)
            
            return metrics

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting context metrics: {str(e)}"
            )

    async def get_context_performance(
        self,
        context_id: str,
        time_range: str = "24h",
        include_gpt_metrics: bool = True,
        include_interaction_metrics: bool = True,
        include_resource_metrics: bool = True
    ) -> Dict:
        """Get detailed performance data for a context."""
        try:
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Context not found"
                )
            
            performance = {
                "context_id": context_id,
                "timestamp": datetime.utcnow().isoformat(),
                "time_range": time_range
            }
            
            if include_gpt_metrics:
                performance["gpt_metrics"] = await self._get_gpt_performance_metrics(context, time_range)
            
            if include_interaction_metrics:
                performance["interaction_metrics"] = await self._get_interaction_performance_metrics(context, time_range)
            
            if include_resource_metrics:
                performance["resource_metrics"] = await self._get_resource_performance_metrics(context, time_range)
            
            return performance

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting context performance: {str(e)}"
            )

    async def optimize_context(
        self,
        context_id: str,
        optimization_target: str,
        optimization_params: Optional[Dict] = None
    ) -> Dict:
        """Optimize a context for specific targets."""
        try:
            context = self.db.query(GPTContext).filter(
                GPTContext.id == context_id
            ).first()
            
            if not context:
                raise HTTPException(
                    status_code=404,
                    detail="Context not found"
                )
            
            # Get current metrics
            current_metrics = await self._get_context_metrics(context)
            
            # Generate optimization plan
            optimization_plan = await self._generate_optimization_plan(
                context,
                optimization_target,
                current_metrics,
                optimization_params
            )
            
            # Apply optimization plan
            optimization_result = await self._apply_optimization_plan(
                context,
                optimization_plan
            )
            
            # Get updated metrics
            updated_metrics = await self._get_context_metrics(context)
            
            return {
                "context_id": context_id,
                "optimization_target": optimization_target,
                "timestamp": datetime.utcnow().isoformat(),
                "optimization_plan": optimization_plan,
                "optimization_result": optimization_result,
                "metrics_before": current_metrics,
                "metrics_after": updated_metrics
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing context: {str(e)}"
            )

    async def _get_context_metrics(
        self,
        context: GPTContext,
        time_range: str = "24h"
    ) -> Dict:
        """Get base metrics for a context."""
        metrics = {
            "total_interactions": await self._count_interactions(context, time_range),
            "active_gpts": len(context.active_gpts),
            "shared_contexts": await self._count_shared_contexts(context, time_range),
            "average_response_time": await self._calculate_average_response_time(context, time_range),
            "success_rate": await self._calculate_success_rate(context, time_range),
            "error_rate": await self._calculate_error_rate(context, time_range),
            "resource_utilization": await self._calculate_resource_utilization(context, time_range)
        }
        return metrics

    async def _analyze_interaction_patterns(self, context: GPTContext) -> Dict:
        """Analyze interaction patterns in a context."""
        patterns = {
            "common_sequences": await self._find_common_sequences(context),
            "peak_usage_times": await self._find_peak_usage_times(context),
            "gpt_interactions": await self._analyze_gpt_interactions(context),
            "data_sharing_patterns": await self._analyze_data_sharing(context)
        }
        return patterns

    async def _generate_context_insights(self, context: GPTContext) -> Dict:
        """Generate insights for a context."""
        insights = {
            "performance_insights": await self._analyze_performance(context),
            "efficiency_insights": await self._analyze_efficiency(context),
            "bottleneck_analysis": await self._analyze_bottlenecks(context),
            "improvement_opportunities": await self._identify_improvements(context)
        }
        return insights

    async def _generate_optimization_recommendations(self, context: GPTContext) -> List[Dict]:
        """Generate optimization recommendations for a context."""
        recommendations = []
        
        # Analyze performance metrics
        performance = await self._analyze_performance(context)
        if performance["issues"]:
            recommendations.extend([
                {
                    "type": "performance",
                    "issue": issue,
                    "recommendation": solution,
                    "priority": priority
                }
                for issue, solution, priority in performance["issues"]
            ])
        
        # Analyze resource utilization
        utilization = await self._analyze_resource_utilization(context)
        if utilization["issues"]:
            recommendations.extend([
                {
                    "type": "resource",
                    "issue": issue,
                    "recommendation": solution,
                    "priority": priority
                }
                for issue, solution, priority in utilization["issues"]
            ])
        
        # Analyze interaction patterns
        patterns = await self._analyze_interaction_patterns(context)
        if patterns["issues"]:
            recommendations.extend([
                {
                    "type": "interaction",
                    "issue": issue,
                    "recommendation": solution,
                    "priority": priority
                }
                for issue, solution, priority in patterns["issues"]
            ])
        
        return sorted(recommendations, key=lambda x: x["priority"], reverse=True)

    async def _validate_compatibility(self, context: GPTContext, result: Dict):
        """Validate compatibility between GPTs in a context."""
        for gpt1 in context.active_gpts:
            for gpt2 in context.active_gpts:
                if gpt1 != gpt2:
                    compatibility = await self._check_gpt_compatibility(gpt1, gpt2)
                    if not compatibility["compatible"]:
                        result["is_valid"] = False
                        result["issues"].append({
                            "type": "compatibility",
                            "gpts": [gpt1.id, gpt2.id],
                            "reason": compatibility["reason"]
                        })

    async def _validate_integrity(self, context: GPTContext, result: Dict):
        """Validate data integrity in a context."""
        # Check context data integrity
        data_integrity = await self._check_data_integrity(context)
        if not data_integrity["valid"]:
            result["is_valid"] = False
            result["issues"].append({
                "type": "data_integrity",
                "reason": data_integrity["reason"]
            })
        
        # Check interaction history integrity
        history_integrity = await self._check_history_integrity(context)
        if not history_integrity["valid"]:
            result["is_valid"] = False
            result["issues"].append({
                "type": "history_integrity",
                "reason": history_integrity["reason"]
            })

    async def _validate_performance(self, context: GPTContext, result: Dict):
        """Validate performance metrics of a context."""
        # Check response times
        response_times = await self._check_response_times(context)
        if not response_times["valid"]:
            result["warnings"].append({
                "type": "response_time",
                "reason": response_times["reason"]
            })
        
        # Check error rates
        error_rates = await self._check_error_rates(context)
        if not error_rates["valid"]:
            result["warnings"].append({
                "type": "error_rate",
                "reason": error_rates["reason"]
            })
        
        # Check resource utilization
        utilization = await self._check_resource_utilization(context)
        if not utilization["valid"]:
            result["warnings"].append({
                "type": "resource_utilization",
                "reason": utilization["reason"]
            })

    async def _validate_security(self, context: GPTContext, result: Dict):
        """Validate security aspects of a context."""
        # Check access controls
        access_controls = await self._check_access_controls(context)
        if not access_controls["valid"]:
            result["is_valid"] = False
            result["issues"].append({
                "type": "access_control",
                "reason": access_controls["reason"]
            })
        
        # Check data sharing security
        data_sharing = await self._check_data_sharing_security(context)
        if not data_sharing["valid"]:
            result["is_valid"] = False
            result["issues"].append({
                "type": "data_sharing",
                "reason": data_sharing["reason"]
            })
        
        # Check audit trail
        audit_trail = await self._check_audit_trail(context)
        if not audit_trail["valid"]:
            result["warnings"].append({
                "type": "audit_trail",
                "reason": audit_trail["reason"]
            }) 