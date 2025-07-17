"""
Real-time Notification Service

This module provides real-time notification capabilities for the Faraday AI Dashboard,
including WebSocket support and different notification types.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import asyncio
from fastapi import WebSocket, HTTPException
from sqlalchemy.orm import Session
import json
import pytz
import openai

from ..models import (
    DashboardUser as User,
    Organization,
    Notification,
    NotificationPreference,
    NotificationChannel
)

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user's WebSocket."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a user's WebSocket."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for dead in dead_connections:
                await self.disconnect(dead, user_id)

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[str] = None):
        """Broadcast a message to all connected users."""
        dead_connections = []
        for user_id, connections in self.active_connections.items():
            if user_id != exclude:
                for connection in connections:
                    try:
                        await connection.send_json(message)
                    except:
                        dead_connections.append((connection, user_id))
        
        # Clean up dead connections
        for dead_conn, user_id in dead_connections:
            await self.disconnect(dead_conn, user_id)

class RealTimeNotificationService:
    """Service for managing real-time notifications."""

    def __init__(self, db: Session):
        self.db = db
        self.connection_manager = ConnectionManager()
        self.translation_service = get_translation_service()
        self.twilio_service = get_twilio_service()
        self.notification_types = {
            "system": self._handle_system_notification,
            "resource": self._handle_resource_notification,
            "security": self._handle_security_notification,
            "optimization": self._handle_optimization_notification,
            "collaboration": self._handle_collaboration_notification,
            "achievement": self._handle_achievement_notification
        }
        self.batch_queue = {}
        self.batch_timers = {}

    async def _should_batch_notification(
        self,
        user_id: str,
        notification_type: str,
        priority: str,
        preferences: Dict
    ) -> bool:
        """Determine if a notification should be batched based on user preferences and context."""
        if not preferences.get("batching", {}).get("batch_enabled", False):
            return False

        if priority == "urgent":
            return False

        batching_prefs = preferences.get("batching", {})
        if priority_threshold := batching_prefs.get("priority_threshold"):
            priorities = ["low", "normal", "high", "urgent"]
            if priorities.index(priority) >= priorities.index(priority_threshold):
                return False

        # Check quiet hours
        current_time = datetime.now(pytz.timezone(preferences.get("timezone", "UTC")))
        for quiet_period in batching_prefs.get("quiet_hours", []):
            start = datetime.strptime(quiet_period["start"], "%H:%M").time()
            end = datetime.strptime(quiet_period["end"], "%H:%M").time()
            if start <= current_time.time() <= end:
                return True

        return True

    async def _process_batch_queue(self, user_id: str):
        """Process batched notifications for a user."""
        if user_id not in self.batch_queue:
            return

        notifications = self.batch_queue[user_id]
        if not notifications:
            return

        # Group notifications by type and context
        grouped_notifications = self._group_notifications(notifications)
        
        # Generate summarized messages for each group
        for group in grouped_notifications:
            summary = await self._generate_group_summary(group)
            
            # Send the summarized notification
            await self.send_notification(
                user_id=user_id,
                notification_type=group["type"],
                title=summary["title"],
                message=summary["message"],
                data={
                    "group_size": len(group["notifications"]),
                    "original_notifications": group["notifications"],
                    "summary_context": group["context"]
                },
                priority=self._calculate_group_priority(group["notifications"]),
                channel="all"  # Send through all channels
            )

        # Clear the queue
        self.batch_queue[user_id] = []
        if user_id in self.batch_timers:
            self.batch_timers[user_id].cancel()
            del self.batch_timers[user_id]

    async def _generate_group_summary(self, group: Dict) -> Dict[str, str]:
        """Generate a summary for a group of notifications using AI."""
        notifications = group["notifications"]
        context = group["context"]
        
        # Use GPT to generate a natural summary
        prompt = f"Summarize these {len(notifications)} notifications:\n"
        for n in notifications:
            prompt += f"- {n['title']}: {n['message']}\n"
        prompt += f"\nContext: {json.dumps(context)}"
        
        try:
            summary = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a notification summarizer. Create concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return {
                "title": f"Summary of {len(notifications)} {group['type']} notifications",
                "message": summary.choices[0].message.content
            }
        except Exception as e:
            # Fallback to simple summary if AI fails
            return {
                "title": f"Multiple {group['type']} notifications",
                "message": f"You have {len(notifications)} new notifications about {group['type']}"
            }

    def _group_notifications(self, notifications: List[Dict]) -> List[Dict]:
        """Group notifications by type and context."""
        groups = {}
        for notification in notifications:
            key = notification["type"]
            if key not in groups:
                groups[key] = {
                    "type": key,
                    "notifications": [],
                    "context": {
                        "time_range": [notification["timestamp"], notification["timestamp"]],
                        "common_entities": set(),
                        "priority_distribution": {"low": 0, "normal": 0, "high": 0, "urgent": 0}
                    }
                }
            
            group = groups[key]
            group["notifications"].append(notification)
            group["context"]["priority_distribution"][notification["priority"]] += 1
            
            # Extract and track common entities
            entities = self._extract_entities(notification)
            if not group["context"]["common_entities"]:
                group["context"]["common_entities"] = entities
            else:
                group["context"]["common_entities"] &= entities

        return list(groups.values())

    def _extract_entities(self, notification: Dict) -> Set[str]:
        """Extract relevant entities from a notification for context grouping."""
        entities = set()
        
        # Extract entities from the notification data
        if "data" in notification:
            data = notification["data"]
            if "resource_id" in data:
                entities.add(f"resource:{data['resource_id']}")
            if "user" in data:
                entities.add(f"user:{data['user'].get('id')}")
            if "component" in data:
                entities.add(f"component:{data['component']}")

        return entities

    def _calculate_group_priority(self, notifications: List[Dict]) -> str:
        """Calculate the priority for a group of notifications."""
        priority_scores = {
            "low": 1,
            "normal": 2,
            "high": 3,
            "urgent": 4
        }
        
        max_score = max(priority_scores[n["priority"]] for n in notifications)
        count_high_priority = sum(1 for n in notifications if priority_scores[n["priority"]] >= 3)
        
        if max_score == 4 or count_high_priority >= 3:
            return "urgent"
        elif max_score == 3 or count_high_priority >= 2:
            return "high"
        elif max_score == 2:
            return "normal"
        else:
            return "low"

    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        channel: str = "all",
        target_language: Optional[str] = None,
        source_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Send a notification to a user.
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional notification data
            priority: Notification priority (low, normal, high, urgent)
            channel: Notification channel (websocket, email, all)
            target_language: Target language for translation
            source_language: Source language for translation
        """
        try:
            # Get user preferences including batching preferences
            preferences = await self._get_user_preferences(user_id)
            
            # Check if notification should be batched
            if await self._should_batch_notification(user_id, notification_type, priority, preferences):
                if user_id not in self.batch_queue:
                    self.batch_queue[user_id] = []
                
                self.batch_queue[user_id].append({
                    "type": notification_type,
                    "title": title,
                    "message": message,
                    "data": data,
                    "priority": priority,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Set or reset batch timer
                if user_id in self.batch_timers:
                    self.batch_timers[user_id].cancel()
                
                batch_interval = preferences.get("batching", {}).get("batch_interval", 30)
                timer = asyncio.create_task(
                    self._delayed_batch_processing(user_id, batch_interval)
                )
                self.batch_timers[user_id] = timer
                
                return {
                    "status": "batched",
                    "batch_size": len(self.batch_queue[user_id]),
                    "estimated_delivery": (
                        datetime.utcnow() + timedelta(minutes=batch_interval)
                    ).isoformat()
                }

            # Validate notification type
            if notification_type not in self.notification_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid notification type: {notification_type}"
                )

            # Get user preferences
            if not preferences.get(notification_type, True):
                return {"status": "skipped", "reason": "user_preference"}

            # Translate message if needed
            translated_message = message
            if target_language and target_language != source_language:
                translation_result = await self.translation_service.translate_text(
                    text=message,
                    target_language=target_language,
                    source_language=source_language
                )
                if translation_result["status"] == "success":
                    translated_message = translation_result["translated_text"]

            # Create notification record
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=translated_message,
                data=data or {},
                priority=priority,
                status="pending",
                created_at=datetime.utcnow()
            )
            self.db.add(notification)
            await self.db.commit()

            # Handle notification based on type
            handler = self.notification_types[notification_type]
            notification_data = await handler(notification)

            # Send through appropriate channels
            delivery_results = []
            
            if channel in ["websocket", "all"]:
                await self.connection_manager.send_personal_message(
                    message={
                        "type": "notification",
                        "notification_type": notification_type,
                        "title": title,
                        "message": translated_message,
                        "data": notification_data,
                        "priority": priority,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    user_id=user_id
                )
                delivery_results.append({"channel": "websocket", "status": "delivered"})

            if channel in ["sms", "all"]:
                # Get user's phone number from preferences or data
                phone_number = preferences.get("phone_number") or data.get("phone_number")
                if phone_number:
                    sms_result = await self.twilio_service.send_sms(
                        to_number=phone_number,
                        message=translated_message
                    )
                    delivery_results.append({
                        "channel": "sms",
                        "status": sms_result.get("status", "error"),
                        "details": sms_result
                    })

            # Update notification status
            notification.status = "delivered"
            notification.delivered_at = datetime.utcnow()
            await self.db.commit()

            return {
                "status": "success",
                "notification_id": notification.id,
                "delivered_at": notification.delivered_at.isoformat(),
                "delivery_results": delivery_results
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error sending notification: {str(e)}"
            )

    async def broadcast_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        priority: str = "normal",
        exclude_user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Broadcast a notification to all users.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional notification data
            priority: Notification priority
            exclude_user: User ID to exclude from broadcast
        """
        try:
            # Validate notification type
            if notification_type not in self.notification_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid notification type: {notification_type}"
                )

            # Create notification record
            notification = Notification(
                type=notification_type,
                title=title,
                message=message,
                data=data or {},
                priority=priority,
                status="pending",
                created_at=datetime.utcnow(),
                is_broadcast=True
            )
            self.db.add(notification)
            await self.db.commit()

            # Handle notification based on type
            handler = self.notification_types[notification_type]
            notification_data = await handler(notification)

            # Broadcast to all connected users
            await self.connection_manager.broadcast(
                message={
                    "type": "notification",
                    "notification_type": notification_type,
                    "title": title,
                    "message": message,
                    "data": notification_data,
                    "priority": priority,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude=exclude_user
            )

            # Update notification status
            notification.status = "delivered"
            notification.delivered_at = datetime.utcnow()
            await self.db.commit()

            return {
                "status": "success",
                "notification_id": notification.id,
                "delivered_at": notification.delivered_at.isoformat()
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error broadcasting notification: {str(e)}"
            )

    async def get_user_notifications(
        self,
        user_id: str,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            notification_type: Optional notification type filter
            status: Optional status filter
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
        """
        try:
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id
            )

            if notification_type:
                query = query.filter(Notification.type == notification_type)
            if status:
                query = query.filter(Notification.status == status)

            query = query.order_by(Notification.created_at.desc())
            notifications = query.offset(offset).limit(limit).all()

            return [
                {
                    "id": n.id,
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "data": n.data,
                    "priority": n.priority,
                    "status": n.status,
                    "created_at": n.created_at.isoformat(),
                    "delivered_at": n.delivered_at.isoformat() if n.delivered_at else None
                }
                for n in notifications
            ]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting notifications: {str(e)}"
            )

    async def mark_notification_read(
        self,
        user_id: str,
        notification_id: str
    ) -> Dict[str, Any]:
        """Mark a notification as read."""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()

            if not notification:
                raise HTTPException(
                    status_code=404,
                    detail="Notification not found"
                )

            notification.status = "read"
            notification.read_at = datetime.utcnow()
            await self.db.commit()

            return {
                "status": "success",
                "notification_id": notification_id,
                "read_at": notification.read_at.isoformat()
            }

        except HTTPException as he:
            raise he
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error marking notification as read: {str(e)}"
            )

    async def update_notification_preferences(
        self,
        user_id: str,
        preferences: Dict[str, bool]
    ) -> Dict[str, Any]:
        """Update notification preferences for a user."""
        try:
            user_prefs = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).first()

            if not user_prefs:
                user_prefs = NotificationPreference(user_id=user_id)
                self.db.add(user_prefs)

            user_prefs.preferences = preferences
            user_prefs.updated_at = datetime.utcnow()
            await self.db.commit()

            return {
                "status": "success",
                "user_id": user_id,
                "preferences": preferences
            }

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating notification preferences: {str(e)}"
            )

    async def _get_user_preferences(self, user_id: str) -> Dict[str, bool]:
        """Get notification preferences for a user."""
        try:
            prefs = self.db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).first()

            return prefs.preferences if prefs else {}

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting notification preferences: {str(e)}"
            )

    async def _handle_system_notification(self, notification: Notification) -> Dict[str, Any]:
        """Handle system notification."""
        return {
            "system_info": {
                "component": notification.data.get("component"),
                "action": notification.data.get("action"),
                "details": notification.data.get("details")
            }
        }

    async def _handle_resource_notification(self, notification: Notification) -> Dict[str, Any]:
        """Handle resource notification."""
        return {
            "resource_info": {
                "resource_id": notification.data.get("resource_id"),
                "resource_type": notification.data.get("resource_type"),
                "action": notification.data.get("action"),
                "metrics": notification.data.get("metrics")
            }
        }

    async def _handle_security_notification(self, notification: Notification) -> Dict[str, Any]:
        """Handle security notification."""
        return {
            "security_info": {
                "alert_type": notification.data.get("alert_type"),
                "severity": notification.data.get("severity"),
                "details": notification.data.get("details"),
                "recommendations": notification.data.get("recommendations")
            }
        }

    async def _handle_optimization_notification(self, notification: Notification) -> Dict[str, Any]:
        """Handle optimization notification."""
        return {
            "optimization_info": {
                "metric": notification.data.get("metric"),
                "current_value": notification.data.get("current_value"),
                "threshold": notification.data.get("threshold"),
                "recommendations": notification.data.get("recommendations")
            }
        }

    async def _handle_collaboration_notification(self, notification: Notification) -> Dict[str, Any]:
        """Handle collaboration notification."""
        return {
            "collaboration_info": {
                "action": notification.data.get("action"),
                "user": notification.data.get("user"),
                "resource": notification.data.get("resource"),
                "details": notification.data.get("details")
            }
        }

    async def _handle_achievement_notification(self, notification: Notification) -> Dict[str, Any]:
        """Handle achievement notification."""
        return {
            "achievement_info": {
                "achievement_type": notification.data.get("achievement_type"),
                "level": notification.data.get("level"),
                "description": notification.data.get("description"),
                "rewards": notification.data.get("rewards")
            }
        }

    async def _delayed_batch_processing(self, user_id: str, delay_minutes: int):
        """Process batch queue after specified delay."""
        await asyncio.sleep(delay_minutes * 60)
        await self._process_batch_queue(user_id) 