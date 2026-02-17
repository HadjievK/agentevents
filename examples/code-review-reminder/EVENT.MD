---
name: code-review-reminder
description: Remind team members about pending code reviews
schedule: "0 */4 * * *"
enabled: true
---

# Code Review Reminder Event

This event finds pull requests that need attention and sends targeted reminders to reviewers.

## Event Instructions

Find pull requests that need attention and send targeted reminders to reviewers.

**Criteria for stale PRs:**
- Open for 24+ hours
- No reviews yet OR reviews requested changes 48+ hours ago
- Not in draft mode
- Labeled "ready for review"

**For each stale PR, check:**
- Assigned reviewers
- Review request date
- PR complexity (files changed, lines added/deleted)
- Author availability (check if they're on PTO/OOO)

### Reminder Actions

1. **Slack DM to each reviewer:**
   ```
   👋 Hi [name], you have a pending review request:
   
   📋 [PR title]
   🔗 [PR link]
   👤 Author: [author name]
   ⏰ Waiting: [X hours/days]
   📊 Size: [+X -Y lines across N files]
   
   [Brief PR description from first comment]
   ```

2. **If >3 days old, escalate:**
   - Tag author's manager in #code-reviews channel
   - Include PR link and waiting time
   - Suggest reassigning if reviewer unavailable

3. **Special handling:**
   - If reviewer on PTO → skip DM, notify author to reassign
   - If PR has merge conflicts → notify author first
   - If PR has failing CI → skip until tests pass

### Do NOT remind if:
- Reviewer already commented today
- PR was updated in last 4 hours
- PR is marked as blocked or on-hold

### Summary Email

At end of each check, send summary to engineering-leads@company.com:
- Total PRs pending review
- Average wait time
- Top 5 longest-waiting PRs
- Reviewers with most pending reviews

## Skills

This event uses the following skills:
- github-pr-analysis
- slack-notify
- team-calendar

## Configuration

- **Max retries:** 1
- **Timeout:** 180 seconds

## Metadata

- **Author:** engineering-team
- **Version:** 1.0.0
- **Tags:** code-review, reminder, productivity
