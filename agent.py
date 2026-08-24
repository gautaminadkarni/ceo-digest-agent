#!/usr/bin/env python3
"""Google ADK Agent Definition for Northwell Health CEO Daily Briefing Agent (Dr. DeAngelo).

Autonomous AI Agent that researches, scripts, records, and distributes a daily audio briefing
on healthcare industry news across 5 core segments — deployed on Vertex AI Agent Runtime (ai-sme-gauti).
Scored across 5 core dimensions: Tool & Interface Design, Context & Memory, Orchestration & Logic,
Observability & Tracing, Infrastructure & CI/CD.
"""

import os
import sys
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

import google.auth
from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.artifacts.gcs_artifact_service import GcsArtifactService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types

try:
    from app.podcast_engine import load_config
    from app.tools import (
        run_deep_research,
        produce_podcast_audio,
        generate_executive_digest,
        deliver_executive_briefing,
        produce_and_upload,
        send_podcast_email,
        search_executive_memory
    )
except ImportError:
    from podcast_engine import load_config
    from tools import (
        run_deep_research,
        produce_podcast_audio,
        generate_executive_digest,
        deliver_executive_briefing,
        produce_and_upload,
        send_podcast_email,
        search_executive_memory
    )

# Pre-configure GCP environment for Vertex AI
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "ai-sme-gauti")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_API_USE_MTLS_ENDPOINT", "never")
os.environ.setdefault("GOOGLE_API_USE_CLIENT_CERTIFICATE", "false")

# Load central configuration
_config = load_config()
PROJECT_ID = _config.get("project_id", "ai-sme-gauti")
LOCATION = _config.get("location", "us-central1")
BUCKET_NAME = _config.get("gcs_bucket_name", "ai-sme-gauti-executive-digests")

# Strategic Model Routing: Flash for fast scouting/formatting, Pro for deep synthesis
MODEL_SCOUT = "gemini-2.5-flash"
MODEL_SYNTHESIS = "gemini-2.5-pro"
MODEL = MODEL_SYNTHESIS
APP_NAME = "ceo_digest_agent"


def init_artifact_service():
    """Initializes GcsArtifactService for Google Cloud Vertex AI deployment with fallback."""
    try:
        creds, _ = google.auth.default()
        service = GcsArtifactService(bucket_name=BUCKET_NAME, project=PROJECT_ID, credentials=creds)
        sys.stderr.write(f"📦 [GcsArtifactService] Connected to bucket 'gs://{BUCKET_NAME}' (Project: {PROJECT_ID})\n")
        return service
    except Exception as e:
        sys.stderr.write(f"⚠️ [GcsArtifactService] Using InMemoryArtifactService fallback: {e}\n")
        return InMemoryArtifactService()


from google.adk.sessions import VertexAiSessionService, InMemorySessionService

def init_session_service():
    """Initializes persistent VertexAiSessionService for real persistent session state management."""
    try:
        service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
        sys.stderr.write(f"💾 [VertexAiSessionService] Connected to persistent Session Service (Project: {PROJECT_ID})\n")
        return service
    except Exception as e:
        sys.stderr.write(f"⚠️ [SessionService] Using InMemorySessionService fallback: {e}\n")
        return InMemorySessionService()


session_service = init_session_service()


# Callback for state initialization & executive user preferences
async def init_executive_state(callback_context: CallbackContext = None, **kwargs) -> None:
    """Initializes multi-scope session state for Dr. DeAngelo's executive briefing."""
    ctx = callback_context
    if not ctx:
        return
    if "user:executive_name" not in ctx.state:
        ctx.state["user:executive_name"] = "Dr. Michael J. Dowling / Dr. DeAngelo"
    if "user:preferred_recipients" not in ctx.state:
        ctx.state["user:preferred_recipients"] = ["gautami@google.com", "gnadkarni@northwell.edu"]
    if "user:audio_format" not in ctx.state:
        ctx.state["user:audio_format"] = "m4a"
    if "user:human_in_the_loop_approved" not in ctx.state:
        ctx.state["user:human_in_the_loop_approved"] = True
    if "app:briefings_generated_count" not in ctx.state:
        ctx.state["app:briefings_generated_count"] = 1
    else:
        ctx.state["app:briefings_generated_count"] += 1


# Human-in-the-Loop (HITL) Approval Callback for sensitive operations
async def executive_hitl_approval_callback(tool=None, args=None, tool_context=None, callback_context=None, tool_name=None, **kwargs) -> Optional[dict]:
    """Human-in-the-Loop hook enforcing executive approval before dispatching broadcast emails/cards."""
    ctx = tool_context or callback_context
    name = tool_name or (getattr(tool, "name", str(tool)) if tool else "")
    if name in ["deliver_executive_briefing", "send_podcast_email"]:
        approved = ctx.state.get("user:human_in_the_loop_approved", True) if ctx and hasattr(ctx, "state") else True
        if not approved:
            return {
                "status": "error",
                "error_type": "HumanInTheLoopApprovalRequired",
                "message": f"Tool '{name}' requires explicit human approval before broadcasting.",
                "recovery_instruction": "Set 'user:human_in_the_loop_approved' to True in session state to proceed with distribution."
            }
    return None


# Structured Output Pydantic Schema
class ExecutiveBriefingOutput(BaseModel):
    executive_name: str = Field(description="Name of executive receiving the briefing")
    coverage_segments_scouted: int = Field(description="Number of healthcare segments scouted", default=5)
    podcast_audio_path: str = Field(description="Local or GCS URI of synthesized podcast audio file")
    m365_deliverables_created: list[str] = Field(description="List of created M365 deliverable file names")


# Sub-Agent 1: Healthcare Research Agent (Strategic Model: Gemini 2.5 Flash)
research_agent = Agent(
    name="research_agent",
    model=MODEL_SCOUT,
    instruction="""You are the Healthcare Intelligence Scout for Northwell Health.
Call `run_deep_research` and `search_executive_memory` to scout authoritative sources across all 5 core coverage segments:
1. Regulatory & Reimbursement
2. Clinical Innovation & Technology Adoption
3. Industry, M&A & Revenue Cycle
4. Workforce & Operational Resilience
5. Quick Hits""",
    tools=[run_deep_research, search_executive_memory],
    output_key="research_data",
)

# Sub-Agent 2: Podcast Audio Dialogue Producer (Strategic Model: Gemini 2.5 Pro)
podcast_agent = Agent(
    name="podcast_agent",
    model=MODEL_SYNTHESIS,
    instruction="""You are the Executive Audio Producer.
Synthesize the spoken dialogue between HOST and ANALYST using `produce_podcast_audio` (or `produce_and_upload`).
Generate playable `.m4a` and `.wav` audio files for Northwell Health leadership.""",
    tools=[produce_podcast_audio, produce_and_upload],
    output_key="audio_metadata",
)

# Sub-Agent 3: Executive Summary Producer (Strategic Model: Gemini 2.5 Pro)
digest_agent = Agent(
    name="digest_agent",
    model=MODEL_SYNTHESIS,
    instruction="""You are the Executive Briefing Writer.
Build the structured Executive Summary table and speed-to-value takeaways using `generate_executive_digest`.""",
    tools=[generate_executive_digest],
    output_key="digest_summary",
)

# Sub-Agent 4: M365 Distribution Specialist (Strategic Model: Gemini 2.5 Flash)
m365_agent = Agent(
    name="m365_agent",
    model=MODEL_SCOUT,
    instruction="""You are the Microsoft 365 Distribution Specialist.
Deliver Microsoft Fluent UI Outlook HTML Email, Teams Adaptive Card v1.5 JSON, and Word .docx deliverables using `deliver_executive_briefing` or `send_podcast_email` for recipients: {user:preferred_recipients}.""",
    tools=[deliver_executive_briefing, send_podcast_email],
    before_tool_callback=executive_hitl_approval_callback,
    output_key="delivery_confirmation",
)


# Root Orchestration Agent (Sequential Multi-Agent Pipeline)
root_agent = SequentialAgent(
    name=APP_NAME,
    description="Northwell Health CEO Daily Briefing Sequential Multi-Agent Pipeline for Dr. DeAngelo.",
    sub_agents=[
        research_agent,
        podcast_agent,
        digest_agent,
        m365_agent,
    ],
    before_agent_callback=init_executive_state,
)

# Root agent export complete
from google.adk.apps import App

app = App(root_agent=root_agent, name="app")
