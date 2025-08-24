#!/usr/bin/env python3
"""
Timeout Handler Service for Help Request Lifecycle Management

This service handles request timeouts, escalations, and lifecycle transitions
to ensure no customer request is left hanging.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from help_request_db import help_request_db, HelpRequest, HelpRequestStatus
from supervisor_notifier import supervisor_notifier

logger = logging.getLogger(__name__)

class TimeoutHandler:
    """
    Manages help request timeouts and escalations.
    Implements the full request lifecycle: PENDING → TIMEOUT → UNRESOLVED
    """
    
    def __init__(self):
        self.db = help_request_db
        self.notifier = supervisor_notifier
        self.escalation_config = self._load_escalation_config()
    
    def _load_escalation_config(self) -> Dict[str, Any]:
        """Load escalation configuration for different priority levels"""
        return {
            'urgent': {
                'timeout_minutes': 5,
                'escalation_levels': 3,
                'escalation_windows': [2, 3, 5]  # Minutes between escalations
            },
            'high': {
                'timeout_minutes': 10,
                'escalation_levels': 3,
                'escalation_windows': [5, 7, 10]
            },
            'medium': {
                'timeout_minutes': 15,
                'escalation_levels': 2,
                'escalation_windows': [10, 15]
            },
            'low': {
                'timeout_minutes': 30,
                'escalation_levels': 2,
                'escalation_windows': [20, 30]
            }
        }
    
    async def process_timeouts(self) -> List[Dict[str, Any]]:
        """
        Process all timed-out requests and handle escalations.
        Returns list of actions taken.
        """
        actions = []
        
        try:
            # Check for timed-out requests
            timed_out_requests = self.db.check_timeouts()
            
            for request in timed_out_requests:
                action = await self._handle_timeout(request)
                if action:
                    actions.append(action)
            
            # Check for requests that need final escalation
            await self._check_final_escalations()
            
        except Exception as e:
            logger.error(f"Error processing timeouts: {e}")
        
        return actions
    
    async def _handle_timeout(self, request: HelpRequest) -> Dict[str, Any]:
        """Handle a single timed-out request"""
        try:
            current_level = getattr(request, 'escalation_level', 0)
            priority_key = request.priority.value.lower()
            
            if priority_key not in self.escalation_config:
                priority_key = 'medium'  # Default fallback
            
            config = self.escalation_config[priority_key]
            max_levels = config['escalation_levels']
            
            if current_level >= max_levels:
                # Final escalation - mark as unresolved
                return await self._mark_final_unresolved(request)
            
            # Escalate to next level
            next_level = current_level + 1
            backup_supervisor = self._get_backup_supervisor(request, next_level)
            
            if backup_supervisor:
                # Escalate to backup supervisor
                success = self.db.escalate_request(
                    request.id, 
                    next_level, 
                    backup_supervisor['name'],
                    f"Escalated from level {current_level} to {next_level}"
                )
                
                if success:
                    # Notify backup supervisor
                    try:
                        await self.notifier.notify_supervisor(request, backup_supervisor)
                    except Exception as e:
                        logger.warning(f"Failed to notify supervisor during escalation: {e}")
                    
                    return {
                        'action': 'escalated',
                        'request_id': request.id,
                        'level': next_level,
                        'supervisor': backup_supervisor['name'],
                        'reason': f"Escalated to level {next_level}"
                    }
            
            # No backup supervisor available - mark as unresolved
            return await self._mark_final_unresolved(request)
            
        except Exception as e:
            logger.error(f"Error handling timeout for request {request.id}: {e}")
            return None
    
    async def _mark_final_unresolved(self, request: HelpRequest) -> Dict[str, Any]:
        """Mark a request as finally unresolved after all escalation attempts"""
        try:
            reason = f"All {getattr(request, 'escalation_level', 0)} escalation levels exhausted"
            success = self.db.mark_unresolved(request.id, reason)
            
            if success:
                return {
                    'action': 'unresolved',
                    'request_id': request.id,
                    'reason': reason,
                    'final_status': 'unresolved'
                }
            
        except Exception as e:
            logger.error(f"Error marking request {request.id} as unresolved: {e}")
        
        return None
    
    def _get_backup_supervisor(self, request: HelpRequest, level: int) -> Dict[str, Any]:
        """Get backup supervisor for escalation level"""
        # This is a simplified version - in production you'd have more sophisticated logic
        supervisors = supervisor_notifier.get_all_supervisors()
        
        # Simple round-robin escalation
        supervisor_list = list(supervisors.values())
        if not supervisor_list:
            return None
        
        # Skip the currently assigned supervisor
        current_supervisor = getattr(request, 'assigned_to', None)
        available_supervisors = [
            s for s in supervisor_list 
            if s['name'] != current_supervisor
        ]
        
        if not available_supervisors:
            available_supervisors = supervisor_list
        
        # Select supervisor based on level and availability
        selected_index = (level - 1) % len(available_supervisors)
        return available_supervisors[selected_index]
    
    async def _check_final_escalations(self):
        """Check for requests that have been in timeout too long and need final resolution"""
        try:
            # This would check for requests that have been in TIMEOUT state
            # for too long and need to be marked as UNRESOLVED
            # Implementation depends on your specific timeout rules
            pass
            
        except Exception as e:
            logger.error(f"Error checking final escalations: {e}")
    
    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """Get statistics about request lifecycle and timeouts"""
        try:
            stats = self.db.get_statistics()
            
            # Add lifecycle-specific metrics
            lifecycle_stats = {
                'total_requests': stats.get('total_requests', 0),
                'pending_requests': stats.get('status_counts', {}).get('pending', 0),
                'timeout_requests': stats.get('status_counts', {}).get('timeout', 0),
                'unresolved_requests': stats.get('status_counts', {}).get('unresolved', 0),
                'resolved_requests': stats.get('status_counts', {}).get('resolved', 0),
                'timeout_count': stats.get('timeout_count', 0),
                'avg_escalation_level': stats.get('avg_escalation_level', 0),
                'escalation_success_rate': self._calculate_escalation_success_rate()
            }
            
            return lifecycle_stats
            
        except Exception as e:
            logger.error(f"Error getting lifecycle stats: {e}")
            return {}
    
    def _calculate_escalation_success_rate(self) -> float:
        """Calculate the success rate of escalations"""
        try:
            stats = self.db.get_statistics()
            total_timeouts = stats.get('timeout_count', 0)
            total_unresolved = stats.get('status_counts', {}).get('unresolved', 0)
            
            if total_timeouts == 0:
                return 100.0
            
            success_rate = ((total_timeouts - total_unresolved) / total_timeouts) * 100
            return round(success_rate, 1)
            
        except Exception as e:
            logger.error(f"Error calculating escalation success rate: {e}")
            return 0.0

# Global timeout handler instance
timeout_handler = TimeoutHandler() 