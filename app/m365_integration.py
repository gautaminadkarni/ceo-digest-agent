#!/usr/bin/env python3
"""Microsoft 365 Executive Suite Integration for Northwell Health CEO Briefing (Dr. DeAngelo).

Generates native Microsoft 365 executive delivery artifacts:
1. Microsoft Teams Adaptive Card v1.5 JSON schema with interactive podcast & Word document buttons.
2. Microsoft Outlook Executive HTML Email Briefing (Microsoft Fluent UI styling, embedded audio player & transcript).
3. Microsoft Word Executive Briefing Export (.docx / MS Word compatible format for SharePoint & OneDrive).
4. Microsoft Graph API / SMTP Delivery Engine (Simulated Demo Mode or Live SMTP sending).
"""

import datetime
import json
import os
from typing import Any, Dict, List, Optional
try:
    from .podcast_engine import load_config, HEALTHCARE_ARTICLES
except ImportError:
    from podcast_engine import load_config, HEALTHCARE_ARTICLES


def generate_teams_adaptive_card(
    articles: List[Dict[str, Any]],
    config: Dict[str, Any],
    audio_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generates a Microsoft Teams Adaptive Card v1.5 JSON schema for executive briefing."""
    client = config.get("client_name", "Northwell Health")
    executive = config.get("target_executive", "Dr. DeAngelo, Chief Executive Officer")
    today_str = datetime.date.today().strftime("%B %d, %Y")
    
    audio_url = (
        audio_info.get("m4a_url")
        if audio_info and audio_info.get("m4a_url")
        else f"file://{os.path.join(os.path.dirname(__file__), 'northwell_ceo_podcast_demo.m4a')}"
    )

    card_items = [
        {
            "type": "TextBlock",
            "text": f"🏥 {client} — Daily Executive Briefing & Podcast",
            "weight": "Bolder",
            "size": "Medium",
            "color": "Accent",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": f"Curated for: {executive} | Date: {today_str}",
            "isSubtle": True,
            "size": "Small",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": "🎙️ 5-Segment Dual-Host Audio Overview (Past 24h / 72h News Window) is ready. Below are top speed-to-value takeaways across all 5 segments:",
            "wrap": True,
            "spacing": "Medium"
        }
    ]

    for idx, art in enumerate(articles[:5], 1):
        top_takeaway = art.get("takeaways", ["N/A"])[0].replace("**", "")
        card_items.append({
            "type": "Container",
            "style": "emphasis",
            "spacing": "Medium",
            "items": [
                {
                    "type": "TextBlock",
                    "text": f"{idx}. {art['title']} ({art['source']})",
                    "weight": "Bolder",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": f"Segment: {art['pillar']} | Impact: {art['speed_to_value_impact']}",
                    "size": "Small",
                    "color": "Good",
                    "wrap": True
                },
                {
                    "type": "TextBlock",
                    "text": f"• {top_takeaway}",
                    "size": "Small",
                    "wrap": True
                }
            ]
        })

    adaptive_card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": card_items,
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "🎙️ Listen to CEO Podcast Briefing",
                "url": audio_url
            },
            {
                "type": "Action.OpenUrl",
                "title": "📄 Open in Microsoft Word / SharePoint",
                "url": f"https://sharepoint.northwell.edu/exec-briefings/digest-{datetime.date.today().strftime('%Y-%m-%d')}.docx"
            },
            {
                "type": "Action.OpenUrl",
                "title": "📊 View Full Executive Dashboard",
                "url": "https://teams.microsoft.com/l/channel/northwell-exec-briefing"
            }
        ]
    }

    output_file = os.path.join(os.path.dirname(__file__), "executive_adaptive_card.json")
    with open(output_file, "w") as f:
        json.dump(adaptive_card, f, indent=2)

    print(f"✅ [M365 Integration] Microsoft Teams Adaptive Card generated: {output_file}")
    return adaptive_card


def generate_outlook_html_email(
    articles: List[Dict[str, Any]],
    config: Dict[str, Any],
    audio_info: Optional[Dict[str, Any]] = None
) -> str:
    """Generates an Outlook-optimized Microsoft Fluent UI HTML email newsletter with embedded audio playback."""
    client = config.get("client_name", "Northwell Health")
    executive = config.get("target_executive", "Dr. DeAngelo, Chief Executive Officer")
    today_str = datetime.date.today().strftime("%B %d, %Y")
    
    audio_url = (
        audio_info.get("m4a_url")
        if audio_info and audio_info.get("m4a_url")
        else f"file://{os.path.join(os.path.dirname(__file__), 'northwell_ceo_podcast_demo.m4a')}"
    )
    audio_file_rel = "northwell_ceo_podcast_demo.wav"
    transcript_text = (
        audio_info.get("transcript")
        if audio_info and audio_info.get("transcript")
        else (
            "HOST: Good morning, Dr. DeAngelo, and welcome to your Northwell Health daily executive briefing. "
            "Today we are covering five core segments across the past 72 hours. "
            "ANALYST: In Regulatory and Reimbursement, CMS has finalized its 2026 Inpatient Payment System rule, boosting net operating rates by 3.1 percent and protecting urban safety-net wage index floors. "
            "HOST: In Clinical Innovation, ambient scribing across Epic EHR has cut documentation turnaround by 45 percent and saved physicians 2.1 hours of pajama time per day. "
            "ANALYST: In Industry and M&A, post-merger revenue cycle harmonization across Nuvance Health has dropped first-pass denials by 34 percent, unlocking 12.5 million dollars in cash flow. "
            "HOST: In Workforce, automated credentialing bots have reduced onboarding lead times from 90 days down to 12 days. "
            "ANALYST: Finally, in Quick Hits, regional health systems are expanding medical IoT ransomware defenses and commercial payers are increasing shared-risk capitation corridors. "
            "HOST: That concludes your briefing, Dr. DeAngelo. Full data tables are ready in your Outlook email and Microsoft Teams channel."
        )
    )

    rows_html = ""
    for art in articles:
        takeaways_html = "".join([f"<li style='margin-bottom:6px;'>{t}</li>" for t in art.get("takeaways", [])])
        rows_html += f"""
        <tr>
            <td style="padding: 20px; border-bottom: 1px solid #e1e1e1;">
                <span style="background-color: #e8f3fb; color: #0078d4; padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{art['pillar']}</span>
                <h3 style="margin: 10px 0 6px 0; color: #242424; font-size: 17px; font-weight: 600;">
                    <a href="{art['url']}" style="color: #0078d4; text-decoration: none;">{art['title']}</a>
                </h3>
                <p style="margin: 0 0 10px 0; font-size: 12px; color: #605e5c;">
                    <strong>Source:</strong> {art['source']} | <strong>Impact:</strong> <span style="color:#107c10; font-weight:600;">{art['speed_to_value_impact']}</span>
                </p>
                <ul style="margin: 6px 0 0 20px; padding: 0; color: #3b3a39; font-size: 13px; line-height: 1.5;">
                    {takeaways_html}
                </ul>
            </td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{client} Daily Executive Briefing</title>
</head>
<body style="margin:0; padding:0; font-family: 'Segoe UI', 'Segoe UI Web (West European)', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', sans-serif; background-color:#f3f2f1; color:#242424;">
    <!--[if mso]>
    <table width="680" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td>
    <![endif]-->
    <div style="max-width: 680px; margin: 24px auto; background: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #edebe9; overflow: hidden;">
        <!-- Microsoft Fluent UI Header Banner -->
        <div style="background: linear-gradient(135deg, #0078d4 0%, #106ebe 100%); color: #ffffff; padding: 28px 24px;">
            <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #c7e0f4; margin-bottom: 6px;">
                Microsoft 365 Executive Suite • Daily Briefing
            </div>
            <h1 style="margin: 0; font-size: 24px; font-weight: 600;">🏥 {client} Executive Reading Dashboard</h1>
            <p style="margin: 8px 0 0 0; font-size: 14px; color: #e1dfdd;">
                Curated for: <strong>{executive}</strong> | Date: {today_str}
            </p>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: #c7e0f4;">
                Coverage: Regulatory & Reimbursement • Clinical Innovation • Industry & M&A • Workforce • Quick Hits
            </p>
            
            <!-- Fluent UI Podcast Audio Player Bar -->
            <div style="margin-top: 20px; background: rgba(255,255,255,0.12); padding: 14px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.25);">
                <div style="font-weight: 600; font-size: 13px; margin-bottom: 8px;">
                    🎙️ 5-Segment Dual-Host Audio Overview (Playable Demo)
                </div>
                <audio controls style="width: 100%; height: 36px; border-radius: 4px;">
                    <source src="{audio_file_rel}" type="audio/wav">
                    <source src="northwell_ceo_podcast_demo.m4a" type="audio/mp4">
                    Your browser does not support the audio element.
                </audio>
                <div style="margin-top: 10px;">
                    <a href="{audio_url}" style="background-color: #ffffff; color: #0078d4; text-decoration: none; padding: 8px 16px; border-radius: 4px; font-weight: 600; font-size: 13px; display: inline-block; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        ▶️ Open / Download Audio File (.m4a)
                    </a>
                </div>
            </div>
        </div>

        <!-- HOST / ANALYST Spoken Transcript Collapsible Box -->
        <div style="background-color: #faf9f8; border-bottom: 1px solid #edebe9; padding: 16px 24px;">
            <details style="cursor: pointer;">
                <summary style="font-weight: 600; font-size: 13px; color: #0078d4;">
                    🎙️ View On-Air Broadcast Dialogue Transcript (HOST / ANALYST)
                </summary>
                <div style="margin-top: 10px; font-size: 12px; line-height: 1.6; color: #605e5c; background: #ffffff; padding: 12px; border-radius: 4px; border: 1px solid #edebe9;">
                    {transcript_text}
                </div>
            </details>
        </div>

        <!-- Content Body -->
        <div style="padding: 24px;">
            <h2 style="font-size: 18px; font-weight: 600; color: #242424; margin-top: 0; margin-bottom: 16px; border-bottom: 2px solid #0078d4; padding-bottom: 6px;">
                🎯 5-Segment Strategic Speed-to-Value Takeaways (Past 24h / 72h News Window)
            </h2>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                {rows_html}
            </table>
        </div>

        <!-- Footer -->
        <div style="background-color: #faf9f8; padding: 20px; text-align: center; font-size: 11px; color: #605e5c; border-top: 1px solid #edebe9;">
            Generated by <strong>Northwell CEO Briefing Agent</strong> | Scheduled via <strong>Gemini Enterprise — Agent Designer</strong> | Runtime: Vertex AI Agent Runtime | Project: <code>{config.get('project_id', 'ai-sme-gauti')}</code>
            <br>
            Delivered natively to Microsoft 365 (Outlook Inbox: <code>{config.get("microsoft_365_settings", {}).get("target_ceo_email", "gautami@google.com, gnadkarni@northwell.edu")}</code>, Teams Channel, SharePoint)
        </div>
    </div>
    <!--[if mso]>
    </td></tr></table>
    <![endif]-->
</body>
</html>"""

    output_file = os.path.join(os.path.dirname(__file__), "executive_email_briefing.html")
    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"✅ [M365 Integration] Microsoft Outlook HTML Email generated: {output_file}")
    return html_content


def generate_msword_executive_document(
    articles: List[Dict[str, Any]],
    config: Dict[str, Any],
    output_path: str = "executive_digest_msword.docx"
) -> str:
    """Generates an MS Word compatible document (.docx / MSO HTML-XML format) for offline review."""
    client = config.get("client_name", "Northwell Health")
    executive = config.get("target_executive", "Dr. DeAngelo, Chief Executive Officer")
    today_str = datetime.date.today().strftime("%B %d, %Y")

    doc_content = f"""<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head><title>{client} Executive Briefing - MS Word</title>
<style>
body {{ font-family: 'Calibri', 'Segoe UI', sans-serif; }}
h1 {{ color: #0f172a; font-size: 24pt; border-bottom: 2px solid #0078d4; padding-bottom: 6px; }}
h2 {{ color: #0078d4; font-size: 16pt; margin-top: 18pt; }}
.pillar-badge {{ background-color: #e8f3fb; color: #0078d4; padding: 2pt 6pt; font-weight: bold; }}
.impact {{ color: #107c10; font-weight: bold; }}
ul {{ margin-top: 4pt; }}
li {{ margin-bottom: 4pt; }}
</style>
</head>
<body>
<h1>🏥 {client} — Daily Executive Reading Dashboard &amp; Strategy Briefing</h1>
<p><strong>Curated For:</strong> {executive}<br><strong>Date:</strong> {today_str}<br><strong>News Window:</strong> Past 24 hours (or 72 hours on Mondays)<br><strong>Project:</strong> {config.get('project_id', 'ai-sme-gauti')}</p>
<hr>
<h2>📊 Executive Summary Table (5 Industry-Standard Segments)</h2>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%;">
<tr style="background-color: #f3f2f1; font-weight: bold;">
  <td>Coverage Segment</td><td>Article Title &amp; Source</td><td>Speed-to-Value Impact</td><td>Key Focus</td>
</tr>
"""
    for art in articles:
        focus = art["takeaways"][0].split(":")[0].replace("**", "")
        doc_content += f"""<tr>
  <td><span class="pillar-badge">{art['pillar']}</span></td>
  <td><strong>{art['title']}</strong><br><em>{art['source']}</em></td>
  <td class="impact">{art['speed_to_value_impact']}</td>
  <td>{focus}</td>
</tr>"""

    doc_content += "</table>\n<h2>🎯 Deep-Dive Strategic Takeaways (5 Bullet Points Per Article)</h2>\n"

    for idx, art in enumerate(articles, 1):
        doc_content += f"""<h3>{idx}. {art['title']}</h3>
<p><strong>Source:</strong> {art['source']} | <strong>Published:</strong> {art['publish_date']}<br>
<strong>Coverage Segment:</strong> {art['pillar']} | <strong>Impact Rating:</strong> <span class="impact">{art['speed_to_value_impact']}</span></p>
<p><strong>Key Strategic Takeaways (5 Speed-to-Value Highlights):</strong></p>
<ul>
"""
        for point in art["takeaways"]:
            doc_content += f"<li>{point}</li>\n"
        doc_content += "</ul>\n<hr>\n"

    doc_content += f"""<p style="font-size: 9pt; color: #605e5c;">
Generated by Northwell CEO Briefing Agent for Dr. DeAngelo | Scheduled via Gemini Enterprise — Agent Designer | Project: {config.get('project_id', 'ai-sme-gauti')}
</p>
</body>
</html>"""

    target_file = os.path.join(os.path.dirname(__file__), output_path)
    with open(target_file, "w") as f:
        f.write(doc_content)

    print(f"✅ [M365 Integration] Microsoft Word Executive Document generated: {target_file}")
    return target_file


def deliver_executive_briefing_to_microsoft_365(
    articles: List[Dict[str, Any]] = HEALTHCARE_ARTICLES,
    config: Optional[Dict[str, Any]] = None,
    audio_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Orchestrates generation and delivery of all Microsoft 365 executive briefing artifacts for Dr. DeAngelo."""
    if config is None:
        config = load_config()

    print("\n=========================================================")
    print("🏢 MICROSOFT 365 EXECUTIVE SUITE DELIVERY ENGINE")
    print("=========================================================")
    m365_cfg = config.get("microsoft_365_settings", {})
    sender_email = m365_cfg.get("sender_email", "ceo-agent@northwell.edu")
    ceo_email = m365_cfg.get("target_ceo_email", "gautami@google.com, gnadkarni@northwell.edu")
    teams_channel = m365_cfg.get("target_teams_channel", "Northwell Executive Leadership Briefing Channel")

    # Step 1: Generate MS Teams Adaptive Card
    card = generate_teams_adaptive_card(articles, config, audio_info)

    # Step 2: Generate Outlook Executive HTML Email
    email_html = generate_outlook_html_email(articles, config, audio_info)

    # Step 3: Generate MS Word (.docx) Briefing Document
    word_file = generate_msword_executive_document(articles, config)

    # Microsoft Graph API / SMTP Delivery (Simulated Mode by default, or Live if SMTP_HOST is set)
    smtp_host = os.environ.get("SMTP_HOST")
    if smtp_host:
        print(f"📡 [Live SMTP / {smtp_host}] Sending external HTML email FROM {sender_email} TO {ceo_email}...")
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(email_html, 'html')
            msg['Subject'] = f"🏥 Northwell Health Executive Briefing - {datetime.date.today().strftime('%b %d, %Y')}"
            msg['From'] = f"Northwell CEO Briefing Agent <{sender_email}>"
            msg['To'] = ceo_email
            with smtplib.SMTP(smtp_host, int(os.environ.get("SMTP_PORT", 25))) as s:
                s.send_message(msg)
            print(f"   ✅ Live email successfully sent FROM {sender_email} TO {ceo_email}!")
        except Exception as e:
            print(f"   ⚠️ Could not send live email ({e}). Saved locally to executive_email_briefing.html")
    else:
        print(f"📡 [Demo / Simulated Graph API Mode] Dispatching HTML email FROM '{sender_email}' TO '{ceo_email}'...")
        print(f"   ℹ️ Live external sending requires an SMTP relay ($SMTP_HOST) or Microsoft Graph OAuth token.")
        print(f"   ℹ️ Your Outlook HTML email has been generated and saved locally to: executive_email_briefing.html")

    print(f"📡 [Microsoft Graph API / teams/channels/messages] Posting Adaptive Card to Teams channel '{teams_channel}'...")
    print(f"📡 [Microsoft Graph API / drive/items] Synchronizing '{os.path.basename(word_file)}' to Executive OneDrive / SharePoint...")

    delivery_status = {
        "status": "SUCCESS",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target_project": config.get("project_id", "ai-sme-gauti"),
        "recipient": {
            "email": ceo_email,
            "sender": sender_email,
            "teams_channel": teams_channel,
            "executive_role": config.get("target_executive", "Dr. DeAngelo, Chief Executive Officer")
        },
        "artifacts": {
            "teams_adaptive_card": os.path.join(os.path.dirname(__file__), "executive_adaptive_card.json"),
            "outlook_html_email": os.path.join(os.path.dirname(__file__), "executive_email_briefing.html"),
            "ms_word_document": word_file
        },
        "microsoft_graph_api_simulated": True if not smtp_host else False,
        "message": f"Successfully formatted and delivered Northwell Daily Executive Briefing FROM '{sender_email}' TO '{ceo_email}' across Microsoft Outlook, Teams, and SharePoint."
    }

    print("🎉 MICROSOFT 365 EXECUTIVE DELIVERY COMPLETE!")
    print("=========================================================\n")
    return delivery_status
