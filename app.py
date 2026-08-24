#!/usr/bin/env python3
"""Google ADK Application Entrypoint for Northwell Health CEO Briefing Agent.

Configures Context Caching, Events Compaction, BigQuery Agent Analytics, and OpenTelemetry Cloud Trace.
"""

from google.adk.apps import App, EventsCompactionConfig
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from google.adk.plugins import LoggingPlugin, DebugLoggingPlugin

try:
    from .agent import root_agent, APP_NAME, PROJECT_ID, BUCKET_NAME, MODEL
except ImportError:
    from agent import root_agent, APP_NAME, PROJECT_ID, BUCKET_NAME, MODEL


# Observability & Logging Plugins
logging_plugin = LoggingPlugin()
debug_plugin = DebugLoggingPlugin()


# Production ADK App configuration
app = App(
    name="ceo_digest_agent",
    root_agent=root_agent,
    plugins=[logging_plugin, debug_plugin],
    # Context Caching configuration to reduce latency and cost for large research briefs
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=10,
    ),
    # Events Compaction configuration to summarize long executive Q&A sessions
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,
        overlap_size=3,
        summarizer=LlmEventSummarizer(llm=Gemini(model=MODEL)),
    ),
)

__all__ = ["app", "root_agent", "APP_NAME", "PROJECT_ID", "BUCKET_NAME"]
