"""
Performance Logger - Comprehensive latency tracking for all system operations

Tracks timing for:
- LLM API calls (GPT-4.1-mini)
- TTS generation (SeolMinSeok, Typecast)
- Network operations
- Database operations
- Tool orchestration steps
- Frontend-backend communication
"""

import time
import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
import traceback

# Configure performance logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

# Create performance-specific formatter
perf_formatter = logging.Formatter(
    '%(asctime)s | PERF | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S.%f'
)

# Add console handler for performance logs
if not perf_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(perf_formatter)
    perf_logger.addHandler(console_handler)

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    operation: str
    start_time: float
    end_time: float
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    character_id: Optional[str] = None
    
    @property
    def timestamp(self) -> str:
        return datetime.fromtimestamp(self.start_time).isoformat()

@dataclass
class RequestPerformanceTracker:
    """Tracks performance for an entire request lifecycle"""
    request_id: str
    session_id: Optional[str]
    character_id: Optional[str]
    user_input: str
    start_time: float
    metrics: List[PerformanceMetric] = field(default_factory=list)
    end_time: Optional[float] = None
    
    @property
    def total_duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0
    
    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric to this request"""
        metric.session_id = self.session_id
        metric.character_id = self.character_id
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary for this request"""
        llm_metrics = [m for m in self.metrics if m.operation.startswith('llm_')]
        tts_metrics = [m for m in self.metrics if m.operation.startswith('tts_')]
        network_metrics = [m for m in self.metrics if m.operation.startswith('network_')]
        
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "character_id": self.character_id,
            "user_input": self.user_input[:50] + "..." if len(self.user_input) > 50 else self.user_input,
            "total_duration_ms": self.total_duration_ms,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat(),
            "metrics_count": len(self.metrics),
            "llm_operations": {
                "count": len(llm_metrics),
                "total_duration_ms": sum(m.duration_ms for m in llm_metrics),
                "avg_duration_ms": sum(m.duration_ms for m in llm_metrics) / len(llm_metrics) if llm_metrics else 0,
                "success_rate": sum(1 for m in llm_metrics if m.success) / len(llm_metrics) if llm_metrics else 0
            },
            "tts_operations": {
                "count": len(tts_metrics),
                "total_duration_ms": sum(m.duration_ms for m in tts_metrics),
                "avg_duration_ms": sum(m.duration_ms for m in tts_metrics) / len(tts_metrics) if tts_metrics else 0,
                "success_rate": sum(1 for m in tts_metrics if m.success) / len(tts_metrics) if tts_metrics else 0
            },
            "network_operations": {
                "count": len(network_metrics),
                "total_duration_ms": sum(m.duration_ms for m in network_metrics),
                "avg_duration_ms": sum(m.duration_ms for m in network_metrics) / len(network_metrics) if network_metrics else 0,
                "success_rate": sum(1 for m in network_metrics if m.success) / len(network_metrics) if network_metrics else 0
            },
            "breakdown": [
                {
                    "operation": m.operation,
                    "duration_ms": m.duration_ms,
                    "success": m.success,
                    "metadata": m.metadata
                }
                for m in self.metrics
            ]
        }

class PerformanceLogger:
    """Central performance logging system"""
    
    def __init__(self):
        self.active_requests: Dict[str, RequestPerformanceTracker] = {}
        self.completed_requests: List[RequestPerformanceTracker] = []
        self.max_completed_requests = 1000  # Keep last 1000 requests
    
    def start_request(self, request_id: str, session_id: Optional[str], character_id: Optional[str], user_input: str) -> RequestPerformanceTracker:
        """Start tracking a new request"""
        tracker = RequestPerformanceTracker(
            request_id=request_id,
            session_id=session_id,
            character_id=character_id,
            user_input=user_input,
            start_time=time.time()
        )
        self.active_requests[request_id] = tracker
        
        perf_logger.info(f"🚀 REQUEST_START | ID: {request_id} | Session: {session_id} | Character: {character_id} | Input: {user_input[:50]}...")
        
        return tracker
    
    def end_request(self, request_id: str):
        """End request tracking and move to completed"""
        if request_id in self.active_requests:
            tracker = self.active_requests[request_id]
            tracker.end_time = time.time()
            
            # Move to completed requests
            self.completed_requests.append(tracker)
            del self.active_requests[request_id]
            
            # Maintain max size
            if len(self.completed_requests) > self.max_completed_requests:
                self.completed_requests = self.completed_requests[-self.max_completed_requests:]
            
            # Log comprehensive summary
            summary = tracker.get_summary()
            perf_logger.info(f"✅ REQUEST_COMPLETE | ID: {request_id} | Total: {summary['total_duration_ms']:.1f}ms | LLM: {summary['llm_operations']['total_duration_ms']:.1f}ms | TTS: {summary['tts_operations']['total_duration_ms']:.1f}ms | Network: {summary['network_operations']['total_duration_ms']:.1f}ms")
            
            # Detailed breakdown
            for metric in tracker.metrics:
                status = "✅" if metric.success else "❌"
                perf_logger.info(f"  {status} {metric.operation}: {metric.duration_ms:.1f}ms {json.dumps(metric.metadata) if metric.metadata else ''}")
    
    def get_tracker(self, request_id: str) -> Optional[RequestPerformanceTracker]:
        """Get active request tracker"""
        return self.active_requests.get(request_id)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        if not self.completed_requests:
            return {"message": "No completed requests yet"}
        
        recent_requests = self.completed_requests[-100:]  # Last 100 requests
        
        # Calculate averages
        total_durations = [r.total_duration_ms for r in recent_requests]
        llm_durations = []
        tts_durations = []
        network_durations = []
        
        for request in recent_requests:
            llm_ops = [m for m in request.metrics if m.operation.startswith('llm_')]
            tts_ops = [m for m in request.metrics if m.operation.startswith('tts_')]
            network_ops = [m for m in request.metrics if m.operation.startswith('network_')]
            
            if llm_ops:
                llm_durations.extend([m.duration_ms for m in llm_ops])
            if tts_ops:
                tts_durations.extend([m.duration_ms for m in tts_ops])
            if network_ops:
                network_durations.extend([m.duration_ms for m in network_ops])
        
        return {
            "total_requests_tracked": len(self.completed_requests),
            "recent_requests_analyzed": len(recent_requests),
            "active_requests": len(self.active_requests),
            "avg_total_duration_ms": sum(total_durations) / len(total_durations) if total_durations else 0,
            "avg_llm_duration_ms": sum(llm_durations) / len(llm_durations) if llm_durations else 0,
            "avg_tts_duration_ms": sum(tts_durations) / len(tts_durations) if tts_durations else 0,
            "avg_network_duration_ms": sum(network_durations) / len(network_durations) if network_durations else 0,
            "llm_operations_count": len(llm_durations),
            "tts_operations_count": len(tts_durations),
            "network_operations_count": len(network_durations),
            "timestamp": datetime.now().isoformat()
        }

# Global performance logger instance
performance_logger = PerformanceLogger()

@asynccontextmanager
async def track_async_operation(operation_name: str, request_id: Optional[str] = None, **metadata):
    """Context manager for tracking async operations"""
    start_time = time.time()
    success = True
    error_message = None
    
    perf_logger.info(f"⏳ {operation_name.upper()}_START | Request: {request_id} | Metadata: {json.dumps(metadata) if metadata else '{}'}")
    
    try:
        yield
    except Exception as e:
        success = False
        error_message = str(e)
        perf_logger.error(f"❌ {operation_name.upper()}_ERROR | Request: {request_id} | Error: {error_message}")
        raise
    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        status = "✅" if success else "❌"
        perf_logger.info(f"{status} {operation_name.upper()}_COMPLETE | Duration: {duration_ms:.1f}ms | Request: {request_id}")
        
        # Add to request tracker if available
        if request_id:
            tracker = performance_logger.get_tracker(request_id)
            if tracker:
                metric = PerformanceMetric(
                    operation=operation_name,
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_message,
                    metadata=metadata
                )
                tracker.add_metric(metric)

def track_sync_operation(operation_name: str, request_id: Optional[str] = None, **metadata):
    """Decorator for tracking synchronous operations"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None
            
            perf_logger.info(f"⏳ {operation_name.upper()}_START | Request: {request_id} | Metadata: {json.dumps(metadata) if metadata else '{}'}")
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                perf_logger.error(f"❌ {operation_name.upper()}_ERROR | Request: {request_id} | Error: {error_message}")
                raise
            finally:
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                status = "✅" if success else "❌"
                perf_logger.info(f"{status} {operation_name.upper()}_COMPLETE | Duration: {duration_ms:.1f}ms | Request: {request_id}")
                
                # Add to request tracker if available
                if request_id:
                    tracker = performance_logger.get_tracker(request_id)
                    if tracker:
                        metric = PerformanceMetric(
                            operation=operation_name,
                            start_time=start_time,
                            end_time=end_time,
                            duration_ms=duration_ms,
                            success=success,
                            error_message=error_message,
                            metadata=metadata
                        )
                        tracker.add_metric(metric)
        
        return wrapper
    return decorator

def track_async_operation_decorator(operation_name: str, request_id_param: str = None, **metadata):
    """Decorator for tracking async operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request_id from parameters if specified
            req_id = None
            if request_id_param:
                # Try to get request_id from kwargs first
                req_id = kwargs.get(request_id_param)
                # If not found, try to get from args based on function signature
                if not req_id and hasattr(func, '__code__'):
                    param_names = func.__code__.co_varnames[:func.__code__.co_argcount]
                    if request_id_param in param_names:
                        param_index = param_names.index(request_id_param)
                        if param_index < len(args):
                            req_id = args[param_index]
            
            async with track_async_operation(operation_name, req_id, **metadata):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Convenience functions for common operations
async def track_llm_call(request_id: str, model: str, prompt_length: int, response_length: int = 0):
    """Track LLM API call performance"""
    async with track_async_operation(
        "llm_api_call", 
        request_id, 
        model=model, 
        prompt_length=prompt_length, 
        response_length=response_length
    ):
        yield

async def track_tts_generation(request_id: str, service: str, text_length: int, character_id: str = None):
    """Track TTS generation performance"""
    async with track_async_operation(
        "tts_generation", 
        request_id, 
        service=service, 
        text_length=text_length, 
        character_id=character_id
    ):
        yield

async def track_network_request(request_id: str, endpoint: str, method: str = "POST"):
    """Track external network request performance"""
    async with track_async_operation(
        "network_request", 
        request_id, 
        endpoint=endpoint, 
        method=method
    ):
        yield

@contextmanager
def track_sync_network_request(request_id: str, endpoint: str, method: str = "POST"):
    """Track external network request performance (synchronous version)"""
    start_time = time.time()
    success = True
    error_message = None
    
    metadata = {"endpoint": endpoint, "method": method}
    perf_logger.info(f"⏳ NETWORK_REQUEST_START | Request: {request_id} | Metadata: {json.dumps(metadata)}")
    
    try:
        yield
    except Exception as e:
        success = False
        error_message = str(e)
        perf_logger.error(f"❌ NETWORK_REQUEST_ERROR | Request: {request_id} | Error: {error_message}")
        raise
    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        status = "✅" if success else "❌"
        perf_logger.info(f"{status} NETWORK_REQUEST_COMPLETE | Duration: {duration_ms:.1f}ms | Request: {request_id}")
        
        # Add to request tracker if available
        if request_id:
            tracker = performance_logger.get_tracker(request_id)
            if tracker:
                metric = PerformanceMetric(
                    operation="network_request",
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_message,
                    metadata=metadata
                )
                tracker.add_metric(metric)

async def track_database_operation(request_id: str, operation: str, collection: str = None):
    """Track database operation performance"""
    async with track_async_operation(
        "database_operation", 
        request_id, 
        operation=operation, 
        collection=collection
    ):
        yield

def get_request_id_from_context() -> Optional[str]:
    """Extract request ID from current context (if available)"""
    # This would need to be implemented based on your context management
    # For now, return None - can be enhanced with context variables
    return None

# Export main components
__all__ = [
    'performance_logger',
    'track_async_operation',
    'track_sync_operation',
    'track_async_operation_decorator',
    'track_llm_call',
    'track_tts_generation',
    'track_network_request',
    'track_sync_network_request',
    'track_database_operation',
    'PerformanceMetric',
    'RequestPerformanceTracker',
    'PerformanceLogger'
]
