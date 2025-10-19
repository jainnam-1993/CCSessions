# Changelog

All notable changes to cc-sessions will be documented in this file.

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
