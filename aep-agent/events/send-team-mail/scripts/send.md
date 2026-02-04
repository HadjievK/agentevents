# Send Team Status Mail

This script runs every time the `send-team-mail` event fires.

## Steps

1. Read the recipient list from `references/team-members.md`.
   Each line that is not blank and does not start with `#` is one email address.

2. Read the mail body from `references/mail-template.md`.

3. Call the MCP mail server tool `mail_send` with:
   - **to**      → the list of addresses from step 1
   - **subject** → `Dev Team — Status Update`
   - **body**    → the content from step 2

4. Log the result (success / failure + timestamp).

## MCP tool signature

The mail MCP server exposes one tool:

```
mail_send(to: list[str], subject: str, body: str) → {status, message_id}
```

`to` is a list of email addresses.
`status` is `"sent"` or `"error"`.
`message_id` is a unique ID for tracking if needed.
```
