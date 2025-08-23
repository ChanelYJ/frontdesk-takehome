#!/usr/bin/env python3
"""
Supervisor Dashboard

A command-line interface for supervisors to manage help requests
and respond to customer inquiries.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from help_request_db import help_request_db, HelpRequestStatus, HelpRequestPriority
from supervisor_notifier import supervisor_notifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupervisorDashboard:
    """Command-line dashboard for supervisors"""
    
    def __init__(self):
        self.current_supervisor = None
        self.running = True
    
    async def start(self):
        """Start the supervisor dashboard"""
        print("👔 Supervisor Dashboard")
        print("=" * 40)
        
        # Login
        await self._login()
        
        if not self.current_supervisor:
            print("❌ Login failed. Exiting.")
            return
        
        # Main dashboard loop
        while self.running:
            await self._show_main_menu()
    
    async def _login(self):
        """Handle supervisor login"""
        print("\n🔐 Supervisor Login")
        print("-" * 20)
        
        supervisors = supervisor_notifier.get_all_supervisors()
        
        print("Available supervisors:")
        for i, (sup_id, sup_info) in enumerate(supervisors.items(), 1):
            print(f"{i}. {sup_info['name']} ({sup_info['role']})")
        
        try:
            choice = input("\nSelect supervisor (1-3): ").strip()
            if choice == "1":
                self.current_supervisor = "maria_rodriguez"
            elif choice == "2":
                self.current_supervisor = "jennifer_smith"
            elif choice == "3":
                self.current_supervisor = "david_chen"
            else:
                print("❌ Invalid choice")
                return
            
            sup_info = supervisors[self.current_supervisor]
            print(f"\n✅ Welcome, {sup_info['name']}!")
            
        except (ValueError, IndexError):
            print("❌ Invalid selection")
    
    async def _show_main_menu(self):
        """Display main menu options"""
        print("\n" + "=" * 40)
        print("📋 MAIN MENU")
        print("=" * 40)
        print("1. View Pending Help Requests")
        print("2. View All Help Requests")
        print("3. Update Request Status")
        print("4. View Statistics")
        print("5. View Supervisor Info")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            await self._view_pending_requests()
        elif choice == "2":
            await self._view_all_requests()
        elif choice == "3":
            await self._update_request_status()
        elif choice == "4":
            await self._view_statistics()
        elif choice == "5":
            await self._view_supervisor_info()
        elif choice == "6":
            self.running = False
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
    
    async def _view_pending_requests(self):
        """Display pending help requests"""
        print("\n🚨 PENDING HELP REQUESTS")
        print("-" * 40)
        
        requests = help_request_db.get_pending_requests()
        
        if not requests:
            print("✅ No pending requests!")
            return
        
        for i, request in enumerate(requests, 1):
            print(f"\n{i}. Request #{request.id}")
            print(f"   Customer: {request.customer_name}")
            print(f"   Question: {request.question}")
            print(f"   Priority: {request.priority.value}")
            print(f"   Tags: {', '.join(request.tags) if request.tags else 'None'}")
            print(f"   Created: {request.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def _view_all_requests(self):
        """Display all help requests"""
        print("\n📊 ALL HELP REQUESTS")
        print("-" * 30)
        
        # Get statistics to show total count
        stats = help_request_db.get_statistics()
        total = stats.get('total_requests', 0)
        
        if total == 0:
            print("✅ No help requests found!")
            return
        
        print(f"Total requests: {total}")
        
        # Show requests by status
        status_counts = stats.get('status_counts', {})
        for status, count in status_counts.items():
            print(f"{status.title()}: {count}")
        
        # Show recent requests
        print(f"\n📝 Recent Requests:")
        requests = help_request_db.get_pending_requests(limit=10)
        for i, request in enumerate(requests, 1):
            print(f"{i}. #{request.id} - {request.customer_name} - {request.status.value}")
    
    async def _update_request_status(self):
        """Update the status of a help request"""
        print("\n✏️ UPDATE REQUEST STATUS")
        print("-" * 30)
        
        # Show pending requests
        requests = help_request_db.get_pending_requests()
        
        if not requests:
            print("✅ No pending requests to update!")
            return
        
        print("Pending requests:")
        for i, request in enumerate(requests, 1):
            print(f"{i}. #{request.id} - {request.customer_name}")
        
        try:
            choice = int(input("\nSelect request to update (1-{}): ".format(len(requests))))
            if choice < 1 or choice > len(requests):
                print("❌ Invalid choice")
                return
            
            selected_request = requests[choice - 1]
            
            print(f"\nUpdating request #{selected_request.id}")
            print(f"Customer: {selected_request.customer_name}")
            print(f"Question: {selected_request.question}")
            
            # Show status options
            print("\nAvailable statuses:")
            for i, status in enumerate(HelpRequestStatus, 1):
                print(f"{i}. {status.value}")
            
            status_choice = int(input("\nSelect new status (1-4): "))
            if status_choice < 1 or status_choice > 4:
                print("❌ Invalid status choice")
                return
            
            new_status = list(HelpRequestStatus)[status_choice - 1]
            
            # Get additional info
            assigned_to = input("Assign to (press Enter to keep current): ").strip() or None
            resolution = input("Resolution notes (optional): ").strip() or None
            
            # Update the request
            success = help_request_db.update_request_status(
                selected_request.id,
                new_status,
                assigned_to,
                resolution
            )
            
            if success:
                print(f"✅ Request #{selected_request.id} updated successfully!")
            else:
                print("❌ Failed to update request")
                
        except (ValueError, IndexError) as e:
            print(f"❌ Error: {e}")
    
    async def _view_statistics(self):
        """Display help request statistics"""
        print("\n📈 HELP REQUEST STATISTICS")
        print("-" * 35)
        
        stats = help_request_db.get_statistics()
        
        if not stats:
            print("❌ No statistics available")
            return
        
        print(f"Total Requests: {stats.get('total_requests', 0)}")
        
        print("\nStatus Breakdown:")
        status_counts = stats.get('status_counts', {})
        for status, count in status_counts.items():
            print(f"  {status.title()}: {count}")
        
        print("\nPriority Breakdown:")
        priority_counts = stats.get('priority_counts', {})
        for priority, count in priority_counts.items():
            print(f"  {priority.title()}: {count}")
        
        avg_response = stats.get('avg_response_time_minutes', 0)
        print(f"\nAverage Response Time: {avg_response} minutes")
    
    async def _view_supervisor_info(self):
        """Display current supervisor information"""
        print("\n👤 SUPERVISOR INFORMATION")
        print("-" * 30)
        
        if not self.current_supervisor:
            print("❌ No supervisor logged in")
            return
        
        sup_info = supervisor_notifier.get_supervisor_info(self.current_supervisor)
        
        if not sup_info:
            print("❌ Supervisor information not found")
            return
        
        print(f"Name: {sup_info['name']}")
        print(f"Role: {sup_info['role']}")
        print(f"Phone: {sup_info['phone']}")
        print(f"Email: {sup_info['email']}")
        print(f"Availability: {sup_info['availability']}")
        print(f"Specialties: {', '.join(sup_info['specialties'])}")
        
        # Show notification history
        notifications = supervisor_notifier.get_notification_history(limit=5)
        if notifications:
            print(f"\nRecent Notifications ({len(notifications)}):")
            for notif in notifications:
                timestamp = datetime.fromisoformat(notif['timestamp'])
                print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')} - {notif['message']}")

async def main():
    """Main entry point"""
    dashboard = SupervisorDashboard()
    await dashboard.start()

if __name__ == "__main__":
    asyncio.run(main()) 