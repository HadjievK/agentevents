# Agent Events Format Specification

**Version:** 1.0  
**Status:** Draft  
**Last Updated:** February 2026

## Abstract

Agent Events is an open format for defining scheduled, event-driven workflows that AI agents can discover and execute automatically. This specification defines the structure, semantics, and execution model for Agent Events.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Event Structure](#event-structure)
4. [Schedule Format](#schedule-format)
5. [Skill Integration](#skill-integration)
6. [Execution Model](#execution-model)
7. [State Management](#state-management)
8. [Security Considerations](#security-considerations)
9. [Conformance](#conformance)

## 1. Introduction

### 1.1 Purpose

Agent Events enable AI agents to:
- Execute workflows on time-based schedules
- Maintain long-running automated processes
- React to external triggers and events
- Compose complex behaviors from reusable skills

### 1.2 Design Goals

- **Simplicity:** Easy to author and understand
- **Portability:** Work across different agent platforms
- **Composability:** Integrate with Agent Skills and MCP tools
- **Auditability:** Full execution history and logging
- **Reliability:** Graceful error handling and recovery

### 1.3 Non-Goals

- Real-time event processing (use webhooks or message queues instead)
- Complex workflow orchestration (use workflow engines for that)
- Data transformation pipelines (use ETL tools)

## 2. Core Concepts

### 2.1 Event

An **Event** is a schedulable unit of work defined by:
- **Name:** Unique identifier
- **Schedule:** When to execute (cron format)
- **Instruction:** What to do (natural language)
- **Skills:** Capabilities to load (optional)
- **Metadata:** Additional properties (optional)

### 2.2 Event Engine

An **Event Engine** is responsible for:
1. **Discovery:** Scanning directories for event definitions
2. **Scheduling:** Maintaining execution schedule
3. **Execution:** Running events at scheduled times
4. **Logging:** Recording execution history

### 2.3 Execution Context

Each event execution has:
- **Timestamp:** When execution started
- **Event ID:** Which event fired
- **Loaded Skills:** Which skills were activated
- **Tool Calls:** Which MCP tools were invoked
- **Result:** Execution outcome (success/failure/error)

## 3. Event Structure

### 3.1 Directory Layout

Events are organized as directories containing at minimum an `event.yaml` file:

```
events/
└── <event-name>/
    ├── event.yaml          # Event definition (REQUIRED)
    ├── skills/             # Local skills (OPTIONAL)
    │   └── <skill-name>/
    │       └── SKILL.md
    └── assets/             # Templates, data (OPTIONAL)
        └── <filename>
```

### 3.2 Naming Conventions

Event names MUST:
- Be lowercase with hyphens (kebab-case)
- Start with a letter
- Contain only letters, numbers, and hyphens
- Be unique within the events directory

**Valid:** `daily-report`, `code-review-reminder`, `health-check-01`  
**Invalid:** `Daily Report`, `code_review`, `1st-check`, `my.event`

### 3.3 event.yaml Schema

#### 3.3.1 Required Fields

```yaml
name: string              # Event identifier (REQUIRED)
description: string       # Human-readable description (REQUIRED)
schedule: string          # Cron schedule (REQUIRED)
enabled: boolean          # Enable/disable execution (REQUIRED)
```

#### 3.3.2 Optional Fields

```yaml
instruction: string       # Task description in natural language
skills: string[]          # Skills to load (local or global paths)
metadata:                 # Custom metadata
  author: string
  version: string
  tags: string[]
max_retries: integer      # Retry failed executions (default: 3)
timeout: integer          # Max execution time in seconds (default: 300)
dependencies: string[]    # Events that must succeed first
```

#### 3.3.3 Example

```yaml
name: daily-standup
description: Compile and send daily team status report
schedule: "0 9 * * MON-FRI"
enabled: true

instruction: |
  Gather updates from the last 24 hours:
  - Slack messages in #engineering
  - JIRA tickets moved to Done
  - GitHub PRs merged
  
  Compile into HTML email and send to team@company.com

skills:
  - slack-history
  - jira-query
  - github-activity
  - mail-compose

metadata:
  author: engineering-team
  version: "1.2.0"
  tags: ["communication", "standup"]
  
max_retries: 2
timeout: 120
```

### 3.4 Field Semantics

#### 3.4.1 name

- **Type:** String
- **Required:** Yes
- **Constraints:** Must match directory name, must be unique
- **Purpose:** Identifier for logging, UI display, and dependencies

#### 3.4.2 description

- **Type:** String
- **Required:** Yes
- **Constraints:** 1-500 characters recommended
- **Purpose:** Human-readable explanation of what the event does

#### 3.4.3 schedule

- **Type:** String
- **Required:** Yes
- **Format:** Standard cron format (5 fields)
- **Validation:** Must be valid cron expression
- **Purpose:** Determines when event fires

#### 3.4.4 enabled

- **Type:** Boolean
- **Required:** Yes
- **Purpose:** Master switch to enable/disable event execution
- **Note:** Disabled events are discovered but never executed

#### 3.4.5 instruction

- **Type:** String
- **Required:** No (but strongly recommended)
- **Format:** Natural language, supports markdown
- **Purpose:** Tells the agent what to do when event fires
- **Best Practice:** Be specific, include context, define success criteria

#### 3.4.6 skills

- **Type:** Array of strings
- **Required:** No
- **Format:** Skill names or paths
- **Resolution:**
  - Plain names → search global skills directory
  - Relative paths → search event's local skills directory
  - Absolute paths → use exact path
- **Purpose:** Load specialized capabilities on demand

#### 3.4.7 metadata

- **Type:** Object
- **Required:** No
- **Purpose:** Store additional properties not defined by spec
- **Flexibility:** Implementations MAY ignore unknown metadata fields

#### 3.4.8 max_retries

- **Type:** Integer
- **Required:** No
- **Default:** 3
- **Constraints:** 0-10 recommended
- **Purpose:** How many times to retry on failure

#### 3.4.9 timeout

- **Type:** Integer
- **Required:** No
- **Default:** 300 (5 minutes)
- **Unit:** Seconds
- **Purpose:** Max execution time before forced termination

#### 3.4.10 dependencies

- **Type:** Array of strings
- **Required:** No
- **Format:** Event names
- **Purpose:** Declare events that must complete successfully first
- **Behavior:** If dependency failed, skip execution

## 4. Schedule Format

### 4.1 Cron Syntax

Events use standard cron format with 5 fields:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * *
```

### 4.2 Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `,` | Value list | `0,30 * * * *` = every hour at :00 and :30 |
| `-` | Range | `0 9-17 * * *` = 9 AM to 5 PM |
| `/` | Step | `*/15 * * * *` = every 15 minutes |
| `MON-FRI` | Named range | `0 9 * * MON-FRI` = weekdays at 9 AM |

### 4.3 Examples

```yaml
schedule: "*/5 * * * *"         # Every 5 minutes
schedule: "0 * * * *"           # Every hour at :00
schedule: "0 9 * * *"           # Daily at 9 AM
schedule: "0 9 * * MON-FRI"     # Weekdays at 9 AM
schedule: "0 9 1 * *"           # First day of month at 9 AM
schedule: "0 9 * * SUN"         # Every Sunday at 9 AM
schedule: "0 */4 * * *"         # Every 4 hours
schedule: "0 9-17 * * MON-FRI"  # Business hours, every hour
```

### 4.4 Validation

Implementations MUST:
- Validate cron syntax before scheduling
- Reject invalid expressions with clear error messages
- Handle edge cases (leap years, DST transitions)

## 5. Skill Integration

### 5.1 Agent Skills Compatibility

Agent Events integrate seamlessly with [Agent Skills](https://agentskills.io):

- Events can reference skills by name
- Skills are loaded on-demand when event fires
- Multiple events can share the same skills
- Skills follow progressive disclosure pattern

### 5.2 Skill Resolution

When an event references a skill, the engine searches in order:

1. **Local skills:** `events/<event-name>/skills/<skill-name>/`
2. **Global skills:** `~/.claude/skills/<skill-name>/`
3. **System skills:** Implementation-defined paths

### 5.3 Skill Loading

When loading a skill:

1. **Read SKILL.md:** Parse YAML frontmatter + markdown body
2. **Extract metadata:** Name, description, version
3. **Load instructions:** Full markdown body
4. **Make available:** Pass to agent as available capability

### 5.4 Example

Event definition:
```yaml
skills:
  - mail-compose              # Global skill
  - ./custom-analysis         # Local skill
```

Directory structure:
```
events/daily-report/
├── event.yaml
└── skills/
    └── custom-analysis/
        └── SKILL.md

~/.claude/skills/
└── mail-compose/
    └── SKILL.md
```

## 6. Execution Model

### 6.1 Execution Lifecycle

```
Discovery → Scheduling → Trigger → Load → Execute → Log → Cleanup
```

#### 6.1.1 Discovery Phase

1. Scan `events/` directory
2. For each subdirectory:
   - Check for `event.yaml`
   - Parse and validate
   - Add to event registry
3. Log discovery summary

#### 6.1.2 Scheduling Phase

1. For each discovered event:
   - Parse cron schedule
   - Calculate next execution time
   - Add to scheduler queue
2. Start scheduler loop

#### 6.1.3 Trigger Phase

When scheduler fires:
1. Check if event is enabled
2. Check dependencies (if any)
3. Verify not already running (if max_concurrency=1)
4. Proceed to execution or skip

#### 6.1.4 Load Phase

1. Load event definition
2. Resolve and load skills
3. Build execution context
4. Prepare agent prompt

#### 6.1.5 Execute Phase

1. Call agent API with:
   - Instruction from event
   - Loaded skills
   - Available MCP tools
2. Process agent response:
   - Extract tool calls
   - Execute each tool
   - Collect results
3. Handle errors with retry logic

#### 6.1.6 Log Phase

1. Record execution:
   - Timestamp
   - Event ID
   - Status (success/failure/error)
   - Tool calls made
   - Duration
   - Error messages (if any)
2. Append to log file
3. Update execution history

#### 6.1.7 Cleanup Phase

1. Release resources
2. Calculate next execution
3. Reschedule event

### 6.2 Error Handling

#### 6.2.1 Retry Logic

On execution failure:
1. Check retry count < max_retries
2. Wait with exponential backoff
3. Retry execution
4. If all retries exhausted, log final failure

Backoff formula: `delay = min(2^retry_count * base_delay, max_delay)`

Example: 1s, 2s, 4s, 8s, 16s (capped at 30s)

#### 6.2.2 Failure Types

| Failure Type | Retry? | Action |
|--------------|--------|--------|
| Network timeout | Yes | Retry with backoff |
| Invalid credentials | No | Log error, skip retries |
| Rate limit | Yes | Retry after cooldown |
| Malformed response | Yes | Retry up to max |
| Tool not found | No | Log error, skip retries |
| Timeout exceeded | Yes | Retry with longer timeout |

### 6.3 Concurrency

Implementations SHOULD:
- Execute events concurrently when possible
- Respect dependencies between events
- Limit total concurrent executions
- Prevent same event from running twice simultaneously (default)

### 6.4 State Persistence

Between executions, events can maintain state:

```yaml
# Read state from previous run
last_run: 2024-02-03T09:00:00Z
last_status: success
processed_items: ["item1", "item2"]

# Update state for next run
current_run: 2024-02-04T09:00:00Z
current_status: success
processed_items: ["item1", "item2", "item3"]
```

Implementations MAY store state in:
- JSON files in event directory
- Database tables
- Key-value stores
- Implementation-defined locations

## 7. State Management

### 7.1 Execution History

Implementations MUST maintain execution history including:
- Timestamp
- Event ID
- Status (success/failure/error)
- Duration
- Tool calls
- Error messages

### 7.2 Log Format

Recommended format: JSON Lines (one JSON object per line)

```jsonl
{"timestamp":"2024-02-03T09:00:00Z","event":"daily-standup","status":"success","duration":12.5,"tool_calls":["mail_send"]}
{"timestamp":"2024-02-03T09:15:00Z","event":"health-check","status":"success","duration":2.1,"tool_calls":["http_get"]}
{"timestamp":"2024-02-03T09:30:00Z","event":"daily-standup","status":"failure","duration":5.3,"error":"Network timeout"}
```

### 7.3 Log Rotation

Implementations SHOULD:
- Rotate logs daily or when size exceeds threshold
- Compress old logs
- Archive or delete logs after retention period
- Provide log viewing and search capabilities

## 8. Security Considerations

### 8.1 Event Validation

Implementations MUST:
- Validate event.yaml syntax before loading
- Sanitize skill names to prevent path traversal
- Validate instruction length to prevent prompt injection
- Check cron syntax to prevent CPU exhaustion

### 8.2 Execution Sandboxing

Implementations SHOULD:
- Run events in isolated contexts
- Limit resource usage (CPU, memory, network)
- Set execution timeouts
- Rate limit tool calls

### 8.3 Credential Management

Implementations MUST:
- Never store credentials in event.yaml
- Use environment variables or secure vaults
- Support OAuth/token-based authentication
- Rotate credentials regularly

### 8.4 Audit Logging

Implementations MUST:
- Log all event executions
- Log all tool calls with parameters
- Log authentication attempts
- Retain logs for compliance requirements

### 8.5 Access Control

Implementations SHOULD:
- Require authentication to manage events
- Support role-based access control
- Audit privilege escalation attempts
- Encrypt sensitive data at rest and in transit

## 9. Conformance

### 9.1 Conformance Levels

#### Level 1: Basic (REQUIRED)

- Discover events from directory
- Parse and validate event.yaml
- Schedule events using cron
- Execute events at scheduled times
- Log execution history

#### Level 2: Skills (RECOMMENDED)

- Load and apply Agent Skills
- Support local and global skills
- Progressive skill disclosure

#### Level 3: Advanced (OPTIONAL)

- Event dependencies
- State persistence
- Concurrent execution
- Webhook triggers
- Advanced error recovery

### 9.2 Implementation Requirements

Conformant implementations MUST:
- Support all required fields in event.yaml
- Follow cron syntax specification
- Implement basic error handling
- Maintain execution logs
- Validate event definitions

Conformant implementations SHOULD:
- Support Agent Skills integration
- Provide UI for event management
- Support MCP tool integration
- Implement retry logic
- Handle edge cases gracefully

### 9.3 Validation

To test conformance:

1. **Discovery:** Create test events, verify they're found
2. **Scheduling:** Verify events fire at correct times
3. **Execution:** Verify instructions are followed
4. **Logging:** Verify logs contain required fields
5. **Error Handling:** Verify retries and error messages

### 9.4 Reference Implementation

The [AEP Agent](https://github.com/HadjievK/agentevents) is a reference implementation demonstrating Level 2 conformance.

## Appendix A: Examples

See [examples/](examples/) directory for complete event definitions.

## Appendix B: FAQ

**Q: Can I use environment variables in event.yaml?**  
A: Not directly in YAML, but instructions can reference them: "Use API key from $API_KEY"

**Q: What happens if an event takes longer than its schedule interval?**  
A: Default behavior is to skip the overlapping execution. Configure max_concurrency if needed.

**Q: Can events trigger other events?**  
A: Yes, via dependencies field or by having one event modify another's schedule.

**Q: How do I pass data between event executions?**  
A: Use state persistence or external storage (database, files, etc.)

**Q: Are there limits on instruction length?**  
A: Implementations MAY limit instruction length. Recommended max: 10,000 characters.

## Appendix C: Change Log

**Version 1.0 (February 2026)**
- Initial specification
- Core event format
- Schedule syntax
- Skills integration
- Execution model

## Appendix D: References

- [Agent Skills Specification](https://agentskills.io/specification)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Cron Format Standard](https://en.wikipedia.org/wiki/Cron)
- [YAML 1.2 Specification](https://yaml.org/spec/1.2/)

---

**Specification Authors:** Agent Events Community  
**License:** CC0 1.0 Universal (Public Domain)  
**Repository:** https://github.com/HadjievK/agentevents
