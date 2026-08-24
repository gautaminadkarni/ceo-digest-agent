#!/usr/bin/env python3
"""ADK Tools for Northwell Health CEO Daily Briefing Agent (Dr. DeAngelo).

Provides modular, cleanly typed ADK tools for the root Agent:
1. run_deep_research: Conducts autonomous research across 5 coverage segments & synthesizes HOST/ANALYST spoken dialogue script.
2. produce_podcast_audio: Converts dialogue script into real playable TTS audio files (.m4a and .wav).
3. generate_executive_digest: Compiles the Executive Reading Dashboard markdown file (executive_digest.md).
4. deliver_executive_briefing: Formats and delivers Microsoft 365 artifacts (Outlook HTML email, Teams Card, Word doc).
"""

import datetime
import os
from typing import Any, Dict, List, Optional
try:
    from .podcast_engine import (
        load_config,
        HEALTHCARE_ARTICLES,
        generate_podcast_transcript,
        synthesize_podcast_audio
    )
    from .m365_integration import deliver_executive_briefing_to_microsoft_365
except ImportError:
    from podcast_engine import (
        load_config,
        HEALTHCARE_ARTICLES,
        generate_podcast_transcript,
        synthesize_podcast_audio
    )
    from m365_integration import deliver_executive_briefing_to_microsoft_365


def run_deep_research() -> Dict[str, Any]:
    """Conducts autonomous research across 5 healthcare coverage segments (Regulatory, Clinical, M&A, Workforce, Quick Hits) and synthesizes a HOST/ANALYST spoken dialogue script.

    Returns:
        Dict containing researched articles, 5 coverage segments, attribution rules, and spoken transcript.
    """
    config = load_config()
    transcript = generate_podcast_transcript(HEALTHCARE_ARTICLES)
    segments = [s.get("name") for s in config.get("coverage_segments", [])] if "coverage_segments" in config else [
        "Regulatory & Reimbursement",
        "Clinical Innovation & Technology Adoption",
        "Industry, M&A & Revenue Cycle",
        "Workforce & Operational Resilience",
        "Quick Hits"
    ]

    return {
        "status": "SUCCESS",
        "client": config.get("client_name", "Northwell Health"),
        "target_executive": config.get("target_executive", "Dr. DeAngelo, Chief Executive Officer"),
        "news_window": config.get("news_window_rule", "Past 24 hours (or 72 hours on Monday)"),
        "coverage_segments": segments,
        "articles_count": len(HEALTHCARE_ARTICLES),
        "articles": HEALTHCARE_ARTICLES,
        "attribution_mode": "Natural on-air spoken attribution (HOST / ANALYST)",
        "transcript": transcript
    }


def produce_podcast_audio() -> Dict[str, Any]:
    """Converts the synthesized HOST/ANALYST dialogue script into playable podcast audio files (.m4a and .wav).

    Returns:
        Dict containing audio file paths, playable URLs, duration, and status.
    """
    transcript = generate_podcast_transcript(HEALTHCARE_ARTICLES)
    audio_res = synthesize_podcast_audio(transcript, output_basename="northwell_ceo_podcast_demo")
    return {
        "status": audio_res["status"],
        "m4a_path": audio_res["m4a_path"],
        "wav_path": audio_res["wav_path"],
        "m4a_url": audio_res["m4a_url"],
        "wav_url": audio_res["wav_url"],
        "duration_seconds": audio_res["duration_seconds"],
        "transcript": transcript
    }


def generate_executive_digest() -> Dict[str, Any]:
    """Generates the Markdown Executive Reading Dashboard (executive_digest.md) with summary table and takeaways.

    Returns:
        Dict containing markdown digest file path, byte size, and status.
    """
    config = load_config()
    today_str = datetime.date.today().strftime("%B %d, %Y")
    executive = config.get("target_executive", "Dr. DeAngelo, Chief Executive Officer")
    client = config.get("client_name", "Northwell Health")

    md_lines = [
        f"# 🏥 Executive Reading Dashboard & Strategy Briefing",
        f"**Curated For:** {executive} ({client})",
        f"**Date:** {today_str}",
        f"**News Window:** {config.get('news_window_rule', 'Past 24 hours (or 72 hours on Mondays)')}\n",
        "---",
        "## 📊 Executive Summary Table (5 Industry-Standard Segments)\n",
        "| Coverage Segment | Article Title & Source | Speed-to-Value Impact | Key Focus |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for art in HEALTHCARE_ARTICLES:
        title_link = f"[{art['title']}]({art['url']})"
        source_badge = f"**{art['source']}**"
        pillar_badge = f"`{art['pillar']}`"
        impact = art["speed_to_value_impact"]
        focus = art["takeaways"][0].split(":")[0].replace("**", "")
        md_lines.append(f"| {pillar_badge} | {title_link}<br>_{source_badge}_ | {impact} | {focus} |")

    md_lines.append("\n---")
    md_lines.append("## 🎯 Deep-Dive Strategic Takeaways\n")

    for idx, art in enumerate(HEALTHCARE_ARTICLES, 1):
        md_lines.append(f"### {idx}. {art['title']}")
        md_lines.append(f"- **Source:** {art['source']} | **Published:** {art['publish_date']}")
        md_lines.append(f"- **Segment:** `{art['pillar']}`")
        md_lines.append(f"- **Impact Rating:** {art['speed_to_value_impact']}")
        md_lines.append(f"- **Link:** [{art['url']}]({art['url']})\n")
        md_lines.append("**Key Strategic Takeaways:**")
        for point in art["takeaways"]:
            md_lines.append(f"  - {point}")
        md_lines.append("")

    target_file = os.path.join(os.path.dirname(__file__), "executive_digest.md")
    content = "\n".join(md_lines)
    with open(target_file, "w") as f:
        f.write(content)

    print(f"✅ [Executive Digest] Saved markdown dashboard to: {target_file}")
    return {
        "status": "SUCCESS",
        "file_path": target_file,
        "content_length_bytes": len(content),
        "target_project": config.get("project_id", "ai-sme-gauti")
    }


def deliver_executive_briefing() -> Dict[str, Any]:
    """Formats and delivers the briefing across Microsoft 365 (Outlook HTML Email, Teams Adaptive Card, MS Word .docx).

    Returns:
        Dict confirming delivery routing to Outlook inbox, Teams channel, and SharePoint document library.
    """
    config = load_config()
    audio_info = produce_podcast_audio()
    m365_res = deliver_executive_briefing_to_microsoft_365(HEALTHCARE_ARTICLES, config, audio_info)
    return m365_res


# Standard Alias Wrappers for Partner Architecture Compatibility
def produce_and_upload() -> Dict[str, Any]:
    """Partner Tool 2 Alias: Converts dialogue script to audio and uploads to storage."""
    return produce_podcast_audio()


def send_podcast_email() -> Dict[str, Any]:
    """Partner Tool 3 Alias: Delivers branded email to executive recipients via Outlook/M365."""
    return deliver_executive_briefing()
