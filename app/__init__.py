try:
    from .agent import root_agent
except ImportError:
    from agent import root_agent

__all__ = ["root_agent"]
