# MCP Mail Server

This is the mail MCP server available in this environment.

## Available tool

### `mail_send`

Sends an email.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `to` | list of strings | yes | Recipient email addresses |
| `subject` | string | yes | Mail subject line |
| `body` | string | yes | Mail body (plain text or markdown) |

**Returns:**

| Field | Type | Description |
|---|---|---|
| `status` | string | `"sent"` or `"error"` |
| `message_id` | string | Unique ID for the sent message |
| `error` | string | Error details (only if status is `"error"`) |

## Example call

```
mail_send(
  to=["alice@example.com", "bob@example.com"],
  subject="Hello",
  body="This is a test."
)
→ { status: "sent", message_id: "msg-0042" }
```
