#!/usr/bin/env python3
"""
LiveKit Salon AI Agent - Main Application

This application demonstrates a simulated AI agent for a fake salon business
that can receive calls, answer business questions, and trigger help requests.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

from salon_agent import SalonAgent
from token_generator import generate_agent_token, get_livekit_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SalonAgentApp:
    """Main application class for the Salon AI Agent"""
    
    def __init__(self):
        self.agent: Optional[SalonAgent] = None
        self.running = False
        
    async def start(self):
        """Start the salon agent application"""
        try:
            logger.info("Starting Salon AI Agent...")
            
            # Create the salon agent
            self.agent = SalonAgent()
            
            # Get LiveKit configuration
            url = get_livekit_url()
            token = generate_agent_token()
            
            logger.info(f"Connecting to LiveKit at: {url}")
            logger.info(f"Agent identity: {self.agent.room.local_participant.identity}")
            
            # Connect to LiveKit
            await self.agent.connect(url, token)
            
            self.running = True
            logger.info("Salon AI Agent is now running and ready to receive calls!")
            logger.info("Press Ctrl+C to stop the agent")
            
            # Keep the application running
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Error starting agent: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the salon agent application"""
        if self.agent and self.running:
            logger.info("Stopping Salon AI Agent...")
            await self.agent.disconnect()
            self.running = False
            logger.info("Salon AI Agent stopped")
    
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False

async def main():
    """Main entry point"""
    app = SalonAgentApp()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)
    
    try:
        await app.start()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

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
    
    # Run the application
    asyncio.run(main())
