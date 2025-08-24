import os
from livekit import api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_agent_token(identity: str = None, name: str = None, room: str = None) -> str:
    """
    Generate a LiveKit access token for the AI agent
    
    Args:
        identity: Agent identity (defaults to env var)
        name: Agent display name (defaults to env var)
        room: Room name (defaults to env var)
    
    Returns:
        JWT token string
    """
    identity = identity or os.getenv("AGENT_IDENTITY", "salon-agent")
    name = name or os.getenv("AGENT_NAME", "Salon Assistant")
    room = room or os.getenv("ROOM_NAME", "salon-support")
    
    # Get API credentials from environment
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET environment variables are required")
    
    # Create access token with API credentials
    token = api.AccessToken(api_key=api_key, api_secret=api_secret) \
        .with_identity(identity) \
        .with_name(name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room,
            can_publish=True,
            can_subscribe=True
        ))
    
    return token.to_jwt()

def generate_participant_token(identity: str, name: str, room: str = None) -> str:
    """
    Generate a LiveKit access token for a participant
    
    Args:
        identity: Participant identity
        name: Participant display name
        room: Room name (defaults to env var)
    
    Returns:
        JWT token string
    """
    room = room or os.getenv("ROOM_NAME", "salon-support")
    
    # Get API credentials from environment
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET environment variables are required")
    
    # Create access token with API credentials
    token = api.AccessToken(api_key=api_key, api_secret=api_secret) \
        .with_identity(identity) \
        .with_name(name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room,
            can_subscribe=True
        ))
    
    return token.to_jwt()

def get_livekit_url() -> str:
    """Get LiveKit URL from environment variables"""
    return os.getenv("LIVEKIT_URL", "wss://your-project.livekit.cloud")

if __name__ == "__main__":
    # Example usage
    print("Agent Token:")
    print(generate_agent_token())
    print("\nParticipant Token:")
    print(generate_participant_token("test-user", "Test User"))
    print(f"\nLiveKit URL: {get_livekit_url()}") 