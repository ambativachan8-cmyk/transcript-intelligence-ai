# Security Notes

This workflow is intended for public portfolio documentation and safe local reuse. It must not expose private credentials or personal email data.

## Never Commit

- `.env` files
- API keys
- OAuth credential files
- email provider tokens
- n8n credential exports
- raw personal email bodies
- passwords
- private webhook URLs

## n8n Export Risk

n8n workflow JSON can contain credential IDs, credential names, webhook URLs, account identifiers, chat IDs, and hardcoded node parameters. Before uploading an export publicly, sanitize it.

The workflow JSON in this repository is sanitized. Placeholders such as `YOUR_EMAIL_ADDRESS`, `YOUR_OPENAI_API_KEY`, and `YOUR_GMAIL_CREDENTIAL` must be replaced only inside a private n8n environment.

## Human Review

Email sending should remain human-reviewed. The recommended default is:

1. Generate draft.
2. Send draft to reviewer.
3. Require explicit approve/edit/reject action.
4. Send only after approval.

## Least Privilege

Use the minimum permissions required:

- Read only the inbox or labels needed.
- Send only from the intended account.
- Restrict webhook access.
- Rotate keys if any credential is exposed.

## If a Secret Is Exposed

1. Revoke the key or OAuth credential immediately.
2. Rotate the credential.
3. Remove it from Git history if it was committed.
4. Re-check workflow exports before making them public again.
