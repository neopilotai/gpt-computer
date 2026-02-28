import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from enum import Enum

from gpt_computer.helpers.log import Log

if TYPE_CHECKING:
    from gpt_computer.core.agent_runtime import Agent

@dataclass
class UserMessage:
    message: str
    system_message: List[str] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)

@dataclass
class AgentConfig:
    chat_model: Any = None
    utility_model: Any = None
    embeddings_model: Any = None
    browser_model: Any = None
    profile: str = "default"
    memory_subdir: str = ""
    knowledge_subdirs: List[str] = field(default_factory=list)
    mcp_servers: Any = None
    browser_http_headers: Dict = field(default_factory=dict)
    additional: Dict = field(default_factory=dict)

class AgentContextType(Enum):
    USER = "user"
    TASK = "task"
    BACKGROUND = "background"

class AgentContext:
    _contexts: Dict[str, "AgentContext"] = {}
    _contexts_lock = threading.RLock()
    _current_context = threading.local()
    
    def __init__(self, config: AgentConfig = None, id: Optional[str] = None, name: str = "Agent", type: AgentContextType = AgentContextType.USER, log: Log = None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.type = type
        self.created_at = datetime.now()
        self.last_message = datetime.now()
        self.data: Dict[str, Any] = {}
        self.output_data: Dict[str, Any] = {}
        
        self.log = log or Log()
        self.log.context = self
        self.config = config or AgentConfig()
        
        # Initialize default agent
        from gpt_computer.core.agent_runtime import Agent
        self.agent0 = Agent(self, number=0)
        self.streaming_agent = self.agent0

        with AgentContext._contexts_lock:
            AgentContext._contexts[self.id] = self

    @classmethod
    def get(cls, id: str) -> Optional["AgentContext"]:
        with cls._contexts_lock:
            return cls._contexts.get(id)

    @classmethod
    def all(cls) -> List["AgentContext"]:
        with cls._contexts_lock:
            return list(cls._contexts.values())

    @classmethod
    def first(cls) -> Optional["AgentContext"]:
        with cls._contexts_lock:
            if not cls._contexts:
                return None
            return next(iter(cls._contexts.values()))

    @classmethod
    def use(cls, id: str):
        context = cls.get(id)
        if context:
            cls._current_context.value = context
        else:
            # If not found, create a temporary one to prevent crashes during recovery
            context = AgentContext(id=id, name="RecoveredContext")
            cls._current_context.value = context

    @classmethod
    def current(cls) -> "AgentContext":
        ctx = getattr(cls._current_context, "value", None)
        if not ctx:
            # Return a default context if none set
            ctx = AgentContext(name="DefaultContext")
            cls._current_context.value = ctx
        return ctx

    @classmethod
    def get_notification_manager(cls):
        # Placeholder for notification manager
        return None

    @classmethod
    def log_to_all(cls, type: str, content: str, **kwargs):
        with cls._contexts_lock:
            for ctx in cls._contexts.values():
                ctx.log.log(type=type, content=content, **kwargs)
