"""Production Application Entrypoint for Northwell Health CEO Daily Briefing Agent.

Registers App with:
1. Context Caching (ContextCacheConfig)
2. Sliding Event Compaction (EventsCompactionConfig + LlmEventSummarizer)
3. Observability Plugins (LoggingPlugin, DebugLoggingPlugin)
4. Guardrails & PII Redaction Plugins (PiiRedactionPlugin, ExecutiveGuardrailPlugin)
"""

import os
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig
from google.adk.apps.compaction import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from google.adk.plugins import LoggingPlugin, DebugLoggingPlugin

try:
    from app.agent import root_agent, APP_NAME, PROJECT_ID, BUCKET_NAME, MODEL
    from app.plugins import PiiRedactionPlugin, ExecutiveGuardrailPlugin
except ImportError:
    from agent import root_agent, APP_NAME, PROJECT_ID, BUCKET_NAME, MODEL
    from plugins import PiiRedactionPlugin, ExecutiveGuardrailPlugin


# Observability & Guardrail Plugins
logging_plugin = LoggingPlugin()
debug_plugin = DebugLoggingPlugin()
pii_plugin = PiiRedactionPlugin(name="pii_redaction_plugin")
guardrail_plugin = ExecutiveGuardrailPlugin(name="executive_guardrail_plugin")


# Production ADK App configuration
app = App(
    name="ceo_digest_agent",
    root_agent=root_agent,
    plugins=[logging_plugin, debug_plugin, pii_plugin, guardrail_plugin],
    context_cache_config=ContextCacheConfig(
        min_tokens=2048,
        ttl_seconds=1800,
        cache_intervals=10,
    ),
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=20,
        overlap_size=3,
        summarizer=LlmEventSummarizer(llm=Gemini(model="gemini-2.5-flash")),
    ),
)
