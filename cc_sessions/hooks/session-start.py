#!/usr/bin/env python3
"""Session start hook to initialize Claude Code Sessions context."""
import json
import os
import sys
import subprocess
from pathlib import Path
from shared_state import get_project_root, ensure_state_dir, get_task_state

# Get project root
PROJECT_ROOT = get_project_root()

# Get developer name from config
try:
    CONFIG_FILE = PROJECT_ROOT / 'sessions' / 'sessions-config.json'
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            developer_name = config.get('developer_name', 'the developer')
    else:
        developer_name = 'the developer'
except:
    developer_name = 'the developer'

# Quick configuration checks
needs_setup = False
quick_checks = []

# 1. Check if daic command exists
try:
    import shutil
    import os
    # Cross-platform command detection
    if os.name == 'nt':
        # Windows - check for .cmd or .ps1 versions
        if not (shutil.which('daic.cmd') or shutil.which('daic.ps1') or shutil.which('daic')):
            needs_setup = True
            quick_checks.append("daic command")
    else:
        # Unix/Mac - use which command
        if not shutil.which('daic'):
            needs_setup = True
            quick_checks.append("daic command")
except:
    needs_setup = True
    quick_checks.append("daic command")

# 2. Check if DAIC state file exists (create if not)
ensure_state_dir()
daic_state_file = PROJECT_ROOT / '.claude' / 'state' / 'daic-mode.json'
if not daic_state_file.exists():
    # Create default state
    with open(daic_state_file, 'w') as f:
        json.dump({"mode": "discussion"}, f, indent=2)

# 3. Clear context warning flags for new session
warning_75_flag = PROJECT_ROOT / '.claude' / 'state' / 'context-warning-75.flag'
warning_90_flag = PROJECT_ROOT / '.claude' / 'state' / 'context-warning-90.flag'
if warning_75_flag.exists():
    warning_75_flag.unlink()
if warning_90_flag.exists():
    warning_90_flag.unlink()

# Only output context if there are warnings/errors
context = ""
if needs_setup:
    context = f"""You are beginning a new context window with {developer_name}.

[Setup Required]
Missing components: {', '.join(quick_checks)}

To complete setup:
1. Run the cc-sessions installer
2. Ensure the daic command is in your PATH

The sessions system helps manage discussion/implementation workflow discipline.
"""

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context
    }
}
print(json.dumps(output))