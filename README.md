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
    ├── EVENT.MD         # Event definition (required)
    ├── scripts/            # Optional: bundled scripts
    ├── references/         # Optional: bundled references
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
- **Messaging** - Post to Slack, Teams, Discord
- **APIs** - Call any HTTP API with authentication

## Reference Implementation

The **AEP Agent** is a complete reference implementation featuring:

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
