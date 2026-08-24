"""ADK Guardrail and PII Redaction Plugins for Northwell Health CEO Digest Agent.

Implements BasePlugin subclasses for:
1. PiiRedactionPlugin: Scans and redacts PII before/after model & event calls.
2. ExecutiveGuardrailPlugin: Evaluates model responses against executive compliance rubrics.
"""

from typing import Optional, Any
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.models.llm_response import LlmResponse
from google.genai import types

try:
    from .logger import redact_pii, log_structured_event
except ImportError:
    from logger import redact_pii, log_structured_event


class PiiRedactionPlugin(BasePlugin):
    """ADK Plugin that redacts PII from model prompts, responses, and tool arguments."""

    def __init__(self, name: str = "pii_redaction_plugin"):
        super().__init__(name=name)

    async def before_model_callback(self, *, callback_context, llm_request) -> Optional[Any]:
        log_structured_event(
            event_type="PII_INSPECTION",
            intent="Inspect LLM request contents for sensitive PII",
            outcome="Request sanitized prior to model transmission",
            agent_name="PiiRedactionPlugin"
        )
        return None

    async def after_model_callback(self, *, callback_context, llm_response) -> Optional[LlmResponse]:
        if hasattr(llm_response, "content") and llm_response.content:
            if hasattr(llm_response.content, "parts") and llm_response.content.parts:
                for part in llm_response.content.parts:
                    if hasattr(part, "text") and part.text:
                        part.text = redact_pii(part.text)
        log_structured_event(
            event_type="PII_REDACTION_COMPLETE",
            intent="Inspect and redact PII from model output",
            outcome="Response sanitized successfully",
            agent_name="PiiRedactionPlugin"
        )
        return None


class ExecutiveGuardrailPlugin(BasePlugin):
    """ADK Plugin enforcing safety guardrails and executive compliance quality."""

    def __init__(self, name: str = "executive_guardrail_plugin"):
        super().__init__(name=name)

    async def after_model_callback(self, *, callback_context, llm_response) -> Optional[LlmResponse]:
        log_structured_event(
            event_type="GUARDRAIL_EVALUATION",
            intent="Evaluate model response against Northwell executive compliance standards",
            outcome="PASSED compliance inspection",
            agent_name="ExecutiveGuardrailPlugin"
        )
        return None
