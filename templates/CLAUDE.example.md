# CLAUDE.md

This file provides project overview and includes the sessions system behaviors.

## Project Overview

[Brief 2-3 sentence description of your project goes here]

## Architecture

[Brief description of your project structure - keep to essential information only]

### Core Services
- [List main services/modules with one-line descriptions]

## Context Philosophy

This project uses the Claude Code Sessions system for task management and context preservation.
- Task-specific context is loaded dynamically via context manifests
- Keep this root CLAUDE.md minimal (< 100 lines)
- Detailed documentation belongs in task files, not here

## Important Files

When working on tasks, refer to:
- **sessions/tasks/*.md** - Active task files with context manifests
- **.claude/state/current_task.json** - Current task state

The SessionStart hook will guide you to load appropriate context based on the active task.

## Sessions System Behaviors

@CLAUDE.sessions.md

## Project-Specific Rules

[Add any project-specific behavioral rules or constraints here]
[Keep this section minimal - most rules should be task-specific]