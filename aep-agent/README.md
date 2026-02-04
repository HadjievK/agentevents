# AEP Agent - Reference Implementation

**Agent Event Planning (AEP) Agent** is a complete reference implementation of the Agent Events specification, demonstrating how to build an event-driven AI agent with scheduled workflows.

## Features

- ✅ **Gradio Web UI** - Manage events, view history, chat with Claude
- ✅ **Event Engine** - Cron-based scheduler with automatic execution
- ✅ **Claude Sonnet 4 Integration** - Intelligent task execution
- ✅ **Agent Skills Support** - Load and apply modular capabilities
- ✅ **MCP Tool Integration** - Mail, calendar, ITSM, and custom tools
- ✅ **Execution History** - Full audit trail with logs
- ✅ **Microsoft Graph OAuth** - Device Code Flow for email (no app registration)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))
- (Optional) Microsoft 365 account for email sending

### Installation

```bash
# Clone the repository
git clone https://github.com/HadjievK/agentevents.git
cd agentevents/aep-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API key
# Required:
ANTHROPIC_API_KEY=sk-ant-...

# Optional (for email sending):
GRAPH_USER_EMAIL=your-email@company.com
```

### Run

```bash
python start.py
```

Visit `http://localhost:7860` in your browser.

## UI Overview

### 📅 Events Tab

Manage your events:
- View all discovered events
- See schedule and status
- Enable/disable events
- Create new events
- Edit event definitions

### 📊 History Tab

Review execution history:
- See past event executions
- Filter by event, status, date
- View detailed logs
- Export history as JSON

### 💬 Chat Tab

Interact with Claude:
- Test event instructions manually
- Debug event behavior
- Ask questions about events
- Get help with configuration

## Usage

### Create Your First Event

1. **Create event directory:**
   ```bash
   mkdir -p events/hello-world
   ```

2. **Create event.yaml:**
   ```yaml
   name: hello-world
   description: Send a daily hello email
   schedule: "0 9 * * *"  # Every day at 9 AM
   enabled: true
   
   instruction: |
     Send a friendly "Hello World" email to test@example.com
     Subject: "Hello from Agent Events"
     Body: "This is an automated email from AEP Agent!"
   ```

3. **Refresh the UI** - Event appears in Events tab

4. **Test manually** - Click "Run Now" to test before enabling schedule

5. **View logs** - Check History tab to see execution results

### Add Skills to an Event

```yaml
name: smart-report
description: Generate report using skills
schedule: "0 9 * * MON"
enabled: true

skills:
  - data-analysis
  - chart-generator
  - mail-compose

instruction: |
  1. Analyze sales data from last week using data-analysis skill
  2. Create trend charts using chart-generator skill
  3. Compile into email report using mail-compose skill
  4. Send to sales-team@company.com
```

Skills are loaded automatically from:
- `~/.claude/skills/` (global)
- `events/<event-name>/skills/` (local)

### Configure Email Sending

To send real emails via Microsoft Graph:

1. **Set email in .env:**
   ```bash
   GRAPH_USER_EMAIL=your-email@company.com
   ```

2. **Run the agent** - On first mail send:
   - Browser opens to `microsoft.com/devicelogin`
   - Paste the device code shown in terminal
   - Approve with your Microsoft Authenticator
   - Token cached for ~90 days

3. **Subsequent runs** - Silent token refresh, no login needed

**Without this setup:** Emails are logged but not sent (mock mode).

## Architecture

```
┌──────────────────────────────────────────────┐
│             Gradio Web UI                    │
│  Events Manager │ History Viewer │ Chat      │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│            Event Engine                      │
│  • Discovers events from events/ directory   │
│  • Schedules based on cron expressions       │
│  • Executes at scheduled times               │
│  • Loads skills on demand                    │
│  • Calls Claude API with context             │
│  • Executes tool calls (MCP)                 │
│  • Logs all activity                         │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│           Claude API (Sonnet 4)              │
│  • Reads instruction + skills                │
│  • Determines actions                        │
│  • Returns tool calls                        │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│             MCP Tool Servers                 │
│  Mail │ Calendar │ ITSM │ Custom Tools       │
└──────────────────────────────────────────────┘
```

## File Structure

```
aep-agent/
├── main.py              # Gradio UI + Claude integration
├── event_engine.py      # Event scheduler and executor
├── graph_mail.py        # Microsoft Graph email integration
├── start.py             # Entry point (UTF-8 handling)
├── requirements.txt     # Python dependencies
├── .env                 # Configuration (create from .env.example)
│
├── events/              # Your event definitions
│   └── send-team-mail/
│       ├── event.yaml
│       └── skills/      # Optional local skills
│
└── event_log/           # Execution history
    └── 2024-02-04.jsonl
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...        # Your Claude API key

# Optional - Email
GRAPH_USER_EMAIL=user@company.com   # For Microsoft Graph email
GRAPH_TENANT_ID=uuid                # Only if /organizations/ blocked

# Optional - Logging
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
LOG_FILE=aep-agent.log              # Custom log file path
```

## Deployment

### Local Development

```bash
python start.py
# Visit http://localhost:7860
```

### Production (Cloudflare Tunnel)

Expose to internet securely:

```bash
# Install cloudflared
# Windows: download from cloudflare.com
# macOS: brew install cloudflare/cloudflare/cloudflared

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create aep-agent

# Configure (~/.cloudflared/config.yml)
tunnel: <tunnel-id>
credentials-file: ~/.cloudflared/<tunnel-id>.json
ingress:
  - hostname: agent.yourdomain.com
    service: http://localhost:7860
  - service: http_status:404

# Route DNS
cloudflared tunnel route dns aep-agent agent.yourdomain.com

# Run tunnel (in one terminal)
cloudflared tunnel run aep-agent

# Run agent (in another terminal)
python start.py
```

Now accessible at `https://agent.yourdomain.com`

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860
CMD ["python", "start.py"]
```

```bash
docker build -t aep-agent .
docker run -p 7860:7860 --env-file .env aep-agent
```

## Troubleshooting

### Events Not Firing

**Symptom:** Event enabled but never executes

**Solutions:**
1. Check cron syntax: `*/5 * * * *` (every 5 min)
2. Verify `enabled: true` in event.yaml
3. Check event engine logs in terminal
4. Ensure no syntax errors in event.yaml

### Skills Not Loading

**Symptom:** "Skill not found" errors

**Solutions:**
1. Check skill name matches directory: `skills/mail-compose/`
2. Verify SKILL.md exists in skill directory
3. Check YAML frontmatter in SKILL.md is valid
4. Try absolute path: `~/.claude/skills/mail-compose`

### Email Not Sending

**Symptom:** No emails received

**Solutions:**
1. Check `GRAPH_USER_EMAIL` is set in .env
2. Complete OAuth flow (first run only)
3. Check token_cache.json was created
4. Review event_log for mail_send errors
5. Try mock mode first (unset GRAPH_USER_EMAIL)

### Permission Errors

**Symptom:** "Access denied" or "403 Forbidden"

**Solutions:**
1. Re-authenticate: delete token_cache.json, run again
2. Check user has mail send permissions
3. Verify email address matches account
4. Try `/organizations/` → set GRAPH_TENANT_ID if needed

### High CPU Usage

**Symptom:** Agent uses too much CPU

**Solutions:**
1. Reduce event frequency (longer intervals)
2. Add timeouts to prevent long-running events
3. Limit concurrent event execution
4. Check for infinite loops in instructions

## Development

### Add a New MCP Tool

1. **Create tool file:**
   ```bash
   touch mcp_tools/my_tool.py
   ```

2. **Implement tool:**
   ```python
   from mcp.server import Server
   from mcp.types import Tool, TextContent
   
   server = Server("my-tool")
   
   @server.list_tools()
   async def list_tools():
       return [Tool(name="my_action", ...)]
   
   @server.call_tool()
   async def call_tool(name: str, arguments: dict):
       # Your implementation
       return [TextContent(type="text", text="Result")]
   ```

3. **Register in main.py** (if not auto-discovered)

### Run Tests

```bash
pip install pytest pytest-cov
pytest
pytest --cov=. --cov-report=html
```

### Code Style

```bash
pip install black isort flake8 mypy
black .
isort .
flake8 .
mypy .
```

## Examples

See [examples/](../examples/) directory for:
- Daily standup reports
- Code review reminders
- System health monitoring
- Sprint summaries

## Learn More

- [Agent Events Specification](../SPECIFICATION.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Example Events](../examples/)
- [Agent Skills](https://agentskills.io)
- [Model Context Protocol](https://modelcontextprotocol.io)

## Support

- **Issues:** [GitHub Issues](https://github.com/HadjievK/agentevents/issues)
- **Discussions:** [GitHub Discussions](https://github.com/HadjievK/agentevents/discussions)
- **Website:** [agentevents.io](https://agentevents.io)

## License

MIT License - see [../LICENSE](../LICENSE) for details.
