#!/usr/bin/env python3
"""Turnkey Test Script for Northwell Health CEO Daily Briefing Agent (Dr. DeAngelo).

Executes the full Google ADK pipeline:
1. Deep research across 5 healthcare coverage segments.
2. Podcast dialogue synthesis & playable audio generation (.m4a and .wav).
3. Executive Reading Dashboard markdown generation.
4. Microsoft 365 Executive Suite delivery (Outlook HTML email, Teams Adaptive Card, MS Word doc).
"""

import os
import sys

from tools import (
    run_deep_research,
    produce_podcast_audio,
    generate_executive_digest,
    deliver_executive_briefing
)


def main():
    print("==========================================================================")
    print("🏥 NORTHWELL HEALTH CEO DAILY BRIEFING AGENT — TURNKEY TEST RUNNER")
    print("   Target Executive: Dr. DeAngelo, Chief Executive Officer")
    print("   Google Cloud Project: ai-sme-gauti | Runtime: Vertex AI Agent Runtime")
    print("==========================================================================\n")

    # Step 1: Deep Research & Scripting
    print("Step 1/4: Conducting autonomous research across 5 healthcare segments...")
    research_res = run_deep_research()
    print(f"   ✅ Scouted {research_res['articles_count']} articles across: {', '.join(research_res['coverage_segments'])}")
    print(f"   🕒 News Window: {research_res['news_window']}\n")

    # Step 2: Executive Digest Dashboard
    print("Step 2/4: Compiling Executive Reading Dashboard (executive_digest.md)...")
    digest_res = generate_executive_digest()
    print(f"   ✅ Markdown Digest saved to: {digest_res['file_path']} ({digest_res['content_length_bytes']} bytes)\n")

    # Step 3: Podcast Audio Synthesis
    print("Step 3/4: Synthesizing spoken dialogue & generating playable audio files...")
    audio_res = produce_podcast_audio()
    print(f"   🎙️ Playable M4A Audio: {audio_res['m4a_path']}")
    print(f"   🔊 Playable WAV Audio: {audio_res['wav_path']}\n")

    # Step 4: Microsoft 365 Executive Suite Delivery
    print("Step 4/4: Formatting & delivering Microsoft 365 Executive Suite deliverables...")
    m365_res = deliver_executive_briefing()

    print("==========================================================================")
    print("🎉 END-TO-END TEST COMPLETE — DELIVERABLE SUMMARY:")
    print("==========================================================================")
    print(f"1. Playable Podcast Audio (.m4a): {audio_res['m4a_path']}")
    print(f"2. Playable Podcast Audio (.wav): {audio_res['wav_path']}")
    print(f"3. Executive Digest Markdown:     {digest_res['file_path']}")
    print(f"4. Microsoft Teams Adaptive Card: {m365_res['artifacts']['teams_adaptive_card']}")
    print(f"5. Microsoft Outlook HTML Email:  {m365_res['artifacts']['outlook_html_email']}")
    print(f"6. Microsoft Word (.docx) Export: {m365_res['artifacts']['ms_word_document']}")
    print("==========================================================================")
    print(f"Sender:    {m365_res['recipient']['sender']}")
    print(f"Recipient: {m365_res['recipient']['email']}")
    print(f"Executive: {m365_res['recipient']['executive_role']}")
    print("==========================================================================\n")


if __name__ == "__main__":
    main()
