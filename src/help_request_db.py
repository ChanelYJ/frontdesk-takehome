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
    """Status of help requests"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

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
                        metadata TEXT
                    )
                """)
                
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
    
    def create_help_request(self, 
                          customer_id: str, 
                          customer_name: str, 
                          question: str,
                          priority: HelpRequestPriority = HelpRequestPriority.MEDIUM,
                          tags: Optional[List[str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> HelpRequest:
        """Create a new help request"""
        try:
            now = datetime.utcnow()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO help_requests 
                    (customer_id, customer_name, question, status, priority, created_at, updated_at, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    customer_id,
                    customer_name,
                    question,
                    HelpRequestStatus.PENDING.value,
                    priority.value,
                    now,
                    now,
                    json.dumps(tags) if tags else None,
                    json.dumps(metadata) if metadata else None
                ))
                
                request_id = cursor.lastrowid
                conn.commit()
                
                help_request = HelpRequest(
                    id=request_id,
                    customer_id=customer_id,
                    customer_name=customer_name,
                    question=question,
                    status=HelpRequestStatus.PENDING,
                    priority=priority,
                    created_at=now,
                    updated_at=now,
                    tags=tags,
                    metadata=metadata
                )
                
                logger.info(f"Created help request {request_id} for customer {customer_id}")
                return help_request
                
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
        """Get statistics about help requests"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total requests
                cursor.execute("SELECT COUNT(*) FROM help_requests")
                total = cursor.fetchone()[0]
                
                # Requests by status
                cursor.execute("""
                    SELECT status, COUNT(*) FROM help_requests 
                    GROUP BY status
                """)
                status_counts = dict(cursor.fetchall())
                
                # Requests by priority
                cursor.execute("""
                    SELECT priority, COUNT(*) FROM help_requests 
                    GROUP BY priority
                """)
                priority_counts = dict(cursor.fetchall())
                
                # Average response time (for resolved requests)
                cursor.execute("""
                    SELECT AVG(JULIANDAY(updated_at) - JULIANDAY(created_at)) * 24 * 60
                    FROM help_requests 
                    WHERE status = ? AND assigned_to IS NOT NULL
                """, (HelpRequestStatus.RESOLVED.value,))
                
                avg_response_time = cursor.fetchone()[0] or 0
                
                return {
                    "total_requests": total,
                    "status_counts": status_counts,
                    "priority_counts": priority_counts,
                    "avg_response_time_minutes": round(avg_response_time, 2)
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
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

# Global database instance
help_request_db = HelpRequestDB() 