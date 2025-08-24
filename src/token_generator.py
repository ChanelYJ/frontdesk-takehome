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
    
    # Create access token with basic grants
    token = api.AccessToken() \
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
    
    # Create access token with basic grants
    token = api.AccessToken() \
        .with_identity(identity) \
        .with_name(name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room,
            can_publish=True,
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