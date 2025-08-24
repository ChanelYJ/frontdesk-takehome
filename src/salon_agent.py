import asyncio
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from livekit import rtc, api
from business_logic import SalonBusinessLogic
from help_request_service import HelpRequestService

# Load environment variables
load_dotenv()

class SalonAgent:
    """
    A simulated AI agent for a fake salon business that can:
    - Receive calls via LiveKit
    - Respond to business questions using business logic
    - Trigger "request help" events when needed
    """
    
    def __init__(self):
        self.room = rtc.Room()
        self.business_logic = SalonBusinessLogic()
        self.help_request_service = HelpRequestService()
        
        # Set up event handlers
        self._setup_event_handlers()
        
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
        welcome_message = f"Welcome to {self.business_logic.salon_info['business_name']}! I'm your AI assistant. How can I help you today?"
        self._send_message(welcome_message, participant)
    
    async def _handle_message(self, message: str, participant: rtc.RemoteParticipant):
        """Process incoming messages and generate responses"""
        message_lower = message.lower()
        
        # Check if we can answer the question
        response = self.business_logic.generate_response(message_lower)
        
        if response:
            await self._send_message(response, participant)
        else:
            # Trigger "request help" event
            await self._trigger_help_request(message, participant)
    
    async def _trigger_help_request(self, message: str, participant: rtc.RemoteParticipant):
        """Trigger a help request when the agent doesn't know the answer"""
        try:
            # Use the help request service to create the request
            help_request = await self.help_request_service.create_help_request(message, participant)
            
            if help_request:
                # Send message to participant
                help_message = "Let me check with my supervisor and get back to you."
                await self._send_message(help_message, participant)
                logging.info(f"Help request {help_request.id} created and supervisor notified")
            else:
                # Fallback message if help request creation failed
                fallback_message = "I'm sorry, I don't have information about that. Please call us directly for assistance."
                await self._send_message(fallback_message, participant)
                
        except Exception as e:
            logging.error(f"Failed to create help request: {e}")
            # Fallback message
            fallback_message = "I'm sorry, I don't have information about that. Please call us directly for assistance."
            await self._send_message(fallback_message, participant)
    
    def _send_message(self, message: str, participant: rtc.RemoteParticipant):
        """Send a message to a specific participant"""
        try:
            # Check if we're connected and have a local participant
            if not hasattr(self.room, 'local_participant') or self.room.local_participant is None:
                logging.warning("Cannot send message: not connected to room")
                return
                
            data = message.encode('utf-8')
            self.room.local_participant.publish_data(data, topic="chat")
            logging.info(f"Sent message to {participant.identity}: {message}")
        except Exception as e:
            logging.error(f"Error sending message: {e}")
    
    async def connect(self, url: str, token: str):
        """Connect to LiveKit room"""
        try:
            logging.info(f"Attempting to connect to LiveKit room...")
            logging.info(f"URL: {url}")
            logging.info(f"Token length: {len(token)} characters")
            
            await self.room.connect(url, token)
            
            # Wait a moment for connection to stabilize
            await asyncio.sleep(1)
            
            if hasattr(self.room, 'local_participant') and self.room.local_participant:
                logging.info(f"Successfully connected to room: {self.room.name}")
                logging.info(f"Local participant identity: {self.room.local_participant.identity}")
            else:
                logging.warning("Connected but local participant not available yet")
                
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            logging.error(f"Connection details - URL: {url}, Token valid: {bool(token)}")
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
        return self.help_request_service.get_help_requests()
    
    def get_help_request_stats(self) -> dict:
        """Get help request statistics"""
        return self.help_request_service.get_help_request_stats() 