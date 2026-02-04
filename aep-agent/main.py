"""
main.py — AEP Claude Agent
───────────────────────────
A simple AI agent that manages AEP events.

• Chat with Claude Sonnet — ask questions, create events, fire them manually.
• Event engine runs in the background — scheduled events fire automatically.
• Live dashboard shows loaded events, their status, and a log of every firing.

Run:
    pip install -r requirements.txt
    cp .env.example .env          # paste your ANTHROPIC_API_KEY
    python main.py                # opens http://localhost:7860
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import gradio as gr
import yaml
from dotenv import load_dotenv
from anthropic import Anthropic

# ─── env ─────────────────────────────────────────────────────────────────────
load_dotenv()
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    print("⚠️  ANTHROPIC_API_KEY not set.  Copy .env.example → .env and fill it in.")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ─── paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
EVENTS_DIR  = BASE_DIR / "events"

# ─── import our event engine ─────────────────────────────────────────────────
import event_engine as ee  # NLSchedule, MCPClient, AEPEventEngine, EventDef, parse_event_md

# ══════════════════════════════════════════════════════════════════════════════
# SHARED STATE   (main thread + engine thread both read/write)
# ══════════════════════════════════════════════════════════════════════════════

event_log: list[dict] = []          # every firing appends here
engine: ee.AEPEventEngine | None = None
engine_loop: asyncio.AbstractEventLoop | None = None   # the engine's asyncio loop


# ══════════════════════════════════════════════════════════════════════════════
# MOCK MCP MAIL SERVER
# ══════════════════════════════════════════════════════════════════════════════

# ── helper: parse "to" whether it arrives as a list or raw .md text ───────
def _parse_recipients(raw_to) -> list[str]:
    if isinstance(raw_to, str):
        return [line.strip() for line in raw_to.splitlines()
                if line.strip() and not line.strip().startswith("#")]
    return raw_to


# ── MOCK sender (used when GRAPH_CLIENT_ID is not set) ────────────────────
async def _mock_mail_send(to: list[str], subject: str, body: str) -> dict:
    """Simulates sending — logs to event_log, no network."""
    await asyncio.sleep(0.3)
    msg_id = f"mock-{len(event_log) + 1:04d}"
    event_log.append({
        "time":    datetime.now(tz=timezone.utc).strftime("%H:%M:%S UTC"),
        "event":   "send-team-mail",
        "action":  "mail_send (mock)",
        "status":  "✅ simulated",
        "detail":  f"→ {len(to)} recipient(s)  |  {msg_id}",
        "to":      ", ".join(to),
        "subject": subject,
    })
    return {"status": "sent", "message_id": msg_id}


# ── REAL sender (used when GRAPH_CLIENT_ID is set) ────────────────────────
async def _real_mail_send(to: list[str], subject: str, body: str) -> dict:
    """Calls Microsoft Graph /me/sendMail via graph_mail module."""
    import graph_mail
    result = await graph_mail.send_mail(to=to, subject=subject, body=body)
    status_label = "✅ sent" if result["status"] == "sent" else f"❌ {result.get('error','?')}"
    event_log.append({
        "time":    datetime.now(tz=timezone.utc).strftime("%H:%M:%S UTC"),
        "event":   "send-team-mail",
        "action":  "mail_send (Graph)",
        "status":  status_label,
        "detail":  f"→ {len(to)} recipient(s)  |  {result.get('message_id', 'n/a')}",
        "to":      ", ".join(to),
        "subject": subject,
    })
    return result


# ── ROUTER: picks real or mock based on .env ───────────────────────────────
_USE_GRAPH = bool(os.environ.get("GRAPH_USER_EMAIL", "").strip())

async def mail_send(params: dict) -> dict:
    """
    MCP tool entry point.  Parses params, routes to Graph or mock.
    Set GRAPH_CLIENT_ID in .env to use real Outlook sending.
    """
    to      = _parse_recipients(params.get("to", []))
    subject = params.get("subject", "(no subject)")
    body    = params.get("body", "")

    if _USE_GRAPH:
        print(f"  📨 Sending via Microsoft Graph…")
        return await _real_mail_send(to, subject, body)
    else:
        print(f"  📨 Sending via mock (set GRAPH_USER_EMAIL in .env to send real mail)")
        return await _mock_mail_send(to, subject, body)


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE BOOT   (runs once at import time, before Gradio starts)
# ══════════════════════════════════════════════════════════════════════════════

def _boot_engine():
    """Create the engine, load events, start the scheduler in a daemon thread."""
    global engine, engine_loop

    # MCP client with our mock mail tool
    mcp = ee.MCPClient()
    mcp.register_tool("mail_send", mail_send)

    # create engine, load events from disk
    engine = ee.AEPEventEngine(events_root=EVENTS_DIR, mcp=mcp)
    engine.load()

    # run the scheduler loop in a background thread
    def _run():
        global engine_loop
        engine_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(engine_loop)
        engine_loop.run_until_complete(engine.run())   # blocks forever

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    print("⏳ Event engine started in background thread.")

_boot_engine()


# ══════════════════════════════════════════════════════════════════════════════
# CLAUDE AGENT
# ══════════════════════════════════════════════════════════════════════════════

def _event_state_snapshot() -> str:
    """Build a text block describing current events — injected into every prompt."""
    if not engine:
        return "No events loaded."
    lines = []
    for ev in engine.events:
        status = "⏳ scheduled"
        last   = engine._last_fired.get(ev.name)
        if last:
            status = f"last fired {last.strftime('%H:%M:%S UTC')}"
        lines.append(
            f"  • {ev.name}\n"
            f"      description: {ev.description.strip()}\n"
            f"      type:        {ev.event_type}\n"
            f"      schedule:    {ev.schedule_raw}\n"
            f"      action:      {ev.action.get('mcp') or ev.action.get('script')}\n"
            f"      status:      {status}"
        )
    return "\n".join(lines) if lines else "No events loaded."


def _recent_log(n: int = 5) -> str:
    """Last N log entries as text for the prompt."""
    if not event_log:
        return "  (no events have fired yet)"
    for entry in event_log[-n:]:
        yield (f"  [{entry['time']}] {entry['event']} → {entry['status']}  {entry['detail']}")
    return "\n".join(list(_recent_log(n)))


SYSTEM_PROMPT_TEMPLATE = """\
You are the AEP Event Agent — a smart assistant that manages event-driven workflows.

You have access to an event engine that discovers and runs events defined as folders
on disk.  Each event folder contains an EVENT.md (schedule + description) and
scripts/ + references/ that define what happens when it fires.

══ CURRENT EVENTS ══
{event_state}

══ RECENT EVENT LOG ══
{recent_log}

══ WHAT YOU CAN DO ══

1. Answer questions about events, schedules, and the event log.

2. Fire an event manually.  When the user asks you to trigger / run / fire an event,
   respond with your explanation AND include this exact XML block:

     <aep_action>
     {{"action": "fire", "event": "<event-name>"}}
     </aep_action>

3. Create a new event.  When the user wants a new scheduled event, respond with your
   explanation AND include:

     <aep_action>
     {{"action": "create", "name": "<kebab-case-name>", "description": "<one line>", "schedule": "<natural language>", "mcp_tool": "<tool name>"}}
     </aep_action>

   Use natural-language schedules: "every 5 minutes", "every hour", "every Tuesday at 9 AM".

4. List events — just describe what's loaded.  No special tag needed.

══ RULES ══
• Keep responses concise and friendly.
• If the user asks to create or fire something, always include the <aep_action> block.
• If you are unsure about a schedule or event name, ask the user to clarify.
• The mock mail MCP tool is called "mail_send".  More tools can be added later.
"""


def build_system_prompt() -> str:
    log_lines = []
    for entry in event_log[-5:]:
        log_lines.append(f"  [{entry['time']}] {entry['event']} → {entry['status']}  {entry['detail']}")
    return SYSTEM_PROMPT_TEMPLATE.format(
        event_state = _event_state_snapshot(),
        recent_log  = "\n".join(log_lines) if log_lines else "  (no events have fired yet)",
    )


def parse_aep_action(text: str) -> dict | None:
    """Extract <aep_action>...</aep_action> JSON from Claude's response."""
    m = re.search(r"<aep_action>\s*(.*?)\s*</aep_action>", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


async def _fire_event_async(event_name: str) -> str:
    """Fire a single event right now (runs on the engine's loop)."""
    if not engine:
        return "❌ Engine not running."
    for ev in engine.events:
        if ev.name == event_name:
            await engine._dispatch(ev)
            engine._last_fired[ev.name] = datetime.now(tz=timezone.utc)
            return f"✅ Fired **{event_name}** manually."
    return f"❌ Event '{event_name}' not found.  Available: {[e.name for e in engine.events]}"


def fire_event_now(event_name: str) -> str:
    """Thread-safe bridge: schedule the async fire on the engine's loop."""
    if engine_loop and engine_loop.is_running():
        future = asyncio.run_coroutine_threadsafe(_fire_event_async(event_name), engine_loop)
        return future.result(timeout=10)
    return "❌ Engine loop not running."


def create_event_on_disk(cmd: dict) -> str:
    """
    Create a new event folder from the <aep_action> create command.
    Returns a status string.
    """
    name        = cmd.get("name", "").strip().lower().replace(" ", "-")
    description = cmd.get("description", "No description.")
    schedule    = cmd.get("schedule", "every 10 minutes")
    mcp_tool    = cmd.get("mcp_tool", "mail_send")

    if not name:
        return "❌ No event name provided."

    # validate the schedule parses
    try:
        ee.NLSchedule.parse(schedule)
    except ValueError as e:
        return f"❌ Bad schedule: {e}"

    # create folder
    event_dir = EVENTS_DIR / name
    if event_dir.exists():
        return f"⚠️  Event '{name}' already exists."

    event_dir.mkdir(parents=True)
    (event_dir / "scripts").mkdir()
    (event_dir / "references").mkdir()

    # EVENT.md
    event_md = (
        f"---\n"
        f"name: {name}\n"
        f"description: >\n"
        f"  {description}\n"
        f"type: scheduled\n"
        f"schedule: {schedule}\n"
        f"action:\n"
        f"  mcp: {mcp_tool}\n"
        f"  params:\n"
        f"    message: \"Event {name} fired\"\n"
        f"---\n\n"
        f"# {name}\n\n"
        f"{description}\n\n"
        f"Fires on schedule: `{schedule}`\n"
        f"Action: calls MCP tool `{mcp_tool}`\n"
    )
    (event_dir / "EVENT.md").write_text(event_md, encoding="utf-8")

    # reload engine
    if engine:
        try:
            ev = ee.parse_event_md(event_dir)
            engine.events.append(ev)
            event_log.append({
                "time":    datetime.now(tz=timezone.utc).strftime("%H:%M:%S UTC"),
                "event":   name,
                "action":  "created",
                "status":  "✅ created",
                "detail":  f"schedule: {schedule}  |  tool: {mcp_tool}",
                "to":      "",
                "subject": "",
            })
            return f"✅ Created event **{name}** — fires {schedule}."
        except Exception as e:
            return f"⚠️  Folder created but engine reload failed: {e}"

    return f"✅ Created event folder **{name}** on disk."


def execute_action(cmd: dict) -> str:
    """Route an <aep_action> command."""
    action = cmd.get("action", "")

    if action == "fire":
        return fire_event_now(cmd.get("event", ""))

    elif action == "create":
        return create_event_on_disk(cmd)

    return f"⚠️  Unknown action: {action}"


# ══════════════════════════════════════════════════════════════════════════════
# GRADIO UI
# ══════════════════════════════════════════════════════════════════════════════

# ── state helpers ────────────────────────────────────────────────────────────

def get_events_table() -> list[list[str]]:
    """Current events as rows for the DataFrame."""
    if not engine:
        return []
    rows = []
    for ev in engine.events:
        last = engine._last_fired.get(ev.name)
        rows.append([
            ev.name,
            ev.event_type,
            ev.schedule_raw or "—",
            ev.action.get("mcp") or ev.action.get("script") or "—",
            last.strftime("%H:%M:%S UTC") if last else "not yet",
        ])
    return rows


def get_log_table() -> list[list[str]]:
    """Event log as rows for the DataFrame."""
    return [
        [e["time"], e["event"], e["action"], e["status"], e["detail"]]
        for e in event_log
    ]


# ── chat handler ─────────────────────────────────────────────────────────────

def chat(user_msg: str, history: list[list[str]]) -> tuple[list[list[str]], str]:
    """
    Called by Gradio when the user sends a message.
    Returns (updated history, cleared input).
    """
    if not user_msg.strip():
        return history, ""

    if not ANTHROPIC_API_KEY:
        history.append([user_msg, "⚠️  ANTHROPIC_API_KEY not set.  Add it to your .env file."])
        return history, ""

    # build messages list for the API
    messages = []
    for h in history:
        if h[0]:
            messages.append({"role": "user",      "content": h[0]})
        if h[1]:
            messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": user_msg})

    try:
        response = client.messages.create(
            model          = "claude-sonnet-4-20250514",
            max_tokens     = 1024,
            system         = build_system_prompt(),
            messages       = messages,
        )
        reply = response.content[0].text
    except Exception as e:
        reply = f"❌ API error: {e}"
        history.append([user_msg, reply])
        return history, ""

    # check for an <aep_action> command in the reply
    cmd = parse_aep_action(reply)
    if cmd:
        result = execute_action(cmd)
        # append the action result after Claude's reply
        reply = reply + f"\n\n> 🔧 {result}"

    history.append([user_msg, reply])
    return history, ""


# ── manual fire handler ──────────────────────────────────────────────────────

def manual_fire(event_name: str) -> str:
    if not event_name.strip():
        return "⚠️  Pick an event name from the list."
    return fire_event_now(event_name.strip())


# ── refresh callbacks ────────────────────────────────────────────────────────

def refresh_events():
    return gr.update(value=get_events_table())

def refresh_log():
    return gr.update(value=get_log_table())


# ══════════════════════════════════════════════════════════════════════════════
# BUILD THE APP
# ══════════════════════════════════════════════════════════════════════════════

theme = gr.themes.Soft(
    primary_hue   = gr.themes.colors.blue,
    secondary_hue = gr.themes.colors.emerald,
    neutral_hue   = gr.themes.colors.slate,
)

with gr.Blocks(theme=theme, title="AEP — Event Agent") as demo:

    # ── header ──────────────────────────────────────────────────────────────
    gr.Markdown("""
    # 🔄 AEP Event Agent
    An AI-powered event manager.  Chat to create, fire, or ask about events.
    The event engine runs in the background and fires scheduled events automatically.
    """)

    # ── tabs ────────────────────────────────────────────────────────────────
    with gr.Tabs():

        # ════════ TAB 1: CHAT ════════════════════════════════════════════════
        with gr.Tab("💬 Chat"):
            chatbot = gr.Chatbot(
                label="Agent",
                height=480,
                elem_id="chatbot",
            )
            with gr.Row():
                txt_input = gr.Textbox(
                    show_label=False,
                    placeholder="Ask me anything… e.g. 'what events are running?' or 'create an event…'",
                    scale=4,
                )
                send_btn = gr.Button("Send", variant="primary", scale=1)

            # example prompts
            gr.Examples(
                examples=[
                    ["What events are currently loaded?"],
                    ["Fire the send-team-mail event now"],
                    ["Create a new event called health-check that fires every 5 minutes using mail_send"],
                    ["Show me the recent event log"],
                ],
                inputs=txt_input,
            )

            # wire up
            send_btn.click(chat, inputs=[txt_input, chatbot], outputs=[chatbot, txt_input])
            txt_input.submit(chat, inputs=[txt_input, chatbot], outputs=[chatbot, txt_input])

        # ════════ TAB 2: EVENTS DASHBOARD ════════════════════════════════════
        with gr.Tab("📦 Events"):
            gr.Markdown("### Loaded Events")
            events_df = gr.DataFrame(
                value=get_events_table(),
                headers=["Name", "Type", "Schedule", "MCP Tool", "Last Fired"],
                label="Events",
                interactive=False,
            )

            gr.Markdown("### Manual Fire")
            with gr.Row():
                fire_input  = gr.Textbox(
                    show_label=False,
                    placeholder="event name, e.g. send-team-mail",
                    scale=3,
                )
                fire_btn    = gr.Button("🚀 Fire Now", variant="primary", scale=1)
            fire_status = gr.Textbox(show_label=False, interactive=False, placeholder="status…")

            fire_btn.click(manual_fire, inputs=fire_input, outputs=fire_status)



        # ════════ TAB 3: EVENT LOG ═══════════════════════════════════════════
        with gr.Tab("📜 Event Log"):
            gr.Markdown("### Live Event Log")
            log_df = gr.DataFrame(
                value=get_log_table(),
                headers=["Time", "Event", "Action", "Status", "Detail"],
                label="Event Log",
                interactive=False,
            )

    # ── periodic refresh for Events + Log tabs ─────────────────────────────
    # Gradio Timer fires a fn periodically; we update both DataFrames.
    timer = gr.Timer(interval=3)
    timer.tick(refresh_events, outputs=events_df)
    timer.tick(refresh_log,    outputs=log_df)


# ══════════════════════════════════════════════════════════════════════════════
# LAUNCH
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
