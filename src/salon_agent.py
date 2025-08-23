import asyncio
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from livekit import rtc, api

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
        self.help_requests = []
        
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
                self._handle_message(message, participant)
            except Exception as e:
                logging.error(f"Error processing message: {e}")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            logging.info(f"Track subscribed: {publication.sid} from {participant.identity}")
    
    def _handle_new_participant(self, participant: rtc.RemoteParticipant):
        """Handle new participant joining the room"""
        welcome_message = f"Welcome to {self.salon_info['business_name']}! I'm your AI assistant. How can I help you today?"
        self._send_message(welcome_message, participant)
    
    def _handle_message(self, message: str, participant: rtc.RemoteParticipant):
        """Process incoming messages and generate responses"""
        message_lower = message.lower()
        
        # Check if we can answer the question
        response = self._generate_response(message_lower)
        
        if response:
            self._send_message(response, participant)
        else:
            # Trigger "request help" event
            self._trigger_help_request(message, participant)
    
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
    
    def _trigger_help_request(self, message: str, participant: rtc.RemoteParticipant):
        """Trigger a help request when the agent doesn't know the answer"""
        help_request = {
            "timestamp": asyncio.get_event_loop().time(),
            "participant_id": participant.identity,
            "message": message,
            "type": "unknown_question"
        }
        
        self.help_requests.append(help_request)
        
        # Send message to participant
        help_message = "I'm sorry, I don't have information about that. I've requested help from a human staff member who will assist you shortly."
        self._send_message(help_message, participant)
        
        # Log the help request
        logging.info(f"Help request triggered: {help_request}")
        
        # In a real implementation, you might:
        # - Send to a help desk system
        # - Notify human staff
        # - Create a ticket
        # - Forward to a supervisor
    
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
        """Get list of help requests"""
        return self.help_requests.copy()
    
    def clear_help_requests(self):
        """Clear help requests (for testing)"""
        self.help_requests.clear() 