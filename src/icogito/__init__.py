# src/icogito/__init__.py
from .factory import AgentFactory
from .models import AgentConfig
from .core import create_scaffolding

__all__ = ["AgentFactory", "AgentConfig", "create_scaffolding"]