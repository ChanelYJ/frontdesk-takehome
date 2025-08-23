import asyncio
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from livekit import rtc, api
from help_request_db import help_request_db, HelpRequestPriority
from supervisor_notifier import supervisor_notifier

# Load environment variables
load_dotenv()

class SalonAgent:
    """
    A simulated AI agent for a fake salon business that can:
    - Receive calls via LiveKit
    - Respond to business questions
    - Trigger "request help" events when needed
    """
    
    def __init__(self):
        self.room = rtc.Room()
        self.salon_info = self._load_salon_business_info()
        
        # Set up event handlers
        self._setup_event_handlers()
        
    def _load_salon_business_info(self) -> Dict[str, Any]:
        """Load fake salon business information for the agent to use"""
        return {
            "business_name": "Glamour & Grace Salon",
            "address": "123 Beauty Lane, Style City, SC 12345",
            "phone": "(555) 123-4567",
            "hours": {
                "monday": "9:00 AM - 7:00 PM",
                "tuesday": "9:00 AM - 7:00 PM", 
                "wednesday": "9:00 AM - 7:00 PM",
                "thursday": "9:00 AM - 7:00 PM",
                "friday": "9:00 AM - 7:00 PM",
                "saturday": "10:00 AM - 6:00 PM",
                "sunday": "Closed"
            },
            "services": {
                "haircut": "$45-75",
                "hair_color": "$85-150",
                "highlights": "$120-200",
                "manicure": "$35-50",
                "pedicure": "$45-65",
                "facial": "$60-90",
                "massage": "$80-120"
            },
            "specialties": [
                "Bridal hair and makeup",
                "Color correction",
                "Keratin treatments",
                "Hair extensions",
                "Spa packages"
            ],
            "staff": {
                "owner": "Maria Rodriguez",
                "senior_stylist": "Jennifer Smith",
                "color_specialist": "David Chen",
                "nail_technician": "Lisa Johnson"
            }
        }
    
    def _setup_event_handlers(self):
        """Set up LiveKit event handlers"""
        
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logging.info(f"Participant connected: {participant.identity}")
            self._handle_new_participant(participant)
        
        @self.room.on("data_received")
        def on_data_received(payload: bytes, participant: rtc.RemoteParticipant):
            try:
                message = payload.decode('utf-8')
                logging.info(f"Received message from {participant.identity}: {message}")
                # Handle message asynchronously
                asyncio.create_task(self._handle_message(message, participant))
            except Exception as e:
                logging.error(f"Error processing message: {e}")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            logging.info(f"Track subscribed: {publication.sid} from {participant.identity}")
    
    def _handle_new_participant(self, participant: rtc.RemoteParticipant):
        """Handle new participant joining the room"""
        welcome_message = f"Welcome to {self.salon_info['business_name']}! I'm your AI assistant. How can I help you today?"
        self._send_message(welcome_message, participant)
    
    async def _handle_message(self, message: str, participant: rtc.RemoteParticipant):
        """Process incoming messages and generate responses"""
        message_lower = message.lower()
        
        # Check if we can answer the question
        response = self._generate_response(message_lower)
        
        if response:
            self._send_message(response, participant)
        else:
            # Trigger "request help" event
            await self._trigger_help_request(message, participant)
    
    def _generate_response(self, message: str) -> Optional[str]:
        """Generate a response based on the message content"""
        
        # Business hours
        if any(word in message for word in ["hours", "open", "close", "time"]):
            hours_text = "\n".join([f"{day.title()}: {time}" for day, time in self.salon_info["hours"].items()])
            return f"Our business hours are:\n{hours_text}"
        
        # Services and pricing
        elif any(word in message for word in ["service", "price", "cost", "rate", "how much"]):
            services_text = "\n".join([f"{service.title()}: {price}" for service, price in self.salon_info["services"].items()])
            return f"Here are our services and pricing:\n{services_text}"
        
        # Address and location
        elif any(word in message for word in ["address", "location", "where", "directions"]):
            return f"We're located at: {self.salon_info['address']}"
        
        # Phone number
        elif any(word in message for word in ["phone", "call", "contact", "number"]):
            return f"You can reach us at: {self.salon_info['phone']}"
        
        # Staff information
        elif any(word in message for word in ["stylist", "staff", "who", "employee"]):
            staff_text = "\n".join([f"{role.replace('_', ' ').title()}: {name}" for role, name in self.salon_info["staff"].items()])
            return f"Our team includes:\n{staff_text}"
        
        # Specialties
        elif any(word in message for word in ["specialty", "special", "bridal", "wedding"]):
            specialties_text = "\n".join([f"• {specialty}" for specialty in self.salon_info["specialties"]])
            return f"Our specialties include:\n{specialties_text}"
        
        # General salon info
        elif any(word in message for word in ["salon", "business", "about"]):
            return f"{self.salon_info['business_name']} is a full-service salon offering hair, nail, and spa services. We're committed to making you look and feel your best!"
        
        # No answer found
        return None
    
    async def _trigger_help_request(self, message: str, participant: rtc.RemoteParticipant):
        """Trigger a help request when the agent doesn't know the answer"""
        try:
            # Create help request in database
            help_request = help_request_db.create_help_request(
                customer_id=participant.identity,
                customer_name=participant.name or participant.identity,
                question=message,
                priority=self._determine_priority(message),
                tags=self._extract_tags(message),
                metadata={
                    "room_name": self.room.name if self.room.name else "unknown",
                    "participant_identity": participant.identity,
                    "timestamp": asyncio.get_event_loop().time()
                }
            )
            
            # Send message to participant
            help_message = "Let me check with my supervisor and get back to you."
            self._send_message(help_message, participant)
            
            # Notify supervisor
            await supervisor_notifier.notify_supervisor(help_request)
            
            logging.info(f"Help request {help_request.id} created and supervisor notified")
            
        except Exception as e:
            logging.error(f"Failed to create help request: {e}")
            # Fallback message
            fallback_message = "I'm sorry, I don't have information about that. Please call us directly for assistance."
            self._send_message(fallback_message, participant)
    
    def _determine_priority(self, message: str) -> HelpRequestPriority:
        """Determine priority level based on message content"""
        message_lower = message.lower()
        
        # High priority keywords
        if any(word in message_lower for word in ["urgent", "emergency", "broken", "problem", "issue", "complaint"]):
            return HelpRequestPriority.HIGH
        
        # Medium priority keywords  
        if any(word in message_lower for word in ["appointment", "booking", "reservation", "schedule", "time"]):
            return HelpRequestPriority.MEDIUM
        
        # Default to low priority
        return HelpRequestPriority.LOW
    
    def _extract_tags(self, message: str) -> list:
        """Extract relevant tags from the message"""
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
    
    def _send_message(self, message: str, participant: rtc.RemoteParticipant):
        """Send a message to a specific participant"""
        try:
            data = message.encode('utf-8')
            self.room.local_participant.publish_data(data, topic="chat")
            logging.info(f"Sent message to {participant.identity}: {message}")
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    
    async def connect(self, url: str, token: str):
        """Connect to LiveKit room"""
        try:
            await self.room.connect(url, token)
            logging.info(f"Connected to room: {self.room.name}")
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from LiveKit room"""
        try:
            await self.room.disconnect()
            logging.info("Disconnected from room")
        except Exception as e:
            logging.error(f"Error disconnecting: {e}")
    
    def get_help_requests(self) -> list:
        """Get list of help requests from database"""
        return help_request_db.get_pending_requests()
    
    def get_help_request_stats(self) -> dict:
        """Get help request statistics"""
        return help_request_db.get_statistics() 