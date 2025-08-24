#!/usr/bin/env python3
"""
Demo Script for Salon AI Agent

This script demonstrates the salon agent's capabilities without requiring
a LiveKit connection. It shows how the agent would respond to various
customer questions and handle help requests.
"""

import asyncio
import logging
from salon_agent import SalonAgent
from help_request_db import help_request_db
from supervisor_notifier import supervisor_notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DemoParticipant:
    """Mock participant for demo purposes"""
    
    def __init__(self, identity: str, name: str):
        self.identity = identity
        self.name = name

async def run_demo():
    """Run a demonstration of the salon agent's capabilities"""
    
    print("🎭 LiveKit Salon AI Agent Demo")
    print("=" * 50)
    print("This demo shows how the agent would respond to customer questions")
    print("and handle help requests with supervisor notifications.\n")
    
    # Create the salon agent
    agent = SalonAgent()
    
    # Demo questions to test different capabilities
    demo_questions = [
        "Hi there!",
        "What are your business hours?",
        "How much does a haircut cost?",
        "Where are you located?",
        "What's your phone number?",
        "Who are your stylists?",
        "Do you do bridal hair?",
        "What services do you offer?",
        "What's the weather like today?",  # Should trigger help request
        "Can you recommend a restaurant nearby?",  # Should trigger help request
        "Do you have parking?",  # Should trigger help request
        "I have an urgent hair emergency!",  # Should trigger high priority help request
        "What are your specialties?"
    ]
    
    print("📋 Demo Questions and Responses:")
    print("-" * 40)
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{i}. Customer: {question}")
        
        # Create a mock participant
        mock_participant = DemoParticipant(f"customer-{i}", f"Customer {i}")
        
        # Process the question and get response
        if i == 1:  # First question is a greeting
            welcome_message = f"Welcome to {agent.business_logic.get_business_name()}! I'm your AI assistant. How can I help you today?"
            print(f"   Agent: {welcome_message}")
        else:
            # Get the response without sending it
            response = agent.business_logic.generate_response(question.lower())
            if response:
                print(f"   Agent: {response}")
            else:
                print(f"   Agent: Let me check with my supervisor and get back to you.")
                # For demo purposes, create help request directly through the service
                # instead of trying to use LiveKit methods
                try:
                    help_request = await agent.help_request_service.create_help_request(question, mock_participant)
                    if help_request:
                        print(f"   📝 Help request created: #{help_request.id}")
                    else:
                        print(f"   ❌ Failed to create help request")
                except Exception as e:
                    print(f"   ❌ Error creating help request: {e}")
        
        # Small delay for readability
        await asyncio.sleep(0.3)
    
    # Show help requests from database
    help_requests = agent.get_help_requests()
    if help_requests:
        print(f"\n🚨 Help Requests in Database ({len(help_requests)}):")
        print("-" * 50)
        for i, request in enumerate(help_requests, 1):
            print(f"{i}. ID: #{request.id}")
            print(f"   Customer: {request.customer_name} ({request.customer_id})")
            print(f"   Question: {request.question}")
            print(f"   Priority: {request.priority.value}")
            print(f"   Status: {request.status.value}")
            print(f"   Tags: {', '.join(request.tags) if request.tags else 'None'}")
            print(f"   Created: {request.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    # Show help request statistics
    stats = agent.get_help_request_stats()
    if stats:
        print("📊 Help Request Statistics:")
        print("-" * 30)
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        print(f"Status Breakdown: {stats.get('status_counts', {})}")
        print(f"Priority Breakdown: {stats.get('priority_counts', {})}")
        print(f"Avg Response Time: {stats.get('avg_response_time_minutes', 0)} minutes")
        print(f"Timeout Count: {stats.get('timeout_count', 0)}")
        print(f"Avg Escalation Level: {stats.get('avg_escalation_level', 0)}")
        print()
    
    # Show lifecycle demonstration
    print("🔄 Request Lifecycle Demonstration:")
    print("-" * 40)
    
    # Import timeout handler for demo
    from timeout_handler import timeout_handler
    
    # Show lifecycle stats
    lifecycle_stats = timeout_handler.get_lifecycle_stats()
    print(f"Pending Requests: {lifecycle_stats.get('pending_requests', 0)}")
    print(f"Timeout Requests: {lifecycle_stats.get('timeout_requests', 0)}")
    print(f"Unresolved Requests: {lifecycle_stats.get('unresolved_requests', 0)}")
    print(f"Resolved Requests: {lifecycle_stats.get('resolved_requests', 0)}")
    print(f"Escalation Success Rate: {lifecycle_stats.get('escalation_success_rate', 0)}%")
    print()
    
    # Demonstrate timeout processing
    print("⏰ Processing Timeouts and Escalations...")
    try:
        timeout_actions = await timeout_handler.process_timeouts()
        if timeout_actions:
            print(f"   🔄 {len(timeout_actions)} timeout actions processed:")
            for action in timeout_actions:
                if action['action'] == 'escalated':
                    print(f"      📤 Request #{action['request_id']} escalated to {action['supervisor']} (Level {action['level']})")
                elif action['action'] == 'unresolved':
                    print(f"      ❌ Request #{action['request_id']} marked as unresolved: {action['reason']}")
        else:
            print("   ✅ No timeout actions needed")
    except Exception as e:
        print(f"   ❌ Error processing timeouts: {e}")
    print()
    
    # Show supervisor information
    supervisors = supervisor_notifier.get_all_supervisors()
    print("👥 Available Supervisors:")
    print("-" * 30)
    for sup_id, sup_info in supervisors.items():
        print(f"• {sup_info['name']} ({sup_info['role']})")
        print(f"  Phone: {sup_info['phone']}")
        print(f"  Email: {sup_info['email']}")
        print(f"  Availability: {sup_info['availability']}")
        print(f"  Specialty: {', '.join(sup_info['specialties'])}")
        print()
    
    # Show salon business information
    print("🏪 Salon Business Information:")
    print("-" * 35)
    salon_info = agent.business_logic.get_business_info()
    
    print(f"Business: {salon_info['business_name']}")
    print(f"Address: {salon_info['address']}")
    print(f"Phone: {salon_info['phone']}")
    
    print("\nHours:")
    for day, hours in salon_info['hours'].items():
        print(f"  {day.title()}: {hours}")
    
    print("\nServices:")
    for service, price in salon_info['services'].items():
        print(f"  {service.title()}: {price}")
    
    print("\nSpecialties:")
    for specialty in salon_info['specialties']:
        print(f"  • {specialty}")
    
    print("\nStaff:")
    for role, name in salon_info['staff'].items():
        print(f"  {role.replace('_', ' ').title()}: {name}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("The agent demonstrated:")
    print("  • Business knowledge and responses")
    print("  • Help request creation and database storage")
    print("  • Supervisor notification system")
    print("  • Priority-based request handling")
    print("  • Tag-based categorization")
    print("  • Structured business information handling")
    print("  • Request lifecycle management")
    print("  • Timeout handling and escalations")
    print("\n🔄 Request Lifecycle System:")
    print("  • PENDING → TIMEOUT → UNRESOLVED")
    print("  • Automatic escalation to backup supervisors")
    print("  • Priority-based timeout thresholds")
    print("  • Escalation success rate tracking")
    print("\n⏰ Timeout Thresholds:")
    print("  • URGENT: 5 minutes (3 escalation levels)")
    print("  • HIGH: 10 minutes (3 escalation levels)")
    print("  • MEDIUM: 15 minutes (2 escalation levels)")
    print("  • LOW: 30 minutes (2 escalation levels)")
    print("\nTo run with LiveKit:")
    print("  1. Set up your .env file with LiveKit credentials")
    print("  2. Run: python src/main.py")
    print("  3. In another terminal: python src/test_client.py")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_demo()) 