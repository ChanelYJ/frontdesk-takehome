#!/usr/bin/env python3
"""
Help Request Database Module

Handles storage and management of help requests when the AI agent
needs human assistance. Uses SQLite for simplicity and speed.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class HelpRequestStatus(Enum):
    """Status of help requests with full lifecycle support"""
    PENDING = "pending"           # Initial state, waiting for supervisor
    IN_PROGRESS = "in_progress"   # Supervisor actively working on it
    TIMEOUT = "timeout"           # Escalating to backup supervisor
    RESOLVED = "resolved"         # Successfully completed
    UNRESOLVED = "unresolved"     # Failed to resolve after all escalations

class HelpRequestPriority(Enum):
    """Priority levels for help requests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class HelpRequest:
    """Data structure for help requests"""
    id: Optional[int]
    customer_id: str
    customer_name: str
    question: str
    status: HelpRequestStatus
    priority: HelpRequestPriority
    created_at: datetime
    updated_at: datetime
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class HelpRequestDB:
    """Database manager for help requests"""
    
    def __init__(self, db_path: str = "help_requests.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create help requests table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS help_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_id TEXT NOT NULL,
                        customer_name TEXT NOT NULL,
                        question TEXT NOT NULL,
                        status TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        assigned_to TEXT,
                        resolution TEXT,
                        tags TEXT,
                        metadata TEXT,
                        timeout_at TIMESTAMP,
                        escalation_level INTEGER DEFAULT 0,
                        escalation_history TEXT
                    )
                """)
                
                # Check if new columns exist and add them if they don't
                self._migrate_schema(cursor)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_status ON help_requests(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_priority ON help_requests(priority)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at ON help_requests(created_at)
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _get_connection(self):
        """Get a database connection for external use"""
        return sqlite3.connect(self.db_path)
    
    def _migrate_schema(self, cursor):
        """Migrate existing database schema to add new columns"""
        try:
            # Check if timeout_at column exists
            cursor.execute("PRAGMA table_info(help_requests)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Add timeout_at column if it doesn't exist
            if 'timeout_at' not in columns:
                cursor.execute("ALTER TABLE help_requests ADD COLUMN timeout_at TIMESTAMP")
                logger.info("Added timeout_at column")
            
            # Add escalation_level column if it doesn't exist
            if 'escalation_level' not in columns:
                cursor.execute("ALTER TABLE help_requests ADD COLUMN escalation_level INTEGER DEFAULT 0")
                logger.info("Added escalation_level column")
            
            # Add escalation_history column if it doesn't exist
            if 'escalation_history' not in columns:
                cursor.execute("ALTER TABLE help_requests ADD COLUMN escalation_history TEXT DEFAULT '[]'")
                logger.info("Added escalation_history column")
                
        except Exception as e:
            logger.error(f"Schema migration failed: {e}")
            # Continue anyway - the table will work with existing columns
    
    def create_help_request(self, 
                          customer_id: str, 
                          customer_name: str, 
                          question: str, 
                          priority: HelpRequestPriority,
                          tags: Optional[List[str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> HelpRequest:
        """Create a new help request"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                now = datetime.now()
                
                # Calculate timeout based on priority
                timeout_minutes = self._calculate_timeout_minutes(priority)
                timeout_at = now.replace(second=0, microsecond=0)
                timeout_at = timeout_at.replace(minute=timeout_at.minute + timeout_minutes)
                
                # Insert the new request
                cursor.execute("""
                    INSERT INTO help_requests (
                        customer_id, customer_name, question, status, priority,
                        created_at, updated_at, tags, metadata, timeout_at,
                        escalation_level, escalation_history
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_id, customer_name, question, 
                    HelpRequestStatus.PENDING.value, priority.value,
                    now, now, 
                    json.dumps(tags or []), 
                    json.dumps(metadata or {}),
                    timeout_at,
                    0,  # Initial escalation level
                    "[]"  # Empty escalation history
                ))
                
                request_id = cursor.lastrowid
                conn.commit()
                
                # Create and return the HelpRequest object
                return HelpRequest(
                    id=request_id,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    question=question,
                    status=HelpRequestStatus.PENDING,
                    priority=priority,
                    created_at=now,
                    updated_at=now,
                    tags=tags or [],
                    metadata=metadata or {},
                    assigned_to=None,
                    resolution=None
                )
                
        except Exception as e:
            logger.error(f"Failed to create help request: {e}")
            raise
    
    def get_help_request(self, request_id: int) -> Optional[HelpRequest]:
        """Retrieve a help request by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM help_requests WHERE id = ?", (request_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_help_request(row)
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve help request {request_id}: {e}")
            return None
    
    def get_pending_requests(self, limit: int = 50) -> List[HelpRequest]:
        """Get all pending help requests"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM help_requests 
                    WHERE status = ? 
                    ORDER BY priority DESC, created_at ASC 
                    LIMIT ?
                """, (HelpRequestStatus.PENDING.value, limit))
                
                rows = cursor.fetchall()
                return [self._row_to_help_request(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to retrieve pending requests: {e}")
            return []
    
    def update_request_status(self, request_id: int, status: HelpRequestStatus, 
                            assigned_to: Optional[str] = None, 
                            resolution: Optional[str] = None) -> bool:
        """Update the status of a help request"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                update_fields = ["status = ?", "updated_at = ?"]
                params = [status.value, datetime.utcnow()]
                
                if assigned_to is not None:
                    update_fields.append("assigned_to = ?")
                    params.append(assigned_to)
                
                if resolution is not None:
                    update_fields.append("resolution = ?")
                    params.append(resolution)
                
                params.append(request_id)
                
                query = f"UPDATE help_requests SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, params)
                
                conn.commit()
                logger.info(f"Updated help request {request_id} status to {status.value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update help request {request_id}: {e}")
            return False
    
    def get_requests_by_customer(self, customer_id: str) -> List[HelpRequest]:
        """Get all help requests for a specific customer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM help_requests 
                    WHERE customer_id = ? 
                    ORDER BY created_at DESC
                """, (customer_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_help_request(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to retrieve requests for customer {customer_id}: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about help requests"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total requests
                cursor.execute("SELECT COUNT(*) FROM help_requests")
                total_requests = cursor.fetchone()[0]
                
                # Status breakdown
                cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM help_requests 
                    GROUP BY status
                """)
                status_counts = dict(cursor.fetchall())
                
                # Priority breakdown
                cursor.execute("""
                    SELECT priority, COUNT(*) 
                    FROM help_requests 
                    GROUP BY priority
                """)
                priority_counts = dict(cursor.fetchall())
                
                # Average response time (time from creation to resolution)
                cursor.execute("""
                    SELECT AVG(
                        (julianday(updated_at) - julianday(created_at)) * 24 * 60
                    ) 
                    FROM help_requests 
                    WHERE status = 'resolved'
                """)
                avg_response_time = cursor.fetchone()[0] or 0
                
                # Timeout statistics
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM help_requests 
                    WHERE status IN ('timeout', 'unresolved')
                """)
                timeout_count = cursor.fetchone()[0]
                
                # Escalation statistics
                cursor.execute("""
                    SELECT AVG(escalation_level) 
                    FROM help_requests 
                    WHERE escalation_level > 0
                """)
                avg_escalation_level = cursor.fetchone()[0] or 0
                
                return {
                    'total_requests': total_requests,
                    'status_counts': status_counts,
                    'priority_counts': priority_counts,
                    'avg_response_time_minutes': round(avg_response_time, 1),
                    'timeout_count': timeout_count,
                    'avg_escalation_level': round(avg_escalation_level, 1)
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def check_timeouts(self) -> List[HelpRequest]:
        """Check for requests that have timed out and need escalation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find requests that are pending and past their timeout
                cursor.execute("""
                    SELECT * FROM help_requests 
                    WHERE status = 'pending' 
                    AND timeout_at IS NOT NULL 
                    AND timeout_at < datetime('now')
                """)
                
                rows = cursor.fetchall()
                return [self._row_to_help_request(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to check timeouts: {e}")
            return []
    
    def escalate_request(self, request_id: int, escalation_level: int, 
                        assigned_to: str, reason: str) -> bool:
        """Escalate a request to the next level"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current escalation history
                cursor.execute("""
                    SELECT escalation_history FROM help_requests WHERE id = ?
                """, (request_id,))
                current_history = cursor.fetchone()[0] or "[]"
                
                # Parse and update history
                history = json.loads(current_history)
                history.append({
                    'timestamp': datetime.now().isoformat(),
                    'level': escalation_level,
                    'assigned_to': assigned_to,
                    'reason': reason
                })
                
                # Update the request
                cursor.execute("""
                    UPDATE help_requests 
                    SET status = ?, 
                        escalation_level = ?, 
                        assigned_to = ?,
                        escalation_history = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, ('timeout', escalation_level, assigned_to, 
                      json.dumps(history), request_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to escalate request {request_id}: {e}")
            return False
    
    def mark_unresolved(self, request_id: int, reason: str) -> bool:
        """Mark a request as unresolved after all escalation attempts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE help_requests 
                    SET status = ?, 
                        resolution = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, ('unresolved', f"Unresolved: {reason}", request_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to mark request {request_id} as unresolved: {e}")
            return False
    
    def _row_to_help_request(self, row: tuple) -> HelpRequest:
        """Convert database row to HelpRequest object"""
        return HelpRequest(
            id=row[0],
            customer_id=row[1],
            customer_name=row[2],
            question=row[3],
            status=HelpRequestStatus(row[4]),
            priority=HelpRequestPriority(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7]),
            assigned_to=row[8],
            resolution=row[9],
            tags=json.loads(row[10]) if row[10] else None,
            metadata=json.loads(row[11]) if row[11] else None
        )
    
    def close(self):
        """Close database connections"""
        # SQLite connections are automatically closed, but this method
        # can be used for cleanup if needed
        pass

    def _calculate_timeout_minutes(self, priority: HelpRequestPriority) -> int:
        """Calculate timeout minutes based on priority"""
        timeout_map = {
            HelpRequestPriority.URGENT: 5,    # 5 minutes for urgent
            HelpRequestPriority.HIGH: 10,     # 10 minutes for high
            HelpRequestPriority.MEDIUM: 15,   # 15 minutes for medium
            HelpRequestPriority.LOW: 30       # 30 minutes for low
        }
        return timeout_map.get(priority, 15)  # Default to 15 minutes

# Global database instance
help_request_db = HelpRequestDB() 