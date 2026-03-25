# send-email

## Overview

Send an email using a configured SMTP server or API. Composes and delivers the message from the provided subject, body, and recipient list.

## Steps

1. **Gather information**
   - Extract any details the user already provided
   - Ask only for what is missing:
     - **To** — recipient email address(es)
     - **Subject** — email subject line
     - **Body** — email body (plain text or Markdown)

2. **Run the script**
   ```bash
   python scripts/python/send_email.py --to "$TO" --subject "$SUBJECT" --body "$BODY"
   ```

3. **Verify the result**
   - Confirm the success message: `✓ Email sent successfully.`
   - On failure, check SMTP credentials and network connectivity

## Options

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--to` | Yes | — | Recipient email address(es), comma-separated |
| `--subject` | Yes | — | Email subject |
| `--body` | Yes | — | Email body text |
| `--dry-run` | No | `false` | Preview without sending |

## Examples

### Basic usage

```
/send-email to user@example.com about "Weekly Report" with the content of report.md
```
