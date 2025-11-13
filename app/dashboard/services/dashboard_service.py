"""
Dashboard Service

This module provides the main service layer for the Faraday AI Dashboard,
coordinating various functionalities including GPT management and context sharing.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
import csv
import io
import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from app.core.config import get_settings

from .gpt_coordination_service import GPTCoordinationService
from .recommendation_service import RecommendationService
from .resource_sharing_service import ResourceSharingService
from ..models import (
    DashboardUser as User,
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    Dashboard,
    DashboardWidget,
    WidgetType,
    WidgetLayout,
    DashboardShare,
    DashboardFilter,
    DashboardProject,
    Organization
)
from ..models.context import GPTContext
from app.services.collaboration.realtime_collaboration_service import RealtimeCollaborationService
from ..models.gpt_models import (
    GPTDefinition,
    DashboardGPTSubscription,
    GPTPerformance,
    GPTUsage,
    GPTAnalytics,
    GPTFeedback
)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.gpt_coordination = GPTCoordinationService(db)
        self.recommendation = RecommendationService(db)
        self.collaboration_service = RealtimeCollaborationService()
        self.resource_sharing = ResourceSharingService(db=db)  # Pass db parameter explicitly

    async def initialize_user_dashboard(
        self,
        user_id: str,
        preferences: Optional[Dict] = None
    ) -> Dict:
        """Initialize dashboard for a new user."""
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            # Get user's GPT subscriptions
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id
            ).all()

            # Get active contexts
            active_contexts = await self.gpt_coordination.get_active_contexts(user_id)

            # Initialize dashboard state
            dashboard_state = {
                "user_id": user_id,
                "active_gpts": [sub.gpt_definition_id for sub in subscriptions],
                "active_contexts": active_contexts,
                "preferences": preferences or {},
                "initialized_at": datetime.utcnow().isoformat()
            }

            return dashboard_state

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error initializing dashboard: {str(e)}"
            )

    async def get_dashboard_state(
        self,
        user_id: str,
        include_contexts: bool = True
    ) -> Dict:
        """Get current dashboard state for a user."""
        try:
            # Get user's GPT subscriptions
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id
            ).all()

            # Get performance metrics
            performance = self.db.query(GPTPerformance).filter(
                GPTPerformance.subscription_id.in_([sub.id for sub in subscriptions])
            ).all()

            # Build state
            state = {
                "user_id": user_id,
                "gpts": [{
                    "gpt_id": sub.gpt_definition_id,
                    "status": sub.status,
                    "is_primary": sub.is_primary,
                    "performance": next(
                        (p.metrics for p in performance if p.subscription_id == sub.id),
                        None
                    )
                } for sub in subscriptions],
                "last_updated": datetime.utcnow().isoformat()
            }

            if include_contexts:
                state["active_contexts"] = await self.gpt_coordination.get_active_contexts(user_id)

            return state

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving dashboard state: {str(e)}"
            )

    async def switch_primary_gpt(
        self,
        user_id: str,
        gpt_id: str
    ) -> Dict:
        """Switch the primary GPT for a user."""
        try:
            # Update subscriptions
            subscriptions = self.db.query(DashboardGPTSubscription).filter(
                DashboardGPTSubscription.user_id == user_id
            )
            
            # Set all to non-primary
            subscriptions.update({"is_primary": False})
            
            # Set new primary
            target_sub = subscriptions.filter(
                DashboardGPTSubscription.gpt_definition_id == gpt_id
            ).first()
            
            if not target_sub:
                raise HTTPException(
                    status_code=404,
                    detail="GPT subscription not found"
                )
            
            target_sub.is_primary = True
            self.db.commit()

            # Initialize new context if needed
            active_contexts = await self.gpt_coordination.get_active_contexts(
                user_id,
                gpt_id=gpt_id
            )

            if not active_contexts:
                context = await self.gpt_coordination.initialize_context(
                    user_id=user_id,
                    primary_gpt_id=gpt_id,
                    context_data={
                        "switch_type": "primary_gpt",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    name=f"Primary GPT Switch - {datetime.utcnow().isoformat()}"
                )
            else:
                context = active_contexts[0]

            return {
                "status": "success",
                "primary_gpt": gpt_id,
                "active_context": context
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error switching primary GPT: {str(e)}"
            )

    async def update_dashboard_preferences(
        self,
        user_id: str,
        preferences: Dict
    ) -> Dict:
        """Update dashboard preferences for a user."""
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            # Update preferences
            current_prefs = user.preferences or {}
            current_prefs.update(preferences)
            user.preferences = current_prefs
            
            self.db.commit()
            
            return {
                "status": "success",
                "preferences": user.preferences
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating preferences: {str(e)}"
            )

    async def get_gpt_recommendations(
        self,
        user_id: str,
        context_id: Optional[str] = None
    ) -> List[Dict]:
        """Get GPT recommendations for a user."""
        try:
            return await self.recommendation.get_recommendations(
                user_id=user_id,
                context_id=context_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting GPT recommendations: {str(e)}"
            )

    async def get_dashboard_layout(
        self,
        user_id: str,
        include_widgets: bool = True,
        include_positions: bool = True,
        include_sizes: bool = True
    ) -> Dict:
        """Get dashboard layout configuration."""
        try:
            # Get user's layout configuration
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            layout = user.dashboard_layout or {}
            result = {"layout_id": layout.get("id")}

            if include_widgets:
                result["widgets"] = layout.get("widgets", [])

            if include_positions:
                result["positions"] = layout.get("positions", {})

            if include_sizes:
                result["sizes"] = layout.get("sizes", {})

            return result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting dashboard layout: {str(e)}"
            )

    async def update_dashboard_layout(
        self,
        user_id: str,
        layout: Dict,
        validate: bool = True
    ) -> Dict:
        """Update dashboard layout configuration."""
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            # Validate layout if requested
            if validate:
                await self._validate_layout(layout)

            # Update layout
            current_layout = user.dashboard_layout or {}
            current_layout.update(layout)
            user.dashboard_layout = current_layout

            self.db.commit()

            return {
                "status": "success",
                "layout": user.dashboard_layout
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating dashboard layout: {str(e)}"
            )

    async def get_dashboard_widgets(
        self,
        user_id: str,
        widget_type: Optional[str] = None,
        include_data: bool = True,
        include_config: bool = True
    ) -> List[Dict]:
        """Get dashboard widgets for a user."""
        try:
            # Get user's widgets
            widgets = self.db.query(DashboardWidget).filter(
                DashboardWidget.user_id == user_id
            ).all()

            if widget_type:
                widgets = [w for w in widgets if w.widget_type == widget_type]

            result = []
            for widget in widgets:
                # Convert widget_type enum to string if needed
                widget_type_str = widget.widget_type.value if hasattr(widget.widget_type, 'value') else str(widget.widget_type)
                widget_data = {
                    'id': widget.id,
                    'type': widget_type_str,
                    'name': widget.name,
                    'description': widget.description,
                    'created_at': widget.created_at.isoformat() if widget.created_at else datetime.utcnow().isoformat(),
                    'updated_at': widget.updated_at.isoformat() if widget.updated_at else datetime.utcnow().isoformat()
                }

                if include_config:
                    widget_data['configuration'] = widget.configuration

                if include_data:
                    # Add resource sharing widget data handlers
                    if widget.widget_type == 'resource_usage':
                        widget_data['data'] = await self._get_resource_usage_data(widget.configuration)
                    elif widget.widget_type == 'resource_optimization':
                        widget_data['data'] = await self._get_resource_optimization_data(widget.configuration)
                    elif widget.widget_type == 'resource_prediction':
                        widget_data['data'] = await self._get_resource_prediction_data(widget.configuration)
                    elif widget.widget_type == 'cross_org_patterns':
                        widget_data['data'] = await self._get_cross_org_patterns_data(widget.configuration)
                    elif widget.widget_type == 'security_metrics':
                        widget_data['data'] = await self._get_security_metrics_data(widget.configuration)
                    else:
                        widget_data['data'] = await self._get_widget_data(widget)

                result.append(widget_data)

            return result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get dashboard widgets: {str(e)}"
            )

    async def create_dashboard_widget(
        self,
        user_id: str,
        widget_type: str,
        configuration: Dict,
        position: Optional[Dict] = None,
        size: Optional[Dict] = None
    ) -> Dict:
        """Create a new dashboard widget."""
        try:
            # Validate widget type
            valid_types = [
                'resource_usage',
                'resource_optimization',
                'resource_prediction',
                'cross_org_patterns',
                'security_metrics'
            ]
            
            if widget_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid widget type. Must be one of: {', '.join(valid_types)}"
                )

            # Validate configuration
            if not configuration.get('organization_id'):
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for resource sharing widgets"
                )

            # Create widget
            # Map widget_type string to WidgetType enum
            from ..models.dashboard_models import WidgetType, WidgetLayout
            
            # Convert widget_type string to enum (defaulting to CUSTOM if not found)
            # Since 'resource_usage' is not in WidgetType enum, always use CUSTOM but preserve original type
            widget_type_enum = WidgetType.CUSTOM
            # Store original widget_type in configuration for reference
            if isinstance(configuration, dict):
                configuration['original_widget_type'] = widget_type
            
            # Set default size if not provided
            default_size = size if size else {"width": 2, "height": 2}
            
            # Create widget - DashboardWidget model doesn't have 'position', uses 'layout_position'
            widget = DashboardWidget(
                user_id=int(user_id) if isinstance(user_id, str) and user_id.isdigit() else None,
                widget_type=widget_type_enum,
                layout_position=WidgetLayout.TOP_LEFT,  # Default layout position
                size=default_size,
                name=configuration.get('name', f"{widget_type.replace('_', ' ').title()} Widget"),
                description=configuration.get('description', ''),
                configuration=configuration,
                dashboard_id=1,  # Default dashboard_id - should be passed as parameter or retrieved
                organization_id=int(configuration.get('organization_id')) if configuration.get('organization_id') and str(configuration.get('organization_id')).isdigit() else None
            )
            
            # If position was provided, store it in configuration instead
            if position:
                widget.configuration = {**widget.configuration, 'position': position}

            self.db.add(widget)
            self.db.commit()
            self.db.refresh(widget)

            # Return original widget_type from configuration if available, otherwise use enum value
            returned_type = widget.widget_type.value if hasattr(widget.widget_type, 'value') else str(widget.widget_type)
            if isinstance(widget.configuration, dict) and 'original_widget_type' in widget.configuration:
                returned_type = widget.configuration.get('original_widget_type', returned_type)
            
            return {
                'id': str(widget.id) if widget.id else None,
                'type': returned_type,
                'name': widget.name,
                'description': widget.description,
                'configuration': widget.configuration,
                'position': widget.configuration.get('position') if isinstance(widget.configuration, dict) else None,
                'size': widget.size,
                'created_at': widget.created_at.isoformat() if widget.created_at else datetime.utcnow().isoformat(),
                'updated_at': widget.updated_at.isoformat() if widget.updated_at else datetime.utcnow().isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create dashboard widget: {str(e)}"
            )

    async def update_dashboard_widget(
        self,
        user_id: str,
        widget_id: str,
        configuration: Optional[Dict] = None,
        position: Optional[Dict] = None,
        size: Optional[Dict] = None
    ) -> Dict:
        """Update a dashboard widget."""
        try:
            # Get widget
            widget = self.db.query(DashboardWidget).filter(
                DashboardWidget.id == widget_id,
                DashboardWidget.user_id == user_id
            ).first()

            if not widget:
                raise HTTPException(
                    status_code=404,
                    detail="Widget not found"
                )

            # Update configuration if provided
            if configuration:
                await self._validate_widget_configuration(widget.widget_type, configuration)
                widget.configuration.update(configuration)

            # Update position if provided
            if position:
                widget.position = position

            # Update size if provided
            if size:
                widget.size = size

            self.db.commit()

            return {
                "id": widget.id,
                "type": widget.widget_type,
                "name": widget.name,
                "configuration": widget.configuration,
                "position": widget.position,
                "size": widget.size
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating dashboard widget: {str(e)}"
            )

    async def delete_dashboard_widget(
        self,
        user_id: str,
        widget_id: str
    ) -> Dict:
        """Delete a dashboard widget."""
        try:
            # Get widget
            widget = self.db.query(DashboardWidget).filter(
                DashboardWidget.id == widget_id,
                DashboardWidget.user_id == user_id
            ).first()

            if not widget:
                raise HTTPException(
                    status_code=404,
                    detail="Widget not found"
                )

            self.db.delete(widget)
            self.db.commit()

            return {
                "status": "success",
                "widget_id": widget_id
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting dashboard widget: {str(e)}"
            )

    async def get_dashboard_themes(
        self,
        user_id: str,
        include_custom: bool = True,
        include_preview: bool = True
    ) -> List[Dict]:
        """Get available dashboard themes."""
        try:
            # Get built-in themes
            themes = self._get_builtin_themes()

            # Add custom themes if requested
            if include_custom:
                custom_themes = self.db.query(DashboardTheme).filter(
                    DashboardTheme.user_id == user_id
                ).all()

                themes.extend([
                    {
                        "id": theme.id,
                        "name": theme.name,
                        "description": theme.description,
                        "colors": theme.colors,
                        "typography": theme.typography,
                        "spacing": theme.spacing,
                        "custom": True
                    }
                    for theme in custom_themes
                ])

            # Add previews if requested
            if include_preview:
                for theme in themes:
                    theme["preview"] = self._generate_theme_preview(theme)

            return themes

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting dashboard themes: {str(e)}"
            )

    async def create_dashboard_theme(
        self,
        user_id: str,
        theme: Dict
    ) -> Dict:
        """Create a custom dashboard theme."""
        try:
            # Validate theme configuration
            await self._validate_theme_configuration(theme)

            # Create theme
            theme_obj = DashboardTheme(
                id=f"theme-{uuid.uuid4()}",
                user_id=user_id,
                name=theme["name"],
                description=theme.get("description"),
                colors=theme["colors"],
                typography=theme["typography"],
                spacing=theme["spacing"]
            )

            self.db.add(theme_obj)
            self.db.commit()

            return {
                "id": theme_obj.id,
                "name": theme_obj.name,
                "description": theme_obj.description,
                "colors": theme_obj.colors,
                "typography": theme_obj.typography,
                "spacing": theme_obj.spacing,
                "custom": True
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating dashboard theme: {str(e)}"
            )

    async def update_dashboard_theme(
        self,
        user_id: str,
        theme_id: str,
        theme: Dict
    ) -> Dict:
        """Update a custom dashboard theme."""
        try:
            # Get theme
            theme_obj = self.db.query(DashboardTheme).filter(
                DashboardTheme.id == theme_id,
                DashboardTheme.user_id == user_id
            ).first()

            if not theme_obj:
                raise HTTPException(
                    status_code=404,
                    detail="Theme not found"
                )

            # Validate theme configuration
            await self._validate_theme_configuration(theme)

            # Update theme
            theme_obj.name = theme["name"]
            theme_obj.description = theme.get("description")
            theme_obj.colors = theme["colors"]
            theme_obj.typography = theme["typography"]
            theme_obj.spacing = theme["spacing"]

            self.db.commit()

            return {
                "id": theme_obj.id,
                "name": theme_obj.name,
                "description": theme_obj.description,
                "colors": theme_obj.colors,
                "typography": theme_obj.typography,
                "spacing": theme_obj.spacing,
                "custom": True
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating dashboard theme: {str(e)}"
            )

    async def delete_dashboard_theme(
        self,
        user_id: str,
        theme_id: str
    ) -> Dict:
        """Delete a custom dashboard theme."""
        try:
            # Get theme
            theme = self.db.query(DashboardTheme).filter(
                DashboardTheme.id == theme_id,
                DashboardTheme.user_id == user_id
            ).first()

            if not theme:
                raise HTTPException(
                    status_code=404,
                    detail="Theme not found"
                )

            self.db.delete(theme)
            self.db.commit()

            return {
                "status": "success",
                "theme_id": theme_id
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting dashboard theme: {str(e)}"
            )

    async def export_dashboard(
        self,
        user_id: str,
        format: str,
        include_data: bool = True,
        include_config: bool = True,
        time_range: Optional[str] = None
    ) -> Dict:
        """Export dashboard data and configuration."""
        try:
            # Get user's dashboard configuration
            # Convert user_id to int if it's a string
            try:
                user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=404,
                    detail="Invalid user ID"
                )
            
            user = self.db.query(User).filter(User.id == user_id_int).first()
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            export_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "format": format
            }

            if include_config:
                export_data["configuration"] = {
                    "layout": getattr(user, 'dashboard_layout', {}),
                    "preferences": getattr(user, 'preferences', {}),
                    "widgets": await self.get_dashboard_widgets(
                        user_id=str(user_id_int),
                        include_data=False
                    )
                }

            if include_data:
                export_data["data"] = await self._get_dashboard_data(
                    user_id=str(user_id_int),
                    time_range=time_range
                )

            # Convert to requested format
            if format == "json":
                return export_data
            elif format == "csv":
                return await self._convert_to_csv(export_data)
            elif format == "pdf":
                return await self._convert_to_pdf(export_data)
            else:
                # Invalid format - default to JSON
                self.logger.warning(f"Invalid format '{format}', defaulting to JSON")
                return export_data

        except HTTPException:
            # Re-raise HTTP exceptions (like 404)
            raise
        except Exception as e:
            self.logger.error(f"Error exporting dashboard: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error exporting dashboard: {str(e)}"
            )

    async def share_dashboard(
        self,
        user_id: str,
        share_type: str,
        expiration: Optional[int] = None,
        permissions: Optional[Dict] = None
    ) -> Dict:
        """Share dashboard with others."""
        try:
            # Create share configuration
            # Note: id is auto-generated by database (Integer primary key)
            share = DashboardShare(
                user_id=user_id,
                share_type=share_type,
                permissions=permissions or {},
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=expiration) if expiration else None
            )

            self.db.add(share)
            self.db.flush()  # Flush to get the auto-generated ID
            self.db.commit()

            # Generate share URL or embed code
            if share_type == "link":
                share_data = await self._generate_share_link(share)
            elif share_type == "embed":
                share_data = await self._generate_embed_code(share)
            elif share_type == "export":
                share_data = await self._generate_export_link(share)

            return {
                "share_id": share.id,
                "share_type": share_type,
                "share_data": share_data,
                "expires_at": share.expires_at.isoformat() if share.expires_at else None,
                "permissions": share.permissions
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error sharing dashboard: {str(e)}"
            )

    async def search_dashboard(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict] = None,
        include_widgets: bool = True,
        include_data: bool = True
    ) -> Dict:
        """Search dashboard content."""
        try:
            results = {
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "matches": []
            }

            # Search widgets if requested
            if include_widgets:
                widget_matches = await self._search_widgets(
                    user_id=user_id,
                    query=query,
                    filters=filters
                )
                results["matches"].extend(widget_matches)

            # Search dashboard data if requested
            if include_data:
                data_matches = await self._search_dashboard_data(
                    user_id=user_id,
                    query=query,
                    filters=filters
                )
                results["matches"].extend(data_matches)

            # Sort matches by relevance
            results["matches"].sort(key=lambda x: x["relevance"], reverse=True)

            return results

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching dashboard: {str(e)}"
            )

    async def get_dashboard_filters(
        self,
        user_id: str,
        filter_type: Optional[str] = None,
        include_values: bool = True,
        include_usage: bool = True
    ) -> List[Dict]:
        """Get available dashboard filters."""
        try:
            # Get filters
            query = self.db.query(DashboardFilter).filter(
                DashboardFilter.user_id == user_id
            )

            if filter_type:
                query = query.filter(DashboardFilter.filter_type == filter_type)

            filters = query.all()
            result = []

            for filter_obj in filters:
                filter_data = {
                    "id": filter_obj.id,
                    "type": filter_obj.filter_type,
                    "name": filter_obj.name,
                    "configuration": filter_obj.configuration
                }

                if include_values:
                    filter_data["values"] = await self._get_filter_values(filter_obj)

                if include_usage:
                    filter_data["usage"] = await self._get_filter_usage(filter_obj)

                result.append(filter_data)

            return result

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting dashboard filters: {str(e)}"
            )

    async def create_dashboard_filter(
        self,
        user_id: str,
        filter_type: str,
        configuration: Dict,
        apply_to: Optional[List[str]] = None
    ) -> Dict:
        """Create a new dashboard filter."""
        try:
            # Validate filter configuration
            await self._validate_filter_configuration(filter_type, configuration)

            # Create filter
            filter_obj = DashboardFilter(
                id=f"filter-{uuid.uuid4()}",
                user_id=user_id,
                filter_type=filter_type,
                name=configuration.get("name", f"New {filter_type} Filter"),
                configuration=configuration,
                applied_to=apply_to or []
            )

            self.db.add(filter_obj)
            self.db.commit()

            return {
                "id": filter_obj.id,
                "type": filter_obj.filter_type,
                "name": filter_obj.name,
                "configuration": filter_obj.configuration,
                "applied_to": filter_obj.applied_to
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating dashboard filter: {str(e)}"
            )

    async def update_dashboard_filter(
        self,
        user_id: str,
        filter_id: str,
        configuration: Dict,
        apply_to: Optional[List[str]] = None
    ) -> Dict:
        """Update a dashboard filter."""
        try:
            # Get filter
            filter_obj = self.db.query(DashboardFilter).filter(
                DashboardFilter.id == filter_id,
                DashboardFilter.user_id == user_id
            ).first()

            if not filter_obj:
                raise HTTPException(
                    status_code=404,
                    detail="Filter not found"
                )

            # Validate filter configuration
            await self._validate_filter_configuration(filter_obj.filter_type, configuration)

            # Update filter
            filter_obj.configuration.update(configuration)
            if apply_to is not None:
                filter_obj.applied_to = apply_to

            self.db.commit()

            return {
                "id": filter_obj.id,
                "type": filter_obj.filter_type,
                "name": filter_obj.name,
                "configuration": filter_obj.configuration,
                "applied_to": filter_obj.applied_to
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating dashboard filter: {str(e)}"
            )

    async def delete_dashboard_filter(
        self,
        user_id: str,
        filter_id: str
    ) -> Dict:
        """Delete a dashboard filter."""
        try:
            # Get filter
            filter_obj = self.db.query(DashboardFilter).filter(
                DashboardFilter.id == filter_id,
                DashboardFilter.user_id == user_id
            ).first()

            if not filter_obj:
                raise HTTPException(
                    status_code=404,
                    detail="Filter not found"
                )

            self.db.delete(filter_obj)
            self.db.commit()

            return {
                "status": "success",
                "filter_id": filter_id
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting dashboard filter: {str(e)}"
            )

    async def _validate_layout(self, layout: Dict):
        """Validate dashboard layout configuration."""
        try:
            # Validate layout structure
            if not isinstance(layout, dict):
                raise ValueError("Layout must be a dictionary")
            
            # Validate required fields
            required_fields = ['columns', 'rows', 'widgets']
            for field in required_fields:
                if field not in layout:
                    raise ValueError(f"Layout missing required field: {field}")
            
            # Validate columns and rows (must be positive integers)
            if not isinstance(layout['columns'], int) or layout['columns'] < 1:
                raise ValueError("Layout columns must be a positive integer")
            
            if not isinstance(layout['rows'], int) or layout['rows'] < 1:
                raise ValueError("Layout rows must be a positive integer")
            
            # Validate widgets array
            if not isinstance(layout['widgets'], list):
                raise ValueError("Layout widgets must be a list")
            
            # Validate each widget position
            for widget in layout['widgets']:
                if not isinstance(widget, dict):
                    raise ValueError("Each widget must be a dictionary")
                
                # Validate widget position
                if 'x' not in widget or 'y' not in widget:
                    raise ValueError("Widget missing position (x, y)")
                
                x, y = widget['x'], widget['y']
                if not isinstance(x, int) or not isinstance(y, int):
                    raise ValueError("Widget position (x, y) must be integers")
                
                if x < 0 or x >= layout['columns']:
                    raise ValueError(f"Widget x position {x} out of bounds (0-{layout['columns']-1})")
                
                if y < 0 or y >= layout['rows']:
                    raise ValueError(f"Widget y position {y} out of bounds (0-{layout['rows']-1})")
                
                # Validate widget size if provided
                if 'width' in widget:
                    if not isinstance(widget['width'], int) or widget['width'] < 1:
                        raise ValueError("Widget width must be a positive integer")
                    if widget['x'] + widget['width'] > layout['columns']:
                        raise ValueError(f"Widget width exceeds layout columns")
                
                if 'height' in widget:
                    if not isinstance(widget['height'], int) or widget['height'] < 1:
                        raise ValueError("Widget height must be a positive integer")
                    if widget['y'] + widget['height'] > layout['rows']:
                        raise ValueError(f"Widget height exceeds layout rows")
            
            return True
        except ValueError as e:
            self.logger.error(f"Layout validation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error validating layout: {str(e)}")
            raise ValueError(f"Layout validation failed: {str(e)}")

    async def _validate_widget_configuration(self, widget_type: str, configuration: Dict):
        """Validate widget configuration."""
        try:
            # Validate configuration is a dictionary
            if not isinstance(configuration, dict):
                raise ValueError("Widget configuration must be a dictionary")
            
            # Validate widget_type is a valid enum value
            try:
                widget_type_enum = WidgetType(widget_type)
            except ValueError:
                raise ValueError(f"Invalid widget type: {widget_type}")
            
            # Common required fields for all widgets
            common_fields = ['title', 'data_source']
            for field in common_fields:
                if field not in configuration:
                    self.logger.warning(f"Widget configuration missing optional field: {field}")
            
            # Type-specific validation
            if widget_type_enum == WidgetType.CHART:
                if 'chart_type' not in configuration:
                    raise ValueError("Chart widgets require 'chart_type' field")
                valid_chart_types = ['line', 'bar', 'pie', 'scatter', 'area', 'gauge']
                if configuration['chart_type'] not in valid_chart_types:
                    raise ValueError(f"Invalid chart type. Must be one of: {valid_chart_types}")
            
            elif widget_type_enum == WidgetType.TABLE:
                if 'columns' not in configuration:
                    raise ValueError("Table widgets require 'columns' field")
                if not isinstance(configuration['columns'], list):
                    raise ValueError("Table 'columns' must be a list")
            
            elif widget_type_enum == WidgetType.METRIC:
                if 'metric_type' not in configuration:
                    raise ValueError("Metric widgets require 'metric_type' field")
                if 'value' not in configuration and 'data_source' not in configuration:
                    raise ValueError("Metric widgets require either 'value' or 'data_source'")
            
            elif widget_type_enum == WidgetType.TEXT:
                if 'content' not in configuration:
                    raise ValueError("Text widgets require 'content' field")
            
            # Validate refresh_interval if provided
            if 'refresh_interval' in configuration:
                interval = configuration['refresh_interval']
                if not isinstance(interval, int) or interval < 0:
                    raise ValueError("Refresh interval must be a non-negative integer")
            
            # Validate size if provided
            if 'size' in configuration:
                size = configuration['size']
                if not isinstance(size, dict):
                    raise ValueError("Size must be a dictionary")
                if 'width' in size and (not isinstance(size['width'], int) or size['width'] < 1):
                    raise ValueError("Size width must be a positive integer")
                if 'height' in size and (not isinstance(size['height'], int) or size['height'] < 1):
                    raise ValueError("Size height must be a positive integer")
            
            return True
        except ValueError as e:
            self.logger.error(f"Widget configuration validation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error validating widget configuration: {str(e)}")
            raise ValueError(f"Widget configuration validation failed: {str(e)}")

    async def _get_widget_data(self, widget: DashboardWidget) -> Dict:
        """Get data for a dashboard widget."""
        try:
            # Get base widget data
            data = await self._get_base_widget_data(widget)

            # Apply visualization settings
            if widget.visualization:
                data = await self._apply_visualization_settings(data, widget.visualization)

            # Add correlated metrics if specified
            if widget.metric_correlations:
                data["correlated_metrics"] = await self._get_correlated_metrics(
                    widget.user_id,
                    widget.metric_correlations
                )

            return data
        except Exception as e:
            logger.error(f"Error getting widget data: {str(e)}")
            raise

    async def _apply_visualization_settings(
        self,
        data: Dict,
        visualization: Dict
    ) -> Dict:
        """Apply visualization settings to widget data."""
        try:
            # Apply color scheme
            if "color_scheme" in visualization:
                data["visualization"] = {
                    "colors": self._get_color_scheme(visualization["color_scheme"])
                }

            # Apply chart types
            if "primary_type" in visualization:
                data["visualization"]["primary_chart"] = {
                    "type": visualization["primary_type"],
                    "config": self._get_chart_config(visualization["primary_type"])
                }

            if "secondary_type" in visualization:
                data["visualization"]["secondary_chart"] = {
                    "type": visualization["secondary_type"],
                    "config": self._get_chart_config(visualization["secondary_type"])
                }

            # Apply display options
            if "display_options" in visualization:
                data["visualization"]["options"] = visualization["display_options"]

            # Apply layout settings
            if "layout" in visualization:
                data["visualization"]["layout"] = visualization["layout"]

            return data
        except Exception as e:
            logger.error(f"Error applying visualization settings: {str(e)}")
            raise

    async def _get_correlated_metrics(
        self,
        user_id: str,
        correlations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get correlated metrics for a widget."""
        try:
            correlated_data = {}
            
            for correlation in correlations:
                metric_type = correlation["metric"]
                correlation_type = correlation["correlation_type"]
                threshold = correlation["threshold"]
                visualization = correlation.get("visualization", "scatter_plot")

                # Get base metric data
                if metric_type == "resource_utilization":
                    metric_data = await self.collaboration_service.get_resource_metrics(
                        user_id=user_id
                    )
                elif metric_type == "team_performance":
                    metric_data = await self.collaboration_service.get_team_metrics(
                        user_id=user_id
                    )
                elif metric_type == "quality_metrics":
                    metric_data = await self.collaboration_service.get_quality_metrics(
                        user_id=user_id
                    )

                # Calculate correlation
                correlation_data = await self._calculate_correlation(
                    metric_data,
                    correlation_type,
                    threshold
                )

                # Add visualization config
                correlation_data["visualization"] = {
                    "type": visualization,
                    "config": self._get_chart_config(visualization)
                }

                correlated_data[metric_type] = correlation_data

            return correlated_data
        except Exception as e:
            logger.error(f"Error getting correlated metrics: {str(e)}")
            raise

    async def _calculate_correlation(
        self,
        metric_data: Dict[str, Any],
        correlation_type: str,
        threshold: float
    ) -> Dict[str, Any]:
        """Calculate correlation between metrics."""
        try:
            # Calculate basic correlation
            correlation_score = await self.collaboration_service.calculate_correlation(
                metric_data,
                correlation_type
            )

            return {
                "score": correlation_score,
                "threshold": threshold,
                "is_significant": correlation_score >= threshold,
                "correlation_type": correlation_type,
                "trend": "increasing" if correlation_score > 0 else "decreasing",
                "strength": self._get_correlation_strength(correlation_score)
            }
        except Exception as e:
            logger.error(f"Error calculating correlation: {str(e)}")
            raise

    def _get_correlation_strength(self, score: float) -> str:
        """Get correlation strength category."""
        abs_score = abs(score)
        if abs_score >= 0.8:
            return "very_strong"
        elif abs_score >= 0.6:
            return "strong"
        elif abs_score >= 0.4:
            return "moderate"
        elif abs_score >= 0.2:
            return "weak"
        else:
            return "very_weak"

    def _get_color_scheme(self, scheme_name: str) -> Dict[str, str]:
        """Get color scheme configuration."""
        color_schemes = {
            "performance": {
                "primary": "#2196F3",
                "secondary": "#4CAF50",
                "accent": "#FFC107",
                "error": "#F44336",
                "gradient": ["#1976D2", "#2196F3", "#64B5F6", "#BBDEFB"]
            },
            "engagement": {
                "primary": "#9C27B0",
                "secondary": "#E91E63",
                "accent": "#3F51B5",
                "error": "#F44336",
                "gradient": ["#7B1FA2", "#9C27B0", "#BA68C8", "#E1BEE7"]
            },
            "quality": {
                "primary": "#4CAF50",
                "secondary": "#8BC34A",
                "accent": "#CDDC39",
                "error": "#F44336",
                "gradient": ["#388E3C", "#4CAF50", "#81C784", "#C8E6C9"]
            },
            "innovation": {
                "primary": "#FF4081",
                "secondary": "#FF80AB",
                "accent": "#F50057",
                "error": "#F44336",
                "gradient": ["#C51162", "#FF4081", "#FF80AB", "#FCE4EC"]
            },
            "analytics": {
                "primary": "#00BCD4",
                "secondary": "#26C6DA",
                "accent": "#00ACC1",
                "error": "#F44336",
                "gradient": ["#0097A7", "#00BCD4", "#4DD0E1", "#B2EBF2"]
            }
        }
        return color_schemes.get(scheme_name, color_schemes["performance"])

    def _get_chart_config(self, chart_type: str) -> Dict[str, Any]:
        """Get chart configuration."""
        configs = {
            "line_chart": {
                "showPoints": True,
                "showGrid": True,
                "showLegend": True,
                "animate": True,
                "curve": "smooth",
                "areaFill": True,
                "yAxisFormat": "percentage"
            },
            "bar_chart": {
                "showValues": True,
                "showGrid": True,
                "showLegend": True,
                "animate": True,
                "barWidth": 0.7,
                "groupPadding": 0.2
            },
            "gauge": {
                "showValue": True,
                "showThresholds": True,
                "animate": True,
                "min": 0,
                "max": 100,
                "arcWidth": 0.2
            },
            "pie_chart": {
                "showLabels": True,
                "showLegend": True,
                "animate": True,
                "donut": False,
                "labelPosition": "outside"
            },
            "heatmap": {
                "showValues": True,
                "animate": True,
                "cellSize": "medium",
                "legendPosition": "right",
                "colorScale": "sequential"
            },
            "scatter_plot": {
                "showPoints": True,
                "showGrid": True,
                "showTrendline": True,
                "animate": True,
                "pointSize": 6
            },
            "bubble_chart": {
                "showLabels": True,
                "showGrid": True,
                "animate": True,
                "bubbleSize": [5, 20],
                "showLegend": True
            },
            "radar_chart": {
                "showLabels": True,
                "showGrid": True,
                "animate": True,
                "fillArea": True,
                "startAngle": 0
            },
            "funnel_chart": {
                "showLabels": True,
                "showValues": True,
                "animate": True,
                "gradientDirection": "horizontal"
            },
            "tree_map": {
                "showLabels": True,
                "showValues": True,
                "animate": True,
                "layoutAlgorithm": "squarified"
            },
            "sankey_diagram": {
                "nodeWidth": 20,
                "nodePadding": 8,
                "iterations": 32,
                "curvature": 0.5,
                "align": "justify",
                "linkColor": "gradient"
            },
            "force_directed_graph": {
                "forceStrength": 0.1,
                "distance": 100,
                "collisionRadius": 5,
                "clusterPadding": 6,
                "centerGravity": 0.1,
                "animate": True
            },
            "gantt_chart": {
                "barHeight": 20,
                "barPadding": 4,
                "showProgress": True,
                "showDependencies": True,
                "dateFormat": "YYYY-MM-DD",
                "showToday": True
            },
            "violin_plot": {
                "bandwidth": "auto",
                "showBoxPlot": True,
                "showMean": True,
                "orientation": "vertical",
                "showPoints": True
            },
            "parallel_coordinates": {
                "lineTension": 0.5,
                "brushingEnabled": True,
                "axisPadding": 40,
                "highlightOpacity": 0.8,
                "dimensions": "auto"
            },
            "sunburst_chart": {
                "innerRadius": 0,
                "cornerRadius": 3,
                "padding": 1,
                "sortByValue": True,
                "showLabels": True
            },
            "network_graph": {
                "nodeSize": "degree",
                "edgeWidth": "weight",
                "communityDetection": True,
                "layout": "force_atlas2",
                "interactive": True
            },
            "choropleth_map": {
                "projection": "mercator",
                "scaleType": "quantize",
                "steps": 7,
                "borderWidth": 0.5,
                "showLegend": True
            }
        }
        return configs.get(chart_type, {})

    async def _validate_theme_configuration(self, theme: Dict):
        """Validate theme configuration."""
        try:
            # Validate theme is a dictionary
            if not isinstance(theme, dict):
                raise ValueError("Theme must be a dictionary")
            
            # Validate required fields
            required_fields = ['name', 'colors']
            for field in required_fields:
                if field not in theme:
                    raise ValueError(f"Theme missing required field: {field}")
            
            # Validate name
            if not isinstance(theme['name'], str) or len(theme['name']) == 0:
                raise ValueError("Theme name must be a non-empty string")
            
            # Validate colors
            if not isinstance(theme['colors'], dict):
                raise ValueError("Theme colors must be a dictionary")
            
            required_colors = ['primary', 'secondary', 'background', 'text']
            for color in required_colors:
                if color not in theme['colors']:
                    raise ValueError(f"Theme missing required color: {color}")
                # Validate color format (hex, rgb, or named color)
                color_value = theme['colors'][color]
                if not isinstance(color_value, str):
                    raise ValueError(f"Color '{color}' must be a string")
            
            # Validate typography if provided
            if 'typography' in theme:
                if not isinstance(theme['typography'], dict):
                    raise ValueError("Theme typography must be a dictionary")
                if 'font_family' in theme['typography']:
                    if not isinstance(theme['typography']['font_family'], str):
                        raise ValueError("Font family must be a string")
                if 'font_size' in theme['typography']:
                    font_size = theme['typography']['font_size']
                    if not isinstance(font_size, (int, float)) or font_size <= 0:
                        raise ValueError("Font size must be a positive number")
            
            # Validate spacing if provided
            if 'spacing' in theme:
                if not isinstance(theme['spacing'], dict):
                    raise ValueError("Theme spacing must be a dictionary")
                spacing_fields = ['padding', 'margin', 'gap']
                for field in spacing_fields:
                    if field in theme['spacing']:
                        spacing_value = theme['spacing'][field]
                        if not isinstance(spacing_value, (int, float)) or spacing_value < 0:
                            raise ValueError(f"Spacing '{field}' must be a non-negative number")
            
            return True
        except ValueError as e:
            self.logger.error(f"Theme configuration validation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error validating theme configuration: {str(e)}")
            raise ValueError(f"Theme configuration validation failed: {str(e)}")

    def _get_builtin_themes(self) -> List[Dict]:
        """Get built-in dashboard themes."""
        return [
            {
                "name": "Default",
                "description": "Clean and professional default theme",
                "colors": {
                    "primary": "#2196F3",
                    "secondary": "#4CAF50",
                    "background": "#FFFFFF",
                    "text": "#212121",
                    "accent": "#FFC107",
                    "error": "#F44336",
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "info": "#2196F3"
                },
                "typography": {
                    "font_family": "Roboto, sans-serif",
                    "font_size": 14,
                    "heading_font": "Roboto, sans-serif"
                },
                "spacing": {
                    "padding": 16,
                    "margin": 8,
                    "gap": 12
                }
            },
            {
                "name": "Dark",
                "description": "Dark theme for reduced eye strain",
                "colors": {
                    "primary": "#64B5F6",
                    "secondary": "#81C784",
                    "background": "#121212",
                    "text": "#FFFFFF",
                    "accent": "#FFB74D",
                    "error": "#E57373",
                    "success": "#81C784",
                    "warning": "#FFB74D",
                    "info": "#64B5F6"
                },
                "typography": {
                    "font_family": "Roboto, sans-serif",
                    "font_size": 14,
                    "heading_font": "Roboto, sans-serif"
                },
                "spacing": {
                    "padding": 16,
                    "margin": 8,
                    "gap": 12
                }
            },
            {
                "name": "High Contrast",
                "description": "High contrast theme for accessibility",
                "colors": {
                    "primary": "#0000FF",
                    "secondary": "#008000",
                    "background": "#FFFFFF",
                    "text": "#000000",
                    "accent": "#FF0000",
                    "error": "#FF0000",
                    "success": "#008000",
                    "warning": "#FFA500",
                    "info": "#0000FF"
                },
                "typography": {
                    "font_family": "Arial, sans-serif",
                    "font_size": 16,
                    "heading_font": "Arial, sans-serif"
                },
                "spacing": {
                    "padding": 20,
                    "margin": 10,
                    "gap": 16
                }
            },
            {
                "name": "Professional",
                "description": "Professional theme for business use",
                "colors": {
                    "primary": "#1976D2",
                    "secondary": "#388E3C",
                    "background": "#FAFAFA",
                    "text": "#263238",
                    "accent": "#F57C00",
                    "error": "#D32F2F",
                    "success": "#388E3C",
                    "warning": "#F57C00",
                    "info": "#1976D2"
                },
                "typography": {
                    "font_family": "Open Sans, sans-serif",
                    "font_size": 14,
                    "heading_font": "Open Sans, sans-serif"
                },
                "spacing": {
                    "padding": 16,
                    "margin": 8,
                    "gap": 12
                }
            },
            {
                "name": "Colorful",
                "description": "Vibrant and colorful theme",
                "colors": {
                    "primary": "#9C27B0",
                    "secondary": "#E91E63",
                    "background": "#FFFFFF",
                    "text": "#212121",
                    "accent": "#FF5722",
                    "error": "#F44336",
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "info": "#00BCD4"
                },
                "typography": {
                    "font_family": "Comic Sans MS, sans-serif",
                    "font_size": 14,
                    "heading_font": "Comic Sans MS, sans-serif"
                },
                "spacing": {
                    "padding": 16,
                    "margin": 8,
                    "gap": 12
                }
            }
        ]

    def _generate_theme_preview(self, theme: Dict) -> str:
        """Generate preview image for a theme.
        
        Returns a base64-encoded SVG preview of the theme colors and styling.
        For production, this could be enhanced with PIL/Pillow for PNG generation.
        """
        try:
            import base64
            
            # Extract theme colors
            colors = theme.get("colors", {})
            primary = colors.get("primary", "#1a1a1a")
            secondary = colors.get("secondary", "#4a4a4a")
            background = colors.get("background", "#ffffff")
            text = colors.get("text", "#1a1a1a")
            accent = colors.get("accent", "#007bff")
            
            # Generate simple SVG preview
            svg = f'''<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">
                <rect width="200" height="150" fill="{background}"/>
                <rect x="10" y="10" width="60" height="60" fill="{primary}" rx="4"/>
                <rect x="80" y="10" width="60" height="60" fill="{secondary}" rx="4"/>
                <rect x="150" y="10" width="40" height="60" fill="{accent}" rx="4"/>
                <text x="10" y="90" font-family="Arial" font-size="14" fill="{text}">{theme.get("name", "Theme")}</text>
                <rect x="10" y="100" width="180" height="10" fill="{primary}" opacity="0.3" rx="2"/>
                <rect x="10" y="115" width="120" height="10" fill="{secondary}" opacity="0.3" rx="2"/>
                <rect x="10" y="130" width="80" height="10" fill="{accent}" opacity="0.3" rx="2"/>
            </svg>'''
            
            # Encode to base64
            svg_bytes = svg.encode('utf-8')
            preview = base64.b64encode(svg_bytes).decode('utf-8')
            return f"data:image/svg+xml;base64,{preview}"
        except Exception as e:
            self.logger.error(f"Error generating theme preview: {str(e)}")
            return ""

    async def _get_dashboard_data(self, user_id: str, time_range: Optional[str] = None) -> Dict:
        """Get dashboard data for export."""
        try:
            # Convert user_id to int if it's a string
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            
            # Get user's dashboard widgets with data
            # Use include_data=False to avoid widget data loading issues
            widgets = await self.get_dashboard_widgets(
                user_id=str(user_id_int),
                include_data=False
            )
            
            # Get user's dashboard configuration
            user = self.db.query(User).filter(User.id == user_id_int).first()
            if not user:
                return {}
            
            # Calculate time range
            if time_range:
                if time_range == "week":
                    start_date = datetime.utcnow() - timedelta(days=7)
                elif time_range == "month":
                    start_date = datetime.utcnow() - timedelta(days=30)
                elif time_range == "semester":
                    start_date = datetime.utcnow() - timedelta(days=90)
                elif time_range == "year":
                    start_date = datetime.utcnow() - timedelta(days=365)
                else:
                    start_date = datetime.utcnow() - timedelta(days=30)
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            return {
                "user_id": str(user_id_int),
                "user_name": getattr(user, 'name', getattr(user, 'email', 'Unknown')),
                "export_date": datetime.utcnow().isoformat(),
                "time_range": time_range or "month",
                "start_date": start_date.isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "widgets": widgets,
                "widget_count": len(widgets) if isinstance(widgets, list) else 0,
                "dashboard_layout": getattr(user, 'dashboard_layout', {}),
                "preferences": getattr(user, 'preferences', {})
            }
        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {str(e)}")
            # Try to preserve user_id even if conversion fails
            try:
                user_id_str = str(user_id) if user_id else "unknown"
            except:
                user_id_str = "unknown"
            return {
                "user_id": user_id_str,
                "export_date": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    async def _convert_to_csv(self, data: Dict) -> bytes:
        """Convert dashboard data to CSV format."""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Dashboard Export"])
            writer.writerow(["Export Date", data.get("timestamp", datetime.utcnow().isoformat())])
            writer.writerow([])
            
            # Write configuration if available
            if "configuration" in data:
                writer.writerow(["Configuration"])
                config = data["configuration"]
                if "layout" in config:
                    writer.writerow(["Layout", json.dumps(config["layout"])])
                if "preferences" in config:
                    writer.writerow(["Preferences", json.dumps(config["preferences"])])
                writer.writerow([])
            
            # Write data section
            if "data" in data and data["data"]:
                data_section = data["data"]
                writer.writerow(["Dashboard Data"])
                writer.writerow(["User ID", data_section.get("user_id", "N/A")])
                writer.writerow(["User Name", data_section.get("user_name", "N/A")])
                writer.writerow(["Time Range", data_section.get("time_range", "N/A")])
                writer.writerow(["Widget Count", data_section.get("widget_count", 0)])
                writer.writerow([])
                
                # Write widgets data
                widgets = data_section.get("widgets", [])
                if widgets:
                    writer.writerow(["Widgets"])
                    writer.writerow(["Widget ID", "Widget Type", "Widget Name", "Data"])
                    for widget in widgets:
                        widget_id = widget.get("id", widget.get("widget_id", "N/A"))
                        widget_type = widget.get("type", widget.get("widget_type", "N/A"))
                        widget_name = widget.get("name", widget.get("title", "N/A"))
                        widget_data = json.dumps(widget.get("data", {}))[:100]  # Truncate long data
                        writer.writerow([widget_id, widget_type, widget_name, widget_data])
            
            # Convert to bytes
            output.seek(0)
            return output.getvalue().encode('utf-8')
        except Exception as e:
            logger.error(f"Error converting to CSV: {str(e)}")
            return f"Error generating CSV: {str(e)}".encode('utf-8')

    async def _convert_to_pdf(self, data: Dict) -> bytes:
        """Convert dashboard data to PDF format."""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
            )
            story.append(Paragraph("Dashboard Export", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Export metadata
            export_date = data.get("timestamp", datetime.utcnow().isoformat())
            story.append(Paragraph(f"<b>Export Date:</b> {export_date}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Configuration section
            if "configuration" in data:
                story.append(Paragraph("<b>Configuration</b>", styles['Heading2']))
                config = data["configuration"]
                if "layout" in config:
                    story.append(Paragraph(f"Layout: {json.dumps(config['layout'])[:200]}...", styles['Normal']))
                if "preferences" in config:
                    story.append(Paragraph(f"Preferences: {json.dumps(config['preferences'])[:200]}...", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Data section
            if "data" in data and data["data"]:
                data_section = data["data"]
                story.append(Paragraph("<b>Dashboard Data</b>", styles['Heading2']))
                
                # Create data table
                table_data = [
                    ["Field", "Value"],
                    ["User ID", str(data_section.get("user_id", "N/A"))],
                    ["User Name", data_section.get("user_name", "N/A")],
                    ["Time Range", data_section.get("time_range", "N/A")],
                    ["Widget Count", str(data_section.get("widget_count", 0))],
                ]
                
                table = Table(table_data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
                
                # Widgets section
                widgets = data_section.get("widgets", [])
                if widgets:
                    story.append(Paragraph("<b>Widgets</b>", styles['Heading3']))
                    widget_table_data = [["Widget ID", "Type", "Name"]]
                    for widget in widgets[:20]:  # Limit to 20 widgets for PDF
                        widget_id = str(widget.get("id", widget.get("widget_id", "N/A")))
                        widget_type = widget.get("type", widget.get("widget_type", "N/A"))
                        widget_name = widget.get("name", widget.get("title", "N/A"))
                        widget_table_data.append([widget_id, widget_type, widget_name])
                    
                    widget_table = Table(widget_table_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
                    widget_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
                    ]))
                    story.append(widget_table)
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            self.logger.error(f"Error converting to PDF: {str(e)}")
            # Return a simple error PDF
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = [Paragraph(f"Error generating PDF: {str(e)}", getSampleStyleSheet()['Normal'])]
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

    async def _generate_share_link(self, share: DashboardShare) -> str:
        """Generate shareable link for dashboard."""
        try:
            settings = get_settings()
            # Get base URL from environment or use default
            base_url = os.getenv("FRONTEND_URL", os.getenv("BASE_URL", "http://localhost:3000"))
            
            # Remove trailing slash
            base_url = base_url.rstrip('/')
            
            # Generate share link
            share_link = f"{base_url}/dashboard/share/{share.id}"
            
            # Add expiration info if applicable
            if share.expires_at:
                expires_timestamp = int(share.expires_at.timestamp())
                share_link += f"?expires={expires_timestamp}"
            
            return share_link
        except Exception as e:
            self.logger.error(f"Error generating share link: {str(e)}")
            # Fallback to simple link
            return f"/dashboard/share/{share.id}"

    async def _generate_embed_code(self, share: DashboardShare) -> str:
        """Generate embed code for dashboard."""
        try:
            settings = get_settings()
            # Get base URL from environment or use default
            base_url = os.getenv("FRONTEND_URL", os.getenv("BASE_URL", "http://localhost:3000"))
            
            # Remove trailing slash
            base_url = base_url.rstrip('/')
            
            # Generate embed URL
            embed_url = f"{base_url}/dashboard/embed/{share.id}"
            
            # Generate iframe embed code
            width = share.permissions.get("width", "100%")
            height = share.permissions.get("height", "600px")
            
            embed_code = f'<iframe src="{embed_url}" width="{width}" height="{height}" frameborder="0" allowfullscreen></iframe>'
            
            return embed_code
        except Exception as e:
            self.logger.error(f"Error generating embed code: {str(e)}")
            # Fallback embed code
            return f'<iframe src="/dashboard/embed/{share.id}" width="100%" height="600px" frameborder="0"></iframe>'

    async def _generate_export_link(self, share: DashboardShare) -> str:
        """Generate export link for dashboard."""
        try:
            settings = get_settings()
            # Get base URL from environment or use default
            base_url = os.getenv("API_URL", os.getenv("BASE_URL", "http://localhost:8000"))
            
            # Remove trailing slash
            base_url = base_url.rstrip('/')
            
            # Generate export download link
            export_link = f"{base_url}/api/v1/dashboard/export/{share.id}"
            
            # Add format parameter if specified in permissions
            format_type = share.permissions.get("format", "json")
            export_link += f"?format={format_type}"
            
            # Add expiration info if applicable
            if share.expires_at:
                expires_timestamp = int(share.expires_at.timestamp())
                export_link += f"&expires={expires_timestamp}"
            
            return export_link
        except Exception as e:
            self.logger.error(f"Error generating export link: {str(e)}")
            # Fallback to simple link
            return f"/api/v1/dashboard/export/{share.id}"

    async def _search_widgets(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search dashboard widgets."""
        try:
            from sqlalchemy import or_, text
            
            # Convert user_id to int if needed
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            
            # Build base query
            base_query = self.db.query(DashboardWidget).filter(
                DashboardWidget.user_id == user_id_int
            )
            
            # Apply text search on name, description, and widget_type
            if query:
                search_term = f"%{query.lower()}%"
                base_query = base_query.filter(
                    or_(
                        DashboardWidget.name.ilike(search_term),
                        DashboardWidget.description.ilike(search_term),
                        DashboardWidget.widget_type.ilike(search_term)
                    )
                )
            
            # Apply filters if provided
            if filters:
                if 'widget_type' in filters:
                    base_query = base_query.filter(
                        DashboardWidget.widget_type == filters['widget_type']
                    )
                
                if 'is_active' in filters:
                    base_query = base_query.filter(
                        DashboardWidget.is_active == filters['is_active']
                    )
                
                if 'is_visible' in filters:
                    base_query = base_query.filter(
                        DashboardWidget.is_visible == filters['is_visible']
                    )
                
                if 'dashboard_id' in filters:
                    base_query = base_query.filter(
                        DashboardWidget.dashboard_id == filters['dashboard_id']
                    )
            
            # Execute query with timeout
            try:
                self.db.execute(text("SET LOCAL statement_timeout = '10s'"))
            except:
                pass
            
            widgets = base_query.limit(100).all()  # Limit to 100 results
            
            # Convert to dict format
            results = []
            for widget in widgets:
                results.append({
                    "id": widget.id,
                    "name": widget.name,
                    "description": widget.description,
                    "widget_type": widget.widget_type.value if hasattr(widget.widget_type, 'value') else str(widget.widget_type),
                    "is_active": widget.is_active,
                    "is_visible": widget.is_visible,
                    "dashboard_id": widget.dashboard_id,
                    "created_at": widget.created_at.isoformat() if widget.created_at else None,
                    "updated_at": widget.updated_at.isoformat() if widget.updated_at else None
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching widgets: {str(e)}")
            return []

    async def _search_dashboard_data(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Search dashboard data."""
        try:
            from sqlalchemy import or_, text
            
            # Convert user_id to int if needed
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            
            results = []
            
            # Search widgets
            if query:
                search_term = f"%{query.lower()}%"
                widgets = self.db.query(DashboardWidget).filter(
                    DashboardWidget.user_id == user_id_int,
                    or_(
                        DashboardWidget.name.ilike(search_term),
                        DashboardWidget.description.ilike(search_term)
                    )
                ).limit(50).all()
                
                for widget in widgets:
                    results.append({
                        "type": "widget",
                        "id": widget.id,
                        "name": widget.name,
                        "description": widget.description,
                        "widget_type": widget.widget_type.value if hasattr(widget.widget_type, 'value') else str(widget.widget_type),
                        "dashboard_id": widget.dashboard_id
                    })
            
            # Search dashboards
            dashboards = self.db.query(Dashboard).filter(
                Dashboard.user_id == user_id_int
            )
            
            if query:
                search_term = f"%{query.lower()}%"
                dashboards = dashboards.filter(
                    or_(
                        Dashboard.name.ilike(search_term),
                        Dashboard.description.ilike(search_term)
                    )
                )
            
            if filters and 'dashboard_status' in filters:
                dashboards = dashboards.filter(
                    Dashboard.status == filters['dashboard_status']
                )
            
            dashboards = dashboards.limit(50).all()
            
            for dashboard in dashboards:
                results.append({
                    "type": "dashboard",
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "status": dashboard.status.value if hasattr(dashboard.status, 'value') else str(dashboard.status)
                })
            
            # Search filters
            if query:
                search_term = f"%{query.lower()}%"
                dashboard_filters = self.db.query(DashboardFilter).filter(
                    DashboardFilter.user_id == user_id_int,
                    DashboardFilter.name.ilike(search_term)
                ).limit(50).all()
                
                for filter_obj in dashboard_filters:
                    results.append({
                        "type": "filter",
                        "id": filter_obj.id,
                        "name": filter_obj.name,
                        "filter_type": filter_obj.filter_type
                    })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching dashboard data: {str(e)}")
            return []

    async def _get_filter_values(self, filter_obj: DashboardFilter) -> List:
        """Get available values for a filter."""
        try:
            from sqlalchemy import text
            
            # Get filter configuration
            config = filter_obj.configuration if isinstance(filter_obj.configuration, dict) else {}
            filter_type = filter_obj.filter_type
            
            # Add timeout
            try:
                self.db.execute(text("SET LOCAL statement_timeout = '10s'"))
            except:
                pass
            
            values = []
            
            # Get values based on filter type
            if filter_type == "widget_type":
                # Get all widget types for this user
                widget_types = self.db.query(DashboardWidget.widget_type).filter(
                    DashboardWidget.user_id == filter_obj.user_id
                ).distinct().all()
                values = [wt[0].value if hasattr(wt[0], 'value') else str(wt[0]) for wt in widget_types]
            
            elif filter_type == "dashboard":
                # Get all dashboard names for this user
                dashboards = self.db.query(Dashboard.name, Dashboard.id).filter(
                    Dashboard.user_id == filter_obj.user_id
                ).all()
                values = [{"name": d[0], "id": d[1]} for d in dashboards]
            
            elif filter_type == "date_range":
                # Get date range options
                values = [
                    {"label": "Last 7 days", "value": "7d"},
                    {"label": "Last 30 days", "value": "30d"},
                    {"label": "Last 90 days", "value": "90d"},
                    {"label": "Last year", "value": "1y"},
                    {"label": "Custom", "value": "custom"}
                ]
            
            elif filter_type == "status":
                # Get status options from configuration or use defaults
                if 'options' in config:
                    values = config['options']
                else:
                    values = ["active", "inactive", "archived"]
            
            elif filter_type == "custom":
                # Get custom values from configuration
                if 'values' in config:
                    values = config['values']
                elif 'query' in config:
                    # Execute custom query if provided (with safety checks)
                    try:
                        # Only allow SELECT queries for safety
                        query = config['query']
                        if query.strip().upper().startswith('SELECT'):
                            result = self.db.execute(text(query))
                            values = [row[0] for row in result.fetchall()]
                    except Exception as e:
                        self.logger.error(f"Error executing custom filter query: {str(e)}")
                        values = []
            
            return values
        except Exception as e:
            self.logger.error(f"Error getting filter values: {str(e)}")
            return []

    async def _get_filter_usage(self, filter_obj: DashboardFilter) -> Dict:
        """Get usage statistics for a filter."""
        try:
            from sqlalchemy import func, text
            from datetime import datetime, timedelta
            
            # Add timeout
            try:
                self.db.execute(text("SET LOCAL statement_timeout = '10s'"))
            except:
                pass
            
            # Get widgets this filter is applied to
            applied_to = filter_obj.applied_to if isinstance(filter_obj.applied_to, list) else []
            
            # Count widgets using this filter
            widget_count = len(applied_to) if applied_to else 0
            
            # Get filter usage from dashboard searches (if DashboardSearch model exists)
            # Check if searches table exists and has filter references
            try:
                # Try to query dashboard searches for this filter
                # Note: This assumes DashboardSearch model exists with filter_id or similar
                # If not, we'll just return basic stats
                search_count = 0
                try:
                    from ..models import DashboardSearch
                    search_count = self.db.query(func.count(DashboardSearch.id)).filter(
                        DashboardSearch.user_id == filter_obj.user_id,
                        DashboardSearch.query.contains(filter_obj.name)
                    ).scalar() or 0
                except:
                    # DashboardSearch might not exist or have filter references
                    pass
            except:
                search_count = 0
            
            # Calculate usage frequency (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_usage = 0
            
            # Check if filter was updated recently (indicates usage)
            if filter_obj.updated_at and filter_obj.updated_at >= thirty_days_ago:
                recent_usage = 1
            
            return {
                "filter_id": filter_obj.id,
                "filter_name": filter_obj.name,
                "filter_type": filter_obj.filter_type,
                "widget_count": widget_count,
                "applied_to_widgets": applied_to,
                "search_count": search_count,
                "recent_usage": recent_usage,
                "created_at": filter_obj.created_at.isoformat() if filter_obj.created_at else None,
                "updated_at": filter_obj.updated_at.isoformat() if filter_obj.updated_at else None,
                "usage_frequency": "high" if recent_usage > 0 or widget_count > 5 else "low"
            }
        except Exception as e:
            self.logger.error(f"Error getting filter usage: {str(e)}")
            return {
                "filter_id": filter_obj.id if filter_obj else None,
                "error": str(e)
            }

    async def get_collaboration_metrics(
        self,
        user_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get collaboration metrics for the dashboard."""
        try:
            metrics = {
                "total_sessions": 0,
                "active_sessions": 0,
                "total_documents": 0,
                "active_documents": 0,
                "total_participants": 0,
                "active_participants": 0,
                "session_metrics": {},
                "document_metrics": {},
                "participant_metrics": {},
                "communication_metrics": {},
                "security_metrics": {},
                "compliance_metrics": {},
                "ai_metrics": {},
                "cost_metrics": {},
                "health_metrics": {}
            }

            # Get session metrics
            session_metrics = await self.collaboration_service.get_session_metrics_summary(
                user_id=user_id,
                time_range=time_range
            )
            metrics.update(session_metrics)

            # Get document metrics
            document_metrics = await self.collaboration_service.get_document_metrics_summary(
                user_id=user_id,
                time_range=time_range
            )
            metrics.update(document_metrics)

            # Get participant metrics
            participant_metrics = await self.collaboration_service.get_participant_metrics_summary(
                user_id=user_id,
                time_range=time_range
            )
            metrics.update(participant_metrics)

            # Get communication metrics
            communication_metrics = await self.collaboration_service.get_communication_metrics(
                user_id=user_id,
                time_range=time_range
            )
            metrics["communication_metrics"] = communication_metrics

            # Get security metrics
            security_metrics = await self.collaboration_service.get_security_metrics(
                user_id=user_id,
                time_range=time_range
            )
            metrics["security_metrics"] = security_metrics

            # Get compliance metrics
            compliance_metrics = await self.collaboration_service.get_compliance_metrics(
                user_id=user_id,
                time_range=time_range
            )
            metrics["compliance_metrics"] = compliance_metrics

            # Get AI metrics
            ai_metrics = await self.collaboration_service.get_ai_metrics(
                user_id=user_id,
                time_range=time_range
            )
            metrics["ai_metrics"] = ai_metrics

            # Get cost metrics
            cost_metrics = await self.collaboration_service.get_cost_metrics(
                user_id=user_id,
                time_range=time_range
            )
            metrics["cost_metrics"] = cost_metrics

            # Get health metrics
            health_metrics = await self.collaboration_service.get_health_metrics(
                user_id=user_id,
                time_range=time_range
            )
            metrics["health_metrics"] = health_metrics

            return metrics
        except Exception as e:
            logger.error(f"Error getting collaboration metrics: {str(e)}")
            raise

    async def get_collaboration_analytics(
        self,
        user_id: str,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """Get collaboration analytics for the dashboard."""
        try:
            analytics = {
                "summary": {},
                "trends": {},
                "patterns": {},
                "insights": {},
                "performance": {},
                "engagement": {},
                "recommendations": [],
                "workflow_analytics": {},
                "knowledge_metrics": {},
                "team_dynamics": {},
                "project_metrics": {},
                "resource_analytics": {},
                "skill_analytics": {},
                "learning_metrics": {},
                "productivity_analysis": {},
                "quality_metrics": {},
                "innovation_metrics": {}
            }

            # Get basic analytics summary
            analytics["summary"] = await self.collaboration_service.get_analytics_summary(
                user_id=user_id,
                time_range=time_range
            )

            # Get workflow analytics
            analytics["workflow_analytics"] = await self.collaboration_service.get_workflow_analytics(
                user_id=user_id,
                time_range=time_range
            )

            # Get knowledge metrics
            analytics["knowledge_metrics"] = await self.collaboration_service.get_knowledge_metrics(
                user_id=user_id,
                time_range=time_range
            )

            # Get team dynamics
            analytics["team_dynamics"] = await self.collaboration_service.get_team_dynamics(
                user_id=user_id,
                time_range=time_range
            )

            # Get project metrics
            analytics["project_metrics"] = await self.collaboration_service.get_project_metrics(
                user_id=user_id,
                time_range=time_range
            )

            # Get resource analytics
            analytics["resource_analytics"] = await self.collaboration_service.get_resource_analytics(
                user_id=user_id,
                time_range=time_range
            )

            # Get skill analytics
            analytics["skill_analytics"] = await self.collaboration_service.get_skill_analytics(
                user_id=user_id,
                time_range=time_range
            )

            # Get learning metrics
            analytics["learning_metrics"] = await self.collaboration_service.get_learning_metrics(
                user_id=user_id,
                time_range=time_range
            )

            # Get productivity analysis
            analytics["productivity_analysis"] = await self.collaboration_service.get_productivity_analysis(
                user_id=user_id,
                time_range=time_range
            )

            # Get quality metrics
            analytics["quality_metrics"] = await self.collaboration_service.get_quality_metrics(
                user_id=user_id,
                time_range=time_range
            )

            # Get innovation metrics
            analytics["innovation_metrics"] = await self.collaboration_service.get_innovation_metrics(
                user_id=user_id,
                time_range=time_range
            )

            return analytics
        except Exception as e:
            logger.error(f"Error getting collaboration analytics: {str(e)}")
            raise

    async def get_collaboration_widgets(
        self,
        user_id: str,
        widget_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get collaboration widgets for the dashboard."""
        try:
            widgets = await self.collaboration_service.get_dashboard_widgets(
                user_id=user_id,
                widget_type=widget_type
            )

            # Get widget data based on type
            for widget in widgets:
                if widget["widget_type"] == "active_sessions":
                    widget["data"] = await self._get_active_sessions_data(widget)
                elif widget["widget_type"] == "document_activity":
                    widget["data"] = await self._get_document_activity_data(widget)
                elif widget["widget_type"] == "participant_engagement":
                    widget["data"] = await self._get_participant_engagement_data(widget)
                elif widget["widget_type"] == "collaboration_metrics":
                    widget["data"] = await self._get_collaboration_metrics_data(widget)
                elif widget["widget_type"] == "real_time_activity":
                    widget["data"] = await self._get_real_time_activity_data(widget)
                elif widget["widget_type"] == "team_performance":
                    widget["data"] = await self._get_team_performance_data(widget)
                elif widget["widget_type"] == "resource_usage":
                    widget["data"] = await self._get_resource_usage_data(widget)
                elif widget["widget_type"] == "feature_adoption":
                    widget["data"] = await self._get_feature_adoption_data(widget)
                elif widget["widget_type"] == "session_analytics":
                    widget["data"] = await self._get_session_analytics_data(widget)
                elif widget["widget_type"] == "document_analytics":
                    widget["data"] = await self._get_document_analytics_data(widget)

                # Get widget configuration
                widget["config"] = await self.collaboration_service.get_widget_config(widget["id"])

            return widgets
        except Exception as e:
            logger.error(f"Error getting collaboration widgets: {str(e)}")
            raise

    async def _get_active_sessions_data(self, widget: Dict) -> Dict:
        """Get data for active sessions widget."""
        sessions = await self.collaboration_service.get_active_sessions(
            user_id=widget["user_id"]
        )
        return {
            "sessions": sessions,
            "metrics": {
                "total_sessions": len(sessions),
                "active_participants": sum(len(s["participants"]) for s in sessions),
                "average_duration": sum(s.get("duration", 0) for s in sessions) / len(sessions) if sessions else 0
            }
        }

    async def _get_document_activity_data(self, widget: Dict) -> Dict:
        """Get data for document activity widget."""
        documents = await self.collaboration_service.get_active_documents(
            user_id=widget["user_id"]
        )
        return {
            "documents": documents,
            "metrics": {
                "total_documents": len(documents),
                "active_editors": sum(len(d["editors"]) for d in documents),
                "total_edits": sum(d.get("edit_count", 0) for d in documents)
            }
        }

    async def _get_participant_engagement_data(self, widget: Dict) -> Dict:
        """Get data for participant engagement widget."""
        participants = await self.collaboration_service.get_participant_metrics(
            user_id=widget["user_id"]
        )
        return {
            "participants": participants,
            "metrics": {
                "total_participants": len(participants),
                "active_participants": sum(1 for p in participants if p["is_active"]),
                "average_engagement": sum(p.get("engagement_score", 0) for p in participants) / len(participants) if participants else 0
            }
        }

    async def _get_collaboration_metrics_data(self, widget: Dict) -> Dict:
        """Get data for collaboration metrics widget."""
        metrics = await self.collaboration_service.get_metrics_summary(
            user_id=widget["user_id"]
        )
        return metrics

    async def _get_real_time_activity_data(self, widget: Dict) -> Dict:
        """Get data for real-time activity widget."""
        activity = await self.collaboration_service.get_real_time_activity(
            user_id=widget["user_id"]
        )
        return activity

    async def _get_team_performance_data(self, widget: Dict) -> Dict:
        """Get data for team performance widget."""
        performance = await self.collaboration_service.get_team_performance(
            user_id=widget["user_id"]
        )
        return performance

    async def _get_resource_usage_data(self, widget: Dict) -> Dict:
        """Get data for resource usage widget."""
        usage = await self.collaboration_service.get_resource_usage(
            user_id=widget["user_id"]
        )
        return usage

    async def _get_feature_adoption_data(self, widget: Dict) -> Dict:
        """Get data for feature adoption widget."""
        adoption = await self.collaboration_service.get_feature_adoption(
            user_id=widget["user_id"]
        )
        return adoption

    async def _get_session_analytics_data(self, widget: Dict) -> Dict:
        """Get data for session analytics widget."""
        analytics = await self.collaboration_service.get_session_analytics(
            user_id=widget["user_id"]
        )
        return analytics

    async def _get_document_analytics_data(self, widget: Dict) -> Dict:
        """Get data for document analytics widget."""
        analytics = await self.collaboration_service.get_document_analytics(
            user_id=widget["user_id"]
        )
        return analytics

    async def get_collaboration_sessions(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get collaboration sessions for the dashboard."""
        try:
            sessions = await self.collaboration_service.get_user_sessions(
                user_id=user_id,
                status=status
            )

            # Get additional session data
            for session in sessions:
                session["metrics"] = await self.collaboration_service.get_session_metrics(session["id"])
                session["participants"] = await self.collaboration_service.get_session_participants(session["id"])

            return sessions
        except Exception as e:
            logger.error(f"Error getting collaboration sessions: {str(e)}")
            raise

    async def get_collaboration_documents(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get collaboration documents for the dashboard."""
        try:
            documents = await self.collaboration_service.get_user_documents(
                user_id=user_id,
                session_id=session_id,
                document_type=document_type
            )

            # Get additional document data
            for doc in documents:
                doc["history"] = await self.collaboration_service.get_document_history(doc["id"])
                doc["lock_status"] = await self.collaboration_service.get_lock_status(doc["id"])

            return documents
        except Exception as e:
            logger.error(f"Error getting collaboration documents: {str(e)}")
            raise

    async def get_collaboration_participants(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get collaboration participants for the dashboard."""
        try:
            participants = await self.collaboration_service.get_session_participants(
                session_id=session_id
            ) if session_id else await self.collaboration_service.get_user_participants(
                user_id=user_id
            )

            # Get additional participant data
            for participant in participants:
                participant["metrics"] = await self.collaboration_service.get_participant_metrics(
                    user_id=participant["user_id"],
                    session_id=participant.get("session_id")
                )

            return participants
        except Exception as e:
            logger.error(f"Error getting collaboration participants: {str(e)}")
            raise

    async def _get_communication_metrics_data(self, widget: Dict) -> Dict:
        """Get data for communication metrics widget."""
        metrics = await self.collaboration_service.get_communication_metrics(
            user_id=widget["user_id"]
        )
        return metrics

    async def _get_task_progress_data(self, widget: Dict) -> Dict:
        """Get data for task progress widget."""
        progress = await self.collaboration_service.get_task_progress(
            user_id=widget["user_id"]
        )
        return progress

    async def _get_collaboration_health_data(self, widget: Dict) -> Dict:
        """Get data for collaboration health widget."""
        health = await self.collaboration_service.get_collaboration_health(
            user_id=widget["user_id"]
        )
        return health

    async def _get_user_activity_data(self, widget: Dict) -> Dict:
        """Get data for user activity widget."""
        activity = await self.collaboration_service.get_user_activity(
            user_id=widget["user_id"]
        )
        return activity

    async def _get_content_analytics_data(self, widget: Dict) -> Dict:
        """Get data for content analytics widget."""
        analytics = await self.collaboration_service.get_content_analytics(
            user_id=widget["user_id"]
        )
        return analytics

    async def _get_integration_status_data(self, widget: Dict) -> Dict:
        """Get data for integration status widget."""
        status = await self.collaboration_service.get_integration_status(
            user_id=widget["user_id"]
        )
        return status

    async def _get_security_metrics_data(self, widget: Dict) -> Dict:
        """Get data for security metrics widget."""
        metrics = await self.collaboration_service.get_security_metrics(
            user_id=widget["user_id"]
        )
        return metrics

    async def _get_compliance_status_data(self, widget: Dict) -> Dict:
        """Get data for compliance status widget."""
        status = await self.collaboration_service.get_compliance_status(
            user_id=widget["user_id"]
        )
        return status

    async def _get_cost_analytics_data(self, widget: Dict) -> Dict:
        """Get data for cost analytics widget."""
        analytics = await self.collaboration_service.get_cost_analytics(
            user_id=widget["user_id"]
        )
        return analytics

    async def _get_ai_assistance_data(self, widget: Dict) -> Dict:
        """Get data for AI assistance widget."""
        assistance = await self.collaboration_service.get_ai_assistance(
            user_id=widget["user_id"]
        )
        return assistance

    async def _get_workflow_metrics_data(self, widget: Dict) -> Dict:
        """Get data for workflow metrics widget."""
        metrics = await self.collaboration_service.get_workflow_metrics(
            user_id=widget["user_id"]
        )
        return metrics

    async def _get_knowledge_sharing_data(self, widget: Dict) -> Dict:
        """Get data for knowledge sharing widget."""
        data = await self.collaboration_service.get_knowledge_sharing_metrics(
            user_id=widget["user_id"]
        )
        return data

    async def _get_team_insights_data(self, widget: Dict) -> Dict:
        """Get data for team insights widget."""
        insights = await self.collaboration_service.get_team_insights(
            user_id=widget["user_id"]
        )
        return insights

    async def _get_project_timeline_data(self, widget: Dict) -> Dict:
        """Get data for project timeline widget."""
        timeline = await self.collaboration_service.get_project_timeline(
            user_id=widget["user_id"]
        )
        return timeline

    async def _get_resource_allocation_data(self, widget: Dict) -> Dict:
        """Get data for resource allocation widget."""
        allocation = await self.collaboration_service.get_resource_allocation(
            user_id=widget["user_id"]
        )
        return allocation

    async def _get_skill_matrix_data(self, widget: Dict) -> Dict:
        """Get data for skill matrix widget."""
        matrix = await self.collaboration_service.get_skill_matrix(
            user_id=widget["user_id"]
        )
        return matrix

    async def _get_learning_analytics_data(self, widget: Dict) -> Dict:
        """Get data for learning analytics widget."""
        analytics = await self.collaboration_service.get_learning_analytics(
            user_id=widget["user_id"]
        )
        return analytics

    async def _get_productivity_metrics_data(self, widget: Dict) -> Dict:
        """Get data for productivity metrics widget."""
        metrics = await self.collaboration_service.get_productivity_metrics(
            user_id=widget["user_id"]
        )
        return metrics

    async def _get_quality_metrics_data(self, widget: Dict) -> Dict:
        """Get data for quality metrics widget."""
        metrics = await self.collaboration_service.get_quality_metrics(
            user_id=widget["user_id"]
        )
        return metrics

    async def _get_innovation_tracking_data(self, widget: Dict) -> Dict:
        """Get data for innovation tracking widget."""
        tracking = await self.collaboration_service.get_innovation_tracking(
            user_id=widget["user_id"]
        )
        return tracking

    async def _apply_advanced_analytics(
        self,
        data: Dict[str, Any],
        analytics_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply advanced analytics to widget data."""
        try:
            result = {"raw_data": data, "analytics": {}}

            # Apply statistical methods
            if "statistical_methods" in analytics_config:
                result["analytics"]["statistics"] = await self._apply_statistical_methods(
                    data,
                    analytics_config["statistical_methods"]
                )

            # Apply metric transformations
            if "metric_transformations" in analytics_config:
                result["analytics"]["transformations"] = await self._apply_metric_transformations(
                    data,
                    analytics_config["metric_transformations"]
                )

            # Generate insights
            if "insight_generation" in analytics_config:
                result["analytics"]["insights"] = await self._generate_insights(
                    data,
                    analytics_config["insight_generation"]
                )

            return result
        except Exception as e:
            logger.error(f"Error applying advanced analytics: {str(e)}")
            raise

    async def _apply_statistical_methods(
        self,
        data: Dict[str, Any],
        methods_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply statistical methods to data."""
        results = {}

        # Regression analysis
        if "regression" in methods_config:
            results["regression"] = await self.analytics_service.perform_regression(
                data=data,
                config=methods_config["regression"]
            )

        # Clustering analysis
        if "clustering" in methods_config:
            results["clustering"] = await self.analytics_service.perform_clustering(
                data=data,
                config=methods_config["clustering"]
            )

        # Time series analysis
        if "time_series" in methods_config:
            results["time_series"] = await self.analytics_service.analyze_time_series(
                data=data,
                config=methods_config["time_series"]
            )

        # Anomaly detection
        if "anomaly_detection" in methods_config:
            results["anomalies"] = await self.analytics_service.detect_anomalies(
                data=data,
                config=methods_config["anomaly_detection"]
            )

        return results

    async def _apply_metric_transformations(
        self,
        data: Dict[str, Any],
        transform_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply metric transformations."""
        transformed_data = data.copy()

        # Normalization
        if "normalization" in transform_config:
            transformed_data = await self.analytics_service.normalize_metrics(
                data=transformed_data,
                method=transform_config["normalization"]
            )

        # Aggregation
        if "aggregation" in transform_config:
            transformed_data = await self.analytics_service.aggregate_metrics(
                data=transformed_data,
                method=transform_config["aggregation"]
            )

        # Smoothing
        if "smoothing" in transform_config:
            transformed_data = await self.analytics_service.smooth_metrics(
                data=transformed_data,
                method=transform_config["smoothing"]
            )

        return transformed_data

    async def _generate_insights(
        self,
        data: Dict[str, Any],
        insight_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from data."""
        insights = {}

        # Trend analysis
        if "trend_analysis" in insight_config:
            insights["trends"] = await self.analytics_service.analyze_trends(
                data=data,
                config=insight_config["trend_analysis"]
            )

        # Pattern recognition
        if "pattern_recognition" in insight_config:
            insights["patterns"] = await self.analytics_service.recognize_patterns(
                data=data,
                config=insight_config["pattern_recognition"]
            )

        # Correlation analysis
        if "correlation_analysis" in insight_config:
            insights["correlations"] = await self.analytics_service.analyze_correlations(
                data=data,
                config=insight_config["correlation_analysis"]
            )

        return insights

    async def _apply_real_time_analytics(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply real-time analytics to streaming data."""
        try:
            # Initialize optimization settings
            await self._initialize_optimization(config.get("optimization", {}))

            results = {"raw_data": data, "analytics": {}}

            # Process streaming metrics with advanced windowing
            if "streaming_metrics" in config:
                results["analytics"]["streaming"] = await self._process_streaming_metrics(
                    data,
                    config["streaming_metrics"]
                )

            # Ensemble-based anomaly detection
            if "anomaly_detection" in config:
                results["analytics"]["anomalies"] = await self._detect_anomalies_ensemble(
                    data,
                    config["anomaly_detection"]
                )

            # Advanced pattern matching
            if "pattern_matching" in config:
                results["analytics"]["patterns"] = await self._match_advanced_patterns(
                    data,
                    config["pattern_matching"]
                )

            # Multi-scale trend detection
            if "trend_detection" in config:
                results["analytics"]["trends"] = await self._detect_advanced_trends(
                    data,
                    config["trend_detection"]
                )

            # Multi-dimensional change point detection
            if "change_point_detection" in config:
                results["analytics"]["change_points"] = await self._detect_advanced_change_points(
                    data,
                    config["change_point_detection"]
                )

            # Evolutionary clustering
            if "real_time_clustering" in config:
                results["analytics"]["clusters"] = await self._perform_advanced_clustering(
                    data,
                    config["real_time_clustering"]
                )

            # Online predictive analytics
            if "predictive_analytics" in config:
                results["analytics"]["predictions"] = await self._perform_online_prediction(
                    data,
                    config["predictive_analytics"]
                )

            return results
        except Exception as e:
            logger.error(f"Error applying real-time analytics: {str(e)}")
            raise

    async def _initialize_optimization(self, config: Dict[str, Any]):
        """Initialize optimization settings."""
        try:
            # Configure compute strategy
            if "compute_strategy" in config:
                await self.optimization_service.configure_compute(
                    distributed=config["compute_strategy"].get("distributed_processing", False),
                    gpu_acceleration=config["compute_strategy"].get("gpu_acceleration", "auto"),
                    batch_config=config["compute_strategy"].get("batch_processing", {})
                )

            # Configure memory management
            if "memory_management" in config:
                await self.optimization_service.configure_memory(
                    cache_strategy=config["memory_management"].get("cache_strategy", "lru"),
                    cache_size=config["memory_management"].get("cache_size", "auto"),
                    pressure_handling=config["memory_management"].get("memory_pressure_handling", True)
                )

            # Configure data flow
            if "data_flow" in config:
                await self.optimization_service.configure_data_flow(
                    backpressure=config["data_flow"].get("backpressure_handling", True),
                    throttling=config["data_flow"].get("throttling", {})
                )

            # Configure resource allocation
            if "resource_allocation" in config:
                await self.optimization_service.configure_resources(
                    auto_scaling=config["resource_allocation"].get("auto_scaling", True),
                    priority_based=config["resource_allocation"].get("priority_based", True),
                    limits=config["resource_allocation"].get("resource_limits", {})
                )

        except Exception as e:
            logger.error(f"Error initializing optimization: {str(e)}")
            raise

    async def _detect_anomalies_ensemble(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect anomalies using ensemble methods."""
        try:
            ensemble_config = config.get("ensemble_methods", {})
            results = []

            for algorithm, weight in zip(
                ensemble_config.get("algorithms", []),
                ensemble_config.get("weights", [])
            ):
                detector = await self.analytics_service.get_anomaly_detector(algorithm)
                result = await detector.detect(data)
                results.append({"result": result, "weight": weight})

            return await self.analytics_service.combine_ensemble_results(
                results,
                voting_scheme=ensemble_config.get("voting_scheme", "majority")
            )
        except Exception as e:
            logger.error(f"Error in ensemble anomaly detection: {str(e)}")
            raise

    async def _match_advanced_patterns(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match patterns with advanced features."""
        try:
            advanced_config = config.get("advanced_patterns", {})
            patterns = await self.analytics_service.match_patterns(
                data=data,
                method=config["method"],
                min_support=config["min_support"],
                max_gap=config["max_gap"],
                temporal_constraints=advanced_config.get("temporal_constraints", False),
                hierarchical=advanced_config.get("hierarchical_patterns", False),
                evolution_tracking=advanced_config.get("pattern_evolution", False)
            )
            return patterns
        except Exception as e:
            logger.error(f"Error in advanced pattern matching: {str(e)}")
            raise

    async def _perform_online_prediction(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform online predictive analytics."""
        try:
            predictions = {}
            for model_name, model_config in config.get("models", {}).items():
                predictor = await self.analytics_service.get_online_predictor(
                    model_type=model_name,
                    weight=model_config["weight"],
                    adaptive=model_config.get("adaptive", False),
                    uncertainty=model_config.get("uncertainty", False),
                    online_training=model_config.get("online_training", False)
                )
                predictions[model_name] = await predictor.predict(
                    data,
                    horizon=config["horizon"]
                )

            return await self.analytics_service.combine_predictions(
                predictions,
                method="weighted_average"
            )
        except Exception as e:
            logger.error(f"Error in online prediction: {str(e)}")
            raise

    def _get_specialized_chart_config(self, chart_type: str) -> Dict[str, Any]:
        """Get configuration for specialized chart types."""
        configs = {
            "three_dimensional": {
                "rotation": True,
                "perspective": 45,
                "depth": 100,
                "wireframe": False
            },
            "temporal_density": {
                "smoothing": 0.2,
                "stacked": True,
                "normalized": False
            },
            "relationship_flow": {
                "padAngle": 0.05,
                "cornerRadius": 5,
                "matrix": "symmetric"
            },
            "hierarchical_size": {
                "tiling": "squarified",
                "padding": 1,
                "sort": "descending"
            },
            "multivariate_comparison": {
                "spokes": "auto",
                "fill": 0.7,
                "symmetry": True
            },
            "temporal_distribution": {
                "timeFormat": "auto",
                "overlap": 0.3,
                "animation": True
            },
            "relationship_strength": {
                "cellSize": "auto",
                "colorScale": "diverging",
                "showValues": True
            },
            "network_dynamics": {
                "layout": "force_directed",
                "physics": True,
                "clustering": True,
                "interaction": {
                    "hover": True,
                    "select": True,
                    "drag": True
                }
            },
            "categorical_flow": {
                "orientation": "horizontal",
                "bundling": True,
                "highlighting": True,
                "labels": {
                    "position": "auto",
                    "rotation": "auto"
                }
            },
            "time_series_density": {
                "bands": 4,
                "interpolation": "basis",
                "mirror": True,
                "normalize": True
            },
            "distribution_comparison": {
                "kernel": "gaussian",
                "bandwidth": "scott",
                "show_box": True,
                "show_points": "outliers"
            }
        }
        return configs.get(chart_type, {})

    async def _apply_specialized_algorithms(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply specialized algorithms."""
        try:
            results = {}

            # Bioinformatics processing
            if "bioinformatics" in config:
                results["bio"] = await self._process_bioinformatics(
                    data,
                    config["bioinformatics"]
                )

            # Quantum algorithms
            if "quantum_algorithms" in config:
                results["quantum"] = await self._apply_quantum_algorithms(
                    data,
                    config["quantum_algorithms"]
                )

            # Advanced security
            if "advanced_security" in config:
                results["security"] = await self._apply_security_features(
                    data,
                    config["advanced_security"]
                )

            # Cognitive computing
            if "cognitive_computing" in config:
                results["cognitive"] = await self._apply_cognitive_computing(
                    data,
                    config["cognitive_computing"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in specialized algorithm application: {str(e)}")
            raise

    async def _process_bioinformatics(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process bioinformatics data."""
        try:
            results = {}

            # Sequence analysis
            if "sequence_analysis" in config:
                results["sequence"] = await self.bio_service.analyze_sequence(
                    data=data,
                    algorithm=config["sequence_analysis"]["algorithm"],
                    features=config["sequence_analysis"]["features"]
                )

            # Molecular dynamics
            if "molecular_dynamics" in config:
                results["dynamics"] = await self.bio_service.simulate_molecular_dynamics(
                    data=data,
                    simulation=config["molecular_dynamics"]["simulation"],
                    force_field=config["molecular_dynamics"]["force_field"]
                )

            # Genomic processing
            if "genomic_processing" in config:
                results["genomics"] = await self.bio_service.process_genomics(
                    data=data,
                    variant_calling=config["genomic_processing"]["variant_calling"],
                    methylation=config["genomic_processing"]["methylation_analysis"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in bioinformatics processing: {str(e)}")
            raise

    async def _apply_quantum_algorithms(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply quantum algorithms."""
        try:
            results = {}

            # Quantum ML
            if "quantum_ml" in config:
                results["qml"] = await self.quantum_service.apply_quantum_ml(
                    data=data,
                    circuits=config["quantum_ml"]["variational_circuits"],
                    kernels=config["quantum_ml"]["quantum_kernels"]
                )

            # Quantum optimization
            if "quantum_optimization" in config:
                results["optimization"] = await self.quantum_service.optimize_quantum(
                    data=data,
                    qaoa=config["quantum_optimization"]["qaoa"],
                    annealing=config["quantum_optimization"]["quantum_annealing"]
                )

            # Quantum simulation
            if "quantum_simulation" in config:
                results["simulation"] = await self.quantum_service.simulate_quantum(
                    data=data,
                    hamiltonian=config["quantum_simulation"]["hamiltonian_simulation"],
                    chemistry=config["quantum_simulation"]["quantum_chemistry"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in quantum algorithm application: {str(e)}")
            raise

    async def _apply_security_features(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply advanced security features."""
        try:
            results = {}

            # Quantum cryptography
            if "quantum_cryptography" in config:
                results["crypto"] = await self.security_service.apply_quantum_crypto(
                    data=data,
                    key_distribution=config["quantum_cryptography"]["key_distribution"],
                    post_quantum=config["quantum_cryptography"]["post_quantum"]
                )

            # Behavioral analysis
            if "behavioral_analysis" in config:
                results["behavior"] = await self.security_service.analyze_behavior(
                    data=data,
                    authentication=config["behavioral_analysis"]["continuous_authentication"],
                    threat_hunting=config["behavioral_analysis"]["threat_hunting"]
                )

            # Privacy preservation
            if "privacy_preservation" in config:
                results["privacy"] = await self.security_service.preserve_privacy(
                    data=data,
                    differential_privacy=config["privacy_preservation"]["differential_privacy"],
                    secure_computation=config["privacy_preservation"]["secure_computation"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in security feature application: {str(e)}")
            raise

    async def _apply_cognitive_computing(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply cognitive computing features."""
        try:
            results = {}

            # Attention mechanisms
            if "attention_mechanisms" in config:
                results["attention"] = await self.cognitive_service.apply_attention(
                    data=data,
                    multimodal=config["attention_mechanisms"]["multimodal_attention"],
                    cognitive_load=config["attention_mechanisms"]["cognitive_load"]
                )

            # Knowledge representation
            if "knowledge_representation" in config:
                results["knowledge"] = await self.cognitive_service.represent_knowledge(
                    data=data,
                    semantic=config["knowledge_representation"]["semantic_graphs"],
                    neural_symbolic=config["knowledge_representation"]["neural_symbolic"]
                )

            # Cognitive architecture
            if "cognitive_architecture" in config:
                results["architecture"] = await self.cognitive_service.configure_architecture(
                    data=data,
                    memory=config["cognitive_architecture"]["memory_systems"],
                    learning=config["cognitive_architecture"]["learning_mechanisms"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in cognitive computing application: {str(e)}")
            raise

    async def _optimize_system_resources(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Optimize system resources."""
        try:
            # Quantum resource management
            if "quantum_resource_management" in config:
                await self.optimization_service.manage_quantum_resources(
                    scheduling=config["quantum_resource_management"]["scheduling"],
                    hardware=config["quantum_resource_management"]["hardware_integration"]
                )

            # Cognitive optimization
            if "cognitive_optimization" in config:
                await self.optimization_service.optimize_cognitive(
                    workload=config["cognitive_optimization"]["workload_adaptation"],
                    interface=config["cognitive_optimization"]["interface_optimization"]
                )

            # Security optimization
            if "security_optimization" in config:
                await self.optimization_service.optimize_security(
                    quantum=config["security_optimization"]["quantum_resilience"],
                    zero_trust=config["security_optimization"]["zero_trust"]
                )

        except Exception as e:
            logger.error(f"Error in system resource optimization: {str(e)}")
            raise

    async def _apply_domain_specific_algorithms(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply domain-specific algorithms."""
        try:
            results = {}

            # Natural Language Processing
            if "natural_language" in config:
                results["nlp"] = await self._process_natural_language(
                    data,
                    config["natural_language"]
                )

            # Computer Vision
            if "computer_vision" in config:
                results["vision"] = await self._process_computer_vision(
                    data,
                    config["computer_vision"]
                )

            # Signal Processing
            if "signal_processing" in config:
                results["signal"] = await self._process_signals(
                    data,
                    config["signal_processing"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in domain-specific processing: {str(e)}")
            raise

    async def _process_natural_language(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process natural language data."""
        try:
            results = {}

            # Semantic Analysis
            if "semantic_analysis" in config:
                results["semantics"] = await self.nlp_service.analyze_semantics(
                    data=data,
                    model=config["semantic_analysis"]["model"],
                    fine_tuning=config["semantic_analysis"]["fine_tuning"]
                )

            # Topic Modeling
            if "topic_modeling" in config:
                results["topics"] = await self.nlp_service.model_topics(
                    data=data,
                    method=config["topic_modeling"]["method"],
                    num_topics=config["topic_modeling"]["num_topics"]
                )

            # Sentiment Analysis
            if "sentiment_flow" in config:
                results["sentiment"] = await self.nlp_service.analyze_sentiment_flow(
                    data=data,
                    granularity=config["sentiment_flow"]["granularity"],
                    aspect_based=config["sentiment_flow"]["aspect_based"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in NLP processing: {str(e)}")
            raise

    async def _process_computer_vision(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process computer vision data."""
        try:
            results = {}

            # Object Detection
            if "object_detection" in config:
                results["objects"] = await self.vision_service.detect_objects(
                    data=data,
                    model=config["object_detection"]["model"],
                    confidence=config["object_detection"]["confidence"]
                )

            # Scene Understanding
            if "scene_understanding" in config:
                results["scene"] = await self.vision_service.understand_scene(
                    data=data,
                    segmentation=config["scene_understanding"]["segmentation"],
                    relationships=config["scene_understanding"]["relationship_inference"]
                )

            # Activity Recognition
            if "activity_recognition" in config:
                results["activity"] = await self.vision_service.recognize_activity(
                    data=data,
                    temporal_model=config["activity_recognition"]["temporal_modeling"],
                    multi_stream=config["activity_recognition"]["multi_stream"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in computer vision processing: {str(e)}")
            raise

    async def _process_signals(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process signal data."""
        try:
            results = {}

            # Adaptive Filtering
            if "adaptive_filtering" in config:
                results["filtered"] = await self.signal_service.apply_adaptive_filter(
                    data=data,
                    algorithm=config["adaptive_filtering"]["algorithm"],
                    state_estimation=config["adaptive_filtering"]["state_estimation"]
                )

            # Spectral Analysis
            if "spectral_analysis" in config:
                results["spectral"] = await self.signal_service.analyze_spectrum(
                    data=data,
                    method=config["spectral_analysis"]["method"],
                    resolution=config["spectral_analysis"]["resolution"]
                )

            # Change Detection
            if "change_detection" in config:
                results["changes"] = await self.signal_service.detect_changes(
                    data=data,
                    algorithm=config["change_detection"]["algorithm"],
                    multi_variate=config["change_detection"]["multi_variate"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in signal processing: {str(e)}")
            raise

    async def _apply_optimization_strategies(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Apply advanced optimization strategies."""
        try:
            # Quantum Computing
            if "quantum_computing" in config and config["quantum_computing"]["enabled"]:
                await self.optimization_service.configure_quantum_computing(
                    algorithms=config["quantum_computing"]["algorithms"],
                    resource_management=config["quantum_computing"]["resource_management"]
                )

            # Edge Computing
            if "edge_computing" in config:
                await self.optimization_service.configure_edge_computing(
                    deployment=config["edge_computing"]["deployment"],
                    processing=config["edge_computing"]["processing"],
                    synchronization=config["edge_computing"]["synchronization"]
                )

            # Federated Learning
            if "federated_learning" in config:
                await self.optimization_service.configure_federated_learning(
                    training=config["federated_learning"]["training"],
                    model_management=config["federated_learning"]["model_management"],
                    security=config["federated_learning"]["security"]
                )

        except Exception as e:
            logger.error(f"Error applying optimization strategies: {str(e)}")
            raise

    async def _configure_monitoring_enhancements(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Configure enhanced monitoring capabilities."""
        try:
            # Predictive Monitoring
            if "predictive_monitoring" in config:
                await self.monitoring_service.configure_predictive_monitoring(
                    failure_prediction=config["predictive_monitoring"]["failure_prediction"],
                    capacity_planning=config["predictive_monitoring"]["capacity_planning"],
                    anomaly_forecasting=config["predictive_monitoring"]["anomaly_forecasting"]
                )

            # Distributed Tracing
            if "distributed_tracing" in config:
                await self.monitoring_service.configure_distributed_tracing(
                    trace_sampling=config["distributed_tracing"]["trace_sampling"],
                    dependency_analysis=config["distributed_tracing"]["dependency_analysis"],
                    performance_profiling=config["distributed_tracing"]["performance_profiling"]
                )

            # Security Monitoring
            if "security_monitoring" in config:
                await self.monitoring_service.configure_security_monitoring(
                    threat_detection=config["security_monitoring"]["threat_detection"],
                    access_patterns=config["security_monitoring"]["access_patterns"],
                    compliance_audit=config["security_monitoring"]["compliance_audit"]
                )

        except Exception as e:
            logger.error(f"Error configuring monitoring enhancements: {str(e)}")
            raise

    async def _apply_advanced_quantum_algorithms(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply advanced quantum algorithms."""
        try:
            results = {}

            # Quantum Neural Networks
            if "quantum_neural_networks" in config:
                results["qnn"] = await self.quantum_service.apply_quantum_neural_network(
                    data=data,
                    architecture=config["quantum_neural_networks"]["architecture"],
                    backprop=config["quantum_neural_networks"]["quantum_backprop"],
                    regularization=config["quantum_neural_networks"]["quantum_regularization"]
                )

            # Quantum Reinforcement Learning
            if "quantum_reinforcement" in config:
                results["qrl"] = await self.quantum_service.apply_quantum_reinforcement(
                    data=data,
                    policy=config["quantum_reinforcement"]["policy_optimization"],
                    exploration=config["quantum_reinforcement"]["quantum_exploration"]
                )

            # Quantum Generative Models
            if "quantum_generative" in config:
                results["qgen"] = await self.quantum_service.apply_quantum_generative(
                    data=data,
                    gan=config["quantum_generative"]["quantum_gan"],
                    autoencoder=config["quantum_generative"]["quantum_autoencoder"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in advanced quantum algorithm application: {str(e)}")
            raise

    async def _apply_cognitive_enhancements(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply cognitive enhancements."""
        try:
            results = {}

            # Neural Architectures
            if "neural_architectures" in config:
                results["architectures"] = await self.cognitive_service.enhance_neural_architectures(
                    data=data,
                    cognitive=config["neural_architectures"]["quantum_cognitive"],
                    learning=config["neural_architectures"]["learning_optimization"]
                )

            # Cognitive Processing
            if "cognitive_processing" in config:
                results["processing"] = await self.cognitive_service.enhance_cognitive_processing(
                    data=data,
                    reasoning=config["cognitive_processing"]["quantum_reasoning"],
                    knowledge=config["cognitive_processing"]["knowledge_integration"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in cognitive enhancement application: {str(e)}")
            raise

    async def _apply_security_protocols(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply advanced security protocols."""
        try:
            results = {}

            # Quantum Cryptography
            if "quantum_cryptography" in config:
                results["crypto"] = await self.security_service.apply_quantum_cryptography(
                    data=data,
                    key_management=config["quantum_cryptography"]["key_management"],
                    authentication=config["quantum_cryptography"]["authentication"]
                )

            # Quantum Security
            if "quantum_security" in config:
                results["security"] = await self.security_service.apply_quantum_security(
                    data=data,
                    threat_detection=config["quantum_security"]["threat_detection"],
                    privacy=config["quantum_security"]["privacy_enhancement"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in security protocol application: {str(e)}")
            raise

    async def _optimize_quantum_resources(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Optimize quantum computing resources."""
        try:
            # Quantum Orchestration
            if "quantum_orchestration" in config:
                await self.optimization_service.orchestrate_quantum_resources(
                    allocation=config["quantum_orchestration"]["resource_allocation"],
                    error_mgmt=config["quantum_orchestration"]["error_management"]
                )

            # Performance Optimization
            if "performance_optimization" in config:
                await self.optimization_service.optimize_quantum_performance(
                    compilation=config["performance_optimization"]["quantum_compilation"],
                    execution=config["performance_optimization"]["execution_optimization"]
                )

        except Exception as e:
            logger.error(f"Error in quantum resource optimization: {str(e)}")
            raise

    async def _manage_quantum_memory(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Manage quantum memory resources."""
        try:
            if "memory_management" in config:
                await self.resource_service.manage_quantum_memory(
                    allocation=config["memory_management"]["allocation"],
                    deallocation=config["memory_management"]["deallocation"],
                    caching=config["memory_management"]["caching"]
                )
        except Exception as e:
            logger.error(f"Error in quantum memory management: {str(e)}")
            raise

    async def _coordinate_quantum_execution(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Coordinate quantum execution across resources."""
        try:
            if "execution_optimization" in config:
                await self.coordination_service.optimize_quantum_execution(
                    parallelization=config["execution_optimization"]["parallelization"],
                    memory=config["execution_optimization"]["memory_management"]
                )
        except Exception as e:
            logger.error(f"Error in quantum execution coordination: {str(e)}")
            raise

    async def _monitor_quantum_performance(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Monitor quantum system performance."""
        try:
            if "performance_optimization" in config:
                await self.monitoring_service.monitor_quantum_performance(
                    compilation=config["performance_optimization"]["quantum_compilation"],
                    execution=config["performance_optimization"]["execution_optimization"]
                )
        except Exception as e:
            logger.error(f"Error in quantum performance monitoring: {str(e)}")
            raise

    async def _apply_specialized_quantum_circuits(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply specialized quantum circuits."""
        try:
            results = {}

            # Quantum Error Correction
            if "quantum_error_correction" in config:
                results["error_correction"] = await self.quantum_service.apply_error_correction(
                    data=data,
                    stabilizer=config["quantum_error_correction"]["stabilizer_codes"],
                    distillation=config["quantum_error_correction"]["magic_state_distillation"],
                    protection=config["quantum_error_correction"]["topological_protection"]
                )

            # Quantum Optimization Circuits
            if "quantum_optimization_circuits" in config:
                results["optimization"] = await self.quantum_service.apply_optimization_circuits(
                    data=data,
                    adiabatic=config["quantum_optimization_circuits"]["adiabatic_evolution"],
                    variational=config["quantum_optimization_circuits"]["variational_algorithms"],
                    qaoa=config["quantum_optimization_circuits"]["quantum_approximate_optimization"]
                )

            # Quantum Simulation Circuits
            if "quantum_simulation_circuits" in config:
                results["simulation"] = await self.quantum_service.apply_simulation_circuits(
                    data=data,
                    hamiltonian=config["quantum_simulation_circuits"]["hamiltonian_evolution"],
                    chemistry=config["quantum_simulation_circuits"]["quantum_chemistry"],
                    dynamics=config["quantum_simulation_circuits"]["quantum_dynamics"]
                )

            return results
        except Exception as e:
            logger.error(f"Error in specialized quantum circuit application: {str(e)}")
            raise

    async def _manage_quantum_classical_interface(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Manage quantum-classical interface."""
        try:
            # Hybrid Computation
            if "hybrid_computation" in config:
                await self.interface_service.configure_hybrid_computation(
                    workload=config["hybrid_computation"]["workload_distribution"],
                    data_transfer=config["hybrid_computation"]["data_transfer"],
                    integration=config["hybrid_computation"]["result_integration"]
                )

            # Quantum Control Systems
            if "quantum_control_systems" in config:
                await self.interface_service.configure_control_systems(
                    feedback=config["quantum_control_systems"]["feedback_control"],
                    calibration=config["quantum_control_systems"]["calibration"],
                    verification=config["quantum_control_systems"]["quantum_verification"]
                )

        except Exception as e:
            logger.error(f"Error in quantum-classical interface management: {str(e)}")
            raise

    async def _apply_advanced_quantum_security(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Apply advanced quantum security features."""
        try:
            # Cryptographic Protocols
            if "quantum_cryptographic_protocols" in config:
                await self.security_service.apply_quantum_protocols(
                    key_establishment=config["quantum_cryptographic_protocols"]["key_establishment"],
                    delegation=config["quantum_cryptographic_protocols"]["secure_delegation"],
                    quantum_money=config["quantum_cryptographic_protocols"]["quantum_money"]
                )

            # Security Infrastructure
            if "quantum_security_infrastructure" in config:
                await self.security_service.configure_quantum_infrastructure(
                    key_management=config["quantum_security_infrastructure"]["key_management"],
                    authentication=config["quantum_security_infrastructure"]["authentication_framework"],
                    firewall=config["quantum_security_infrastructure"]["quantum_firewall"]
                )

        except Exception as e:
            logger.error(f"Error in advanced quantum security application: {str(e)}")
            raise

    async def _optimize_quantum_execution(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Optimize quantum execution."""
        try:
            # Circuit Optimization
            if "circuit_optimization" in config:
                await self.optimization_service.optimize_quantum_circuits(
                    synthesis=config["circuit_optimization"]["synthesis"],
                    noise=config["circuit_optimization"]["noise_optimization"],
                    resources=config["circuit_optimization"]["resource_optimization"]
                )

            # Runtime Optimization
            if "runtime_optimization" in config:
                await self.optimization_service.optimize_quantum_runtime(
                    execution=config["runtime_optimization"]["execution_planning"],
                    errors=config["runtime_optimization"]["error_management"],
                    performance=config["runtime_optimization"]["performance_tuning"]
                )

        except Exception as e:
            logger.error(f"Error in quantum execution optimization: {str(e)}")
            raise

    async def _monitor_quantum_system(
        self,
        config: Dict[str, Any]
    ) -> None:
        """Monitor quantum system performance and health."""
        try:
            # Performance Monitoring
            if "performance_tuning" in config:
                await self.monitoring_service.monitor_quantum_performance(
                    parameters=config["performance_tuning"]["parameter_optimization"],
                    calibration=config["performance_tuning"]["hardware_calibration"],
                    characterization=config["performance_tuning"]["system_characterization"]
                )

            # Error Tracking
            if "error_management" in config:
                await self.monitoring_service.track_quantum_errors(
                    detection=config["error_management"]["detection"],
                    correction=config["error_management"]["correction"],
                    prevention=config["error_management"]["prevention"]
                )

        except Exception as e:
            logger.error(f"Error in quantum system monitoring: {str(e)}")
            raise

    async def _get_resource_usage_data(self, widget: Dict) -> Dict:
        """Get resource usage data for the widget."""
        try:
            org_id = widget.get('organization_id')
            if not org_id:
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for resource usage widget"
                )

            metrics = await self.resource_sharing.get_sharing_metrics(
                org_id=org_id,
                time_range=widget.get('time_range', '24h')
            )

            return {
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        except HTTPException:
            raise  # Re-raise HTTPExceptions as-is
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get resource usage data: {str(e)}"
            )

    async def _get_resource_optimization_data(self, widget: Dict) -> Dict:
        """Get resource optimization recommendations for the widget."""
        try:
            org_id = widget.get('organization_id')
            if not org_id:
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for resource optimization widget"
                )

            optimization = await self.resource_sharing.optimize_resource_allocation(
                org_id=org_id,
                resource_type=widget.get('resource_type'),
                time_range=widget.get('time_range', '24h')
            )

            return {
                'optimization': optimization,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get resource optimization data: {str(e)}"
            )

    async def _get_resource_prediction_data(self, widget: Dict) -> Dict:
        """Get resource usage predictions for the widget."""
        try:
            org_id = widget.get('organization_id')
            if not org_id:
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for resource prediction widget"
                )

            predictions = await self.resource_sharing.predict_resource_needs(
                org_id=org_id,
                resource_type=widget.get('resource_type'),
                prediction_window=widget.get('prediction_window', '7d')
            )

            return {
                'predictions': predictions,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get resource prediction data: {str(e)}"
            )

    async def _get_cross_org_patterns_data(self, widget: Dict) -> Dict:
        """Get cross-organization sharing patterns for the widget."""
        try:
            org_id = widget.get('organization_id')
            if not org_id:
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for cross-org patterns widget"
                )

            patterns = await self.resource_sharing.analyze_cross_org_patterns(
                org_id=org_id,
                time_range=widget.get('time_range', '30d')
            )

            return {
                'patterns': patterns,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get cross-org patterns data: {str(e)}"
            )

    async def _get_security_metrics_data(self, widget: Dict) -> Dict:
        """Get security metrics for the widget."""
        try:
            org_id = widget.get('organization_id')
            if not org_id:
                raise HTTPException(
                    status_code=400,
                    detail="Organization ID is required for security metrics widget"
                )

            security = await self.resource_sharing.enhance_security_measures(
                org_id=org_id,
                resource_type=widget.get('resource_type')
            )

            return {
                'security': security,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get security metrics data: {str(e)}"
            )