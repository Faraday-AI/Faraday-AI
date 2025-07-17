"""
Notification Batch Optimizer Service

This module provides optimization functionality for batching notifications
based on user patterns and preferences.
"""

from typing import Dict, List, Any, Set
import asyncio
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import numpy as np
from app.core.config import get_settings


class NotificationBatchOptimizer:
    """Optimizer for notification batches based on user patterns."""
    
    def __init__(self):
        self.settings = get_settings()
        self.user_patterns = defaultdict(lambda: {
            'active_hours': [],
            'response_times': [],
            'preferred_channels': defaultdict(int),
            'batch_sizes': [],
            'language_preferences': defaultdict(int)
        })
        self.batch_window = 300  # 5 minutes
        self.min_batch_size = 2
        self.max_batch_size = 10
        self.learning_rate = 0.1

    async def optimize_batch(
        self,
        notifications: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Optimize notification batch for delivery."""
        if not notifications:
            return []

        # Group notifications by context and priority
        groups = self._group_notifications(notifications)
        
        # Optimize each group
        optimized_batches = []
        for group in groups:
            batch = await self._optimize_group(group, user_id)
            optimized_batches.extend(batch)
        
        return optimized_batches

    def _group_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group notifications by context and relationships."""
        # Initialize groups
        groups = []
        processed = set()
        
        for notification in notifications:
            if notification['id'] in processed:
                continue
                
            # Start new group
            group = [notification]
            processed.add(notification['id'])
            
            # Find related notifications
            related = self._find_related(notification, notifications)
            for related_notification in related:
                if related_notification['id'] not in processed:
                    group.append(related_notification)
                    processed.add(related_notification['id'])
            
            groups.append(group)
        
        return groups

    def _find_related(
        self,
        notification: Dict[str, Any],
        all_notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find notifications related to the given one."""
        related = []
        
        # Check for direct relationships
        thread_id = notification.get('thread_id')
        context_id = notification.get('context_id')
        
        for other in all_notifications:
            if other['id'] == notification['id']:
                continue
                
            # Check various relationship types
            if (
                other.get('thread_id') == thread_id or
                other.get('context_id') == context_id or
                self._are_notifications_related(notification, other)
            ):
                related.append(other)
                
            if len(related) >= self.max_batch_size - 1:
                break
        
        return related

    def _are_notifications_related(
        self,
        notification1: Dict[str, Any],
        notification2: Dict[str, Any]
    ) -> bool:
        """Determine if two notifications are related."""
        # Check type relationship
        if notification1['type'] == notification2['type']:
            return True
            
        # Check content similarity
        if self._calculate_content_similarity(
            notification1.get('message', ''),
            notification2.get('message', '')
        ) > 0.7:
            return True
            
        # Check temporal proximity
        time1 = datetime.fromisoformat(notification1['timestamp'])
        time2 = datetime.fromisoformat(notification2['timestamp'])
        if abs((time1 - time2).total_seconds()) < self.batch_window:
            return True
            
        return False

    def _calculate_content_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text contents."""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    async def _optimize_group(
        self,
        group: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Optimize delivery for a group of related notifications."""
        if not group:
            return []

        # Get user patterns
        patterns = self.user_patterns[user_id]
        
        # Determine optimal batch size
        optimal_size = self._calculate_optimal_batch_size(group, patterns)
        
        # Split into optimal batches
        batches = []
        current_batch = []
        
        for notification in sorted(
            group,
            key=lambda x: self._calculate_priority_score(x, patterns),
            reverse=True
        ):
            current_batch.append(notification)
            
            if len(current_batch) >= optimal_size:
                batches.append(current_batch)
                current_batch = []
        
        if current_batch:
            batches.append(current_batch)
        
        # Optimize delivery timing for each batch
        optimized_batches = []
        for batch in batches:
            delivery_time = await self._calculate_optimal_delivery_time(batch, patterns)
            
            optimized_batch = {
                'notifications': batch,
                'delivery_time': delivery_time,
                'channels': await self._select_delivery_channels(batch, patterns),
                'summary': self._generate_batch_summary(batch)
            }
            
            optimized_batches.append(optimized_batch)
        
        return optimized_batches

    def _calculate_optimal_batch_size(
        self,
        notifications: List[Dict[str, Any]],
        patterns: Dict[str, Any]
    ) -> int:
        """Calculate optimal batch size based on user patterns."""
        if not patterns['batch_sizes']:
            return min(len(notifications), self.max_batch_size)
        
        # Consider historical batch sizes
        avg_batch_size = np.mean(patterns['batch_sizes'])
        
        # Adjust based on response times
        if patterns['response_times']:
            avg_response_time = np.mean(patterns['response_times'])
            if avg_response_time > 60:  # If average response time > 1 minute
                avg_batch_size *= 0.8  # Reduce batch size
            elif avg_response_time < 10:  # If average response time < 10 seconds
                avg_batch_size *= 1.2  # Increase batch size
        
        return int(min(
            max(
                self.min_batch_size,
                avg_batch_size
            ),
            self.max_batch_size
        ))

    def _calculate_priority_score(
        self,
        notification: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> float:
        """Calculate priority score for notification ordering."""
        score = 0.0
        
        # Base priority
        priority_weights = {
            'urgent': 100,
            'high': 75,
            'normal': 50,
            'low': 25
        }
        score += priority_weights.get(notification.get('priority', 'normal'), 50)
        
        # Time factor
        time_delta = (
            datetime.utcnow() -
            datetime.fromisoformat(notification['timestamp'])
        ).total_seconds()
        score += max(0, 100 - (time_delta / 60))  # Decay over time
        
        # User preference factor
        if notification.get('type') in patterns['preferred_channels']:
            score += 25
        
        return score

    async def _calculate_optimal_delivery_time(
        self,
        batch: List[Dict[str, Any]],
        patterns: Dict[str, Any]
    ) -> datetime:
        """Calculate optimal delivery time for a batch."""
        now = datetime.utcnow()
        
        # If urgent notifications exist, deliver immediately
        if any(n.get('priority') == 'urgent' for n in batch):
            return now
        
        # Consider user's active hours
        active_hours = patterns['active_hours']
        if active_hours:
            current_hour = now.hour
            if current_hour not in active_hours:
                # Find next active hour
                next_hour = min(
                    (h for h in active_hours if h > current_hour),
                    default=active_hours[0]
                )
                if next_hour <= current_hour:
                    # Next active hour is tomorrow
                    next_hour += 24
                
                delay = (next_hour - current_hour) * 3600
                return now + timedelta(seconds=delay)
        
        return now

    async def _select_delivery_channels(
        self,
        batch: List[Dict[str, Any]],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Select optimal delivery channels for batch."""
        channels = set()
        
        # Consider user preferences
        preferred_channels = patterns['preferred_channels']
        if preferred_channels:
            # Sort channels by preference count
            sorted_channels = sorted(
                preferred_channels.items(),
                key=lambda x: x[1],
                reverse=True
            )
            channels.update(ch[0] for ch in sorted_channels[:2])
        
        # Ensure at least one channel
        if not channels:
            channels.add('app')  # Default to in-app notification
        
        # Add urgent channel if needed
        if any(n.get('priority') == 'urgent' for n in batch):
            channels.add('push')
        
        return list(channels)

    def _generate_batch_summary(self, batch: List[Dict[str, Any]]) -> str:
        """Generate a summary for the batch."""
        if not batch:
            return ""
            
        # Group by type
        type_groups = defaultdict(list)
        for notification in batch:
            type_groups[notification.get('type', 'general')].append(notification)
            
        # Generate summary
        summary_parts = []
        for type_name, notifications in type_groups.items():
            count = len(notifications)
            if count == 1:
                summary_parts.append(notifications[0].get('message', ''))
            else:
                summary_parts.append(f"{count} {type_name} notifications")
                
        return " | ".join(summary_parts)

    async def update_user_patterns(
        self,
        user_id: str,
        interaction_data: Dict[str, Any]
    ):
        """Update user interaction patterns."""
        patterns = self.user_patterns[user_id]
        
        # Update active hours
        hour = datetime.fromisoformat(
            interaction_data['timestamp']
        ).replace(tzinfo=pytz.UTC).hour
        if hour not in patterns['active_hours']:
            patterns['active_hours'].append(hour)
            patterns['active_hours'].sort()
        
        # Update response times
        if 'response_time' in interaction_data:
            patterns['response_times'].append(interaction_data['response_time'])
            if len(patterns['response_times']) > 100:
                patterns['response_times'] = patterns['response_times'][-100:]
        
        # Update channel preferences
        if 'channel' in interaction_data:
            patterns['preferred_channels'][interaction_data['channel']] += 1
        
        # Update batch sizes
        if 'batch_size' in interaction_data:
            patterns['batch_sizes'].append(interaction_data['batch_size'])
            if len(patterns['batch_sizes']) > 100:
                patterns['batch_sizes'] = patterns['batch_sizes'][-100:]
        
        # Update language preferences
        if 'language' in interaction_data:
            patterns['language_preferences'][interaction_data['language']] += 1 