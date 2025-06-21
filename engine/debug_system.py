
"""
Axarion Engine Debug System
Provides debugging capabilities for AXScript
"""

import traceback
from typing import Dict, List, Set, Any, Optional, Callable
from dataclasses import dataclass

@dataclass
class Breakpoint:
    file_path: str
    line_number: int
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0

@dataclass
class DebugFrame:
    function_name: str
    file_path: str
    line_number: int
    variables: Dict[str, Any]
    
class DebugSession:
    """Debug session for script execution"""
    
    def __init__(self):
        self.breakpoints: Dict[str, Breakpoint] = {}  # id -> breakpoint
        self.call_stack: List[DebugFrame] = []
        self.current_frame = 0
        self.is_paused = False
        self.step_mode = None  # None, 'into', 'over', 'out'
        self.step_target_depth = 0
        
        # Debug output
        self.debug_output: List[str] = []
        self.watch_expressions: Dict[str, str] = {}
        self.watch_values: Dict[str, Any] = {}
        
        # Callbacks
        self.on_break: Optional[Callable] = None
        self.on_step: Optional[Callable] = None
        self.on_exception: Optional[Callable] = None

class DebugSystem:
    """Debug system for AXScript execution"""
    
    def __init__(self):
        self.sessions: Dict[str, DebugSession] = {}
        self.active_session: Optional[str] = None
        self.enabled = True
        
        # Global breakpoints
        self.global_breakpoints: Dict[str, Breakpoint] = {}
        self.breakpoint_counter = 0
        
        # Exception handling
        self.break_on_exceptions = True
        self.caught_exceptions: List[Dict] = []
    
    def create_session(self, session_id: str) -> DebugSession:
        """Create new debug session"""
        session = DebugSession()
        self.sessions[session_id] = session
        return session
    
    def set_active_session(self, session_id: str):
        """Set active debug session"""
        if session_id in self.sessions:
            self.active_session = session_id
    
    def get_session(self, session_id: Optional[str] = None) -> Optional[DebugSession]:
        """Get debug session"""
        if session_id:
            return self.sessions.get(session_id)
        elif self.active_session:
            return self.sessions.get(self.active_session)
        return None
    
    def add_breakpoint(self, file_path: str, line_number: int, 
                      condition: Optional[str] = None) -> str:
        """Add breakpoint"""
        self.breakpoint_counter += 1
        bp_id = f"bp_{self.breakpoint_counter}"
        
        breakpoint = Breakpoint(
            file_path=file_path,
            line_number=line_number,
            condition=condition
        )
        
        self.global_breakpoints[bp_id] = breakpoint
        return bp_id
    
    def remove_breakpoint(self, bp_id: str) -> bool:
        """Remove breakpoint"""
        if bp_id in self.global_breakpoints:
            del self.global_breakpoints[bp_id]
            return True
        return False
    
    def toggle_breakpoint(self, bp_id: str) -> bool:
        """Toggle breakpoint enabled state"""
        if bp_id in self.global_breakpoints:
            self.global_breakpoints[bp_id].enabled = not self.global_breakpoints[bp_id].enabled
            return True
        return False
    
    def should_break(self, file_path: str, line_number: int, 
                    variables: Dict[str, Any]) -> bool:
        """Check if execution should break at this point"""
        if not self.enabled:
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        # Check breakpoints
        for bp in self.global_breakpoints.values():
            if (bp.enabled and 
                bp.file_path == file_path and 
                bp.line_number == line_number):
                
                # Check condition if specified
                if bp.condition:
                    try:
                        # Simple condition evaluation
                        if not self._evaluate_condition(bp.condition, variables):
                            continue
                    except:
                        pass  # Break anyway if condition evaluation fails
                
                bp.hit_count += 1
                return True
        
        # Check step mode
        if session.step_mode:
            current_depth = len(session.call_stack)
            
            if session.step_mode == 'into':
                return True
            elif session.step_mode == 'over':
                return current_depth <= session.step_target_depth
            elif session.step_mode == 'out':
                return current_depth < session.step_target_depth
        
        return False
    
    def break_execution(self, file_path: str, line_number: int, 
                       function_name: str, variables: Dict[str, Any]):
        """Break execution at current point"""
        session = self.get_session()
        if not session:
            return
        
        # Create debug frame
        frame = DebugFrame(
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            variables=variables.copy()
        )
        
        # Update call stack
        session.call_stack = [frame]  # Simplified for now
        session.current_frame = 0
        session.is_paused = True
        session.step_mode = None
        
        # Update watch expressions
        self._update_watch_values(session, variables)
        
        # Trigger callback
        if session.on_break:
            session.on_break(session)
        
        print(f"🛑 Breakpoint hit: {file_path}:{line_number} in {function_name}")
    
    def step_into(self, session_id: Optional[str] = None):
        """Step into next line"""
        session = self.get_session(session_id)
        if session and session.is_paused:
            session.step_mode = 'into'
            session.step_target_depth = len(session.call_stack)
            session.is_paused = False
    
    def step_over(self, session_id: Optional[str] = None):
        """Step over next line"""
        session = self.get_session(session_id)
        if session and session.is_paused:
            session.step_mode = 'over'
            session.step_target_depth = len(session.call_stack)
            session.is_paused = False
    
    def step_out(self, session_id: Optional[str] = None):
        """Step out of current function"""
        session = self.get_session(session_id)
        if session and session.is_paused:
            session.step_mode = 'out'
            session.step_target_depth = len(session.call_stack)
            session.is_paused = False
    
    def continue_execution(self, session_id: Optional[str] = None):
        """Continue execution"""
        session = self.get_session(session_id)
        if session and session.is_paused:
            session.step_mode = None
            session.is_paused = False
    
    def add_watch(self, expression: str, session_id: Optional[str] = None) -> str:
        """Add watch expression"""
        session = self.get_session(session_id)
        if session:
            watch_id = f"watch_{len(session.watch_expressions)}"
            session.watch_expressions[watch_id] = expression
            return watch_id
        return ""
    
    def remove_watch(self, watch_id: str, session_id: Optional[str] = None):
        """Remove watch expression"""
        session = self.get_session(session_id)
        if session and watch_id in session.watch_expressions:
            del session.watch_expressions[watch_id]
            if watch_id in session.watch_values:
                del session.watch_values[watch_id]
    
    def get_variable_value(self, var_name: str, frame_index: int = 0,
                          session_id: Optional[str] = None) -> Any:
        """Get variable value from specific frame"""
        session = self.get_session(session_id)
        if (session and frame_index < len(session.call_stack)):
            frame = session.call_stack[frame_index]
            return frame.variables.get(var_name)
        return None
    
    def get_call_stack(self, session_id: Optional[str] = None) -> List[DebugFrame]:
        """Get current call stack"""
        session = self.get_session(session_id)
        if session:
            return session.call_stack.copy()
        return []
    
    def handle_exception(self, exception: Exception, file_path: str, 
                        line_number: int, function_name: str):
        """Handle exception during script execution"""
        if self.break_on_exceptions:
            exception_info = {
                "type": type(exception).__name__,
                "message": str(exception),
                "file_path": file_path,
                "line_number": line_number,
                "function_name": function_name,
                "traceback": traceback.format_exc()
            }
            
            self.caught_exceptions.append(exception_info)
            
            # Break execution
            session = self.get_session()
            if session and session.on_exception:
                session.on_exception(exception_info)
            
            print(f"💥 Exception in {file_path}:{line_number}: {exception}")
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate breakpoint condition"""
        try:
            # Simple variable substitution
            for var_name, value in variables.items():
                condition = condition.replace(var_name, str(value))
            
            # Basic evaluation (could be expanded)
            return eval(condition)
        except:
            return True  # Break on evaluation error
    
    def _update_watch_values(self, session: DebugSession, variables: Dict[str, Any]):
        """Update watch expression values"""
        for watch_id, expression in session.watch_expressions.items():
            try:
                # Simple evaluation
                session.watch_values[watch_id] = self._evaluate_expression(expression, variables)
            except Exception as e:
                session.watch_values[watch_id] = f"Error: {str(e)}"
    
    def _evaluate_expression(self, expression: str, variables: Dict[str, Any]) -> Any:
        """Evaluate watch expression"""
        # Simple variable substitution
        for var_name, value in variables.items():
            if var_name in expression:
                expression = expression.replace(var_name, repr(value))
        
        return eval(expression)
    
    def get_debug_info(self, session_id: Optional[str] = None) -> Dict:
        """Get current debug information"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "is_paused": session.is_paused,
            "call_stack": [
                {
                    "function": frame.function_name,
                    "file": frame.file_path,
                    "line": frame.line_number,
                    "variables": frame.variables
                }
                for frame in session.call_stack
            ],
            "breakpoints": [
                {
                    "id": bp_id,
                    "file": bp.file_path,
                    "line": bp.line_number,
                    "condition": bp.condition,
                    "enabled": bp.enabled,
                    "hit_count": bp.hit_count
                }
                for bp_id, bp in self.global_breakpoints.items()
            ],
            "watch_expressions": session.watch_expressions,
            "watch_values": session.watch_values,
            "recent_exceptions": self.caught_exceptions[-10:]  # Last 10 exceptions
        }

# Global instance
debug_system = DebugSystem()
