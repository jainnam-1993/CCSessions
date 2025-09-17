# cc-sessions CLAUDE.md

## Purpose (Testing MCP blocking)
Complete Claude Code Sessions framework that enforces Discussion-Alignment-Implementation-Check (DAIC) methodology for AI pair programming workflows.

## Narrative Summary

The cc-sessions package transforms Claude Code from a basic AI coding assistant into a sophisticated workflow management system. It enforces structured collaboration patterns where Claude must discuss approaches before implementing code, maintains persistent task context across sessions, and provides specialized agents for complex operations.

The core innovation is the DAIC (Discussion-Alignment-Implementation-Check) enforcement through Python hooks that cannot be bypassed. When Claude attempts to edit code without explicit user approval ("go ahead", "make it so", etc.), the hooks block the tools and require discussion first. This prevents the common AI coding problem of immediate over-implementation without alignment.

The framework includes persistent task management with git branch enforcement, context preservation through session restarts, specialized subagents for heavy operations, and automatic context compaction when approaching token limits.

## Key Files
- `cc_sessions/install.py` - Cross-platform installer with Windows compatibility and native shell support
- `install.js` - Node.js installer wrapper with Windows command detection and path handling
- `cc_sessions/hooks/sessions-enforce.py` - Core DAIC enforcement and branch protection
- `cc_sessions/hooks/session-start.py` - Automatic task context loading
- `cc_sessions/hooks/user-messages.py` - Trigger phrase detection and mode switching
- `cc_sessions/hooks/post-tool-use.py` - Implementation mode reminders
- `cc_sessions/scripts/daic.cmd` - Windows Command Prompt daic command
- `cc_sessions/scripts/daic.ps1` - Windows PowerShell daic command
- `cc_sessions/agents/logging.md` - Session work log consolidation agent
- `cc_sessions/protocols/task-creation.md` - Structured task creation workflow
- `cc_sessions/templates/CLAUDE.sessions.md` - Behavioral guidance template
- `cc_sessions/knowledge/hooks-reference.md` - Hook system documentation
- `pyproject.toml` - Package configuration with console script entry points

## Installation Methods
- `pipx install cc-sessions` - Isolated Python install (recommended)
- `npm install -g cc-sessions` - Global npm install
- `pip install cc-sessions` - Direct pip install
- Direct bash: `./install.sh` from repository

## Core Features

### DAIC Enforcement
- Blocks Edit/Write/MultiEdit tools in discussion mode
- Pattern-based MCP tool blocking catches file modification tools across all MCP servers
- Requires explicit trigger phrases to enter implementation mode
- Configurable trigger phrases via `/add-trigger` command
- Read-only Bash commands allowed in discussion mode

### Task Management
- Priority-prefixed tasks: h- (high), m- (medium), l- (low), ?- (investigate)
- Automatic git branch creation and enforcement
- Persistent context across session restarts
- Work log consolidation and cleanup

### Branch Enforcement
- Task-to-branch mapping: implement- → feature/, fix- → fix/, etc.
- Blocks code edits if current branch doesn't match task requirements
- Four failure modes: wrong branch, no branch, task missing, branch missing

### Context Preservation
- Automatic context compaction at 75%/90% token usage
- Session restart with full task context loading
- Specialized agents operate in separate contexts

### Specialized Agents
- **context-gathering**: Creates comprehensive task context manifests
- **logging**: Consolidates work logs with cleanup and chronological ordering
- **code-review**: Reviews implementations for quality and patterns
- **context-refinement**: Updates context with session discoveries
- **service-documentation**: Maintains CLAUDE.md files for services

## Integration Points

### Consumes
- Claude Code hooks system for behavioral enforcement
- Git for branch management and enforcement
- Python 3.8+ with tiktoken for token counting
- Shell environment for command execution (Bash/PowerShell/Command Prompt)

### Provides
- `/add-trigger` - Dynamic trigger phrase configuration
- `daic` - Manual mode switching command
- Hook-based tool blocking and behavioral enforcement
- Task file templates and management protocols
- Agent-based specialized operations

## Configuration

Primary configuration in `sessions/sessions-config.json`:
- `developer_name` - How Claude addresses the user
- `trigger_phrases` - Phrases that switch to implementation mode
- `blocked_tools` - Tools blocked in discussion mode
- `branch_enforcement.enabled` - Enable/disable git branch checking
- `task_detection.enabled` - Enable/disable task-based workflows

State files in `.claude/state/`:
- `current_task.json` - Active task metadata
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
- Session start hooks for context loading (session-start.py)
- Shared state management across all hooks (shared_state.py)
- Cross-platform path handling using pathlib.Path throughout
- Windows-specific command prefixing with explicit python interpreter

### Agent Delegation
- Heavy file operations delegated to specialized agents
- Agents receive full conversation transcript for context
- Agent results returned to main conversation thread
- Agent state isolated in separate context windows

### Task Structure
- Markdown files with standardized sections (Purpose, Context, Success Criteria, Work Log)
- Directory-based tasks for complex multi-phase work
- File-based tasks for focused single objectives
- Automatic branch mapping from task naming conventions

### Subagent Protection
- Detection mechanism prevents DAIC reminders in subagent contexts
- Subagents blocked from editing .claude/state files
- Strict separation between main thread and agent operations

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
- Task templates for consistent structure
- CLAUDE.sessions.md behavioral template
- Protocol markdown files for complex workflows
- Agent prompt templates for specialized operations

## Quality Assurance Features

### Context Management
- Token counting and usage warnings at 75%/90% thresholds
- Automatic context compaction protocols
- State preservation across session boundaries
- Clean task file maintenance through logging agent

### Work Quality
- Mandatory discussion before implementation
- Code review agent for quality checks
- Pattern consistency through context gathering
- Branch enforcement prevents wrong-branch commits

### Process Integrity
- Hook-based enforcement cannot be bypassed
- State file protection from unauthorized changes
- Chronological work log maintenance
- Task scope enforcement through structured protocols

## Related Documentation

- docs/INSTALL.md - Detailed installation guide
- docs/USAGE_GUIDE.md - Workflow and feature documentation
- cc_sessions/knowledge/ - Internal architecture documentation
- README.md - Marketing-focused feature overview
- sessions/protocols/ - Workflow protocol specifications (in installed projects)

## Sessions System Behaviors

@CLAUDE.sessions.md
