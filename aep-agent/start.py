# start.py — AEP Agent entry point (Windows-safe)
# ─────────────────────────────────────────────────
# Forces UTF-8 across the board so emojis in main.py / event_engine.py
# don't hit the cp1252 wall on Windows.

import sys
import os

# 1) Reconfigure stdout / stderr to UTF-8 before anything prints
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 2) Make sure we run from the script's own directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Starting AEP Agent…")

# 3) Import main — this executes module-level code (boots the event engine,
#    builds the Gradio app) but does NOT launch because of the
#    `if __name__ == "__main__"` guard in main.py.
import main

# 4) Now launch the UI ourselves
main.demo.launch(server_name="0.0.0.0", server_port=7860)
