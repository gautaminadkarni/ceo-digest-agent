---
name: ceo-digest-agent
description: >
  Generates the daily 5-segment Executive Briefing & Podcast Audio Overview for Dr. DeAngelo, CEO of Northwell Health,
  using a Google ADK Agent on Vertex AI Agent Runtime (ai-sme-gauti).
  Researches 5 core segments, synthesizes HOST/ANALYST spoken dialogue, produces playable .m4a/.wav audio files,
  and formats native Microsoft 365 deliverables (Outlook HTML email with embedded audio, Teams Adaptive Card, MS Word .docx).
metadata:
  author: Google
  version: 4.0.0
  triggers:
    - "/run_ceo_digest"
    - "generate Northwell CEO podcast briefing"
    - "create executive podcast for Dr DeAngelo"
---

# Northwell Health CEO Daily Briefing & Podcast Agent

This skill automates the end-to-end research, scripting, audio recording, and Microsoft 365 deliverable formatting for **Dr. DeAngelo, CEO of Northwell Health**, using **Google ADK** in project `ai-sme-gauti`.

## Quick Execution

Run the turnkey test pipeline:
```bash
/Users/gautami/ceo_digest_agent/run_ceo_digest.sh
```

## Google ADK Architecture
- **App Entrypoint**: `app.py` -> `app = App(root_agent=root_agent, name="ceo_digest_agent")`
- **Agent Definition**: `agent.py` -> `ConfiguredAgent(name="ceo_digest_agent", model="gemini-2.5-pro", tools=[...])`
- **Artifact Service**: `GcsArtifactService(bucket_name="ai-sme-gauti-executive-digests", project="ai-sme-gauti")`
- **Tools**:
  - `run_deep_research`: Scouts news across 5 segments & synthesizes HOST/ANALYST script.
  - `produce_podcast_audio`: Synthesizes spoken script into playable `.m4a` and `.wav` audio files.
  - `generate_executive_digest`: Compiles Executive Reading Dashboard (`executive_digest.md`).
  - `deliver_executive_briefing`: Formats and delivers Microsoft 365 artifacts.

## Deliverables Generated
1. **Playable Podcast Audio (.m4a)**: `northwell_ceo_podcast_demo.m4a`
2. **Playable Podcast Audio (.wav)**: `northwell_ceo_podcast_demo.wav`
3. **Microsoft Outlook HTML Email**: `executive_email_briefing.html` (Microsoft Fluent UI with embedded audio player)
4. **Microsoft Teams Adaptive Card v1.5**: `executive_adaptive_card.json`
5. **Microsoft Word (.docx) Export**: `executive_digest_msword.docx`
6. **Markdown Reading Dashboard**: `executive_digest.md`
