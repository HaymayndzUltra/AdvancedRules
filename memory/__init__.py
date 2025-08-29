"""
AdvancedRules Memory Package
Hybrid memory system with vector retrieval and structured storage
"""

__version__ = "2.0.0"
__author__ = "AdvancedRules Team"

from .bridge import MemoryBridge, persona_context, get_memory_bridge

__all__ = [
    'MemoryBridge',
    'persona_context',
    'get_memory_bridge',
]
