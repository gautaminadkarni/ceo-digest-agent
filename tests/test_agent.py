# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit and Integration Tests for Northwell Health CEO Daily Briefing Agent."""

import os
import pytest
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.app import app, root_agent
from app.tools import (
    run_deep_research,
    produce_podcast_audio,
    generate_executive_digest,
    deliver_executive_briefing
)


def test_domain_tools_functionality():
    """Test all domain tools return expected dictionary structures and status."""
    research_res = run_deep_research()
    assert isinstance(research_res, dict)

    audio_res = produce_podcast_audio()
    assert isinstance(audio_res, dict)

    digest_res = generate_executive_digest()
    assert isinstance(digest_res, dict)

    delivery_res = deliver_executive_briefing()
    assert isinstance(delivery_res, dict)


def test_multi_agent_pipeline_structure():
    """Verify SequentialAgent pipeline composition and sub-agent roles."""
    assert root_agent.name == "ceo_digest_agent"
    sub_names = [agent.name for agent in root_agent.sub_agents]
    assert sub_names == ["research_agent", "podcast_agent", "digest_agent", "m365_agent"]
    assert len(root_agent.sub_agents) == 4


def test_app_enterprise_configuration():
    """Verify App enterprise configuration for context caching, compaction, and plugins."""
    assert app.name == "ceo_digest_agent"
    assert app.context_cache_config is not None
    assert app.context_cache_config.min_tokens == 2048
    assert app.events_compaction_config is not None
    assert len(app.plugins) >= 2


@pytest.mark.asyncio
async def test_full_pipeline_execution():
    """Async integration test verifying runner execution through the agent pipeline."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app.name,
        user_id="dr_deangelo",
        session_id="session_briefing_001"
    )

    runner = Runner(
        agent=root_agent,
        app_name=app.name,
        session_service=session_service
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text="Generate today's executive daily briefing for Dr. DeAngelo across all 5 segments.")]
    )

    events = []
    async for event in runner.run_async(
        user_id="dr_deangelo",
        session_id="session_briefing_001",
        new_message=user_msg
    ):
        events.append(event)

    assert len(events) > 0
