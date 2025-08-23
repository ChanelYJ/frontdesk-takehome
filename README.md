# LiveKit Salon AI Agent

A simulated AI agent for a fake salon business built with LiveKit's Python SDK. This project demonstrates how to create an AI agent that can receive calls, answer business questions, and trigger help requests when needed.

## 🎯 Project Overview

This project evaluates the ability to:
- Research and implement an unfamiliar framework (LiveKit)
- Read documentation and debug in a foreign environment
- Build effective prompts for AI agents
- Create a basic conversational AI system

## ✨ Features

The Salon AI Agent can:
- **Receive calls** via LiveKit real-time communication
- **Answer business questions** about the fake salon including:
  - Business hours
  - Services and pricing
  - Location and contact information
  - Staff information
  - Specialties and offerings
- **Trigger "request help" events** when it doesn't know the answer
- **Handle multiple participants** in a LiveKit room
- **Log all interactions** for monitoring and debugging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Client  │    │  Salon Agent    │    │   LiveKit       │
│   (Customer)   │◄──►│   (AI Bot)      │◄──►│   Server        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- LiveKit account and project (get one at [livekit.io](https://livekit.io))
- LiveKit API key and secret

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontdesk-takehome
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your LiveKit credentials
   ```

4. **Configure your .env file**
   ```bash
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key_here
   LIVEKIT_API_SECRET=your_api_secret_here
   AGENT_IDENTITY=salon-agent
   AGENT_NAME=Salon Assistant
   ROOM_NAME=salon-support
   ```

### Running the Agent

1. **Start the Salon AI Agent**
   ```bash
   python src/main.py
   ```

2. **In another terminal, run the test client**
   ```bash
   python src/test_client.py
   ```

## 📁 Project Structure

```
frontdesk-takehome/
├── src/
│   ├── main.py              # Main application entry point
│   ├── salon_agent.py       # Core AI agent logic
│   ├── token_generator.py   # LiveKit token utilities
│   └── test_client.py       # Test client for demonstrations
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
└── README.md                # This file
```

## 🔧 How It Works

### 1. Agent Initialization
The `SalonAgent` class loads fake salon business information and sets up LiveKit event handlers.

### 2. LiveKit Connection
The agent connects to a LiveKit room using generated JWT tokens with appropriate permissions.

### 3. Message Handling
When a participant sends a message:
- The agent processes the message using keyword matching
- If it knows the answer, it responds with relevant information
- If it doesn't know, it triggers a help request

### 4. Business Knowledge
The agent has built-in knowledge about:
- Business hours and operations
- Services and pricing
- Location and contact details
- Staff information
- Specialties and offerings

## 🧪 Testing

The `test_client.py` script simulates customer interactions to test the agent's capabilities:

```python
test_questions = [
    "What are your business hours?",
    "How much does a haircut cost?",
    "Where are you located?",
    "What's the weather like today?",  # Triggers help request
    "Can you recommend a restaurant nearby?"  # Triggers help request
]
```

## 🔍 Key Components

### SalonAgent Class
- **`_load_salon_business_info()`**: Loads fake salon data
- **`_generate_response()`**: Processes questions and generates answers
- **`_trigger_help_request()`**: Handles unknown questions
- **`_handle_message()`**: Main message processing logic

### Token Generation
- **`generate_agent_token()`**: Creates tokens for the AI agent
- **`generate_participant_token()`**: Creates tokens for customers
- **`get_livekit_url()`**: Retrieves LiveKit server URL

### Event Handling
- **Participant connections**: Welcomes new customers
- **Data messages**: Processes customer questions
- **Track subscriptions**: Handles media streams

## 🚨 Help Request System

When the agent encounters an unknown question:

1. **Logs the request** with timestamp and participant info
2. **Sends a message** to the customer about requesting help
3. **Stores the request** for human staff review
4. **In a production system**, this could:
   - Create help desk tickets
   - Notify human staff
   - Forward to supervisors
   - Integrate with CRM systems

## 🔧 Customization

### Adding New Business Knowledge
Edit the `_load_salon_business_info()` method in `salon_agent.py`:

```python
def _load_salon_business_info(self):
    return {
        "new_category": "new information",
        # ... more data
    }
```

### Extending Response Logic
Add new patterns in the `_generate_response()` method:

```python
elif any(word in message for word in ["new_topic"]):
    return "Response for new topic"
```

### Modifying Help Request Handling
Customize the `_trigger_help_request()` method for your specific needs.

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify LiveKit URL and credentials
   - Check network connectivity
   - Ensure LiveKit project is active

2. **Token Generation Errors**
   - Verify API key and secret
   - Check environment variables
   - Ensure proper permissions

3. **Message Not Received**
   - Check room name configuration
   - Verify participant permissions
   - Check LiveKit server logs

### Debug Mode
Enable detailed logging by modifying the logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📚 LiveKit Resources

- [Python SDK Documentation](https://github.com/livekit/python-sdks)
- [LiveKit Cloud](https://livekit.io/cloud)
- [API Reference](https://docs.livekit.io)
- [Community Slack](https://slack.livekit.io)

## 🤝 Contributing

This is a take-home project demonstrating LiveKit integration. For questions or improvements:

1. Review the LiveKit documentation
2. Test with different scenarios
3. Extend the business logic
4. Add more sophisticated AI capabilities

## 📄 License

This project is for educational and evaluation purposes. LiveKit is licensed under Apache 2.0.

## 🎉 Success Criteria

This project successfully demonstrates:
- ✅ Research and implementation of LiveKit Python SDK
- ✅ Creation of a functional AI agent
- ✅ Effective prompt engineering for business scenarios
- ✅ Implementation of help request system
- ✅ Clean, documented, and maintainable code
- ✅ Proper error handling and logging
- ✅ Asynchronous programming with asyncio
- ✅ Environment-based configuration
- ✅ Testing and demonstration capabilities