# cc-sessions CLAUDE.md

## Purpose (Testing MCP blocking)
Complete Claude Code Sessions framework that enforces Discussion-Alignment-Implementation-Check (DAIC) methodology for AI pair programming workflows.

## Narrative Summary

The cc-sessions package transforms Claude Code from a basic AI coding assistant into a disciplined workflow system. It enforces structured collaboration patterns where Claude must discuss approaches before implementing code.

The core innovation is the DAIC (Discussion-Alignment-Implementation-Check) enforcement through Python hooks that cannot be bypassed. When Claude attempts to edit code without explicit user approval ("go ahead", "make it so", etc.), the hooks block the tools and require discussion first. This prevents the common AI coding problem of immediate over-implementation without alignment.

## Key Files
- `cc_sessions/install.py` - Cross-platform installer with Windows compatibility and native shell support
- `install.js` - Node.js installer wrapper with Windows command detection and path handling
- `cc_sessions/hooks/sessions-enforce.py` - Core DAIC enforcement and MCP tool blocking
- `cc_sessions/hooks/session-start.py` - Session initialization with setup validation
- `cc_sessions/hooks/user-messages.py` - Trigger phrase detection and mode switching
- `cc_sessions/hooks/post-tool-use.py` - Implementation mode reminders
- `cc_sessions/scripts/daic.cmd` - Windows Command Prompt daic command
- `cc_sessions/scripts/daic.ps1` - Windows PowerShell daic command
- `cc_sessions/templates/CLAUDE.sessions.md` - Behavioral guidance template
- `cc_sessions/knowledge/hooks-reference.md` - Hook system documentation
- `pyproject.toml` - Package configuration with console script entry points
- `cc-sessions-auto-setup.sh` - Automated installation wrapper with predefined responses

## Installation Methods
- `pipx install cc-sessions` - Isolated Python install (recommended)
- `npm install -g cc-sessions` - Global npm install
- `pip install cc-sessions` - Direct pip install
- Direct bash: `./install.sh` from repository
- Automated: `./cc-sessions-auto-setup.sh` - Uses expect to automate interactive prompts

## Core Features

### DAIC Enforcement
- Blocks Edit/Write/MultiEdit tools in discussion mode
- Pattern-based MCP tool blocking catches file modification tools across all MCP servers
- Configurable MCP blocking patterns: create, write, edit, replace, insert, delete, modify, update, append, prepend, remove, change, patch, set
- Debug logging to `/tmp/daic-debug.log` records all tool usage with timestamps
- MCP blocking configurable via `mcp_blocking.patterns` and `mcp_blocking.enabled` in sessions-config.json
- Requires explicit trigger phrases to enter implementation mode
- Configurable trigger phrases via `/add-trigger` command
- Read-only Bash commands allowed in discussion mode


## Integration Points

### Consumes
- Claude Code hooks system for behavioral enforcement
- Python 3.8+ for hook execution
- Shell environment for command execution (Bash/PowerShell/Command Prompt)

### Provides
- `/add-trigger` - Dynamic trigger phrase configuration
- `/api-mode` - Toggle ultrathink on/off
- `daic` - Manual mode switching command
- Hook-based tool blocking and behavioral enforcement

## Configuration

Primary configuration in `sessions/sessions-config.json`:
- `developer_name` - How Claude addresses the user
- `trigger_phrases` - Phrases that switch to implementation mode
- `blocked_tools` - Tools blocked in discussion mode
- `mcp_blocking.enabled` - Enable/disable MCP tool pattern blocking
- `mcp_blocking.patterns` - Patterns for detecting file modification MCP tools

State files in `.claude/state/`:
- `daic-mode.json` - Current discussion/implementation mode

Windows-specific configuration in `.claude/settings.json`:
- Hook commands use Windows-style paths with `%CLAUDE_PROJECT_DIR%`
- Python interpreter explicitly specified for `.py` hook execution
- Native `.cmd` and `.ps1` script support for daic command

## Key Patterns

### Hook Architecture
- Pre-tool-use hooks for enforcement (sessions-enforce.py)
- Post-tool-use hooks for reminders (post-tool-use.py)
- User message hooks for trigger detection (user-messages.py)
- Session start hooks for setup validation (session-start.py)
- Shared state management across all hooks (shared_state.py)
- Cross-platform path handling using pathlib.Path throughout
- Windows-specific command prefixing with explicit python interpreter

### Windows Compatibility
- Platform detection using `os.name == 'nt'` (Python) and `process.platform === 'win32'` (Node.js)
- File operations skip Unix permissions on Windows (no chmod calls)
- Command detection handles Windows executable extensions (.exe, .bat, .cmd)
- Global command installation to `%USERPROFILE%\AppData\Local\cc-sessions\bin`
- Hook commands use explicit `python` prefix and Windows environment variable format
- Native Windows scripts: daic.cmd (Command Prompt) and daic.ps1 (PowerShell)

## Package Structure

### Installation Variants
- Python package with pip/pipx/uv support
- NPM package wrapper for JavaScript environments
- Direct bash script for build-from-source installations
- Cross-platform compatibility (macOS, Linux, Windows 10/11)

### Template System
- CLAUDE.sessions.md behavioral template for collaboration guidance

## Quality Assurance Features

### Process Integrity
- Hook-based enforcement cannot be bypassed
- Mandatory discussion before implementation
- State file protection from unauthorized changes

## Related Documentation

- docs/INSTALL.md - Detailed installation guide
- docs/USAGE_GUIDE.md - Workflow and feature documentation
- cc_sessions/knowledge/ - Internal architecture documentation
- README.md - Marketing-focused feature overview

## Obsidian Vault

**Vault Path**: `/Volumes/workplace/tools/Obsidian/01_Projects`
**Context Primer**: `/Volumes/workplace/tools/Obsidian/01_Projects/Personal/CCSessions/README.md`

> **IMPORTANT**: Start each new session by reading the Context Primer. It contains current status (last work, current focus, blockers), active features with progress, file locations, and all essential context for continuing work on this project.

## Sessions System Behaviors

@CLAUDE.sessions.md
