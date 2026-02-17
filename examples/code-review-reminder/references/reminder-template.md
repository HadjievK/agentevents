# Code Review Reminder Template

## Slack DM Template
```
👋 Hi {reviewer_name}, you have a pending review request:

📋 {pr_title}
🔗 {pr_link}
👤 Author: {author_name}
⏰ Waiting: {waiting_time}
📊 Size: {changed_lines} lines across {changed_files} files

{pr_description}
```

## Escalation Message (for >3 days old)
```
⚠️ Code Review Escalation

A pull request has been waiting for review for {waiting_time}:

📋 {pr_title}
🔗 {pr_link}
👤 Author: {author_name}
👔 Author's Manager: {manager_name}
```

## Variables
- `{reviewer_name}` - Name of the reviewer
- `{pr_title}` - Title of the pull request
- `{pr_link}` - GitHub PR URL
- `{author_name}` - Name of the PR author
- `{waiting_time}` - How long PR has been waiting (e.g., "2 days, 4 hours")
- `{changed_lines}` - Total lines added/removed
- `{changed_files}` - Number of files changed
- `{pr_description}` - First comment/description from PR
- `{manager_name}` - Name of author's manager
