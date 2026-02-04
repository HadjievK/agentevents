# Agent Events

**Schedule the Future with Event-Driven AI Agents**

Agent Events is an open format for giving AI agents scheduled workflows and event-driven automation. Define what should happen, when it should happen, and let agents handle the execution.

🌐 **Website:** [agentevents.io](https://agentevents.io)

## Overview

Agent Events are folders containing event definitions, skills, and schedules that agents can discover and execute automatically. They enable agents to:

- **Run scheduled workflows** - Daily reports, weekly summaries, recurring tasks
- **Monitor proactively** - System health checks, alert thresholds, anomaly detection
- **Automate recurring tasks** - Team communications, ticket triage, data processing
- **React to triggers** - CI/CD events, external webhooks, calendar notifications

## Why Agent Events?

Most AI agents operate in request-response mode without the ability to schedule future actions or maintain long-running workflows. Agent Events solve this by providing:

- **Time-based scheduling** - Cron-format schedules for precise timing control
- **Skill integration** - Compose complex workflows from reusable Agent Skills
- **State management** - Events can maintain context between executions
- **Audit trails** - Full execution history and logging
- **Portability** - Write once, deploy across multiple agent platforms

## Quick Example

```yaml
# events/team-status-mail/event.yaml
name: team-status-mail
description: Send daily status email to the team
schedule: "0 9 * * MON-FRI"  # Every weekday at 9 AM
enabled: true

skills:
  - mail-compose
  - team-context

instruction: |
  Draft and send a brief status email to the team with:
  - Yesterday's key accomplishments
  - Current blockers
  - Today's priorities
  
  Use the team distribution list from team-context skill.
```

That's it. The agent discovers this event, loads the referenced skills, and executes on schedule.

## Event Format Specification

### Directory Structure

```
events/
└── <event-name>/
    ├── event.yaml          # Event definition (required)
    ├── skills/             # Optional: bundled skills
    │   └── <skill-name>/
    │       └── SKILL.md
    └── assets/             # Optional: templates, data files
        └── templates/
```

### event.yaml Schema

```yaml
# Required fields
name: string                 # Unique event identifier
description: string          # Human-readable description
schedule: string             # Cron format schedule
enabled: boolean             # Enable/disable execution

# Optional fields
skills: string[]             # Skills to load (local or global)
instruction: string          # Natural language task description
metadata:                    # Custom metadata
  author: string
  version: string
  tags: string[]

# Advanced options
max_retries: integer         # Retry failed executions (default: 3)
timeout: integer             # Max execution time in seconds
dependencies: string[]       # Other events that must succeed first
```

### Schedule Format

Uses standard cron syntax:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * *
```

**Examples:**
- `*/10 * * * *` - Every 10 minutes
- `0 9 * * MON-FRI` - Weekdays at 9 AM
- `0 */4 * * *` - Every 4 hours
- `0 16 * * FRI` - Fridays at 4 PM

## Architecture

### Event Engine

The Event Engine is responsible for:

1. **Discovery** - Scan event directories and parse `event.yaml` files
2. **Scheduling** - Maintain cron-based schedule for each enabled event
3. **Execution** - When an event fires:
   - Load referenced skills (if any)
   - Pass instruction + skills to agent
   - Execute agent response (tool calls)
   - Log execution and results
4. **State Management** - Track execution history, maintain event context

### Integration with Agent Skills

Agent Events work seamlessly with [Agent Skills](https://agentskills.io):

- **Skills provide capabilities** - PDF processing, mail sending, data analysis
- **Events orchestrate execution** - When to use which skills, with what context
- **Progressive loading** - Skills only loaded when event needs them

```yaml
# Event references skills
skills:
  - mail-compose      # Global skill from .claude/skills/
  - ./custom-skill    # Local skill in events/<name>/skills/
```

### Tool Integration (MCP)

Events can leverage Model Context Protocol (MCP) servers for external integrations:

- **Mail** - Send emails via Microsoft Graph, SMTP, or other providers
- **Calendar** - Read/write calendar events
- **ITSM** - Create/update tickets in Jira, ServiceNow, etc.
- **Messaging** - Post to Slack, Teams, Discord
- **APIs** - Call any HTTP API with authentication

## Reference Implementation

The **AEP Agent** (Agent Event Planning) is a complete reference implementation featuring:

- **Gradio UI** - Web interface for managing events
- **Claude Integration** - Uses Claude Sonnet 4 for intelligent execution
- **Event Engine** - Background scheduler with cron support
- **MCP Servers** - Mail, calendar, ITSM integrations
- **Execution History** - Full audit trail with logs

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Gradio UI                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ Events   │  │ History  │  │ Chat with Claude         │  │
│  │ Manager  │  │ Viewer   │  │ (Test events manually)   │  │
│  └──────────┘  └──────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      Event Engine                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Scheduler (cron)                                     │   │
│  │ - Scans events/ directory                            │   │
│  │ - Maintains schedule for enabled events              │   │
│  │ - Fires events at scheduled times                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Event Executor                                        │   │
│  │ - Loads event definition                             │   │
│  │ - Loads referenced skills                            │   │
│  │ - Calls Claude API with instruction + skills + tools │   │
│  │ - Executes tool calls (MCP servers)                  │   │
│  │ - Logs results to event_log/                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Claude API (Sonnet 4)                    │
│  - Reads instruction                                        │
│  - Applies skills                                           │
│  - Returns tool calls                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Servers                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Mail     │  │ Calendar │  │ ITSM     │  │ Custom     │  │
│  │ (Graph)  │  │ (Google) │  │ (SAP)    │  │ Tools      │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
aep-agent/
├── main.py                 # Gradio UI + Claude integration
├── event_engine.py         # Event scheduler and executor
├── start.py                # Entry point (handles Windows UTF-8)
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (API keys, etc.)
│
├── events/                 # Event definitions
│   └── send-team-mail/
│       ├── event.yaml
│       └── skills/
│           └── mail-compose/
│               └── SKILL.md
│
├── event_log/              # Execution history
│   └── YYYY-MM-DD.jsonl    # Daily log files
│
└── mcp_servers/            # MCP server implementations
    ├── mail_server.py      # Microsoft Graph integration
    ├── calendar_server.py  # Google Calendar integration
    └── itsm_server.py      # SAP Cloud ALM integration
```

## Example Use Cases

### 1. Daily Standup Report

**Event:** `daily-standup`
**Schedule:** `0 9 * * MON-FRI` (Weekdays at 9 AM)
**Action:** Compile updates from Slack, JIRA, GitHub and send formatted summary

```yaml
name: daily-standup
description: Compile and send daily standup report
schedule: "0 9 * * MON-FRI"
enabled: true

skills:
  - slack-history
  - jira-query
  - github-activity
  - mail-compose

instruction: |
  Gather team updates from the last 24 hours:
  - Slack messages in #engineering channel
  - JIRA tickets moved to "In Progress" or "Done"
  - GitHub PRs merged or opened
  
  Compile into a clean summary and email to team@company.com
```

### 2. Code Review Reminder

**Event:** `code-review-reminder`
**Schedule:** `0 */4 * * *` (Every 4 hours)
**Action:** Find stale PRs and remind reviewers

```yaml
name: code-review-reminder
description: Remind about pending code reviews
schedule: "0 */4 * * *"
enabled: true

skills:
  - github-pr-analysis
  - slack-notify

instruction: |
  Find pull requests that:
  - Have been open for 24+ hours
  - Have no reviews yet
  - Are marked as "ready for review"
  
  For each PR, send a Slack DM to the assigned reviewer with:
  - PR title and link
  - Author
  - How long it's been waiting
  - Brief description
```

### 3. System Health Check

**Event:** `system-health-check`
**Schedule:** `*/15 * * * *` (Every 15 minutes)
**Action:** Monitor application metrics and alert on anomalies

```yaml
name: system-health-check
description: Monitor system health and alert on issues
schedule: "*/15 * * * *"
enabled: true

skills:
  - metrics-analysis
  - log-parser
  - pagerduty-alert

instruction: |
  Check system health:
  - CPU usage (alert if >80% for 10+ minutes)
  - Memory usage (alert if >90%)
  - Error rate (alert if >1% of requests)
  - Response time (alert if p95 >500ms)
  
  If any threshold exceeded:
  - Create PagerDuty incident
  - Include relevant log excerpts
  - Suggest likely root cause
```

### 4. Weekly Sprint Summary

**Event:** `sprint-summary`
**Schedule:** `0 16 * * FRI` (Fridays at 4 PM)
**Action:** Generate sprint report with metrics and charts

```yaml
name: sprint-summary
description: Generate and send weekly sprint summary
schedule: "0 16 * * FRI"
enabled: true

skills:
  - jira-analytics
  - github-stats
  - chart-generator
  - mail-compose

instruction: |
  Generate sprint summary report:
  
  Metrics:
  - Story points completed vs. planned
  - Bugs opened vs. closed
  - PRs merged
  - Code review cycle time
  
  Create charts for each metric and compile into HTML email.
  Send to team@ and stakeholders@company.com
```

## Integration Guide

### For Agent Developers

To add Agent Events support to your agent:

1. **Event Discovery**
   ```python
   import yaml
   from pathlib import Path
   
   def discover_events(events_dir: Path):
       events = []
       for event_dir in events_dir.iterdir():
           if not event_dir.is_dir():
               continue
           event_file = event_dir / "event.yaml"
           if event_file.exists():
               with open(event_file) as f:
                   event = yaml.safe_load(f)
                   event['path'] = event_dir
                   events.append(event)
       return events
   ```

2. **Schedule Management**
   ```python
   from croniter import croniter
   from datetime import datetime
   
   def should_fire(event, now=None):
       now = now or datetime.now()
       if not event.get('enabled', True):
           return False
       
       schedule = event['schedule']
       cron = croniter(schedule, now)
       
       # Check if event should fire in current minute
       next_run = cron.get_next(datetime)
       return next_run.minute == now.minute and next_run.hour == now.hour
   ```

3. **Event Execution**
   ```python
   def execute_event(event, agent):
       # Load skills
       skills = load_skills(event.get('skills', []))
       
       # Build prompt
       prompt = build_prompt(
           instruction=event['instruction'],
           skills=skills,
           context=get_event_context(event)
       )
       
       # Execute with agent
       result = agent.execute(prompt, tools=get_mcp_tools())
       
       # Log result
       log_execution(event, result)
       
       return result
   ```

### For Skill Authors

Events work seamlessly with Agent Skills. Just reference skills in your event:

```yaml
skills:
  - mail-compose              # Global skill
  - ./custom-analysis         # Local skill in event folder
```

Skills are loaded on-demand when the event fires, keeping memory usage efficient.

## OAuth 2.0 Device Code Flow (for Microsoft Graph)

The reference implementation includes Microsoft Graph integration for sending emails. It uses **Device Code Flow** for authentication - the simplest OAuth method that requires no app registration.

### How It Works

1. **First run:** Agent requests a device code from Microsoft
2. **User action:** Paste code at `microsoft.com/devicelogin`, approve with MFA
3. **Token saved:** Refresh token cached locally, valid for ~90 days
4. **Subsequent runs:** Silent token refresh, no user action needed

### Configuration

Only one environment variable needed:

```bash
GRAPH_USER_EMAIL=user@company.com
```

No client IDs, tenant IDs, or secrets required.

### Endpoints

- Device code: `https://login.microsoftonline.com/organizations/oauth2/v2.0/devicecode`
- Token exchange: `https://login.microsoftonline.com/organizations/oauth2/v2.0/token`
- Mail API: `https://graph.microsoft.com/v1.0/me/sendMail`

### Error Handling

- **401 Unauthorized:** Automatically refreshes token and retries
- **Device code expired:** Shows new code, user re-authenticates
- **Network errors:** Retries with exponential backoff

## MCP Server Examples

### Mail Server (Microsoft Graph)

```python
# mcp_servers/mail_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import requests

server = Server("mail-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="mail_send",
            description="Send email via Microsoft Graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "mail_send":
        token = ensure_token()  # OAuth token from device flow
        
        response = requests.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "message": {
                    "subject": arguments["subject"],
                    "body": {"contentType": "HTML", "content": arguments["body"]},
                    "toRecipients": [{"emailAddress": {"address": arguments["to"]}}]
                }
            }
        )
        
        return [TextContent(
            type="text",
            text=f"Email sent successfully" if response.ok else f"Error: {response.text}"
        )]
```

### ITSM Server (SAP Cloud ALM)

```python
# mcp_servers/itsm_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("itsm-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="itsm_create_ticket",
            description="Create incident ticket in SAP Cloud ALM",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "assignee": {"type": "string"}
                },
                "required": ["title", "description"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "itsm_create_ticket":
        # SAP Cloud ALM API call
        ticket_id = create_calm_incident(
            title=arguments["title"],
            description=arguments["description"],
            priority=arguments.get("priority", "medium"),
            assignee=arguments.get("assignee")
        )
        
        return [TextContent(
            type="text",
            text=f"Created ticket {ticket_id}"
        )]
```

## Deployment Options

### Local Development

```bash
# Clone repository
git clone https://github.com/HadjievK/agentevents.git
cd agentevents/aep-agent

# Install dependencies
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python start.py
```

Visit `http://localhost:7860`

### Production (Cloudflare Tunnel)

Expose local agent to the internet securely:

```bash
# Install cloudflared
# Windows: download from cloudflare.com/products/tunnel
# macOS: brew install cloudflare/cloudflare/cloudflared

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create aep-agent

# Configure (create ~/.cloudflared/config.yml)
tunnel: <tunnel-id>
credentials-file: /path/to/<tunnel-id>.json

ingress:
  - hostname: agent.yourdomain.com
    service: http://localhost:7860
  - service: http_status:404

# Route DNS
cloudflared tunnel route dns aep-agent agent.yourdomain.com

# Run tunnel
cloudflared tunnel run aep-agent

# In another terminal, run the agent
python start.py
```

Now accessible at `https://agent.yourdomain.com`

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "start.py"]
```

```bash
docker build -t aep-agent .
docker run -p 7860:7860 --env-file .env aep-agent
```

## Security Considerations

### API Keys

- Store in `.env` file (never commit to Git)
- Use environment variables in production
- Rotate keys regularly

### OAuth Tokens

- Token cache stored in `token_cache.json`
- Refresh tokens valid for 90 days
- Access tokens refreshed automatically
- Cache should be `.gitignore`d

### Event Validation

- Validate cron syntax before scheduling
- Sanitize skill names to prevent path traversal
- Validate instruction length to prevent prompt injection

### Execution Sandboxing

- Run events in isolated context
- Limit tool call rate
- Set execution timeouts
- Log all tool calls for audit

## Roadmap

### v1.0 (Current)
- ✅ Event format specification
- ✅ Reference implementation (AEP Agent)
- ✅ Cron-based scheduling
- ✅ Agent Skills integration
- ✅ MCP tool support
- ✅ Microsoft Graph OAuth
- ✅ Execution logging

### v1.1 (Q2 2026)
- 🔲 Event dependencies (run A before B)
- 🔲 Conditional execution (if X then run Y)
- 🔲 Event chaining (output of A → input of B)
- 🔲 Parallel execution for independent events
- 🔲 State persistence between runs

### v1.2 (Q3 2026)
- 🔲 Webhook triggers (external events)
- 🔲 Calendar integration (sync with Google/Outlook)
- 🔲 Event templates library
- 🔲 VS Code extension
- 🔲 CLI tool for event management

### v2.0 (Q4 2026)
- 🔲 Multi-agent coordination
- 🔲 Distributed event execution
- 🔲 Event marketplace
- 🔲 Advanced monitoring & analytics
- 🔲 Enterprise features (RBAC, SSO)

## Contributing

We welcome contributions! Areas where help is needed:

- **Skill library:** Create reusable skills for common tasks
- **MCP servers:** Integrate with more external services
- **Agent integrations:** Add Agent Events support to other platforms
- **Documentation:** Tutorials, guides, examples
- **Testing:** Edge cases, performance, reliability

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Community

- **Website:** [agentevents.io](https://agentevents.io)
- **GitHub:** [github.com/HadjievK/agentevents](https://github.com/HadjievK/agentevents)
- **Discussions:** [GitHub Discussions](https://github.com/HadjievK/agentevents/discussions)
- **Issues:** [GitHub Issues](https://github.com/HadjievK/agentevents/issues)

## Related Projects

- **[Agent Skills](https://agentskills.io)** - Modular capabilities for agents (skills)
- **[Model Context Protocol](https://modelcontextprotocol.io)** - Standard for tool integration (MCP)
- **[Claude Code](https://code.claude.com)** - Anthropic's coding agent
- **[Cursor](https://cursor.sh)** - AI-powered code editor

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [Agent Skills](https://agentskills.io) format
- Built with [Anthropic Claude](https://www.anthropic.com/claude) API
- Uses [Model Context Protocol](https://modelcontextprotocol.io) for tool integration
- Authentication via [Microsoft Graph](https://learn.microsoft.com/en-us/graph/) Device Code Flow

---

**Made with ❤️ by the Agent Events community**

*Schedule the future. Automate the present.*
