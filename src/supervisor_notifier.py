#!/usr/bin/env python3
"""
Supervisor Notification System

Handles notifying supervisors when help requests are created.
Simulates texting and can trigger webhooks for real integrations.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from help_request_db import HelpRequest, HelpRequestPriority

logger = logging.getLogger(__name__)

class SupervisorNotifier:
    """Handles supervisor notifications for help requests"""
    
    def __init__(self):
        self.supervisors = self._load_supervisors()
        self.webhook_urls = self._load_webhook_config()
        self.notification_history = []
    
    def _load_supervisors(self) -> Dict[str, Dict[str, Any]]:
        """Load supervisor information"""
        return {
            "maria_rodriguez": {
                "name": "Maria Rodriguez",
                "role": "Owner",
                "phone": "+1-555-123-4567",
                "email": "maria@glamourgrace.com",
                "availability": "9:00 AM - 7:00 PM",
                "specialties": ["general", "escalations", "billing"]
            },
            "jennifer_smith": {
                "name": "Jennifer Smith", 
                "role": "Senior Stylist",
                "phone": "+1-555-123-4568",
                "email": "jennifer@glamourgrace.com",
                "availability": "9:00 AM - 7:00 PM",
                "specialties": ["hair", "color", "styling"]
            },
            "david_chen": {
                "name": "David Chen",
                "role": "Color Specialist",
                "phone": "+1-555-123-4569", 
                "email": "david@glamourgrace.com",
                "availability": "10:00 AM - 6:00 PM",
                "specialties": ["color", "highlights", "corrections"]
            }
        }
    
    def _load_webhook_config(self) -> Dict[str, str]:
        """Load webhook configuration"""
        return {
            "slack": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "teams": "https://your-org.webhook.office.com/webhookb2/YOUR/WEBHOOK",
            "discord": "https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK",
            "custom": "https://your-api.com/webhook/help-requests"
        }
    
    async def notify_supervisor(self, help_request: HelpRequest, 
                              supervisor_id: Optional[str] = None) -> bool:
        """
        Notify supervisor about a help request
        
        Args:
            help_request: The help request to notify about
            supervisor_id: Specific supervisor to notify (auto-assigns if None)
        
        Returns:
            bool: True if notification was successful
        """
        try:
            # Auto-assign supervisor if not specified
            if not supervisor_id:
                supervisor_id = self._auto_assign_supervisor(help_request)
            
            if not supervisor_id:
                logger.error(f"Could not auto-assign supervisor for request {help_request.id}")
                return False
            
            supervisor = self.supervisors.get(supervisor_id)
            if not supervisor:
                logger.error(f"Supervisor {supervisor_id} not found")
                return False
            
            # Create notification message
            notification = self._create_notification(help_request, supervisor)
            
            # Simulate texting supervisor
            await self._simulate_text_message(notification)
            
            # Trigger webhooks
            await self._trigger_webhooks(help_request, supervisor)
            
            # Log notification
            self._log_notification(help_request, supervisor, notification)
            
            logger.info(f"Successfully notified supervisor {supervisor['name']} about request {help_request.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify supervisor: {e}")
            return False
    
    def _auto_assign_supervisor(self, help_request: HelpRequest) -> Optional[str]:
        """Auto-assign supervisor based on request content and availability"""
        question_lower = help_request.question.lower()
        
        # Check if any supervisors are available (simplified availability check)
        current_hour = datetime.now().hour
        
        available_supervisors = []
        for sup_id, sup_info in self.supervisors.items():
            # Simple availability check (9 AM - 7 PM)
            if 9 <= current_hour <= 19:
                available_supervisors.append(sup_id)
        
        if not available_supervisors:
            return None
        
        # Priority-based assignment
        if help_request.priority == HelpRequestPriority.URGENT:
            # Urgent requests go to owner
            return "maria_rodriguez"
        
        # Specialty-based assignment
        if any(word in question_lower for word in ["color", "highlight", "dye", "bleach"]):
            return "david_chen"
        elif any(word in question_lower for word in ["hair", "cut", "style", "curl"]):
            return "jennifer_smith"
        else:
            # General questions go to owner
            return "maria_rodriguez"
    
    def _create_notification(self, help_request: HelpRequest, 
                           supervisor: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification message for supervisor"""
        return {
            "type": "help_request_notification",
            "timestamp": datetime.utcnow().isoformat(),
            "supervisor": supervisor,
            "help_request": {
                "id": help_request.id,
                "customer_name": help_request.customer_name,
                "question": help_request.question,
                "priority": help_request.priority.value,
                "created_at": help_request.created_at.isoformat()
            },
            "message": f"Hey {supervisor['name']}, I need help answering: '{help_request.question}'",
            "action_required": "Please review and respond to customer",
            "priority_level": help_request.priority.value
        }
    
    async def _simulate_text_message(self, notification: Dict[str, Any]) -> None:
        """Simulate sending a text message to supervisor"""
        supervisor = notification["supervisor"]
        message = notification["message"]
        
        # Simulate SMS sending
        print("\n" + "="*60)
        print("📱 SUPERVISOR TEXT MESSAGE")
        print("="*60)
        print(f"To: {supervisor['name']} ({supervisor['phone']})")
        print(f"From: Salon AI Agent")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        print(f"Message: {message}")
        print(f"Customer: {notification['help_request']['customer_name']}")
        print(f"Priority: {notification['help_request']['priority']}")
        print(f"Request ID: #{notification['help_request']['id']}")
        print("="*60 + "\n")
        
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        logger.info(f"Simulated text message sent to {supervisor['name']}")
    
    async def _trigger_webhooks(self, help_request: HelpRequest, 
                               supervisor: Dict[str, Any]) -> None:
        """Trigger webhooks for external integrations"""
        webhook_data = {
            "event_type": "help_request_created",
            "timestamp": datetime.utcnow().isoformat(),
            "help_request": asdict(help_request),
            "assigned_supervisor": supervisor,
            "salon_info": {
                "name": "Glamour & Grace Salon",
                "location": "123 Beauty Lane, Style City, SC 12345"
            }
        }
        
        for webhook_name, webhook_url in self.webhook_urls.items():
            try:
                await self._send_webhook(webhook_name, webhook_url, webhook_data)
            except Exception as e:
                logger.error(f"Failed to send webhook to {webhook_name}: {e}")
    
    async def _send_webhook(self, webhook_name: str, webhook_url: str, 
                           data: Dict[str, Any]) -> None:
        """Send webhook to external service"""
        # Simulate webhook sending
        print(f"🌐 Webhook sent to {webhook_name}: {webhook_url}")
        print(f"   Data: {json.dumps(data, indent=2, default=str)}")
        
        # In a real implementation, you would use aiohttp to send the webhook
        # import aiohttp
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(webhook_url, json=data) as response:
        #         if response.status != 200:
        #             raise Exception(f"Webhook failed with status {response.status}")
        
        # Simulate network delay
        await asyncio.sleep(0.2)
        
        logger.info(f"Webhook sent to {webhook_name}")
    
    def _log_notification(self, help_request: HelpRequest, 
                         supervisor: Dict[str, Any], 
                         notification: Dict[str, Any]) -> None:
        """Log notification for audit purposes"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "help_request_id": help_request.id,
            "supervisor_id": supervisor.get("name", "unknown"),
            "notification_type": "supervisor_alert",
            "message": notification["message"],
            "priority": help_request.priority.value
        }
        
        self.notification_history.append(log_entry)
        
        # Keep only last 1000 notifications in memory
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
    
    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get notification history"""
        return self.notification_history[-limit:]
    
    def get_supervisor_info(self, supervisor_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific supervisor"""
        return self.supervisors.get(supervisor_id)
    
    def get_all_supervisors(self) -> Dict[str, Dict[str, Any]]:
        """Get all supervisor information"""
        return self.supervisors.copy()
    
    def add_supervisor(self, supervisor_id: str, supervisor_info: Dict[str, Any]) -> bool:
        """Add a new supervisor"""
        try:
            self.supervisors[supervisor_id] = supervisor_info
            logger.info(f"Added supervisor: {supervisor_info.get('name', supervisor_id)}")
            return True
        except Exception as e:
            logger.error(f"Failed to add supervisor: {e}")
            return False
    
    def update_webhook_url(self, webhook_name: str, new_url: str) -> bool:
        """Update webhook URL"""
        try:
            self.webhook_urls[webhook_name] = new_url
            logger.info(f"Updated {webhook_name} webhook URL")
            return True
        except Exception as e:
            logger.error(f"Failed to update webhook URL: {e}")
            return False

# Global supervisor notifier instance
supervisor_notifier = SupervisorNotifier() 