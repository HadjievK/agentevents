# Example Events

This directory contains real-world examples of Agent Events demonstrating various use cases and patterns.

## Available Examples

### 1. Daily Standup Report
**Schedule:** Weekdays at 9 AM  
**Purpose:** Compile team updates from Slack, JIRA, and GitHub into a daily email

Demonstrates:
- Multi-source data aggregation
- HTML email generation
- Scheduled business-day execution
- Skill composition (slack-history, jira-query, github-activity, mail-compose)

[View event definition →](daily-standup/event.yaml)

---

### 2. Code Review Reminder
**Schedule:** Every 4 hours  
**Purpose:** Remind reviewers about stale pull requests

Demonstrates:
- Conditional logic (only remind if criteria met)
- Personalized notifications via Slack DM
- Escalation workflows (tag managers for old PRs)
- Smart filtering (skip if reviewer on PTO, PR has conflicts)

[View event definition →](code-review-reminder/event.yaml)

---

### 3. System Health Check
**Schedule:** Every 15 minutes  
**Purpose:** Monitor application metrics and create incidents when thresholds exceeded

Demonstrates:
- Continuous monitoring
- Threshold-based alerting
- Root cause analysis
- PagerDuty integration
- False positive prevention

[View event definition →](system-health-check/event.yaml)

---

### 4. Sprint Summary Report
**Schedule:** Fridays at 4 PM  
**Purpose:** Generate comprehensive sprint report with metrics and charts

Demonstrates:
- Complex data analysis
- Chart generation
- Multi-audience reporting (team, stakeholders, management)
- Trend analysis over time
- PDF and CSV attachments

[View event definition →](sprint-summary/event.yaml)

---

## Usage

### Try an Example

1. **Copy event to your events directory:**
   ```bash
   cp -r examples/daily-standup events/
   ```

2. **Customize the event.yaml:**
   - Update recipients
   - Adjust schedule
   - Modify instructions to match your workflow

3. **Enable the event:**
   ```yaml
   enabled: true
   ```

4. **Test immediately (optional):**
   Via UI or CLI, trigger the event manually to verify it works before waiting for scheduled time.

### Modify an Example

Most examples need customization:

```yaml
# Before (generic)
instruction: |
  Send email to team@company.com

# After (specific to your org)
instruction: |
  Send email to engineering@mycompany.com
  CC: management@mycompany.com
```

### Create Variations

Use examples as templates:

```bash
# Create variation
cp -r examples/daily-standup events/weekly-summary

# Edit event.yaml
vim events/weekly-summary/event.yaml
```

Change:
- `schedule`: From daily to weekly
- `instruction`: Expand scope to full week
- `name`: Update to match new purpose

## Common Patterns

### Pattern 1: Multi-Source Aggregation

```yaml
skills:
  - slack-history
  - jira-query
  - github-activity
  - mail-compose

instruction: |
  1. Gather data from all sources
  2. Correlate and deduplicate
  3. Format into cohesive report
  4. Send via email
```

**Used in:** daily-standup, sprint-summary

---

### Pattern 2: Conditional Execution

```yaml
instruction: |
  1. Query for items matching criteria
  2. If no items found, do nothing
  3. If items found, take action
  4. Send summary of actions taken
```

**Used in:** code-review-reminder, system-health-check

---

### Pattern 3: Threshold-Based Alerting

```yaml
instruction: |
  1. Check metric value
  2. Compare against threshold
  3. If exceeded:
     - Gather context
     - Analyze root cause
     - Create incident
     - Notify on-call
  4. If normal, do nothing
```

**Used in:** system-health-check

---

### Pattern 4: Periodic Reporting

```yaml
instruction: |
  1. Collect metrics for time period
  2. Calculate trends and comparisons
  3. Generate visualizations
  4. Compile into report
  5. Distribute to stakeholders
```

**Used in:** sprint-summary, daily-standup

---

## Skills Referenced

These examples assume the following skills are available:

### Communication Skills
- **mail-compose** - Send formatted emails
- **slack-notify** - Post Slack messages and DMs

### Data Source Skills
- **slack-history** - Read Slack channel messages
- **jira-query** - Query JIRA tickets and boards
- **jira-analytics** - Analyze JIRA metrics
- **github-activity** - Get GitHub repository activity
- **github-stats** - Calculate GitHub metrics
- **github-pr-analysis** - Analyze pull request status

### Monitoring Skills
- **metrics-analysis** - Query and analyze application metrics
- **log-parser** - Parse and analyze log files
- **team-calendar** - Check team availability and PTO

### Integration Skills
- **pagerduty-integration** - Create/update PagerDuty incidents
- **chart-generator** - Generate charts from data

### Creating Skills

If a referenced skill doesn't exist, create it:

```bash
mkdir -p ~/.claude/skills/mail-compose
cat > ~/.claude/skills/mail-compose/SKILL.md << 'EOF'
---
name: mail-compose
description: Compose and send formatted emails via SMTP or API
---

# Mail Compose Skill

Send HTML or plain text emails with attachments.

## When to Use

- Sending reports or notifications
- Distributing documents to team
- Automated email communications

## Available Tools

- `mail_send(to, subject, body, html=true)` - Send email
- `mail_send_with_attachment(to, subject, body, attachments)` - Send with files

## Instructions

1. Format body as HTML or markdown
2. Include all necessary context
3. Use clear subject lines
4. Handle recipient lists properly
EOF
```

## Tips

### Start Simple

Begin with a basic version:
```yaml
instruction: |
  Send a test email to me@company.com with today's date.
```

Once working, gradually add complexity.

### Test Locally First

Run event manually before enabling on schedule:
```bash
# Via CLI
aep-agent execute daily-standup

# Via UI
Navigate to event → Click "Test Now"
```

### Monitor Execution

Check logs after first few runs:
```bash
tail -f event_log/$(date +%Y-%m-%d).jsonl
```

### Iterate Based on Results

Review execution logs and refine:
- Too much data? Add filtering
- Too little context? Gather more sources
- Wrong format? Adjust instructions
- Timing issues? Change schedule

## Troubleshooting

### Event Not Firing

1. Check `enabled: true` in event.yaml
2. Verify cron schedule syntax
3. Check event engine logs
4. Ensure dependencies succeeded (if any)

### Skills Not Loading

1. Verify skill names match exactly
2. Check skill paths (local vs. global)
3. Validate SKILL.md format
4. Review skill discovery logs

### Tool Calls Failing

1. Check MCP server is running
2. Verify authentication/credentials
3. Review tool parameter format
4. Check network connectivity

### Wrong Results

1. Make instructions more specific
2. Add examples in instruction
3. Include edge case handling
4. Verify skill instructions are clear

## Contributing Examples

Have a great event to share? We'd love to add it!

1. Create event in `examples/your-event-name/`
2. Include comprehensive `event.yaml`
3. Add README.md explaining:
   - What it does
   - When to use it
   - How to customize it
   - Required skills/tools
4. Test thoroughly
5. Submit pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Learn More

- [Event Specification](../SPECIFICATION.md) - Formal format documentation
- [Skills Documentation](https://agentskills.io) - Agent Skills standard
- [MCP Documentation](https://modelcontextprotocol.io) - Tool integration
- [AEP Agent](../README.md) - Reference implementation

---

**Questions?** Open an issue or discussion on [GitHub](https://github.com/HadjievK/agentevents)
