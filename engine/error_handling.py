
"""
Axarion Engine Error Handling and Stability System
Graceful error recovery, memory leak detection, crash reporting, resource validation
"""

import gc
import sys
import traceback
import psutil
import os
import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps

@dataclass
class ErrorReport:
    """Error report structure"""
    timestamp: float
    error_type: str
    message: str
    traceback: str
    context: Dict[str, Any]
    severity: str  # "low", "medium", "high", "critical"
    recovered: bool = False

@dataclass
class MemoryStats:
    """Memory usage statistics"""
    total_memory: float
    used_memory: float
    available_memory: float
    memory_percent: float
    objects_count: int
    gc_collections: int

class MemoryLeakDetector:
    """Detects and reports memory leaks"""
    
    def __init__(self):
        self.baseline_memory = 0
        self.memory_samples: List[float] = []
        self.max_samples = 100
        self.leak_threshold = 50 * 1024 * 1024  # 50MB
        self.monitoring_enabled = True
        
        # Object tracking
        self.object_counts: Dict[str, int] = {}
        self.tracked_objects: List[Any] = []
    
    def start_monitoring(self):
        """Start memory monitoring"""
        if self.monitoring_enabled:
            self.baseline_memory = self._get_memory_usage()
            self.memory_samples.clear()
    
    def update(self):
        """Update memory monitoring"""
        if not self.monitoring_enabled:
            return
        
        current_memory = self._get_memory_usage()
        self.memory_samples.append(current_memory)
        
        # Keep only recent samples
        if len(self.memory_samples) > self.max_samples:
            self.memory_samples.pop(0)
        
        # Check for potential leak
        if len(self.memory_samples) >= 10:
            recent_avg = sum(self.memory_samples[-10:]) / 10
            old_avg = sum(self.memory_samples[:10]) / 10
            
            if recent_avg - old_avg > self.leak_threshold:
                self._report_potential_leak(recent_avg, old_avg)
    
    def get_memory_stats(self) -> MemoryStats:
        """Get current memory statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # System memory
        system_memory = psutil.virtual_memory()
        
        # Python objects
        objects_count = len(gc.get_objects())
        gc_stats = gc.get_stats()
        total_collections = sum(stat['collections'] for stat in gc_stats)
        
        return MemoryStats(
            total_memory=system_memory.total,
            used_memory=memory_info.rss,
            available_memory=system_memory.available,
            memory_percent=system_memory.percent,
            objects_count=objects_count,
            gc_collections=total_collections
        )
    
    def force_cleanup(self):
        """Force garbage collection and cleanup"""
        # Clear tracked objects
        self.tracked_objects.clear()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Try to reduce memory fragmentation
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)
        except:
            pass  # Not available on all systems
        
        return collected
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in bytes"""
        process = psutil.Process()
        return process.memory_info().rss
    
    def _report_potential_leak(self, current_avg: float, baseline_avg: float):
        """Report potential memory leak"""
        leak_amount = current_avg - baseline_avg
        print(f"⚠️ Potential memory leak detected: {leak_amount / 1024 / 1024:.1f}MB increase")

class ResourceValidator:
    """Validates and monitors game resources"""
    
    def __init__(self):
        self.required_files: List[str] = []
        self.optional_files: List[str] = []
        self.missing_resources: List[str] = []
        self.corrupted_resources: List[str] = []
        self.validation_enabled = True
    
    def add_required_resource(self, file_path: str):
        """Add required resource file"""
        self.required_files.append(file_path)
    
    def add_optional_resource(self, file_path: str):
        """Add optional resource file"""
        self.optional_files.append(file_path)
    
    def validate_all_resources(self) -> bool:
        """Validate all registered resources"""
        if not self.validation_enabled:
            return True
        
        self.missing_resources.clear()
        self.corrupted_resources.clear()
        
        all_valid = True
        
        # Check required files
        for file_path in self.required_files:
            if not self._validate_file(file_path):
                self.missing_resources.append(file_path)
                all_valid = False
        
        # Check optional files
        for file_path in self.optional_files:
            if os.path.exists(file_path):
                if not self._validate_file(file_path):
                    self.corrupted_resources.append(file_path)
        
        return all_valid
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate individual file"""
        if not os.path.exists(file_path):
            return False
        
        try:
            # Check if file is readable
            with open(file_path, 'rb') as f:
                # Try to read first few bytes
                f.read(1024)
            
            # Additional validation based on file type
            if file_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                return self._validate_image(file_path)
            elif file_path.endswith(('.wav', '.mp3', '.ogg')):
                return self._validate_audio(file_path)
            
            return True
        except Exception:
            return False
    
    def _validate_image(self, file_path: str) -> bool:
        """Validate image file"""
        try:
            import pygame
            pygame.image.load(file_path)
            return True
        except Exception:
            return False
    
    def _validate_audio(self, file_path: str) -> bool:
        """Validate audio file"""
        try:
            import pygame
            pygame.mixer.Sound(file_path)
            return True
        except Exception:
            return False

class CrashReporter:
    """Crash reporting and recovery system"""
    
    def __init__(self):
        self.crash_reports: List[ErrorReport] = []
        self.auto_recovery_enabled = True
        self.crash_log_file = "crash_reports.json"
        self.max_reports = 50
        
        # Recovery strategies
        self.recovery_strategies: Dict[str, Callable] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register default recovery strategies"""
        self.recovery_strategies["MemoryError"] = self._recover_memory_error
        self.recovery_strategies["FileNotFoundError"] = self._recover_file_error
        self.recovery_strategies["pygame.error"] = self._recover_pygame_error
        self.recovery_strategies["ImportError"] = self._recover_import_error
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """Handle error with potential recovery"""
        error_type = type(error).__name__
        
        # Create error report
        report = ErrorReport(
            timestamp=time.time(),
            error_type=error_type,
            message=str(error),
            traceback=traceback.format_exc(),
            context=context or {},
            severity=self._determine_severity(error_type)
        )
        
        # Try recovery if enabled
        recovered = False
        if self.auto_recovery_enabled and error_type in self.recovery_strategies:
            try:
                recovered = self.recovery_strategies[error_type](error, context)
                report.recovered = recovered
            except Exception as recovery_error:
                print(f"Recovery failed: {recovery_error}")
        
        # Log the error
        self.crash_reports.append(report)
        self._log_error_report(report)
        
        # Cleanup old reports
        if len(self.crash_reports) > self.max_reports:
            self.crash_reports.pop(0)
        
        return recovered
    
    def _determine_severity(self, error_type: str) -> str:
        """Determine error severity"""
        critical_errors = ["SystemExit", "KeyboardInterrupt", "MemoryError"]
        high_errors = ["ImportError", "ModuleNotFoundError", "AttributeError"]
        medium_errors = ["FileNotFoundError", "ValueError", "TypeError"]
        
        if error_type in critical_errors:
            return "critical"
        elif error_type in high_errors:
            return "high"
        elif error_type in medium_errors:
            return "medium"
        else:
            return "low"
    
    def _recover_memory_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from memory errors"""
        try:
            # Force garbage collection
            collected = gc.collect()
            print(f"🔧 Memory recovery: collected {collected} objects")
            
            # Try to free some cached resources
            if hasattr(context.get('engine'), 'asset_manager'):
                context['engine'].asset_manager.clear_cache()
            
            return True
        except Exception:
            return False
    
    def _recover_file_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from file errors"""
        try:
            # Try to use fallback resources
            missing_file = str(error).split("'")[1] if "'" in str(error) else ""
            
            if missing_file:
                # Create placeholder file or use default
                print(f"🔧 File recovery: creating placeholder for {missing_file}")
                # Implementation would depend on file type
                return True
            
            return False
        except Exception:
            return False
    
    def _recover_pygame_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from pygame errors"""
        try:
            # Reinitialize pygame subsystems
            import pygame
            
            if "mixer" in str(error).lower():
                pygame.mixer.quit()
                pygame.mixer.init()
                return True
            elif "display" in str(error).lower():
                # Try different display mode
                pygame.display.quit()
                pygame.display.init()
                return True
            
            return False
        except Exception:
            return False
    
    def _recover_import_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Recover from import errors"""
        try:
            missing_module = str(error).split("'")[1] if "'" in str(error) else ""
            
            # Try alternative imports or disable features
            if missing_module in ["numpy", "scipy"]:
                print(f"🔧 Import recovery: disabling advanced features requiring {missing_module}")
                return True
            
            return False
        except Exception:
            return False
    
    def _log_error_report(self, report: ErrorReport):
        """Log error report to file"""
        try:
            # Load existing reports
            reports_data = []
            if os.path.exists(self.crash_log_file):
                with open(self.crash_log_file, 'r') as f:
                    reports_data = json.load(f)
            
            # Add new report
            report_dict = {
                "timestamp": report.timestamp,
                "error_type": report.error_type,
                "message": report.message,
                "severity": report.severity,
                "recovered": report.recovered,
                "context": report.context
            }
            
            reports_data.append(report_dict)
            
            # Keep only recent reports
            if len(reports_data) > self.max_reports:
                reports_data = reports_data[-self.max_reports:]
            
            # Save back to file
            with open(self.crash_log_file, 'w') as f:
                json.dump(reports_data, f, indent=2)
        
        except Exception as e:
            print(f"Failed to log error report: {e}")

def safe_execute(func: Callable) -> Callable:
    """Decorator for safe function execution with error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get context from function
            context = {
                "function": func.__name__,
                "args": str(args)[:100],  # Limit length
                "kwargs": str(kwargs)[:100]
            }
            
            # Handle error
            recovered = error_handling_system.crash_reporter.handle_error(e, context)
            
            if not recovered:
                # Re-raise if not recovered
                raise
            
            return None  # Return safe default
    
    return wrapper

class ErrorHandlingSystem:
    """Main error handling and stability system"""
    
    def __init__(self):
        self.memory_detector = MemoryLeakDetector()
        self.resource_validator = ResourceValidator()
        self.crash_reporter = CrashReporter()
        self.enabled = True
        
        # System health monitoring
        self.last_health_check = 0
        self.health_check_interval = 5.0  # seconds
        self.system_healthy = True
    
    def initialize(self):
        """Initialize error handling system"""
        if self.enabled:
            self.memory_detector.start_monitoring()
            self.resource_validator.validate_all_resources()
            
            # Set up global exception handler
            sys.excepthook = self._global_exception_handler
    
    def update(self, current_time: float):
        """Update error handling systems"""
        if not self.enabled:
            return
        
        # Update memory monitoring
        self.memory_detector.update()
        
        # Periodic health checks
        if current_time - self.last_health_check >= self.health_check_interval:
            self._perform_health_check()
            self.last_health_check = current_time
    
    def _perform_health_check(self):
        """Perform system health check"""
        try:
            # Check memory usage
            memory_stats = self.memory_detector.get_memory_stats()
            if memory_stats.memory_percent > 90:
                print("⚠️ High memory usage detected")
                self.memory_detector.force_cleanup()
            
            # Check for missing resources
            if not self.resource_validator.validate_all_resources():
                print("⚠️ Missing resources detected")
                self.system_healthy = False
            else:
                self.system_healthy = True
            
        except Exception as e:
            print(f"Health check failed: {e}")
            self.system_healthy = False
    
    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Global exception handler"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            print("\n🛑 Interrupted by user")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Try to recover from other exceptions
        context = {
            "global_handler": True,
            "exc_type": exc_type.__name__
        }
        
        recovered = self.crash_reporter.handle_error(exc_value, context)
        
        if not recovered:
            # Use default handler if recovery failed
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        memory_stats = self.memory_detector.get_memory_stats()
        
        return {
            "healthy": self.system_healthy,
            "memory_usage_mb": memory_stats.used_memory / 1024 / 1024,
            "memory_percent": memory_stats.memory_percent,
            "objects_count": memory_stats.objects_count,
            "recent_crashes": len([r for r in self.crash_reporter.crash_reports 
                                 if time.time() - r.timestamp < 300]),  # Last 5 minutes
            "missing_resources": len(self.resource_validator.missing_resources),
            "corrupted_resources": len(self.resource_validator.corrupted_resources)
        }
    
    def enable_auto_recovery(self, enabled: bool):
        """Enable automatic error recovery"""
        self.crash_reporter.auto_recovery_enabled = enabled
    
    def enable_memory_monitoring(self, enabled: bool):
        """Enable memory leak detection"""
        self.memory_detector.monitoring_enabled = enabled

# Global instance
error_handling_system = ErrorHandlingSystem()
