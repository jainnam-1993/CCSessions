# Changelog

All notable changes to cc-sessions will be documented in this file.

## [0.5.3] - 2025-10-22

### Breaking Changes
- **Simplified installation**: Removed Node.js/NPM support - use `./install.sh` only
- **Flattened directory structure**: Moved all files from `cc_sessions/` subdirectory to root
- **Removed Python package support**: No longer installable via pipx/pip

### Removed
- install.js, package.json, package-lock.json (Node/NPM support)
- pyproject.toml, cc_sessions/__init__.py (Python package structure)
- CLAUDE.sessions.md template (using Obsidian for session management)
- cc_sessions/ subdirectory entirely
- Obsolete cc-sessions alias from ~/.aliases

### Changed
- All paths now reference root-level directories: `hooks/`, `scripts/`, `commands/`, `templates/`, `knowledge/`
- install.sh, cc-sessions-auto-setup.sh, bulk-update-projects.sh updated with new paths
- Simpler architecture: single bash installer, no package manager dependencies

### Fixed
- daic commands (bash, cmd, ps1) now use `$CC_SESSIONS_PATH/hooks` instead of `.claude/hooks`
- Documentation updated to reflect flattened structure
- CHANGELOG.md paths corrected

## [0.5.2] - 2025-10-22

### Changed
- **Central statusline script**: Statusline now references central installation instead of local copy
- Settings.json now uses `$CC_SESSIONS_PATH/scripts/statusline-script.sh`
- Removed statusline copying during installation - central script is used directly

### Fixed
- Automatic cleanup of old local statusline-script.sh files during upgrades
- Consistent architecture: all hooks and scripts now centralized

## [0.5.0] - 2025-10-22

### Major Architectural Change: Central Hooks
- **Breaking Change**: Hooks now referenced from central installation instead of copied locally
- Requires `CC_SESSIONS_PATH` environment variable pointing to cc-sessions installation
- All projects now share central hooks at `$CC_SESSIONS_PATH/hooks/`
- Settings version tracking in `.claude/state/settings-version` for smart upgrades

### Added
- Environment variable validation in all installers (requires `CC_SESSIONS_PATH`)
- Settings version checking - only regenerates settings.json when needed
- Automatic cleanup of old local hooks and version files during upgrade
- Stop hook (`response-complete.py`) properly added to settings.json

### Changed
- **settings.json**: Hook paths now use `$CC_SESSIONS_PATH` instead of `$CLAUDE_PROJECT_DIR`
- **State management**: Moved from `sessions-version` to `settings-version`
- **Project structure**: No more `.claude/hooks/` directory (hooks are central)
- **Auto-setup**: Now checks `settings-version` instead of `sessions-version`
- Removed task management remnants (already removed in v0.4.0)

### Fixed
- Heredoc bypass in DAIC enforcement: Added `<<` and `<<<` patterns
- Improved output redirection detection: Changed `>` pattern to exclude pipes
- MCP tool matcher in PreToolUse now includes `mcp__.*` pattern

### Upgrade Notes
**Action Required**: Add to `~/.zshrc`:
```bash
export CC_SESSIONS_PATH="/Volumes/workplace/Scripts/cc-sessions"
```
Then run installer in each project to migrate to central hooks.

## [0.4.1] - 2025-10-22 [SUPERSEDED]

### Fixed
- Heredoc bypass in DAIC enforcement
- Output redirection detection improvements

## [0.4.0] - 2025-10-18

### Added
- Version checking in install.sh for instant skip on same version and automatic upgrades
- Version stored in `.claude/state/sessions-version` for fast installation checks

### Fixed
- daic command blocking now uses exact match instead of substring match
- Prevents false positives when commands reference paths like `/tmp/daic-debug.log`
- Hook no longer blocks legitimate commands containing "daic" in paths or arguments

### Changed
- Removed task management infrastructure (task-based workflows)
- Cleaned up documentation to remove task management references
- Simplified statusline to remove task counting
- Updated CLAUDE.md and CLAUDE.sessions.md to reflect DAIC-only workflow

### Technical
- install.sh exits immediately (~0.1s) if same version detected
- Automatic upgrade when version changes
- Hook improvements to sessions-enforce.py for more precise command blocking

## [0.2.6] - Previous Release

Initial stable release with task management and DAIC enforcement.
