#!/usr/bin/env python3
"""
Test Client for Salon AI Agent

This script simulates a customer calling the salon agent to test
its ability to answer questions and trigger help requests.
"""

import asyncio
import logging
import sys
from typing import List

from livekit import rtc
from token_generator import generate_participant_token, get_livekit_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestClient:
    """Test client to simulate customer interactions with the salon agent"""
    
    def __init__(self, identity: str, name: str):
        self.identity = identity
        self.name = name
        self.room = rtc.Room()
        self.connected = False
        
        # Set up event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up LiveKit event handlers"""
        
        @self.room.on("connected")
        def on_connected():
            logger.info("Connected to LiveKit room")
            self.connected = True
        
        @self.room.on("data_received")
        def on_data_received(payload: bytes, participant: rtc.RemoteParticipant):
            try:
                message = payload.decode('utf-8')
                logger.info(f"Agent response: {message}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
        
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Participant connected: {participant.identity}")
    
    async def connect(self, url: str, token: str):
        """Connect to LiveKit room"""
        try:
            await self.room.connect(url, token)
            logger.info(f"Connected to room: {self.room.name}")
            # Set connected flag after successful connection
            self.connected = True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from LiveKit room"""
        if self.connected:
            await self.room.disconnect()
            self.connected = False
            logger.info("Disconnected from room")
    
    async def send_message(self, message: str):
        """Send a message to the room"""
        if not self.connected:
            logger.error("Not connected to room")
            return
        
        try:
            data = message.encode('utf-8')
            self.room.local_participant.publish_data(data, topic="chat")
            logger.info(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def run_test_scenario(self, questions: List[str]):
        """Run a test scenario with predefined questions"""
        logger.info("Starting test scenario...")
        
        # Double-check connection before starting
        if not self.connected:
            logger.error("Cannot run test scenario - not connected to room")
            return
            
        for i, question in enumerate(questions, 1):
            logger.info(f"\n--- Test Question {i} ---")
            logger.info(f"Customer asks: {question}")
            
            # Send the question
            await self.send_message(question)
            
            # Wait for response
            await asyncio.sleep(2)
        
        logger.info("\n--- Test scenario completed ---")

async def main():
    """Main test function"""
    # Test questions to evaluate the agent's capabilities
    test_questions = [
        "What are your business hours?",
        "How much does a haircut cost?",
        "Where are you located?",
        "What's your phone number?",
        "Who are your stylists?",
        "Do you do bridal hair?",
        "What's the weather like today?",  # This should trigger help request
        "Can you recommend a restaurant nearby?",  # This should trigger help request
        "What services do you offer?"
    ]
    
    # Create test client
    client = TestClient("test-customer", "Test Customer")
    
    try:
        # Get LiveKit configuration
        url = get_livekit_url()
        token = generate_participant_token("test-customer", "Test Customer")
        
        logger.info("Connecting to LiveKit room...")
        await client.connect(url, token)
        
        # Wait a moment for connection to stabilize
        await asyncio.sleep(1)
        
        # Run the test scenario
        await client.run_test_scenario(test_questions)
        
        # Keep connected for a bit to see any additional responses
        logger.info("Waiting for any additional responses...")
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        raise
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Check if required environment variables are set
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        logger.error("See env.example for reference")
        sys.exit(1)
    
    # Run the test
    asyncio.run(main()) 