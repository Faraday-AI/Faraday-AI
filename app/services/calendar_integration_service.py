"""
TODO: Calendar Integration Setup Requirements
----------------------------------------

1. Provider Setup:
   - Google Calendar:
     * Go to Google Cloud Console (https://console.cloud.google.com)
     * Create new project
     * Enable Google Calendar API
     * Create OAuth 2.0 credentials (Client ID & Secret)
     * Set up authorized redirect URIs
     * Store credentials in config/calendar_config.json

   - Microsoft Calendar:
     * Register app in Azure Portal (https://portal.azure.com)
     * Enable Microsoft Graph Calendar permissions
     * Get Application ID and Client Secret
     * Configure redirect URIs
     * Store credentials in config/calendar_config.json

   - Apple Calendar:
     * Register as Apple Developer
     * Set up App ID with Calendar capability
     * Get Team ID and Key ID
     * Generate private key
     * Store credentials in config/calendar_config.json

2. Configuration Setup:
   - Create directory: app/services/config/
   - Create calendar_config.json with structure:
     {
         "google": {
             "client_id": "",
             "client_secret": "",
             "redirect_uri": ""
         },
         "microsoft": {
             "client_id": "",
             "client_secret": "",
             "tenant_id": ""
         },
         "apple": {
             "team_id": "",
             "key_id": "",
             "private_key_path": ""
         },
         "sync_interval": 300,
         "cache_duration": 3600,
         "max_events": 1000,
         "default_reminder": 15,
         "timezone": "UTC"
     }

3. Dependencies:
   - Add to requirements.txt:
     * icalendar
     * python-dateutil
     * pytz
     * aiohttp
     * google-auth
     * google-auth-oauthlib
     * google-auth-httplib2
     * google-api-python-client
     * msal (for Microsoft)

4. Environment Variables:
   - Set up in .env:
     GOOGLE_CLIENT_ID=your_client_id
     GOOGLE_CLIENT_SECRET=your_client_secret
     MICROSOFT_CLIENT_ID=your_client_id
     MICROSOFT_CLIENT_SECRET=your_client_secret
     APPLE_TEAM_ID=your_team_id
     APPLE_KEY_ID=your_key_id

5. Security:
   - Never commit credentials to version control
   - Use environment variables or secure secret management
   - Implement proper OAuth flow for each provider
   - Set up rate limiting and request validation

6. Testing:
   - Set up test accounts for each provider
   - Create test calendars
   - Test all CRUD operations
   - Test sync functionality
   - Test recurring events
   - Test availability calculations

Note: Complete these steps before using the calendar integration service.
Provider-specific authentication implementations still need to be completed
in the respective methods (_google_authenticate, _microsoft_authenticate, etc.)
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import aiohttp
import json
from pathlib import Path
from fastapi import HTTPException
import asyncio
from icalendar import Calendar, Event, vText
from dateutil.rrule import rrulestr
import pytz

logger = logging.getLogger(__name__)

class CalendarIntegrationService:
    def __init__(self):
        """Initialize the Calendar Integration Service."""
        self.config = self._load_config()
        self.session = None
        self.calendar_cache = {}
        self.event_cache = {}
        self.sync_status = {}
        self.supported_providers = ["google", "microsoft", "apple", "generic_ical"]

    def _load_config(self) -> Dict[str, Any]:
        """Load calendar integration configuration."""
        try:
            config_path = Path(__file__).parent / "config" / "calendar_config.json"
            if config_path.exists():
                with open(config_path, "r") as f:
                    return json.load(f)
            return {
                "sync_interval": 300,  # 5 minutes
                "cache_duration": 3600,  # 1 hour
                "max_events": 1000,
                "default_reminder": 15,  # minutes
                "timezone": "UTC"
            }
        except Exception as e:
            logger.error(f"Error loading calendar config: {str(e)}")
            return {}

    async def initialize_session(self) -> None:
        """Initialize HTTP session for API calls."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def connect_calendar(
        self,
        provider: str,
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """Connect to a calendar provider."""
        try:
            if provider not in self.supported_providers:
                raise ValueError(f"Unsupported calendar provider: {provider}")

            await self.initialize_session()
            
            # Authenticate with provider
            auth_result = await self._authenticate(provider, credentials)
            
            # Store connection status
            self.sync_status[provider] = {
                "connected": True,
                "last_sync": datetime.now(),
                "auth_token": auth_result["token"]
            }

            return {
                "status": "success",
                "provider": provider,
                "calendar_id": auth_result["calendar_id"],
                "features": await self._get_supported_features(provider)
            }
        except Exception as e:
            logger.error(f"Error connecting to calendar: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_event(
        self,
        provider: str,
        calendar_id: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a calendar event."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Validate event data
            self._validate_event_data(event_data)
            
            # Create event
            event = await self._create_provider_event(provider, calendar_id, event_data)
            
            # Update cache
            self._update_event_cache(provider, calendar_id, event)

            return event
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def update_event(
        self,
        provider: str,
        calendar_id: str,
        event_id: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a calendar event."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Validate event data
            self._validate_event_data(event_data)
            
            # Update event
            event = await self._update_provider_event(
                provider,
                calendar_id,
                event_id,
                event_data
            )
            
            # Update cache
            self._update_event_cache(provider, calendar_id, event)

            return event
        except Exception as e:
            logger.error(f"Error updating event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_event(
        self,
        provider: str,
        calendar_id: str,
        event_id: str
    ) -> None:
        """Delete a calendar event."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Delete event
            await self._delete_provider_event(provider, calendar_id, event_id)
            
            # Update cache
            self._remove_from_cache(provider, calendar_id, event_id)
        except Exception as e:
            logger.error(f"Error deleting event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_events(
        self,
        provider: str,
        calendar_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get calendar events."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Check cache first
            cache_key = f"{provider}_{calendar_id}"
            if cache_key in self.event_cache:
                cached_events = self._filter_cached_events(
                    self.event_cache[cache_key],
                    start_time,
                    end_time
                )
                if cached_events:
                    return cached_events[:max_results] if max_results else cached_events

            # Fetch events from provider
            events = await self._fetch_provider_events(
                provider,
                calendar_id,
                start_time,
                end_time,
                max_results
            )
            
            # Update cache
            self.event_cache[cache_key] = {
                "timestamp": datetime.now(),
                "data": events
            }

            return events
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def sync_calendars(
        self,
        provider: str,
        full_sync: bool = False
    ) -> Dict[str, Any]:
        """Sync calendars with provider."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Perform sync
            sync_result = await self._sync_with_provider(provider, full_sync)
            
            # Update sync status
            self.sync_status[provider]["last_sync"] = datetime.now()

            return sync_result
        except Exception as e:
            logger.error(f"Error syncing calendars: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_recurring_event(
        self,
        provider: str,
        calendar_id: str,
        event_data: Dict[str, Any],
        recurrence_rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a recurring calendar event."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Validate event data and recurrence rule
            self._validate_event_data(event_data)
            self._validate_recurrence_rule(recurrence_rule)
            
            # Create recurring event
            event = await self._create_recurring_provider_event(
                provider,
                calendar_id,
                event_data,
                recurrence_rule
            )
            
            # Update cache
            self._update_event_cache(provider, calendar_id, event)

            return event
        except Exception as e:
            logger.error(f"Error creating recurring event: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_availability(
        self,
        provider: str,
        calendar_id: str,
        start_time: datetime,
        end_time: datetime,
        duration: int
    ) -> List[Dict[str, Any]]:
        """Get available time slots."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Get events for the period
            events = await self.get_events(provider, calendar_id, start_time, end_time)
            
            # Calculate available slots
            available_slots = self._calculate_available_slots(
                events,
                start_time,
                end_time,
                duration
            )

            return available_slots
        except Exception as e:
            logger.error(f"Error getting availability: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def export_calendar(
        self,
        provider: str,
        calendar_id: str,
        format: str = "ical"
    ) -> str:
        """Export calendar in specified format."""
        try:
            if not self._is_connected(provider):
                raise ValueError(f"Not connected to {provider}")

            # Get all events
            events = await self.get_events(provider, calendar_id)
            
            # Export calendar
            if format.lower() == "ical":
                return self._export_to_ical(events)
            else:
                raise ValueError(f"Unsupported export format: {format}")
        except Exception as e:
            logger.error(f"Error exporting calendar: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    # Helper methods
    def _is_connected(self, provider: str) -> bool:
        """Check if connected to calendar provider."""
        return (
            provider in self.sync_status and
            self.sync_status[provider]["connected"]
        )

    def _validate_event_data(self, event_data: Dict[str, Any]) -> None:
        """Validate event data."""
        required_fields = ["title", "start_time", "end_time"]
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Missing required field: {field}")

    def _validate_recurrence_rule(self, recurrence_rule: Dict[str, Any]) -> None:
        """Validate recurrence rule."""
        required_fields = ["frequency", "interval"]
        for field in required_fields:
            if field not in recurrence_rule:
                raise ValueError(f"Missing required field in recurrence rule: {field}")

    def _update_event_cache(
        self,
        provider: str,
        calendar_id: str,
        event: Dict[str, Any]
    ) -> None:
        """Update event cache."""
        cache_key = f"{provider}_{calendar_id}"
        if cache_key not in self.event_cache:
            self.event_cache[cache_key] = {
                "timestamp": datetime.now(),
                "data": []
            }
        self.event_cache[cache_key]["data"].append(event)

    def _remove_from_cache(
        self,
        provider: str,
        calendar_id: str,
        event_id: str
    ) -> None:
        """Remove event from cache."""
        cache_key = f"{provider}_{calendar_id}"
        if cache_key in self.event_cache:
            self.event_cache[cache_key]["data"] = [
                event for event in self.event_cache[cache_key]["data"]
                if event["id"] != event_id
            ]

    def _filter_cached_events(
        self,
        cached_data: Dict[str, Any],
        start_time: Optional[datetime],
        end_time: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Filter cached events by time range."""
        if not start_time and not end_time:
            return cached_data["data"]

        filtered_events = []
        for event in cached_data["data"]:
            event_start = datetime.fromisoformat(event["start_time"])
            event_end = datetime.fromisoformat(event["end_time"])
            
            if start_time and event_end < start_time:
                continue
            if end_time and event_start > end_time:
                continue
                
            filtered_events.append(event)

        return filtered_events

    def _calculate_available_slots(
        self,
        events: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime,
        duration: int
    ) -> List[Dict[str, Any]]:
        """Calculate available time slots."""
        # Sort events by start time
        sorted_events = sorted(events, key=lambda x: x["start_time"])
        
        available_slots = []
        current_time = start_time

        for event in sorted_events:
            event_start = datetime.fromisoformat(event["start_time"])
            event_end = datetime.fromisoformat(event["end_time"])

            # Check if there's enough time before the event
            if (event_start - current_time).total_seconds() >= duration * 60:
                available_slots.append({
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(minutes=duration)).isoformat()
                })

            current_time = max(current_time, event_end)

        # Check for available time after last event
        if (end_time - current_time).total_seconds() >= duration * 60:
            available_slots.append({
                "start": current_time.isoformat(),
                "end": (current_time + timedelta(minutes=duration)).isoformat()
            })

        return available_slots

    def _export_to_ical(self, events: List[Dict[str, Any]]) -> str:
        """Export events to iCalendar format."""
        cal = Calendar()
        cal.add('prodid', '-//Faraday AI Calendar//EN')
        cal.add('version', '2.0')

        for event_data in events:
            event = Event()
            event.add('summary', event_data["title"])
            event.add('dtstart', datetime.fromisoformat(event_data["start_time"]))
            event.add('dtend', datetime.fromisoformat(event_data["end_time"]))
            
            if "description" in event_data:
                event.add('description', event_data["description"])
            if "location" in event_data:
                event.add('location', vText(event_data["location"]))
            if "recurrence_rule" in event_data:
                event.add('rrule', rrulestr(event_data["recurrence_rule"]))

            cal.add_component(event)

        return cal.to_ical().decode('utf-8')

    # Provider-specific implementations
    async def _authenticate(
        self,
        provider: str,
        credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        """Authenticate with calendar provider."""
        # Implementation varies by provider
        if provider == "google":
            return await self._google_authenticate(credentials)
        elif provider == "microsoft":
            return await self._microsoft_authenticate(credentials)
        elif provider == "apple":
            return await self._apple_authenticate(credentials)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _get_supported_features(
        self,
        provider: str
    ) -> Dict[str, bool]:
        """Get supported features for calendar provider."""
        features = {
            "recurring_events": True,
            "reminders": True,
            "availability": True,
            "export": True,
            "sync": True
        }
        
        if provider == "generic_ical":
            features["reminders"] = False
            features["availability"] = False
        
        return features 
