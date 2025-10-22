#!/bin/bash

# cc-sessions Automated Setup Wrapper
# Automatically installs and configures cc-sessions with predefined responses

set -e

# Package version
SESSIONS_VERSION="0.5.3"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_SESSIONS_INSTALL="$SCRIPT_DIR/install.sh"

# Skip setup if we're in any .claude directory
if [[ "$PWD" == *"/.claude"* ]]; then
    exit 0
fi

# Check for CC_SESSIONS_PATH environment variable
if [[ -z "$CC_SESSIONS_PATH" ]]; then
    echo "❌ CC_SESSIONS_PATH not set. Add to ~/.zshrc:"
    echo "  export CC_SESSIONS_PATH=\"/Volumes/workplace/Scripts/cc-sessions\""
    exit 1
fi

# Settings version check - skip if already up to date
SETTINGS_VERSION_FILE=".claude/state/settings-version"
if [[ -f "$SETTINGS_VERSION_FILE" ]]; then
    INSTALLED_VERSION=$(cat "$SETTINGS_VERSION_FILE")
    if [[ "$INSTALLED_VERSION" == "$SESSIONS_VERSION" ]]; then
        # Silent skip - already configured
        exit 0
    fi
fi

echo "🔧 cc-sessions Auto Setup"
echo "=========================="

# Verify the cc-sessions installer exists
if [[ ! -f "$CC_SESSIONS_INSTALL" ]]; then
    echo "❌ cc-sessions installer not found at: $CC_SESSIONS_INSTALL"
    echo "Please ensure cc-sessions is installed in the same directory as this script"
    exit 1
fi

# Check if expect is installed
if ! command -v expect &> /dev/null; then
    echo "❌ 'expect' command not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install expect
    else
        echo "Please install 'expect' manually: brew install expect"
        exit 1
    fi
fi

# Fix /usr/local/bin permissions if needed (one-time fix)
if [[ ! -w /usr/local/bin ]]; then
    echo "🔧 Fixing /usr/local/bin permissions..."
    sudo chown $USER /usr/local/bin
fi

echo "🚀 Running automated cc-sessions setup..."

# Use expect to automate the interactive installer
expect << EOF
set timeout 30
spawn $CC_SESSIONS_INSTALL

# Handle git warning if not in git repo
expect {
    "Continue anyway? (y/n):" {
        send "y\r"
        exp_continue
    }
    "Your name:" {
        send "Naman\r"
    }
}

# Wait for statusline prompt
expect "Install statusline? (y/n):"
send "y\r"

# Wait for custom trigger prompt
expect "Add custom trigger phrase (Enter to skip):"
send "yes\r"

# Add proceed trigger
expect "Add custom trigger phrase (Enter to skip):"
send "proceed\r"

# Add implement trigger
expect "Add custom trigger phrase (Enter to skip):"
send "implement\r"

# Skip additional triggers
expect "Add custom trigger phrase (Enter to skip):"
send "\r"

# Wait for ultrathink prompt
expect "Enable automatic ultrathink for best performance? (y/n):"
send "n\r"

# Wait for advanced options prompt
expect "Configure advanced options? (y/n):"
send "n\r"

# Wait for installation to complete
expect eof
EOF

echo "✅ cc-sessions installation completed!"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code to activate sessions hooks"
echo "2. Use DAIC workflow: discuss first, then say trigger phrases to implement:"
echo "   • 'make it so' • 'yes' • 'proceed' • 'implement' • 'go ahead' • 'run that'"
