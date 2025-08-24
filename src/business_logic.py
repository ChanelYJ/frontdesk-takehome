#!/usr/bin/env python3
"""
Business Logic Module for Salon AI Agent

This module handles all salon-specific business knowledge and response generation,
separating business logic from communication and technical concerns.
"""

from typing import Dict, Any, Optional

class SalonBusinessLogic:
    """
    Handles all salon-specific business knowledge and responses.
    This class is completely independent of LiveKit or any communication layer.
    """
    
    def __init__(self):
        self.salon_info = self._load_salon_business_info()
    
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
    
    def generate_response(self, message: str) -> Optional[str]:
        """
        Generate a response based on the message content.
        Returns None if the question requires human assistance.
        """
        message_lower = message.lower()
        
        # Business hours
        if any(word in message_lower for word in ["hours", "open", "close", "time"]):
            return self._format_hours_response()
        
        # Services and pricing
        elif any(word in message_lower for word in ["service", "price", "cost", "rate", "how much"]):
            return self._format_services_response()
        
        # Address and location
        elif any(word in message_lower for word in ["address", "location", "where", "directions"]):
            return self._format_address_response()
        
        # Phone number
        elif any(word in message_lower for word in ["phone", "call", "contact", "number"]):
            return self._format_phone_response()
        
        # Staff information
        elif any(word in message_lower for word in ["stylist", "staff", "who", "employee"]):
            return self._format_staff_response()
        
        # Specialties
        elif any(word in message_lower for word in ["specialty", "special", "bridal", "wedding"]):
            return self._format_specialties_response()
        
        # General salon info
        elif any(word in message_lower for word in ["salon", "business", "about"]):
            return self._format_general_info_response()
        
        # No answer found - requires human assistance
        return None
    
    def _format_hours_response(self) -> str:
        """Format business hours response"""
        hours_text = "\n".join([f"{day.title()}: {time}" 
                               for day, time in self.salon_info["hours"].items()])
        return f"Our business hours are:\n{hours_text}"
    
    def _format_services_response(self) -> str:
        """Format services and pricing response"""
        services_text = "\n".join([f"{service.title()}: {price}" 
                                  for service, price in self.salon_info["services"].items()])
        return f"Here are our services and pricing:\n{services_text}"
    
    def _format_address_response(self) -> str:
        """Format address response"""
        return f"We're located at: {self.salon_info['address']}"
    
    def _format_phone_response(self) -> str:
        """Format phone number response"""
        return f"You can reach us at: {self.salon_info['phone']}"
    
    def _format_staff_response(self) -> str:
        """Format staff information response"""
        staff_text = "\n".join([f"{role.replace('_', ' ').title()}: {name}" 
                               for role, name in self.salon_info["staff"].items()])
        return f"Our team includes:\n{staff_text}"
    
    def _format_specialties_response(self) -> str:
        """Format specialties response"""
        specialties_text = "\n".join([f"• {specialty}" 
                                     for specialty in self.salon_info["specialties"]])
        return f"Our specialties include:\n{specialties_text}"
    
    def _format_general_info_response(self) -> str:
        """Format general salon information response"""
        return f"{self.salon_info['business_name']} is a full-service salon offering hair, nail, and spa services. We're committed to making you look and feel your best!"
    
    def get_business_info(self) -> Dict[str, Any]:
        """Get the complete business information"""
        return self.salon_info.copy()
    
    def get_business_name(self) -> str:
        """Get the business name"""
        return self.salon_info["business_name"] 