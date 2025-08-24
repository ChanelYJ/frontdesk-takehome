#!/usr/bin/env python3
"""
Help Request Service Module for Salon AI Agent

This module handles all help request creation, categorization, and management,
separating help request logic from communication and technical concerns.
"""

import asyncio
from typing import Dict, Any, List
from help_request_db import help_request_db, HelpRequestPriority
from supervisor_notifier import supervisor_notifier

class HelpRequestService:
    """
    Handles help request creation, categorization, and management.
    This class is independent of LiveKit or any communication layer.
    """
    
    def __init__(self):
        self.db = help_request_db
        self.notifier = supervisor_notifier
    
    async def create_help_request(self, message: str, participant) -> Any:
        """
        Create a help request when the agent cannot answer a question.
        
        Args:
            message: The customer's question that needs help
            participant: The LiveKit participant object
            
        Returns:
            The created help request object
        """
        try:
            # Create help request in database
            help_request = self.db.create_help_request(
                customer_id=participant.identity,
                customer_name=participant.name or participant.identity,
                question=message,
                priority=self._determine_priority(message),
                tags=self._extract_tags(message),
                metadata=self._create_metadata(message, participant)
            )
            
            # Notify supervisor
            await self.notifier.notify_supervisor(help_request)
            
            return help_request
            
        except Exception as e:
            # Log error but don't crash the system
            print(f"Failed to create help request: {e}")
            return None
    
    def _determine_priority(self, message: str) -> HelpRequestPriority:
        """
        Determine priority level based on message content.
        
        Args:
            message: The customer's message
            
        Returns:
            HelpRequestPriority enum value
        """
        message_lower = message.lower()
        
        # High priority keywords
        if any(word in message_lower for word in ["urgent", "emergency", "broken", "problem", "issue", "complaint"]):
            return HelpRequestPriority.HIGH
        
        # Medium priority keywords  
        if any(word in message_lower for word in ["appointment", "booking", "reservation", "schedule", "time"]):
            return HelpRequestPriority.MEDIUM
        
        # Default to low priority
        return HelpRequestPriority.LOW
    
    def _extract_tags(self, message: str) -> List[str]:
        """
        Extract relevant tags from the message for categorization.
        
        Args:
            message: The customer's message
            
        Returns:
            List of relevant tags
        """
        message_lower = message.lower()
        tags = []
        
        # Service-related tags
        if any(word in message_lower for word in ["hair", "cut", "style"]):
            tags.append("hair")
        if any(word in message_lower for word in ["color", "dye", "highlight"]):
            tags.append("color")
        if any(word in message_lower for word in ["nail", "manicure", "pedicure"]):
            tags.append("nails")
        if any(word in message_lower for word in ["facial", "massage", "spa"]):
            tags.append("spa")
        if any(word in message_lower for word in ["bridal", "wedding", "special"]):
            tags.append("bridal")
        
        # General tags
        if any(word in message_lower for word in ["price", "cost", "how much"]):
            tags.append("pricing")
        if any(word in message_lower for word in ["hours", "open", "close"]):
            tags.append("hours")
        if any(word in message_lower for word in ["location", "address", "directions"]):
            tags.append("location")
        
        return tags
    
    def _create_metadata(self, message: str, participant) -> Dict[str, Any]:
        """
        Create metadata for the help request.
        
        Args:
            message: The customer's message
            participant: The LiveKit participant object
            
        Returns:
            Dictionary of metadata
        """
        return {
            "room_name": getattr(participant, 'room_name', 'unknown'),
            "participant_identity": participant.identity,
            "timestamp": asyncio.get_event_loop().time(),
            "message_length": len(message),
            "has_urgent_keywords": any(word in message.lower() for word in ["urgent", "emergency", "problem"])
        }
    
    def get_help_requests(self) -> List[Any]:
        """Get list of help requests from database"""
        return self.db.get_pending_requests()
    
    def get_help_request_stats(self) -> Dict[str, Any]:
        """Get help request statistics"""
        return self.db.get_statistics()
    
    def get_requests_by_priority(self, priority: HelpRequestPriority) -> List[Any]:
        """Get help requests filtered by priority"""
        all_requests = self.get_help_requests()
        return [req for req in all_requests if req.priority == priority]
    
    def get_requests_by_tag(self, tag: str) -> List[Any]:
        """Get help requests filtered by tag"""
        all_requests = self.get_help_requests()
        return [req for req in all_requests if tag in (req.tags or [])] 