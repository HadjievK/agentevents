---
name: daily-standup
description: Compile and send daily team status report
schedule: "0 9 * * MON-FRI"
enabled: true
---

# Daily Standup Event

This event gathers team updates from the last 24 hours and compiles a daily standup report.

## Event Instructions

Gather team updates from the last 24 hours and compile a daily standup report.

**Sources to check:**
- Slack #engineering channel - key announcements and discussions
- JIRA board - tickets moved to "In Progress" or "Done"
- GitHub repositories - PRs merged, opened, or reviewed

**Report format:**
Create an HTML email with these sections:

1. **Yesterday's Wins** (bullet list)
   - Tickets completed with links
   - PRs merged with titles
   - Key accomplishments mentioned in Slack

2. **Today's Focus** (bullet list)
   - In-progress tickets
   - Scheduled meetings
   - Blockers or dependencies

3. **Team Updates** (if any)
   - Announcements
   - Process changes
   - Upcoming deadlines

**Styling:**
- Use clean HTML with sections
- Include emoji for visual hierarchy (✅ 🚀 ⚠️)
- Link all ticket and PR references
- Keep total length under 500 words

**Recipients:** Send to team@company.com

If no significant updates from any source, send brief message: "Quiet day - no major updates to report."

## Skills

This event uses the following skills:
- slack-history
- jira-query
- github-activity
- mail-compose

## Configuration

- **Max retries:** 2
- **Timeout:** 120 seconds

## Metadata

- **Author:** engineering-team
- **Version:** 1.2.0
- **Tags:** communication, standup, daily
