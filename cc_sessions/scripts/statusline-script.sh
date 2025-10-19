#!/bin/bash

# Claude Code StatusLine Script
# Provides comprehensive session information in a clean format
# System-agnostic version using Python instead of jq

# Read JSON input from stdin
input=$(cat)

# Extract basic info using Python (works on all systems)
cwd=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('workspace', {}).get('current_dir') or data.get('cwd', ''))")
model_name=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('model', {}).get('display_name', 'Claude'))")
session_id=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('session_id', ''))")

# Function to calculate context breakdown and progress
calculate_context() {
    # Get transcript if available
    transcript_path=$(echo "$input" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('transcript_path', ''))")
    
    # Determine usable context limit (80% of theoretical before auto-compact)
    if [[ "$model_name" == *"1M"* ]]; then
        context_limit=800000   # 800k usable for 1M context models
    else
        context_limit=160000   # 160k usable for 200k models (all Sonnets, Opus, Haiku)
    fi
    
    if [[ -n "$transcript_path" && -f "$transcript_path" ]]; then
        # Parse transcript to get real token usage from most recent main-chain message
        total_tokens=$(python3 -c "
import sys, json

try:
    with open('$transcript_path', 'r') as f:
        lines = f.readlines()
    
    most_recent_usage = None
    most_recent_timestamp = None
    
    for line in lines:
        try:
            data = json.loads(line.strip())
            # Skip sidechain entries (subagent calls)
            if data.get('isSidechain', False):
                continue
            
            # Check for usage data in main-chain messages
            if data.get('message', {}).get('usage'):
                timestamp = data.get('timestamp')
                if timestamp and (not most_recent_timestamp or timestamp > most_recent_timestamp):
                    most_recent_timestamp = timestamp
                    most_recent_usage = data['message']['usage']
        except:
            continue
    
    # Calculate context length (input + cache read only, NOT output or cache creation)
    if most_recent_usage:
        context_length = (
            most_recent_usage.get('input_tokens', 0) +
            most_recent_usage.get('cache_read_input_tokens', 0) +
            most_recent_usage.get('cache_creation_input_tokens', 0)
        )
        print(context_length)
    else:
        print(0)
except:
    print(0)
" 2>/dev/null)
        
        # Calculate actual context usage percentage
        if [[ $total_tokens -gt 0 ]]; then
            # Use Python for floating point math (bc not available on all systems)
            progress_pct=$(python3 -c "print(f'{$total_tokens * 100 / $context_limit:.1f}')")
            progress_pct_int=$(python3 -c "print(int($total_tokens * 100 / $context_limit))")
            if [[ $progress_pct_int -gt 100 ]]; then
                progress_pct="100.0"
                progress_pct_int=100
            fi
        else
            progress_pct="0.0"
            progress_pct_int=0
        fi
    else
        # Default values when no transcript available - still add default context
        total_tokens=17900
        progress_pct=$(python3 -c "print(f'{$total_tokens * 100 / $context_limit:.1f}')")
        progress_pct_int=$(python3 -c "print(int($total_tokens * 100 / $context_limit))")
    fi
    
    # Format token count in 'k' format
    formatted_tokens=$(python3 -c "print(f'{$total_tokens // 1000}k')")
    formatted_limit=$(python3 -c "print(f'{$context_limit // 1000}k')")
    
    # Create progress bar (capped at 100%) with Ayu Dark colors
    filled_blocks=$((progress_pct_int / 10))
    if [[ $filled_blocks -gt 10 ]]; then filled_blocks=10; fi
    empty_blocks=$((10 - filled_blocks))
    
    # Ayu Dark colors (converted to closest ANSI 256)
    if [[ $progress_pct_int -lt 50 ]]; then
        bar_color="\033[38;5;114m"  # AAD94C green
    elif [[ $progress_pct_int -lt 80 ]]; then
        bar_color="\033[38;5;215m"  # FFB454 orange
    else
        bar_color="\033[38;5;203m"  # F26D78 red
    fi
    gray_color="\033[38;5;242m"     # Dim for empty blocks
    text_color="\033[38;5;250m"     # BFBDB6 light gray
    reset="\033[0m"
    
    progress_bar="${bar_color}"
    for ((i=0; i<filled_blocks; i++)); do progress_bar+="█"; done
    progress_bar+="${gray_color}"
    for ((i=0; i<empty_blocks; i++)); do progress_bar+="░"; done
    progress_bar+="${reset} ${text_color}${progress_pct}% (${formatted_tokens}/${formatted_limit})${reset}"
    
    echo -e "$progress_bar"
}


# Get DAIC mode with color
get_daic_mode() {
    if [[ -f "$cwd/.claude/state/daic-mode.json" ]]; then
        mode=$(python3 -c "
import sys, json
try:
    with open('$cwd/.claude/state/daic-mode.json', 'r') as f:
        data = json.load(f)
        print(data.get('mode', 'discussion'))
except:
    print('discussion')
" 2>/dev/null)
        if [[ "$mode" == "discussion" ]]; then
            purple="\033[38;5;183m"  # D2A6FF constant purple
            reset="\033[0m"
            echo -e "${purple}DAIC: Discussion${reset}"
        else
            green="\033[38;5;114m"   # AAD94C string green
            reset="\033[0m"
            echo -e "${green}DAIC: Implementation${reset}"
        fi
    else
        purple="\033[38;5;183m"      # D2A6FF constant purple
        reset="\033[0m"
        echo -e "${purple}DAIC: Discussion${reset}"
    fi
}

# Count edited files with color
count_edited_files() {
    yellow="\033[38;5;215m"  # FFB454 func orange
    reset="\033[0m"
    if [[ -d "$cwd/.git" ]]; then
        cd "$cwd"
        # Count modified and staged files
        modified_count=$(git status --porcelain 2>/dev/null | grep -E '^[AM]|^.[AM]' | wc -l || echo "0")
        echo -e "${yellow}✎ $modified_count files${reset}"
    else
        echo -e "${yellow}✎ 0 files${reset}"
    fi
}


# Get current directory with color
get_current_directory() {
    green="[38;5;114m"   # AAD94C string green
    reset="[0m"
    # Get just the directory name (not full path)
    dir_name=$(basename "$cwd")
    echo -e "${green}📁 $dir_name${reset}"
}

# Build the complete statusline
progress_info=$(calculate_context)
daic_info=$(get_daic_mode)
directory_info=$(get_current_directory)

# Output the complete statusline in one line with color support
# Format: Progress bar | DAIC mode | Current directory
echo -e "$progress_info | $daic_info | $directory_info"
