from typing import Dict, Any, Optional
import logging
from datetime import datetime
from app.services.twilio_service import get_twilio_service
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.twilio_service = get_twilio_service()
        self.email_service = get_email_service()
        
    async def send_streak_notification(
        self,
        user_id: str,
        streak_info: Dict[str, Any],
        notification_type: str = "both"
    ) -> Dict[str, Any]:
        """Send streak milestone notifications via email and/or SMS."""
        try:
            message = self._generate_streak_message(streak_info)
            results = {"status": "success", "notifications": []}
            
            if notification_type in ["sms", "both"]:
                sms_result = await self.twilio_service.send_sms(
                    to_number=streak_info.get("phone_number"),
                    message=message
                )
                results["notifications"].append({
                    "type": "sms",
                    "status": sms_result["status"]
                })
                
            if notification_type in ["email", "both"]:
                email_result = await self.email_service.send_email(
                    to_email=streak_info.get("email"),
                    subject=f"🎉 Learning Streak: Day {streak_info['current_streak']}!",
                    body=message
                )
                results["notifications"].append({
                    "type": "email",
                    "status": email_result["status"]
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error sending streak notification: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def send_tier_promotion_notification(
        self,
        user_id: str,
        streak_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification for tier promotions."""
        try:
            message = self._generate_tier_message(streak_info)
            
            # Send both email and SMS for tier promotions
            return await self.send_streak_notification(
                user_id,
                {**streak_info, "promotion_message": message},
                notification_type="both"
            )
            
        except Exception as e:
            logger.error(f"Error sending tier promotion notification: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def send_recovery_notification(
        self,
        user_id: str,
        streak_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification when user exits recovery mode."""
        try:
            message = (
                f"🎉 Congratulations! You've successfully recovered your learning streak!\n"
                f"Current streak: {streak_info['current_streak']} days\n"
                f"Recovery bonus: {streak_info.get('recovery_bonus', 0)} points\n"
                f"Keep up the great work! 💪"
            )
            
            return await self.send_streak_notification(
                user_id,
                {**streak_info, "recovery_message": message},
                notification_type="both"
            )
            
        except Exception as e:
            logger.error(f"Error sending recovery notification: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _generate_streak_message(self, streak_info: Dict[str, Any]) -> str:
        """Generate personalized streak milestone message."""
        streak = streak_info["current_streak"]
        tier_name = streak_info["tier_name"]
        bonus_points = streak_info.get("daily_bonus", 0)
        
        message = [
            f"🎉 Amazing work! You've reached a {streak}-day learning streak!",
            f"Current tier: {tier_name}",
            f"Daily bonus: {bonus_points} points"
        ]
        
        # Add milestone-specific messages
        if streak in [7, 15, 30, 60, 90]:
            message.append(f"\n🏆 Special {streak}-day milestone achieved!")
            if "promotion_message" in streak_info:
                message.append(streak_info["promotion_message"])
                
        # Add recovery achievements
        if "recovery_message" in streak_info:
            message.append(streak_info["recovery_message"])
            
        # Add motivation
        message.append("\nKeep learning and growing! 💪")
        
        return "\n".join(message)
    
    def _generate_tier_message(self, streak_info: Dict[str, Any]) -> str:
        """Generate tier promotion message."""
        return (
            f"🌟 Incredible achievement! You've reached {streak_info['tier_name']} tier!\n"
            f"Streak: {streak_info['current_streak']} days\n"
            f"Bonus multiplier: {streak_info.get('recovery_multiplier', 1.0)}x\n"
            f"Keep up the momentum! 🚀"
        ) 
