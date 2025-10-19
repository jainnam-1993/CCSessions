#!/usr/bin/env python3
"""Pre-tool-use hook to enforce DAIC (Discussion, Alignment, Implementation, Check) workflow."""
import json
import sys
from pathlib import Path
from shared_state import check_daic_mode_bool, get_project_root

# Load configuration from project's .claude directory
PROJECT_ROOT = get_project_root()
CONFIG_FILE = PROJECT_ROOT / "sessions" / "sessions-config.json"

# Default configuration (used if config file doesn't exist)
DEFAULT_CONFIG = {
    "trigger_phrases": ["make it so", "run that"],
    "blocked_tools": ["Edit", "Write", "MultiEdit", "NotebookEdit"],
    "read_only_bash_commands": [
        "ls", "ll", "pwd", "cd", "echo", "cat", "head", "tail", "less", "more",
        "grep", "rg", "find", "which", "whereis", "type", "file", "stat",
        "du", "df", "tree", "basename", "dirname", "realpath", "readlink",
        "whoami", "env", "printenv", "date", "cal", "uptime", "ps", "top",
        "wc", "cut", "sort", "uniq", "comm", "diff", "cmp", "md5sum", "sha256sum",
        "git status", "git log", "git diff", "git show", "git branch",
        "git remote", "git fetch", "git describe", "git rev-parse", "git blame",
        "docker ps", "docker images", "docker logs", "npm list", "npm ls",
        "pip list", "pip show", "yarn list", "curl", "wget", "jq", "awk",
        "sed -n", "tar -t", "unzip -l",
        # Windows equivalents
        "dir", "where", "findstr", "fc", "comp", "certutil -hashfile",
        "Get-ChildItem", "Get-Location", "Get-Content", "Select-String",
        "Get-Command", "Get-Process", "Get-Date", "Get-Item"
    ]
}

def load_config():
    """Load configuration from file or use defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG



# Load input
input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")
tool_input = input_data.get("tool_input", {})

# DEBUG: Log tool information
import datetime
debug_log = "/tmp/daic-debug.log"
with open(debug_log, "a") as f:
    timestamp = datetime.datetime.now().isoformat()
    f.write(f"{timestamp} - Tool: {tool_name}, Input: {tool_input}\n")

# Load configuration
config = load_config()

# For Bash commands, check if it's a read-only operation
if tool_name == "Bash":
    command = tool_input.get("command", "").strip()
    
    # Check for write patterns
    import re
    write_patterns = [
        r'>\s*[^>]',  # Output redirection
        r'>>',         # Append redirection
        r'\btee\b',    # tee command
        r'\bmv\b',     # move/rename
        r'\bcp\b',     # copy
        r'\brm\b',     # remove
        r'\bmkdir\b',  # make directory
        r'\btouch\b',  # create/update file
        r'\bsed\s+(-[a-zA-Z]*i\b|-i\b)',  # sed with -i flag (in-place editing)
        r'\bsed\s+(?!-n\b)',  # sed without -n flag (read-only)
        r'\bnpm\s+install',  # npm install
        r'\bpip\s+install',  # pip install
        r'\bapt\s+install',  # apt install
        r'\byum\s+install',  # yum install
        r'\bbrew\s+install',  # brew install
    ]
    
    has_write_pattern = any(re.search(pattern, command) for pattern in write_patterns)
    
    if not has_write_pattern:
        # Check if ALL commands in chain are read-only
        command_parts = re.split(r'(?:&&|\|\||;|\|)', command)
        all_read_only = True
        
        for part in command_parts:
            part = part.strip()
            if not part:
                continue
            
            # Check against configured read-only commands
            is_part_read_only = any(
                part.startswith(prefix) 
                for prefix in config.get("read_only_bash_commands", DEFAULT_CONFIG["read_only_bash_commands"])
            )
            
            if not is_part_read_only:
                all_read_only = False
                break
        
        if all_read_only:
            # Allow read-only commands without checks
            sys.exit(0)

# Check current mode
discussion_mode = check_daic_mode_bool()

# Block 'daic' command in discussion mode
if discussion_mode and tool_name == "Bash":
    command = tool_input.get("command", "").strip()
    # Only block if daic is the actual command, not just part of a path or argument
    if command == 'daic' or command.startswith('daic '):
        print(f"[DAIC: Command Blocked] The 'daic' command is not allowed in discussion mode.", file=sys.stderr)
        print(f"You're already in discussion mode. Be sure to propose your intended edits/plans to the user and seek their explicit approval, which will unlock implementation mode.", file=sys.stderr)
        sys.exit(2)  # Block with feedback

# Block configured tools in discussion mode
if discussion_mode and tool_name in config.get("blocked_tools", DEFAULT_CONFIG["blocked_tools"]):
    print(f"[DAIC: Tool Blocked] You're in discussion mode. The {tool_name} tool is not allowed. You need to seek alignment first.", file=sys.stderr)
    sys.exit(2)  # Block with feedback

# Pattern-based blocking for MCP file modification tools
# This catches any MCP tool that appears to modify files, regardless of server
mcp_config = config.get("mcp_blocking", {})
if mcp_config.get("enabled", True) and discussion_mode and tool_name.startswith("mcp__"):
    # Get patterns from config or use defaults
    file_modification_patterns = mcp_config.get("patterns", [
        "create", "write", "edit", "replace", "insert", "delete", "modify",
        "update", "append", "prepend", "remove", "change", "patch", "set"
    ])

    # Extract the tool method name (after the last __)
    tool_method = tool_name.split("__")[-1].lower() if "__" in tool_name else tool_name.lower()

    # Check if the tool method contains any file modification pattern
    if any(pattern in tool_method for pattern in file_modification_patterns):
        print(f"[DAIC: MCP Tool Blocked] You're in discussion mode. The {tool_name} tool appears to modify files and is not allowed.", file=sys.stderr)
        print(f"Detected file modification pattern in MCP tool. Seek user alignment first.", file=sys.stderr)
        sys.exit(2)  # Block with feedback



# Allow tool to proceed
sys.exit(0)