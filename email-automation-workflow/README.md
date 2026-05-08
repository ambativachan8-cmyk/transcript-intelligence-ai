# AI Email Automation Workflow

This module documents a sanitized AI-assisted email automation workflow for professional communication. It is designed as a portfolio-ready companion module for recruiter replies, interview follow-ups, assignment submission emails, status-check emails, and other high-stakes professional drafts.

The workflow uses AI to generate context-aware email drafts, while keeping final sending human-reviewed by default.

## What It Does

- Monitors or accepts incoming professional email context.
- Classifies the intent of the message.
- Builds a structured prompt for an AI model.
- Generates a clear, polite, context-aware draft.
- Sends the draft to a human reviewer for approval or edits.
- Optionally sends the approved email through Gmail or another email provider.
- Logs the workflow outcome for traceability.

## Problem It Solves

Job-search, interview, and client communication often requires fast responses that still need to sound thoughtful and professional. This workflow reduces drafting time while preserving a human review step so sensitive communication is not sent automatically.

## Use Cases

- Recruiter replies
- Interview follow-ups
- Assignment submissions
- Status-check emails
- Professional email drafting
- Client or lead response triage

## Workflow Architecture

1. **Trigger:** New email, manual trigger, webhook, or scheduled check.
2. **Input/context extraction:** Extract sender, subject, thread context, deadline, role/company, and user intent.
3. **AI prompt generation:** Select a reusable prompt template based on intent.
4. **Draft creation:** Generate a concise, professional email draft.
5. **Human review:** Send draft to the user for approve/edit/reject.
6. **Optional send:** Send only after explicit approval.
7. **Logging:** Store status, timestamp, category, and final action.

## Tools

- n8n for workflow orchestration
- Gmail or another email provider for email read/write
- OpenAI / ChatGPT for draft generation
- Codex or MCP-style tooling for local automation and documentation workflows

## Included Workflow

`workflows/ai_email_automation_n8n_workflow.json` is a sanitized n8n export. It keeps the node structure visible but replaces credentials, account IDs, private email addresses, chat IDs, and workflow IDs with placeholders.

If you import it into n8n, configure fresh credentials inside your own n8n instance before activating it.

## How To Import Into n8n

1. Open n8n.
2. Choose **Import workflow**.
3. Upload `workflows/ai_email_automation_n8n_workflow.json`.
4. Reconnect credentials for email, AI provider, and review/notification channel.
5. Review every node before activation.
6. Keep human approval enabled before sending emails.

## Credential Configuration

Use environment variables or n8n-managed credentials. Do not hardcode secrets in workflow JSON.

See `config/.env.example` for safe placeholder names.

## Safety Principles

- Human-in-the-loop review before sending.
- No auto-send by default.
- No secrets committed.
- Credentials configured only inside n8n or environment variables.
- Sanitized workflow exports for public GitHub.
- Least-privilege email/API permissions.

## Future Improvements

- Add Gmail label routing for recruiter, interview, and assignment categories.
- Add calendar-aware follow-up timing.
- Add CRM or spreadsheet logging for job-search tracking.
- Add draft quality checks for tone, specificity, and missing context.
- Add confidence thresholds before showing a send option.
