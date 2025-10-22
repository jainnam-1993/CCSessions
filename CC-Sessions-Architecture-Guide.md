# CC-Sessions Complete Architecture Guide

## Overview
cc-sessions transforms Claude Code into a structured workflow management system using Discussion-Alignment-Implementation-Check (DAIC) methodology. It enforces collaboration patterns through Python hooks that block editing tools until explicit user approval.

## Repository Structure

### Two-Level Architecture
```
/cc-sessions/                    # Git repository root
├── README.md                    # Project documentation
├── pyproject.toml              # Python package configuration
├── install.js                  # Node.js installer wrapper
├── install.sh                  # Bash installer
├── hooks/                      # Hook scripts directory
│   ├── __init__.py
│   ├── install.py              # Core installer logic ⭐ KEY FILE
│   ├── hooks/                  # Hook system components
│   │   ├── sessions-enforce.py # DAIC enforcement ⭐ KEY FILE
│   │   ├── shared_state.py     # State management utilities
│   │   ├── user-messages.py    # Trigger phrase detection
│   │   └── post-tool-use.py    # Implementation reminders
│   ├── protocols/              # Workflow protocols
│   ├── agents/                 # Specialized agent definitions
│   └── scripts/                # Platform-specific scripts
```

**Why Two Levels?**
- **Repository level** - Project metadata, build configs, documentation
- **Package level** - Actual importable Python module that gets installed

## Critical Files Deep Dive

### 1. install.sh ⭐
**Purpose**: Cross-platform installer with hook configuration

**Key Sections:**
- **Line 468**: `"matcher": "Write|Edit|MultiEdit|Task|Bash|mcp__serena__.*"`
  - **CRITICAL**: This determines which tools trigger PreToolUse hooks
  - **MCP Integration Point**: Adding `mcp__serena__.*` enables MCP tool blocking
  - **Format**: Pipe-separated regex patterns

**MCP Integration Logic:**
```python
# PreToolUse hook configuration
"PreToolUse": [{
    "matcher": "Write|Edit|MultiEdit|Task|Bash|mcp__serena__.*",
    "hooks": [{
        "type": "command",
        "command": "$CC_SESSIONS_PATH/hooks/sessions-enforce.py"
    }]
}]
```

**Configuration Generation:**
- Creates `.claude/settings.json` with hook configurations
- Installs all hook scripts to `.claude/hooks/`
- Sets up session directories and protocols

### 2. hooks/sessions-enforce.py ⭐
**Purpose**: Core DAIC enforcement engine

**Critical Sections:**

**Input Processing (Lines 67-70):**
```python
input_data = json.load(sys.stdin)
tool_name = input_data.get("tool_name", "")    # e.g., "mcp__serena__create_text_file"
tool_input = input_data.get("tool_input", {})  # Tool parameters
```

**Standard Tool Blocking (Lines 135-138):**
```python
if discussion_mode and tool_name in config.get("blocked_tools", DEFAULT_CONFIG["blocked_tools"]):
    print(f"[DAIC: Tool Blocked] You're in discussion mode...", file=sys.stderr)
    sys.exit(2)  # Block with feedback
```

**MCP Tool Blocking (Lines 147-160):**
```python
serena_file_modification_tools = [
    "mcp__serena__create_text_file",
    "mcp__serena__replace_regex",
    "mcp__serena__delete_lines",
    "mcp__serena__replace_lines",
    "mcp__serena__insert_at_line",
    "mcp__serena__replace_symbol_body",
    "mcp__serena__insert_after_symbol",
    "mcp__serena__insert_before_symbol"
]
if discussion_mode and tool_name in serena_file_modification_tools:
    print(f"[DAIC: Tool Blocked]...", file=sys.stderr)
    sys.exit(2)
```

**Branch Enforcement (Lines 160+):**
- Validates git branches match task expectations
- Handles single repo vs multi-repo scenarios
- Provides specific error messages for each failure mode

### 3. .claude/settings.json (Generated)
**Purpose**: Hook system registration

**Structure:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit|Task|Bash|mcp__serena__.*",
        "hooks": [{"type": "command", "command": "...sessions-enforce.py"}]
      }
    ],
    "PostToolUse": [...],
    "UserPromptSubmit": [...]
  }
}
```

**Matcher Pattern Rules:**
- **Pipe-separated** regex patterns
- **Order matters** - first match wins
- **MCP format**: `mcp__server__.*` for all tools from a server
- **Specific tools**: `mcp__server__specific_tool` for individual tools

## MCP Integration Architecture

### Tool Name Flow
```
MCP Tool Call → Hook System → sessions-enforce.py
mcp__serena__create_text_file → matcher: mcp__serena__.* → tool_name: "mcp__serena__create_text_file"
```

### Integration Points
1. **Matcher Registration** (install.py:468) - Determines which tools get hooked
2. **Tool Name Detection** (sessions-enforce.py:69) - Receives full tool names
3. **Selective Blocking** (sessions-enforce.py:147+) - Blocks only write operations
4. **Permission Control** - Can use "allow", "deny", "ask" responses

### Official Anthropic Documentation Compliance
- **Tool Names**: Full format `mcp__server__function_name`
- **Matcher Patterns**: Regex patterns like `mcp__server__.*`
- **Hook Responses**: Standard permissionDecision format
- **Integration**: Seamless with existing hook architecture

## DAIC State Management

### Mode Files
- **`.claude/state/daic-mode.json`**: `{"mode": "discussion"}` or `{"mode": "implementation"}`
- **Trigger Detection**: User phrases like "yes", "proceed", "implement" switch to implementation mode

### State Flow
```
Discussion Mode (Default) → Trigger Phrase → Implementation Mode → Auto-return to Discussion
```

### Tool Blocking Logic
- **Discussion Mode**: Write tools blocked, read tools allowed
- **Implementation Mode**: All tools allowed
- **Automatic Reversion**: Returns to discussion after implementation

## Configuration Management

### Default Configuration (sessions-enforce.py:14-45)
```python
DEFAULT_CONFIG = {
    "trigger_phrases": ["make it so", "run that"],
    "blocked_tools": ["Edit", "Write", "MultiEdit", "NotebookEdit"],
    "branch_enforcement": {"enabled": True, ...},
    "read_only_bash_commands": ["ls", "git status", "cat", ...]
}
```

### Custom Configuration
- **File**: `sessions/sessions-config.json`
- **Overrides**: Default configuration values
- **Runtime Loading**: Merged with defaults at execution

## Adding New MCP Server Support

### Step 1: Update Matcher Pattern (install.py:468)
```python
# From:
"matcher": "Write|Edit|MultiEdit|Task|Bash|mcp__serena__.*"

# To:
"matcher": "Write|Edit|MultiEdit|Task|Bash|mcp__serena__.*|mcp__newserver__.*"
```

### Step 2: Add Tool Blocking (sessions-enforce.py:147+)
```python
# Add after Serena blocking logic:
newserver_file_modification_tools = [
    "mcp__newserver__write_file",
    "mcp__newserver__delete_file",
    # ... other write operations
]
if discussion_mode and tool_name in newserver_file_modification_tools:
    print(f"[DAIC: Tool Blocked] You're in discussion mode. The {tool_name} tool is not allowed.", file=sys.stderr)
    sys.exit(2)
```

### Step 3: Reinstall
```bash
rm .claude/settings.json
./cc-sessions-auto-setup.sh
```

## Development Workflow

### Local Development Setup
1. **Clone**: `git clone repo`
2. **Install as editable**: `cd cc-sessions && pip install -e .`
3. **Test changes**: Modify code → reinstall → test
4. **Commit**: Standard git workflow

### Testing Hook Integration
1. **Add debug logging** to sessions-enforce.py:
```python
with open("/tmp/daic-debug.log", "a") as f:
    f.write(f"{datetime.now()} - Tool: {tool_name}, Input: {tool_input}\n")
```

2. **Test operations** and check `/tmp/daic-debug.log`
3. **Verify blocking** in discussion mode
4. **Remove debug logging** when complete

### Common Issues and Solutions

**Issue**: MCP tools not being hooked
- **Cause**: Wrong matcher pattern
- **Fix**: Use exact format `mcp__server__.*`

**Issue**: Configuration duplication
- **Cause**: Multiple reinstalls without cleanup
- **Fix**: `rm .claude/settings.json` before reinstall

**Issue**: Tools not blocked despite configuration
- **Cause**: Tool names don't match blocking list
- **Fix**: Add debug logging to capture actual tool names

## Hook System Deep Dive

### Hook Execution Flow
```
Tool Invocation → Matcher Check → Hook Script → Permission Decision → Tool Execution/Block
```

### Input Data Structure
```python
{
    "tool_name": "mcp__serena__create_text_file",  # Full tool identifier
    "tool_input": {                                # Tool parameters
        "relative_path": "file.txt",
        "content": "data"
    }
}
```

### Response Structure
```python
{
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",              # "allow", "deny", "ask"
        "permissionDecisionReason": "Blocked by DAIC"
    }
}
```

### Permission Decisions
- **"allow"**: Tool executes immediately, bypasses further checks
- **"deny"**: Tool blocked completely, error shown to user
- **"ask"**: User prompted for confirmation before execution

## Troubleshooting Guide

### Debug MCP Tool Integration
1. Add temporary logging to sessions-enforce.py
2. Test MCP tool operations
3. Check `/tmp/daic-debug.log` for captured data
4. Verify tool names match blocking lists
5. Remove debug logging when complete

### Fix Configuration Corruption
1. Check for duplicates: `grep -c '"matcher":' .claude/settings.json`
2. Clean slate: `rm .claude/settings.json .claude/state/daic-mode.json`
3. Fresh install: `./cc-sessions-auto-setup.sh`
4. Verify single entries: `grep -c "mcp__" .claude/settings.json`

### Verify Hook Registration
```bash
# Check matcher patterns
grep -A 3 "mcp__serena" .claude/settings.json

# Test hook execution
# (attempt blocked operation in discussion mode)

# Verify mode
cat .claude/state/daic-mode.json
```

## Security Model

### Defense in Depth
1. **Hook-level blocking**: Primary defense via sessions-enforce.py
2. **Permission-level control**: Claude Code's built-in permissions
3. **Mode enforcement**: DAIC workflow state machine
4. **Branch protection**: Git branch consistency checks

### Threat Model Coverage
- **Unauthorized file modifications**: ✅ Blocked in discussion mode
- **Workflow bypass attempts**: ✅ Trigger phrases required
- **Configuration tampering**: ✅ Protected state files
- **Cross-session persistence**: ✅ State preserved across restarts

### Attack Vectors Addressed
- **Direct MCP tool invocation**: ✅ Hooked and blocked appropriately
- **Bash command injection**: ✅ Write pattern detection
- **State file manipulation**: ✅ Subagent boundary protection
- **Branch confusion**: ✅ Git branch enforcement

## Best Practices

### For Users
- Always work in discussion mode first
- Use trigger phrases to switch to implementation
- One task per branch with proper naming
- Let DAIC guide the workflow

### For Developers
- Test hook integration with debug logging
- Use clean reinstalls when modifying configurations
- Follow matcher pattern formats exactly
- Verify both positive and negative test cases

### For System Administrators
- Monitor debug logs for security events
- Keep cc-sessions updated from trusted sources
- Validate hook configurations after updates
- Implement organizational trigger phrase policies

---

## Summary

cc-sessions provides robust DAIC workflow enforcement through a sophisticated hook system that integrates seamlessly with both built-in Claude Code tools and external MCP servers. The architecture is designed for security, extensibility, and maintainability while preserving the natural flow of AI-assisted development.

The MCP integration represents a critical security enhancement that closes potential bypass vectors while maintaining the productivity benefits of external tool ecosystems. This guide provides the complete understanding needed for effective development, deployment, and maintenance of cc-sessions environments.