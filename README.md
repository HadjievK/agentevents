# Agent Events

**Schedule the Future with Event-Driven AI Agents**

Agent Events is an open format for giving AI agents scheduled workflows and event-driven automation.
🌐 **Website:** [agentevents.io](https://agentevents.io)

## Overview

Agent Events are folders containing event definitions, scripts(optional),references(optional), assets(optional) and schedules that agents can discover and execute automatically. They enable agents to:

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
### EVENT.MD Format

The EVENT.md file must contain YAML frontmatter followed by Markdown content:

```markdown
---
name: event-name
description: Brief description of what this event does
schedule: "0 9 * * MON-FRI"
enabled: true
---

# Event Instructions

Natural language instructions for the agent describing:
- What task to perform
- When to execute (schedule above)
- What skills or tools to use
- Expected outputs or actions

## Skills

Optional reference to skills (from bundled skills/ directory or global):
- skill-name-1
- skill-name-2

## Additional Context

Any additional context, examples, or guidelines for execution.
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


## Contributing

We welcome contributions!

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
