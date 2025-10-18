#!/usr/bin/env python3
"""Stop hook to automatically switch back to discussion mode after implementation completes."""
import json
import sys
from pathlib import Path
from shared_state import check_daic_mode_bool, set_daic_mode

# Load input
input_data = json.load(sys.stdin)

# Check current mode
discussion_mode = check_daic_mode_bool()

# If in implementation mode, switch back to discussion
if not discussion_mode:
    set_daic_mode(True)
    # Exit with code 0 and no output - we don't need to block or provide feedback
    # The mode has been switched silently
    sys.exit(0)

# Already in discussion mode, do nothing
sys.exit(0)
