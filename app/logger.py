"""Structured JSON Logger and PII Redaction Engine for Northwell Health CEO Agent.

Provides pervasive structured JSON logging for intent vs outcome tracking and PII redaction.
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Configure standard logger to output to sys.stderr to preserve stdout for JSON APIs
logger = logging.getLogger("ceo_digest_agent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(handler)

# PII Regular Expressions
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
MRN_REGEX = re.compile(r"\bMRN-?\d{6,8}\b", re.IGNORECASE)


def redact_pii(text: str) -> str:
    """Redacts emails, phone numbers, SSNs, and Medical Record Numbers (MRNs) from text."""
    if not isinstance(text, str):
        return text
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
    text = SSN_REGEX.sub("[REDACTED_SSN]", text)
    text = MRN_REGEX.sub("[REDACTED_MRN]", text)
    return text


def log_structured_event(
    event_type: str,
    intent: str,
    outcome: str,
    severity: str = "INFO",
    agent_name: Optional[str] = None,
    tool_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Logs a structured JSON record with intent vs outcome and PII redaction."""
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "agent_name": agent_name or "ceo_digest_agent",
        "tool_name": tool_name or "N/A",
        "intent": redact_pii(intent),
        "outcome": redact_pii(outcome),
        "severity": severity,
        "metadata": metadata or {}
    }
    log_line = json.dumps(payload)
    if severity == "ERROR":
        logger.error(log_line)
    elif severity == "WARNING":
        logger.warning(log_line)
    else:
        logger.info(log_line)
    return payload
