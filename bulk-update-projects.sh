#!/bin/bash
# Bulk update all projects to use central hooks

set -e

export CC_SESSIONS_PATH="/Volumes/workplace/Scripts/cc-sessions"

echo "🔄 Bulk updating all projects to cc-sessions v0.5.1 (central hooks)"
echo "=================================================================="
echo ""

updated=0
skipped=0
failed=0

# Update projects in .claude/projects
for project in /Users/jainnam/.claude/projects/*/; do
    # Extract actual project path from encoded directory name
    project_path=$(basename "$project" | sed "s/-/\//g" | sed "s/^\/\///")

    # Check if actual project exists and has .claude directory
    if [ -d "/$project_path/.claude" ]; then
        echo "📁 Updating: /$project_path"
        cd "/$project_path"

        # Force update by removing settings-version
        rm -f .claude/state/settings-version

        # Run auto-setup (non-interactive)
        if "$CC_SESSIONS_PATH/cc-sessions-auto-setup.sh" >/dev/null 2>&1; then
            echo "  ✅ Updated successfully"
            ((updated++))
        else
            echo "  ❌ Update failed"
            ((failed++))
        fi
    fi
done

echo ""
echo "=================================================================="
echo "✅ Bulk update complete!"
echo "  Updated: $updated projects"
echo "  Skipped: $skipped projects (already up to date)"
echo "  Failed: $failed projects"
