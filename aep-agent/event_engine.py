"""
aep/event_engine.py
───────────────────
The engine that makes EVENT.md folders work.

Responsibilities:
  1. Scan an events/ directory, find every folder with an EVENT.md
  2. Parse the YAML frontmatter (type, schedule, action)
  3. Resolve file references in action.params  (e.g. "references/recipients.txt")
  4. Convert natural-language schedules into intervals/crons
  5. Run the scheduler loop — call the action at the right times
  6. Dispatch actions:
       action.mcp  →  call an MCP server tool
       action.script →  run a local Python script

No external dependencies beyond PyYAML and the standard library.
The MCP client is a thin stub here; in production it connects to a
real MCP server over stdio or HTTP.
"""

from __future__ import annotations

import asyncio
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import yaml


# ─── Natural-language schedule → (kind, interval_seconds, cron) ─────────────

class NLSchedule:
    """
    Parse "every 10 minutes", "every hour", "every day at 9 AM", etc.
    Returns a simple dict the engine can act on.
    """

    _DOW = {
        "sunday": 0, "monday": 1, "tuesday": 2, "wednesday": 3,
        "thursday": 4, "friday": 5, "saturday": 6,
    }

    @classmethod
    def _to24(cls, h: int, m: int, ampm: str | None) -> tuple[int, int]:
        if ampm:
            ampm = ampm.lower()
            if ampm == "pm" and h != 12: h += 12
            if ampm == "am" and h == 12: h = 0
        return h, m

    @classmethod
    def parse(cls, text: str) -> dict[str, Any]:
        """
        Returns one of:
          {"kind": "interval", "seconds": <int>}
          {"kind": "cron",     "cron": "<5-field>"}
        Raises ValueError if not recognised.
        """
        text = text.strip()
        # synonyms
        text = re.sub(r'\bmidnight\b', '12 AM', text, flags=re.IGNORECASE)
        text = re.sub(r'\bnoon\b',     '12 PM', text, flags=re.IGNORECASE)

        # ── "every N minutes / hours / seconds" ──
        m = re.match(r"every\s+(\d+)\s+(seconds?|minutes?|hours?)", text, re.IGNORECASE)
        if m:
            n    = int(m.group(1))
            unit = m.group(2).lower().rstrip("s")
            secs = n * {"second": 1, "minute": 60, "hour": 3600}[unit]
            return {"kind": "interval", "seconds": secs}

        # ── "every hour" ──
        if re.match(r"every\s+hour$", text, re.IGNORECASE):
            return {"kind": "interval", "seconds": 3600}

        # ── "every <dow> at <time>" ──
        m = re.match(
            r"every\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            r"\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$",
            text, re.IGNORECASE
        )
        if m:
            dow    = cls._DOW[m.group(1).lower()]
            h, mn  = cls._to24(int(m.group(2)), int(m.group(3) or 0), m.group(4))
            return {"kind": "cron", "cron": f"{mn} {h} * * {dow}"}

        # ── "every day at <time>" ──
        m = re.match(
            r"every\s+day\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$",
            text, re.IGNORECASE
        )
        if m:
            h, mn = cls._to24(int(m.group(1)), int(m.group(2) or 0), m.group(3))
            return {"kind": "cron", "cron": f"{mn} {h} * * *"}

        # ── "every <dow1> and <dow2> at <time>" ──
        m = re.match(
            r"every\s+((?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
            r"(?:\s*,?\s*(?:and\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))*)"
            r"\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$",
            text, re.IGNORECASE
        )
        if m:
            days   = re.findall(r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                                m.group(1), re.IGNORECASE)
            dows   = ",".join(str(cls._DOW[d.lower()]) for d in days)
            h, mn  = cls._to24(int(m.group(2)), int(m.group(3) or 0), m.group(4))
            return {"kind": "cron", "cron": f"{mn} {h} * * {dows}"}

        # ── "first day of every month at <time>" ──
        m = re.match(
            r"(?:on\s+the\s+)?first\s+day\s+of\s+(?:every\s+)?month\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$",
            text, re.IGNORECASE
        )
        if m:
            h, mn = cls._to24(int(m.group(1)), int(m.group(2) or 0), m.group(3))
            return {"kind": "cron", "cron": f"{mn} {h} 1 * *"}

        raise ValueError(f"Cannot parse schedule: '{text}'")


# ─── Cron matcher (lightweight, no deps) ────────────────────────────────────

def _parse_cron_field(s: str, lo: int, hi: int) -> set[int]:
    out: set[int] = set()
    for part in s.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = lo if base == "*" else int(base)
            out.update(range(start, hi + 1, int(step)))
        elif "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        elif part == "*":
            out.update(range(lo, hi + 1))
        else:
            out.add(int(part))
    return out


def _cron_matches(cron: str, dt: datetime) -> bool:
    fields = cron.strip().split()
    mins, hrs, doms, months, dows = (
        _parse_cron_field(fields[0], 0, 59),
        _parse_cron_field(fields[1], 0, 23),
        _parse_cron_field(fields[2], 1, 31),
        _parse_cron_field(fields[3], 1, 12),
        _parse_cron_field(fields[4], 0, 6),
    )
    # Python weekday: Mon=0…Sun=6  →  cron: Sun=0…Sat=6
    cron_dow = (dt.weekday() + 1) % 7
    return (dt.minute in mins and dt.hour in hrs and dt.day in doms
            and dt.month in months and cron_dow in dows)


# ─── MCP client stub ────────────────────────────────────────────────────────
# In production this would connect to a real MCP server (stdio / HTTP).
# The stub here simulates the call so the demo is self-contained.

class MCPClient:
    """
    Minimal MCP tool caller.

    Registered tools are callables.  In production, tools are discovered
    from connected MCP servers via the standard tool-listing protocol.
    """

    def __init__(self):
        self._tools: dict[str, Any] = {}   # name → callable

    def register_tool(self, name: str, fn: Any) -> None:
        self._tools[name] = fn

    async def call_tool(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        fn = self._tools.get(name)
        if fn is None:
            raise RuntimeError(f"MCP tool '{name}' not found. Available: {list(self._tools.keys())}")
        if asyncio.iscoroutinefunction(fn):
            return await fn(params)
        return fn(params)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


# ─── Event definition (parsed EVENT.md) ─────────────────────────────────────

@dataclass
class EventDef:
    name:        str                          # = folder name
    description: str
    event_type:  str                          # "scheduled" | "event-triggered" | "manual"
    schedule_raw:str | None       = None      # raw NL string
    schedule:    dict | None      = None      # parsed: {kind, seconds} or {kind, cron}
    action:      dict             = field(default_factory=dict)
    event_dir:   Path             = Path(".")
    # resolved params (file refs replaced with content)
    resolved_params: dict         = field(default_factory=dict)


# ─── Parser ─────────────────────────────────────────────────────────────────

def _resolve_value(value: Any, event_dir: Path) -> Any:
    """
    If value is a string that looks like a file path inside the event folder,
    read and return its contents.  Otherwise return value unchanged.
    """
    if not isinstance(value, str):
        return value
    # check if it points to a file inside the event folder
    candidate = (event_dir / value).resolve()
    if candidate.exists() and str(candidate).startswith(str(event_dir.resolve())):
        raw = candidate.read_text(encoding="utf-8")
        # special handling for recipients-style files: strip comments, blank lines
        if value.endswith(".txt"):
            lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.strip().startswith("#")]
            return lines                     # return as list
        return raw.strip()                   # return as string
    return value                             # not a file — return as-is


def parse_event_md(event_dir: Path) -> EventDef:
    """Read EVENT.md from event_dir, parse frontmatter, resolve file refs."""
    event_md = event_dir / "EVENT.md"
    if not event_md.exists():
        raise FileNotFoundError(f"No EVENT.md in {event_dir}")

    raw_text = event_md.read_text(encoding="utf-8")

    # split frontmatter
    if not raw_text.startswith("---"):
        raise ValueError(f"[{event_dir.name}] EVENT.md must start with --- frontmatter")
    parts = raw_text.split("---", maxsplit=2)
    if len(parts) < 3:
        raise ValueError(f"[{event_dir.name}] EVENT.md frontmatter not closed with ---")

    data: dict[str, Any] = yaml.safe_load(parts[1]) or {}

    # ── required fields ──
    # "type" is always required.
    # At least one of "action" or "script" must be present.
    if "type" not in data:
        raise ValueError(f"[{event_dir.name}] EVENT.md missing required field: type")
    if "action" not in data and "script" not in data:
        raise ValueError(f"[{event_dir.name}] EVENT.md must have 'action' or 'script'")

    # normalise: if only "script" is present, wrap it into action so the
    # rest of the engine treats everything uniformly.
    if "action" not in data and "script" in data:
        data["action"] = {"script": data["script"]}

    # ── schedule parsing ──
    schedule_raw = data.get("schedule")
    schedule     = None
    if schedule_raw and data["type"] == "scheduled":
        schedule = NLSchedule.parse(str(schedule_raw))

    # ── resolve file references in action.params ──
    raw_params = data.get("action", {}).get("params", {})
    resolved   = {k: _resolve_value(v, event_dir) for k, v in raw_params.items()}

    return EventDef(
        name             = event_dir.name,
        description      = data.get("description", ""),
        event_type       = data["type"],
        schedule_raw     = schedule_raw,
        schedule         = schedule,
        action           = data["action"],
        event_dir        = event_dir,
        resolved_params  = resolved,
    )


# ─── Event Engine ───────────────────────────────────────────────────────────

class AEPEventEngine:
    """
    Scans events/, loads EVENT.md definitions, runs the scheduler,
    dispatches actions via MCP or script.

    Usage:
        engine = AEPEventEngine(events_root=Path("events"), mcp=my_mcp_client)
        engine.load()
        await engine.run()   # blocks, runs the scheduler loop
    """

    TICK = 1.0   # seconds between scheduler checks

    def __init__(self, events_root: Path, mcp: MCPClient | None = None):
        self.events_root = events_root.resolve()
        self.mcp         = mcp or MCPClient()
        self.events:     list[EventDef] = []
        # runtime state per event
        self._last_fired: dict[str, datetime] = {}
        self._cron_fired_this_minute: dict[str, bool] = {}
        self._running = False

    # ── load ────────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Scan events_root, parse every EVENT.md."""
        if not self.events_root.is_dir():
            raise FileNotFoundError(f"Events root not found: {self.events_root}")

        for candidate in sorted(self.events_root.iterdir()):
            if not candidate.is_dir():
                continue
            if not (candidate / "EVENT.md").exists():
                continue
            try:
                ev = parse_event_md(candidate)
                self.events.append(ev)
                print(f"  📦 Loaded event: {ev.name}")
                print(f"      type:   {ev.event_type}")
                if ev.schedule:
                    print(f"      schedule: {ev.schedule_raw}  →  {ev.schedule}")
                print(f"      action: {ev.action.get('mcp') or ev.action.get('script')}")
                if ev.resolved_params:
                    # show resolved params (truncate long values)
                    for k, v in ev.resolved_params.items():
                        display = str(v)[:60] + ("…" if len(str(v)) > 60 else "")
                        print(f"        {k}: {display}")
            except Exception as e:
                print(f"  ⚠️  Skipping {candidate.name}: {e}")

    # ── dispatch ────────────────────────────────────────────────────────────

    async def _dispatch(self, ev: EventDef) -> None:
        """Run the action defined in EVENT.md."""
        action = ev.action

        if "mcp" in action:
            tool_name = action["mcp"]
            params    = ev.resolved_params
            print(f"\n  🔧 [{ev.name}] Calling MCP tool: {tool_name}")
            print(f"      params: { {k: (str(v)[:50]+'…' if len(str(v))>50 else v) for k,v in params.items()} }")
            try:
                result = await self.mcp.call_tool(tool_name, params)
                print(f"      ✅ Result: {result}")
            except Exception as e:
                print(f"      ❌ MCP error: {e}")

        elif "script" in action:
            script_path = (ev.event_dir / action["script"]).resolve()
            print(f"\n  📜 [{ev.name}] Running script: {script_path.name}")
            if not script_path.exists():
                print(f"      ❌ Script not found: {script_path}")
                return
            # dynamic import + call handle(params)
            import importlib.util
            spec   = importlib.util.spec_from_file_location(f"script_{ev.name}", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "handle"):
                result = module.handle(ev.resolved_params)
                if asyncio.iscoroutine(result):
                    result = await result
                print(f"      ✅ Script result: {result}")
            else:
                print(f"      ⚠️  Script has no handle() function")

        else:
            print(f"  ⚠️  [{ev.name}] No action.mcp or action.script defined")

    # ── scheduler ───────────────────────────────────────────────────────────

    def _is_due(self, ev: EventDef, now: datetime) -> bool:
        if ev.event_type != "scheduled" or ev.schedule is None:
            return False

        sched = ev.schedule
        last  = self._last_fired.get(ev.name)

        if sched["kind"] == "interval":
            if last is None:
                return True                  # first fire immediately
            return (now - last).total_seconds() >= sched["seconds"]

        elif sched["kind"] == "cron":
            # fire once per matching minute
            minute_key = now.strftime("%Y%m%d%H%M")
            cache_key  = f"{ev.name}:{minute_key}"
            if self._cron_fired_this_minute.get(cache_key):
                return False
            if _cron_matches(sched["cron"], now):
                self._cron_fired_this_minute[cache_key] = True
                return True

        return False

    async def _tick(self) -> None:
        now = datetime.now(tz=timezone.utc)
        for ev in self.events:
            if self._is_due(ev, now):
                self._last_fired[ev.name] = now
                await self._dispatch(ev)

    # ── run (blocking scheduler loop) ───────────────────────────────────────

    async def run(self, duration_seconds: float | None = None) -> None:
        """
        Start the scheduler loop.
        If duration_seconds is set, stop after that many seconds (for demos).
        Otherwise runs forever until cancelled.
        """
        self._running = True
        start = datetime.now(tz=timezone.utc)
        print(f"\n⏳ Event engine running… (tick every {self.TICK}s)")
        if duration_seconds:
            print(f"   Will stop after {duration_seconds}s")

        while self._running:
            await self._tick()
            await asyncio.sleep(self.TICK)
            if duration_seconds:
                elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()
                if elapsed >= duration_seconds:
                    break

        print(f"\n⏹️  Event engine stopped.")

    def stop(self) -> None:
        self._running = False

    # ── introspection ───────────────────────────────────────────────────────

    def list_events(self) -> list[dict[str, Any]]:
        return [
            {
                "name":        ev.name,
                "type":        ev.event_type,
                "schedule":    ev.schedule_raw,
                "action":      ev.action.get("mcp") or ev.action.get("script"),
            }
            for ev in self.events
        ]
