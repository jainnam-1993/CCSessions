#!/usr/bin/env python3
"""
Claude Code Sessions Framework - Cross-Platform Python Installer

Complete installation system for the Claude Code Sessions framework with native
Windows, macOS, and Linux support. Handles platform-specific path handling,
command installation, and shell compatibility.

Key Features:
    - Windows compatibility with native .cmd and .ps1 script support
    - Cross-platform path handling using pathlib
    - Platform-aware file permission management
    - Interactive configuration with terminal UI
    - Global daic command installation with PATH integration
    
Platform Support:
    - Windows 10/11 (Command Prompt, PowerShell, Git Bash)
    - macOS (Bash, Zsh)
    - Linux distributions (Bash, other shells)

Installation Locations:
    - Windows: %USERPROFILE%\\AppData\\Local\\cc-sessions\\bin
    - Unix/Mac: /usr/local/bin

See Also:
    - install.js: Node.js installer wrapper with same functionality
    - cc_sessions.scripts.daic: Unix bash implementation
    - cc_sessions.scripts.daic.cmd: Windows Command Prompt implementation
    - cc_sessions.scripts.daic.ps1: Windows PowerShell implementation
"""

import os
import sys
import json
import shutil
import stat
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Colors for terminal output
class Colors:
    RESET = '\033[0m'
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BGRED = '\033[41m'
    BGGREEN = '\033[42m'
    BGYELLOW = '\033[43m'
    BGBLUE = '\033[44m'
    BGMAGENTA = '\033[45m'
    BGCYAN = '\033[46m'

def color(text: str, color_code: str) -> str:
    """Colorize text for terminal output"""
    return f"{color_code}{text}{Colors.RESET}"

def command_exists(command: str) -> bool:
    """Check if a command exists in the system"""
    if os.name == 'nt':
        # Windows - try with common extensions
        for ext in ['', '.exe', '.bat', '.cmd']:
            if shutil.which(command + ext):
                return True
        return False
    return shutil.which(command) is not None

def get_package_dir() -> Path:
    """Get the directory where the package is installed"""
    import cc_sessions
    # All data files are now inside cc_sessions/
    return Path(cc_sessions.__file__).parent

class SessionsInstaller:
    def __init__(self):
        self.package_dir = get_package_dir()
        self.project_root = self.detect_project_directory()
        self.config = {
            "developer_name": "the developer",
            "trigger_phrases": ["make it so", "run that", "go ahead", "yert"],
            "blocked_tools": ["Edit", "Write", "MultiEdit", "NotebookEdit"]
        }
    
    def detect_project_directory(self) -> Path:
        """Detect the correct project directory when running from pip/pipx"""
        current_dir = Path.cwd()
        
        # If running from site-packages or pipx environment
        if 'site-packages' in str(current_dir) or '.local/pipx' in str(current_dir):
            print(color("⚠️  Running from package directory, not project directory.", Colors.YELLOW))
            print()
            project_path = input("Enter the path to your project directory (or press Enter for current directory): ")
            if project_path:
                return Path(project_path).resolve()
            else:
                # Default to user's current working directory before pip ran
                return Path.cwd()
        
        return current_dir
    
    def check_dependencies(self) -> None:
        """Check for required dependencies"""
        print(color("Checking dependencies...", Colors.CYAN))
        
        # Check Python version
        if sys.version_info < (3, 8):
            print(color("❌ Python 3.8+ is required.", Colors.RED))
            sys.exit(1)
        
        # Check pip
        if not command_exists("pip3") and not command_exists("pip"):
            print(color("❌ pip is required but not installed.", Colors.RED))
            sys.exit(1)
        
        # Check Git (warning only)
        if not command_exists("git"):
            print(color("⚠️  Warning: Git not found. Sessions works best with git.", Colors.YELLOW))
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    def create_directories(self) -> None:
        """Create necessary directory structure"""
        print(color("Creating directory structure...", Colors.CYAN))
        
        dirs = [
            ".claude/hooks",
            ".claude/state",
            ".claude/commands",
            "sessions"
        ]
        
        for dir_path in dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
    
    
    def copy_files(self) -> None:
        """Copy all necessary files to the project"""
        # Copy hooks
        print(color("Installing hooks...", Colors.CYAN))
        hooks_dir = self.package_dir / "hooks"
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.py"):
                dest = self.project_root / ".claude/hooks" / hook_file.name
                shutil.copy2(hook_file, dest)
                if os.name != 'nt':
                    dest.chmod(0o755)
        
        
        
        # Copy commands
        print(color("Installing commands...", Colors.CYAN))
        commands_dir = self.package_dir / "commands"
        if commands_dir.exists():
            for command_file in commands_dir.glob("*.md"):
                dest = self.project_root / ".claude/commands" / command_file.name
                shutil.copy2(command_file, dest)
        
    
    def install_daic_command(self) -> None:
        """Install the daic command globally"""
        print(color("Installing daic command...", Colors.CYAN))
        
        if os.name == 'nt':  # Windows
            # Install Windows scripts (.cmd and .ps1)
            daic_cmd_source = self.package_dir / "scripts/daic.cmd"
            daic_ps1_source = self.package_dir / "scripts/daic.ps1"
            
            # Try to install to user's local directory
            local_bin = Path.home() / "AppData" / "Local" / "cc-sessions" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            
            if daic_cmd_source.exists():
                daic_cmd_dest = local_bin / "daic.cmd"
                shutil.copy2(daic_cmd_source, daic_cmd_dest)
                print(color(f"  ✓ Installed daic.cmd to {local_bin}", Colors.GREEN))
            
            if daic_ps1_source.exists():
                daic_ps1_dest = local_bin / "daic.ps1"
                shutil.copy2(daic_ps1_source, daic_ps1_dest)
                print(color(f"  ✓ Installed daic.ps1 to {local_bin}", Colors.GREEN))
            
            print(color(f"  ℹ Add {local_bin} to your PATH to use 'daic' command", Colors.YELLOW))
        else:
            # Unix/Mac installation
            daic_source = self.package_dir / "scripts/daic"
            if not daic_source.exists():
                print(color("⚠️  daic script not found in package.", Colors.YELLOW))
                return
            
            daic_dest = Path("/usr/local/bin/daic")
            
            try:
                shutil.copy2(daic_source, daic_dest)
                daic_dest.chmod(0o755)
            except PermissionError:
                print(color("⚠️  Cannot write to /usr/local/bin. Trying with sudo...", Colors.YELLOW))
                try:
                    subprocess.run(["sudo", "cp", str(daic_source), str(daic_dest)], check=True)
                    subprocess.run(["sudo", "chmod", "+x", str(daic_dest)], check=True)
                except subprocess.CalledProcessError:
                    print(color("⚠️  Could not install daic command globally.", Colors.YELLOW))
    
    def configure(self) -> None:
        """Interactive configuration"""
        print()
        print(color("╔═══════════════════════════════════════════════════════════════╗", Colors.BRIGHT + Colors.CYAN))
        print(color("║                    CONFIGURATION SETUP                        ║", Colors.BRIGHT + Colors.CYAN))
        print(color("╚═══════════════════════════════════════════════════════════════╝", Colors.BRIGHT + Colors.CYAN))
        print()
        
        self.statusline_installed = False
        
        # Developer name section
        print(color(f"\n★ DEVELOPER IDENTITY", Colors.BRIGHT + Colors.MAGENTA))
        print(color("─" * 60, Colors.DIM))
        print(color("  Claude will use this name when addressing you in sessions", Colors.DIM))
        print()
        
        name = input(color("  Your name: ", Colors.CYAN))
        if name:
            self.config["developer_name"] = name
            print(color(f"  ✓ Hello, {name}!", Colors.GREEN))
        
        # Statusline installation section
        print(color(f"\n\n★ STATUSLINE INSTALLATION", Colors.BRIGHT + Colors.MAGENTA))
        print(color("─" * 60, Colors.DIM))
        print(color("  Real-time status display in Claude Code showing:", Colors.WHITE))
        print(color("    • DAIC mode status", Colors.CYAN))
        print(color("    • Token usage with visual progress bar", Colors.CYAN))
        print(color("    • Modified file counts", Colors.CYAN))
        print()
        
        install_statusline = input(color("  Install statusline? (y/n): ", Colors.CYAN))
        
        if install_statusline.lower() == 'y':
            statusline_source = self.package_dir / "scripts/statusline-script.sh"
            if statusline_source.exists():
                print(color("  Installing statusline script...", Colors.DIM))
                statusline_dest = self.project_root / ".claude/statusline-script.sh"
                shutil.copy2(statusline_source, statusline_dest)
                statusline_dest.chmod(0o755)
                self.statusline_installed = True
                print(color("  ✓ Statusline installed successfully", Colors.GREEN))
            else:
                print(color("  ⚠ Statusline script not found in package", Colors.YELLOW))
        
        # DAIC trigger phrases section
        print(color(f"\n\n★ DAIC WORKFLOW CONFIGURATION", Colors.BRIGHT + Colors.MAGENTA))
        print(color("─" * 60, Colors.DIM))
        print(color("  The DAIC system enforces discussion before implementation.", Colors.WHITE))
        print(color("  Trigger phrases tell Claude when you're ready to proceed.", Colors.WHITE))
        print()
        print(color("  Default triggers:", Colors.CYAN))
        for phrase in self.config['trigger_phrases']:
            print(color(f'    → "{phrase}"', Colors.GREEN))
        print()
        print(color('  Hint: Common additions: "implement it", "do it", "proceed"', Colors.DIM))
        print()
        
        # Allow adding multiple custom trigger phrases
        while True:
            custom_trigger = input(color("  Add custom trigger phrase (Enter to skip): ", Colors.CYAN))
            if not custom_trigger:
                break
            self.config["trigger_phrases"].append(custom_trigger)
            print(color(f'  ✓ Added: "{custom_trigger}"', Colors.GREEN))
        
        # API Mode configuration
        print(color(f"\n\n★ THINKING BUDGET CONFIGURATION", Colors.BRIGHT + Colors.MAGENTA))
        print(color("─" * 60, Colors.DIM))
        print(color("  Token usage is not much of a concern with Claude Code Max", Colors.WHITE))
        print(color("  plans, especially the $200 tier. But API users are often", Colors.WHITE))
        print(color("  budget-conscious and want manual control.", Colors.WHITE))
        print()
        print(color("  Sessions was built to preserve tokens across context windows", Colors.CYAN))
        print(color("  but uses saved tokens to enable 'ultrathink' - Claude's", Colors.CYAN))
        print(color("  maximum thinking budget - on every interaction for best results.", Colors.CYAN))
        print()
        print(color("  • Max users (recommended): Automatic ultrathink every message", Colors.DIM))
        print(color("  • API users: Manual control with [[ ultrathink ]] when needed", Colors.DIM))
        print()
        print(color("  You can toggle this anytime with: /api-mode", Colors.DIM))
        print()
        
        enable_ultrathink = input(color("  Enable automatic ultrathink for best performance? (y/n): ", Colors.CYAN))
        if enable_ultrathink.lower() == 'y':
            self.config["api_mode"] = False
            print(color("  ✓ Max mode - ultrathink enabled for best performance", Colors.GREEN))
        else:
            self.config["api_mode"] = True
            print(color("  ✓ API mode - manual ultrathink control (use [[ ultrathink ]])", Colors.GREEN))
        
        # Advanced configuration
        print(color(f"\n\n★ ADVANCED OPTIONS", Colors.BRIGHT + Colors.MAGENTA))
        print(color("─" * 60, Colors.DIM))
        print(color("  Configure tool blocking, task prefixes, and more", Colors.WHITE))
        print()
        
        advanced = input(color("  Configure advanced options? (y/n): ", Colors.CYAN))
        
        if advanced.lower() == 'y':
            # Tool blocking
            print()
            print(color("╭───────────────────────────────────────────────────────────────╮", Colors.CYAN))
            print(color("│              Tool Blocking Configuration                      │", Colors.CYAN))
            print(color("├───────────────────────────────────────────────────────────────┤", Colors.CYAN))
            print(color("│   Tools can be blocked in discussion mode to enforce DAIC     │", Colors.DIM))
            print(color("│   Default: Edit, Write, MultiEdit, NotebookEdit are blocked   │", Colors.DIM))
            print(color("╰───────────────────────────────────────────────────────────────╯", Colors.CYAN))
            print()
            
            tools = [
                ("Edit", "Edit existing files", True),
                ("Write", "Create new files", True),
                ("MultiEdit", "Multiple edits in one operation", True),
                ("NotebookEdit", "Edit Jupyter notebooks", True),
                ("Bash", "Run shell commands", False),
                ("Read", "Read file contents", False),
                ("Grep", "Search file contents", False),
                ("Glob", "Find files by pattern", False),
                ("LS", "List directory contents", False),
                ("WebSearch", "Search the web", False),
                ("WebFetch", "Fetch web content", False),
                ("Task", "Launch specialized agents", False)
            ]
            
            print(color("  Available tools:", Colors.WHITE))
            for i, (name, desc, blocked) in enumerate(tools, 1):
                icon = "🔒" if blocked else "🔓"
                status_color = Colors.YELLOW if blocked else Colors.GREEN
                print(f"    {i:2}. {icon} {color(name.ljust(15), status_color)} - {desc}")
            print()
            print(color("  Hint: Edit tools are typically blocked to enforce discussion-first workflow", Colors.DIM))
            print()
            
            modify_tools = input(color("  Modify blocked tools list? (y/n): ", Colors.CYAN))
            
            if modify_tools.lower() == 'y':
                tool_numbers = input(color("  Enter comma-separated tool numbers to block: ", Colors.CYAN))
                if tool_numbers:
                    tool_names = [t[0] for t in tools]
                    blocked_list = []
                    for num_str in tool_numbers.split(','):
                        try:
                            num = int(num_str.strip())
                            if 1 <= num <= len(tools):
                                blocked_list.append(tool_names[num - 1])
                        except ValueError:
                            pass
                    if blocked_list:
                        self.config["blocked_tools"] = blocked_list
                        print(color("  ✓ Tool blocking configuration saved", Colors.GREEN))
            
    
    def save_config(self) -> None:
        """Save configuration files"""
        print(color("Creating configuration...", Colors.CYAN))
        
        # Save sessions config
        config_file = self.project_root / "sessions/sessions-config.json"
        config_file.write_text(json.dumps(self.config, indent=2))
        
        # Create or update .claude/settings.json with all hooks
        print(color("Configuring hooks in settings.json...", Colors.CYAN))
        settings_file = self.project_root / ".claude/settings.json"
        
        settings = {}
        if settings_file.exists():
            print(color("Found existing settings.json, merging sessions hooks...", Colors.CYAN))
            try:
                settings = json.loads(settings_file.read_text())
            except:
                settings = {}
        else:
            print(color("Creating new settings.json with sessions hooks...", Colors.CYAN))
        
        # Define the sessions hooks
        sessions_hooks = {
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/user-messages.py" if os.name != 'nt' else "python \"%CLAUDE_PROJECT_DIR%\\.claude\\hooks\\user-messages.py\""
                        }
                    ]
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|MultiEdit|Task|Bash|mcp__serena__.*",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/sessions-enforce.py" if os.name != 'nt' else "python \"%CLAUDE_PROJECT_DIR%\\.claude\\hooks\\sessions-enforce.py\""
                        }
                    ]
                },
            ],
            "PostToolUse": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use.py" if os.name != 'nt' else "python \"%CLAUDE_PROJECT_DIR%\\.claude\\hooks\\post-tool-use.py\""
                        }
                    ]
                }
            ],
            "SessionStart": [
                {
                    "matcher": "startup|clear",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.py" if os.name != 'nt' else "python \"%CLAUDE_PROJECT_DIR%\\.claude\\hooks\\session-start.py\""
                        }
                    ]
                }
            ]
        }
        
        # Merge hooks (sessions hooks take precedence)
        if "hooks" not in settings:
            settings["hooks"] = {}
        
        # Merge each hook type
        for hook_type, hook_config in sessions_hooks.items():
            if hook_type not in settings["hooks"]:
                settings["hooks"][hook_type] = hook_config
            else:
                # Append sessions hooks to existing ones
                settings["hooks"][hook_type].extend(hook_config)
        
        # Add statusline if requested
        if hasattr(self, 'statusline_installed') and self.statusline_installed:
            settings["statusLine"] = {
                "type": "command",
                "command": "$CLAUDE_PROJECT_DIR/.claude/statusline-script.sh" if os.name != 'nt' else "%CLAUDE_PROJECT_DIR%\\.claude\\statusline-script.sh",
                "padding": 0
            }
        
        # Save the updated settings
        settings_file.write_text(json.dumps(settings, indent=2))
        print(color("✓ Sessions hooks configured in settings.json", Colors.GREEN))
        
        # Initialize DAIC state
        daic_state = self.project_root / ".claude/state/daic-mode.json"
        daic_state.write_text(json.dumps({"mode": "discussion"}, indent=2))
        
    
    def setup_claude_md(self) -> None:
        """Set up CLAUDE.md integration"""
        print()
        print(color("═══════════════════════════════════════════", Colors.BRIGHT))
        print(color("         CLAUDE.md Integration", Colors.BRIGHT))
        print(color("═══════════════════════════════════════════", Colors.BRIGHT))
        print()
        
        # Check for existing CLAUDE.md
        sessions_md = self.package_dir / "templates/CLAUDE.sessions.md"
        claude_md = self.project_root / "CLAUDE.md"
        
        if claude_md.exists():
            # File exists, preserve it and add sessions as separate file
            print(color("CLAUDE.md already exists, preserving your project-specific rules...", Colors.CYAN))
            
            # Copy CLAUDE.sessions.md as separate file
            if sessions_md.exists():
                dest = self.project_root / "CLAUDE.sessions.md"
                shutil.copy2(sessions_md, dest)
            
            # Check if it already includes sessions
            content = claude_md.read_text()
            if "@CLAUDE.sessions.md" not in content:
                print(color("Adding sessions include to existing CLAUDE.md...", Colors.CYAN))
                
                addition = "\n## Sessions System Behaviors\n\n@CLAUDE.sessions.md\n"
                with claude_md.open("a") as f:
                    f.write(addition)
                
                print(color("✅ Added @CLAUDE.sessions.md include to your CLAUDE.md", Colors.GREEN))
            else:
                print(color("✅ CLAUDE.md already includes sessions behaviors", Colors.GREEN))
        else:
            # File doesn't exist, use sessions as CLAUDE.md
            print(color("No existing CLAUDE.md found, installing sessions as your CLAUDE.md...", Colors.CYAN))
            if sessions_md.exists():
                shutil.copy2(sessions_md, claude_md)
                print(color("✅ CLAUDE.md created with complete sessions behaviors", Colors.GREEN))
    
    def run(self) -> None:
        """Run the full installation process"""
        print(color("╔════════════════════════════════════════════╗", Colors.BRIGHT))
        print(color("║            cc-sessions Installer           ║", Colors.BRIGHT))
        print(color("╚════════════════════════════════════════════╝", Colors.BRIGHT))
        print()
        
        # Check CLAUDE_PROJECT_DIR
        if not os.environ.get("CLAUDE_PROJECT_DIR"):
            print(color(f"⚠️  CLAUDE_PROJECT_DIR not set. Setting it to {self.project_root}", Colors.YELLOW))
            print("   To make this permanent, add to your shell profile:")
            print(f'   export CLAUDE_PROJECT_DIR="{self.project_root}"')
            print()
        
        try:
            self.check_dependencies()
            self.create_directories()
            self.copy_files()
            self.install_daic_command()
            self.configure()
            self.save_config()
            self.setup_claude_md()
            
            # Success message
            print()
            print()
            print(color("╔═══════════════════════════════════════════════════════════════╗", Colors.BRIGHT + Colors.GREEN))
            print(color("║                 🎉 INSTALLATION COMPLETE! 🎉                  ║", Colors.BRIGHT + Colors.GREEN))
            print(color("╚═══════════════════════════════════════════════════════════════╝", Colors.BRIGHT + Colors.GREEN))
            print()
            
            print(color("  Installation Summary:", Colors.BRIGHT + Colors.CYAN))
            print(color("  ─────────────────────", Colors.DIM))
            print(color("  ✓ Directory structure created", Colors.GREEN))
            print(color("  ✓ Hooks installed and configured", Colors.GREEN))
            print(color("  ✓ Commands deployed", Colors.GREEN))
            print(color("  ✓ daic command available globally", Colors.GREEN))
            print(color("  ✓ Configuration saved", Colors.GREEN))
            print(color("  ✓ DAIC state initialized (Discussion mode)", Colors.GREEN))
            
            if hasattr(self, 'statusline_installed') and self.statusline_installed:
                print(color("  ✓ Statusline configured", Colors.GREEN))
            
            print()
            
            # Test daic command
            if command_exists("daic"):
                print(color("  ✓ daic command verified and working", Colors.GREEN))
            else:
                print(color("  ⚠ daic command not in PATH", Colors.YELLOW))
                print(color("       Add /usr/local/bin to your PATH", Colors.DIM))
            
            print()
            print(color("  ★ NEXT STEPS", Colors.BRIGHT + Colors.MAGENTA))
            print(color("  ─────────────", Colors.DIM))
            print()
            print(color("  1. Restart Claude Code to activate the sessions hooks", Colors.WHITE))
            print(color("     → Close and reopen Claude Code", Colors.DIM))
            print()
            print(color("  2. Start working with the DAIC workflow:", Colors.WHITE))
            print(color("     → Discuss approach first", Colors.DIM))
            print(color('     → Say "make it so" to implement', Colors.DIM))
            print(color('     → Run "daic" to return to discussion', Colors.DIM))
            print()
            print(color("  ──────────────────────────────────────────────────────", Colors.DIM))
            print()
            print(color(f"  Welcome aboard, {self.config['developer_name']}! 🚀", Colors.BRIGHT + Colors.CYAN))
            
        except Exception as e:
            print(color(f"❌ Installation failed: {e}", Colors.RED))
            sys.exit(1)

def main():
    """Main entry point for the installer"""
    installer = SessionsInstaller()
    installer.run()

def install():
    """Alias for main() for compatibility"""
    main()

if __name__ == "__main__":
    main()
