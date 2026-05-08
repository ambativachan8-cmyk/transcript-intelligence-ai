# Architecture

The AI Email Automation Workflow is designed as a human-reviewed automation system. Its purpose is to speed up professional email drafting without giving the system unchecked permission to send sensitive messages.

## Flow

```text
Trigger
  -> Gmail/new message/manual trigger/webhook
  -> classify intent
  -> retrieve context
  -> generate email draft
  -> human review
  -> send/archive/label
  -> log outcome
```

## Components

### 1. Trigger

The workflow can start from a new Gmail/email-provider message, an n8n manual trigger, a webhook, or a scheduled inbox check.

### 2. Intent Classification

The message is classified into a practical professional category:

- Recruiter reply
- Interview follow-up
- Assignment submission
- Status check
- General professional response
- No reply needed

### 3. Context Retrieval

The workflow collects context such as sender, subject, prior thread text, role/company, deadline, attached assignment references, and any user-provided notes.

### 4. Prompt Selection

The workflow selects a prompt template from `prompts/` and fills in the relevant context. This keeps responses consistent while still allowing personalization.

### 5. Draft Generation

An AI model generates a draft with a professional tone, concise structure, and clear next action.

### 6. Human Review

The draft is sent to the user for approve, edit, or reject. This is the key safety control.

### 7. Optional Send / Archive / Label

After approval, the workflow can send the email, save it as a draft, apply a label, or archive low-priority messages.

### 8. Logging

The workflow logs metadata such as category, timestamp, action taken, and whether the draft was approved or edited.

## Production Considerations

- Keep credentials in n8n credential storage or environment variables.
- Use least-privilege API scopes.
- Avoid storing raw personal email bodies unless there is a clear reason.
- Add retry/error handling for provider API failures.
- Add audit logs for every send action.
