---
name: sprint-summary
description: Generate and send weekly sprint summary report
schedule: "0 16 * * FRI"
enabled: true
---

# Sprint Summary Event

This event generates a comprehensive sprint summary report and sends it to stakeholders every Friday at 4 PM.

## Event Instructions

Generate a comprehensive sprint summary report and send to stakeholders.

### Data Collection

1. **Sprint Metrics (from JIRA)**
   - Story points: planned vs. completed
   - Tickets: total, completed, carried over
   - Velocity: current sprint vs. 4-sprint average
   - Cycle time: average ticket completion time
   - Bug count: opened vs. closed

2. **Code Activity (from GitHub)**
   - PRs merged: count and total lines changed
   - Code review metrics: average review time
   - Contributors: active developers this sprint
   - Repository activity: commits, branches

3. **Quality Metrics**
   - Test coverage: current percentage and trend
   - CI/CD success rate: builds passed/failed
   - Production incidents: count and severity
   - Technical debt: new issues vs. resolved

4. **Team Insights**
   - Team capacity: planned vs. actual (accounting for PTO)
   - Blocked items: tickets and duration
   - Dependencies: external blockers
   - Process improvements: retrospective action items

### Report Structure

```
📊 Sprint [X] Summary - [Start Date] to [End Date]

## 🎯 Sprint Goals
[List sprint goals from JIRA sprint description]
✅ Goal 1: Completed
⚠️ Goal 2: Partially completed (X of Y stories)
❌ Goal 3: Not started (blocked by...)

## 📈 Key Metrics

| Metric | Planned | Actual | Trend |
|--------|---------|--------|-------|
| Story Points | X | Y | [↑/↓/→] |
| Tickets | X | Y | [↑/↓/→] |
| Bugs Closed | - | X | [↑/↓/→] |
| Velocity | - | Y | [vs 4-sprint avg: Z] |

[Generate trend charts using chart-generator skill]

## 🚀 Highlights
- Feature X shipped to production
- Performance improved by Y%
- Technical debt reduced by Z hours
- New team member onboarded

## 🏆 Top Contributors
[Based on PR merges, code reviews, ticket completions]
1. [Name] - [Key achievement]
2. [Name] - [Key achievement]
3. [Name] - [Key achievement]

## ⚠️ Challenges
- [Issue 1]: [Impact] - [Mitigation plan]
- [Issue 2]: [Impact] - [Mitigation plan]

## 🔄 Carried Over
[List tickets moving to next sprint with reasons]
- [TICKET-123]: [Title] - [Reason for carryover]

## 📅 Next Sprint Preview
- Sprint [X+1] starts [Date]
- Focus areas: [Area 1], [Area 2]
- Key milestones: [Milestone 1], [Milestone 2]

## 📊 Detailed Metrics
[Link to Grafana dashboard]
[Link to JIRA sprint board]
[Link to GitHub insights]
```

### Charts to Generate

1. Burndown chart (planned vs. actual)
2. Velocity trend (last 8 sprints)
3. Bug trend (opened vs. closed)
4. Cycle time distribution

### Recipients

- team@company.com (full report)
- stakeholders@company.com (executive summary only)
- engineering-leads@company.com (full report + raw data)

### Formatting

- HTML email with embedded charts (PNG)
- Responsive design for mobile viewing
- Color coding: green (on track), yellow (at risk), red (blocked)
- Collapsible sections for detailed metrics

### Attachments

- PDF version of full report
- CSV export of all metrics
- Sprint retrospective notes (if available)

## Skills

This event uses the following skills:
- jira-analytics
- github-stats
- chart-generator
- mail-compose

## Configuration

- **Max retries:** 2
- **Timeout:** 300 seconds

## Metadata

- **Author:** engineering-management
- **Version:** 1.5.0
- **Tags:** sprint, reporting, metrics
