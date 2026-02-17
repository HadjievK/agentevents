# Contributing to Agent Events

Thank you for your interest in contributing to Agent Events! This document provides guidelines and instructions for contributing.

## Ways to Contribute

### 1. Create Example Events

Share your event definitions to inspire others:

```bash
# Fork the repository
git clone https://github.com/HadjievK/agentevents.git
cd agentevents

# Create new event directory structure
mkdir -p examples/your-event-name/{references,scripts}
cd examples/your-event-name

# Create EVENT.MD with YAML frontmatter and Markdown content
cat > EVENT.MD << EOF
---
name: your-event-name
description: What your event does
schedule: "0 9 * * *"
enabled: true
---

# Your Event Name

Event description and overview.

## Event Instructions

Clear instructions for what the agent should do:
- Step 1
- Step 2
- Step 3

## Skills

This event uses the following skills:
- skill-name
- another-skill

## Configuration

- **Max retries:** 2
- **Timeout:** 120 seconds

## Metadata

- **Author:** your-github-username
- **Version:** 1.0.0
- **Tags:** tag1, tag2
EOF

# Add reference files for configuration and templates (optional)
cat > references/config.md << EOF
# Configuration Reference

## Settings

- Key: Description
- Key: Description
EOF

# Add scripts for helper functions (optional)
# mkdir scripts

# Commit and push
git add .
git commit -m "Add example: your-event-name"
git push origin main
```

**Event directory structure:**
```
examples/your-event-name/
├── EVENT.MD              # Event definition (required)
├── references/           # Optional: configuration, templates, data files
│   ├── config.md
│   └── template.md
└── scripts/              # Optional: bundled helper scripts
```

**Good example events:**
- Solve a common problem
- Have clear, specific instructions
- Use standard skills where possible
- Include templates and configuration in references/
- Add helper scripts in scripts/ if needed
- Follow the EVENT.MD format with YAML frontmatter

### 2. Build Skills

Create reusable Agent Skills that events can use:

```bash
mkdir -p skills/your-skill-name
cd skills/your-skill-name

cat > SKILL.md << EOF
---
name: your-skill-name
description: What this skill does and when to use it
license: MIT
metadata:
  author: your-github-username
  version: "1.0.0"
---

# Your Skill Name

Clear instructions for the agent on how to use this skill.

## When to Use

- Specific trigger 1
- Specific trigger 2

## Instructions

Step-by-step guidance...

## Examples

Concrete examples of usage...
EOF
```

**Good skills:**
- Are focused on one capability
- Have clear activation criteria
- Include examples
- Handle edge cases

### 3. Create MCP Servers

Integrate new external services:

```python
# mcp_servers/your_service_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("your-service")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="your_service_action",
            description="What this tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "your_service_action":
        # Your implementation
        result = do_something(arguments["param"])
        
        return [TextContent(
            type="text",
            text=f"Result: {result}"
        )]
```

**Good MCP servers:**
- Follow MCP specification
- Handle authentication securely
- Include error handling
- Have comprehensive docstrings

### 4. Improve Documentation

Help others understand Agent Events:

- Add tutorials
- Create video walkthroughs
- Write blog posts
- Improve API docs
- Add code comments

### 5. Report Bugs

Found a bug? Help us fix it:

1. Check [existing issues](https://github.com/HadjievK/agentevents/issues)
2. Create new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs. actual behavior
   - System info (OS, Python version)
   - Relevant logs

### 6. Suggest Features

Have an idea? We'd love to hear it:

1. Check [existing discussions](https://github.com/HadjievK/agentevents/discussions)
2. Create new discussion with:
   - Use case description
   - Proposed solution
   - Alternative approaches
   - Impact assessment

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment tool (venv, conda)

### Clone and Install

```bash
# Clone repository
git clone https://github.com/HadjievK/agentevents.git
cd agentevents

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_event_engine.py
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black .
isort .

# Check linting
flake8 .

# Type check
mypy .
```

Pre-commit hooks run these automatically.

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clear, focused commits
- Follow code style guidelines
- Add tests for new features
- Update documentation

### 3. Test Thoroughly

```bash
# Run tests
pytest

# Check formatting
black --check .
isort --check .
flake8 .

# Type check
mypy .
```

### 4. Commit with Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add webhook trigger support"
git commit -m "fix: handle missing event.yaml gracefully"
git commit -m "docs: add deployment guide"
git commit -m "test: add event engine unit tests"
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style (formatting, no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create Pull Request on GitHub with:
- Clear title (use conventional commit format)
- Description of changes
- Link to related issue(s)
- Screenshots/GIFs if UI changes

### 6. Review Process

- Maintainers will review your PR
- Address feedback promptly
- Keep PR scope focused
- Be patient and respectful

## Code Review Guidelines

### For Contributors

- Respond to feedback constructively
- Explain your approach if unclear
- Be open to alternative solutions
- Update PR based on feedback

### For Reviewers

- Be kind and constructive
- Explain reasoning behind suggestions
- Approve when ready, request changes if needed
- Thank contributors for their time

## Event Best Practices

### Clear Instructions

**Good:**
```markdown
## Event Instructions

Check the production API health endpoint every 5 minutes.
If response time > 500ms or status != 200:
- Create PagerDuty incident with P2 priority
- Include endpoint URL, response time, and status code
- Tag with "performance" label
```

**Bad:**
```markdown
## Event Instructions

Monitor the API and alert if there are problems
```

### Specific Schedules

**Good:**
```markdown
---
name: api-health-check
description: Monitor API health and alert on degradation
schedule: "*/5 * * * *"  # Every 5 minutes
enabled: true
---
```
or
```markdown
schedule: "0 9 * * MON-FRI"  # Weekdays at 9 AM
```

**Bad:**
```markdown
schedule: "* * * * *"  # Every minute (too frequent)
```

### Skill References

**Good:**
```markdown
## Skills

This event uses the following skills:
- api-monitoring       # Clear capability
- pagerduty-alert      # Specific integration
```

**Bad:**
```markdown
## Skills

This event uses the following skills:
- general-helper       # Too vague
- do-stuff             # Unclear purpose
```

### Well-Organized References

**Good reference files:**
- `alert-thresholds.md` - Configuration values with explanations
- `email-template.md` - HTML/text templates with variable placeholders
- `team-structure.md` - Team members, contacts, escalation paths
- `runbook.md` - Troubleshooting procedures and remediation steps

**Example references structure:**
```
references/
├── alert-thresholds.md
├── team-members.md
├── mail-template.md
└── runbook.md
```

## Skill Best Practices

### Clear Activation Criteria

**Good:**
```markdown
## When to Use

Use this skill when:
- User asks to analyze a PDF document
- File extension is .pdf
- Need to extract text or tables from PDF
```

**Bad:**
```markdown
## When to Use

Use this skill for documents.
```

### Comprehensive Instructions

**Good:**
```markdown
## Instructions

1. **Validate input**: Ensure file path exists and is readable
2. **Extract text**: Use pypdf library for text extraction
3. **Parse tables**: Identify table structures via layout analysis
4. **Return results**: Format as markdown with sections for text and tables
5. **Handle errors**: If extraction fails, return error message with details
```

**Bad:**
```markdown
## Instructions

Extract the text from the PDF.
```

### Concrete Examples

**Good:**
```markdown
## Example

Input: `/path/to/invoice.pdf`

Output:
```
# Invoice Analysis

**Text Content:**
Invoice #12345
Date: 2024-01-15
Total: $1,234.56

**Tables:**
| Item | Qty | Price |
|------|-----|-------|
| ...  | ... | ...   |
```
```

**Bad:**
```markdown
## Example

Shows what the PDF contains.
```

## MCP Server Best Practices

### Error Handling

**Good:**
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        result = await api_call(arguments)
        return [TextContent(type="text", text=f"Success: {result}")]
    except ValueError as e:
        return [TextContent(type="text", text=f"Invalid input: {e}")]
    except ConnectionError as e:
        return [TextContent(type="text", text=f"Network error: {e}")]
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]
```

**Bad:**
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    result = await api_call(arguments)  # No error handling
    return [TextContent(type="text", text=result)]
```

### Authentication

**Good:**
```python
def get_api_token():
    """Get API token from environment or cache."""
    token = os.environ.get("API_TOKEN")
    if not token:
        raise ValueError("API_TOKEN not set in environment")
    return token

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    token = get_api_token()
    headers = {"Authorization": f"Bearer {token}"}
    # ... use headers
```

**Bad:**
```python
# Hardcoded credentials
API_TOKEN = "sk-1234567890abcdef"  # DON'T DO THIS
```

### Documentation

**Good:**
```python
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="send_email",
            description="Send email via SMTP. Supports HTML and plain text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body (HTML or plain text)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        )
    ]
```

**Bad:**
```python
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="send_email",
            description="Sends email",
            inputSchema={"type": "object"}  # Missing properties
        )
    ]
```

## Testing Guidelines

### Event Tests

```python
def test_event_discovery():
    """Test that events are discovered correctly."""
    events = discover_events(Path("tests/fixtures/events"))
    
    assert len(events) == 2
    assert events[0]["name"] == "test-event"
    assert events[0]["schedule"] == "*/5 * * * *"

def test_event_execution():
    """Test that events execute and produce expected results."""
    event = load_event("test-event")
    result = execute_event(event, mock_agent)
    
    assert result["status"] == "success"
    assert "tool_calls" in result
```

### MCP Server Tests

```python
@pytest.mark.asyncio
async def test_mail_send():
    """Test mail sending via MCP server."""
    server = MailServer()
    
    result = await server.call_tool(
        "mail_send",
        {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Test message"
        }
    )
    
    assert "success" in result[0].text.lower()
```

## Documentation Guidelines

### README Structure

1. **Overview** - What is it?
2. **Quick Start** - Get running fast
3. **Examples** - Show real usage
4. **API Reference** - Detailed docs
5. **Contributing** - How to help

### Code Comments

**Good:**
```python
def parse_cron_schedule(schedule: str) -> dict:
    """
    Parse cron schedule string into components.
    
    Args:
        schedule: Cron format string (e.g., "*/5 * * * *")
        
    Returns:
        dict: Components with keys: minute, hour, day, month, weekday
        
    Raises:
        ValueError: If schedule format is invalid
        
    Example:
        >>> parse_cron_schedule("0 9 * * MON-FRI")
        {'minute': '0', 'hour': '9', 'day': '*', 'month': '*', 'weekday': 'MON-FRI'}
    """
    # Implementation...
```

**Bad:**
```python
def parse_cron_schedule(schedule):
    # Parse the schedule
    # Implementation...
```

## Questions?

- **General:** [GitHub Discussions](https://github.com/HadjievK/agentevents/discussions)
- **Bugs:** [GitHub Issues](https://github.com/HadjievK/agentevents/issues)
- **Security:** Email security@agentevents.io

Thank you for contributing to Agent Events! 🎉
