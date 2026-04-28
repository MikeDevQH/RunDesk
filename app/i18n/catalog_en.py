"""Translation catalog — English."""

CATALOG_EN = {
    # === Sidebar ===
    "sidebar": {
        "dashboard": "Dashboard",
        "commands": "Commands",
        "scenes": "Scenes",
        "launcher": "Launcher",
        "appearance": "Appearance",
        "languages": "Languages",
        "tutorials": "Help",
        "diagnostics": "Diagnostics",
        "about": "About",
    },
    # === Dashboard ===
    "dashboard": {
        "title": "Dashboard",
        "subtitle": "Overview of RunDesk status",
        "status": "Status",
        "active": "Active",
        "running": "Launcher is running",
        "hotkey": "Shortcut",
        "hotkey_sub": "Activation hotkey",
        "commands": "Commands",
        "commands_sub": "Registered commands",
        "scenes": "Scenes",
        "scenes_sub": "Configured scenes",
        "language": "Language",
        "language_sub": "Active UI language",
        "monitors": "Monitors",
        "monitors_sub": "Auto-detection",
        "monitors_fallback": "Could not detect",
        "primary": "primary",
        "active_count": "{n} active",
        "quick_actions": "Quick actions",
        "quick_hint": "Quick actions will be available in future phases.",
        "total_executions": "Total executions",
        "top_commands": "Most used commands",
        "recent_activity": "Recent activity",
        "no_activity": "No activity yet. Use Ctrl+Space to run your first command!",
        "times": "{n} times",
        "success": "Success",
        "failed": "Failed",
        "today": "Today",
        "yesterday": "Yesterday",
        "days_ago": "{n} days ago",
    },
    # === Commands ===
    "commands": {
        "title": "Commands",
        "subtitle": "Manage the launcher's available commands",
        "search": "Search commands...",
        "add": "New command",
        "all": "All",
        "system": "System",
        "custom": "Custom",
        "col_name": "Name",
        "col_type": "Type",
        "col_category": "Category",
        "col_aliases": "Aliases",
        "col_status": "Status",
        "col_actions": "Actions",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "edit": "Edit",
        "duplicate": "Duplicate",
        "delete": "Delete",
        "enable": "Enable",
        "disable": "Disable",
        "locked": "Locked",
        "locked_edit_msg": "This command is locked and cannot be edited.",
        "toggle": "Toggle",
        "test": "Test",
        "edit_tip": "Edit selected command",
        "duplicate_tip": "Duplicate selected command",
        "toggle_tip": "Toggle command state",
        "delete_tip": "Delete custom command",
        "test_tip": "Run command to test",
        "empty": "No commands found with this filter.",
        "confirm_delete": "Are you sure you want to delete command '{name}'?",
        "confirm_title": "Confirm deletion",
    },
    # === Command Dialog ===
    "cmd_dialog": {
        "title_new": "New command",
        "title_edit": "Edit command",
        "id": "Unique ID",
        "id_hint": "Identifier without spaces (e.g. open_chrome)",
        "name": "Name",
        "name_hint": "Descriptive command name",
        "aliases": "Aliases",
        "aliases_hint": "Comma-separated (e.g. chrome, browse)",
        "type": "Type",
        "category": "Category",
        "path": "Program path",
        "url": "URL",
        "shell": "Shell command",
        "window_position": "Position window on open",
        "monitor": "Monitor",
        "position": "Position",
        "save": "Save",
        "cancel": "Cancel",
        "error": "Error",
        "err_id_required": "ID is required.",
        "err_id_spaces": "ID cannot contain spaces.",
        "err_name_required": "Name is required.",
        "err_id_exists": "A command with this ID already exists.",
    },
    # === Scenes ===
    "scenes": {
        "title": "Scenes",
        "subtitle": "Create routines that execute multiple actions in sequence",
        "add": "New scene",
        "edit": "Edit",
        "toggle_disable": "Disable",
        "toggle_enable": "Enable",
        "delete": "Delete",
        "steps_count": "{n} steps",
        "aliases_label": "Aliases: {aliases}",
        "empty": "No scenes created. Create one to automate tasks.",
        "confirm_delete": "Delete scene '{name}'?",
        "confirm_title": "Confirm deletion",
    },
    # === Scene Dialog ===
    "scene_dialog": {
        "title_new": "New scene",
        "title_edit": "Edit scene",
        "id": "Unique ID",
        "name": "Name",
        "aliases": "Aliases (comma-separated)",
        "steps": "Scene steps",
        "add_step": "+ Add step",
        "add_delay": "Delay",
        "step": "Step {n}",
        "step_type": "Type",
        "step_target": "Target/Value",
        "step_delay": "Delay (ms)",
        "delete_step": "Delete",
        "save": "Save",
        "cancel": "Cancel",
        "error": "Error",
        "err_id_required": "ID is required.",
        "err_id_spaces": "ID cannot contain spaces.",
        "err_name_required": "Name is required.",
        "err_no_steps": "The scene needs at least one step.",
    },
    # === Appearance ===
    "appearance": {
        "title": "Appearance",
        "subtitle": "Customize colors, overlay style, and sounds",
        "accent_color": "Accent color",
        "overlay": "Overlay",
        "blur": "Blur/acrylic effect",
        "glow": "Glow around the input",
        "glow_intensity": "Glow intensity",
        "opacity": "Background opacity",
        "animation": "Animation speed",
        "sounds": "Sounds",
        "sounds_enable": "Feedback sounds enabled",
        "preview_hint": "Overlay preview",
    },
    # === Launcher Settings ===
    "launcher": {
        "title": "Launcher Settings",
        "subtitle": "Keyboard shortcut, overlay, fuzzy matching, and behavior settings",
        "section_activation": "Activation",
        "hotkey": "Keyboard shortcut",
        "hotkey_desc": "Fixed shortcut to show the overlay",
        "overlay_monitor": "Overlay monitor",
        "overlay_monitor_desc": "Where the floating input appears",
        "monitor_active": "Active monitor",
        "section_fuzzy": "Fuzzy Matching",
        "fuzzy_enabled": "Enabled",
        "fuzzy_enabled_desc": "Tolerate typos when typing commands",
        "fuzzy_threshold": "Threshold",
        "fuzzy_threshold_desc": "Sensitivity (0.0 = very permissive, 1.0 = exact)",
        "section_behavior": "Behavior",
        "start_windows": "Start with Windows",
        "start_windows_desc": "Start automatically on boot",
        "start_minimized": "Start minimized",
        "start_minimized_desc": "Start directly in the system tray",
        "timeout": "Execution timeout",
        "timeout_desc": "Maximum wait time per action",
        "history_max": "Max history",
        "history_max_desc": "Recent commands to remember",
        "history_max_value": "{n} commands",
        "yes": "Yes",
        "no": "No",
        "saved": "Saved",
        "restart_hint": "Some changes may require a restart to fully apply.",
    },
    # === Languages ===
    "languages": {
        "title": "Languages",
        "subtitle": "Select RunDesk's interface language",
        "active_badge": "Active",
        "es_name": "Español",
        "es_native": "Interfaz en español",
        "en_name": "English",
        "en_native": "Interface in English",
        "info_title": "About language switching",
        "info_1": "Changes all interface text to the selected language.",
        "info_2": "Command aliases work in any language independently.",
        "info_3": "Custom commands keep the language they were created in.",
        "info_4": "The change is instant, no restart required.",
    },
    # === Tutorials ===
    "tutorials": {
        "title": "Help & tutorials",
        "subtitle": "Learn how to use RunDesk step by step",
        "getting_started": "Getting started",
        "advanced": "Advanced usage",
        "maintenance": "Maintenance",
        "back": "← Back to tutorials",
        "tut_first_title": "Your first custom command",
        "tut_first_desc": (
            "Learn to create a command that opens your favorite app"
            " with a simple alias."
        ),
        "tut_first_level": "Basic",
        "tut_first_step_1": (
            "Open the **Commands** page by clicking on the sidebar."
        ),
        "tut_first_step_2": (
            "Click the **New command** button at the top."
        ),
        "tut_first_step_3": (
            "Fill in the form:\n"
            "  • **ID**: a unique identifier without spaces (e.g. `open_chrome`)\n"
            "  • **Name**: a descriptive name (e.g. Open Chrome)\n"
            "  • **Aliases**: short words to invoke the command (e.g. chrome, nav)\n"
            "  • **Type**: select the action type (program, URL, folder…)\n"
            "  • **Path/URL**: the program path or URL to open"
        ),
        "tut_first_step_4": (
            "Click **Save** to create the command."
        ),
        "tut_first_step_5": (
            "Try it! Press **Ctrl+Space** to open the overlay "
            "and type one of the aliases you configured."
        ),
        "tut_first_action": "Go to Commands",
        "tut_first_tip": (
            "System commands (shutdown, restart, etc.) come "
            "pre-configured and cannot be deleted."
        ),
        "tut_alias_title": "Using aliases and shortcuts",
        "tut_alias_desc": (
            "Set up multiple aliases to quickly"
            " access your commands."
        ),
        "tut_alias_level": "Basic",
        "tut_alias_step_1": (
            "Go to the **Commands** page and select an existing command."
        ),
        "tut_alias_step_2": (
            "Click **Edit** to open the editing form."
        ),
        "tut_alias_step_3": (
            "In the **Aliases** field, type several words "
            "separated by commas.\n"
            "  • Example: `chrome, browser, nav, web`\n"
            "  • Each alias is a different way to invoke the same command."
        ),
        "tut_alias_step_4": (
            "Save the changes. Now you can use any "
            "of those aliases in the overlay."
        ),
        "tut_alias_step_5": (
            "**Fuzzy matching** tolerates typos: "
            "if you type `crhome` instead of `chrome`, it will still find it."
        ),
        "tut_alias_action": "Go to Commands",
        "tut_alias_tip": (
            "Aliases work in any language. "
            "You can mix Spanish and English aliases."
        ),
        "tut_scene_title": "Create a scene from template",
        "tut_scene_desc": (
            "Set up routines that open multiple apps"
            " in specific positions."
        ),
        "tut_scene_level": "Intermediate",
        "tut_scene_step_1": (
            "Go to the **Scenes** page from the sidebar."
        ),
        "tut_scene_step_2": (
            "Click **New scene** to create a routine."
        ),
        "tut_scene_step_3": (
            "Fill in the basic details:\n"
            "  • **ID**: unique identifier (e.g. `work_mode`)\n"
            "  • **Name**: descriptive name (e.g. Work Mode)\n"
            "  • **Aliases**: words to invoke it (e.g. work, trabajo)"
        ),
        "tut_scene_step_4": (
            "Add steps with **+ Add step**. Each step can be:\n"
            "  • **Program**: opens an application\n"
            "  • **URL**: opens a web page in the browser\n"
            "  • **Delay**: waits before the next step\n"
            "  • Enable **Position** to choose monitor and position"
        ),
        "tut_scene_step_5": (
            "Save the scene and test it from the overlay "
            "by typing one of its aliases."
        ),
        "tut_scene_action": "Go to Scenes",
        "tut_scene_tip": (
            "Use delays between steps to give apps time "
            "to open before positioning them."
        ),
        "tut_monitor_title": "Multi-monitor positioning",
        "tut_monitor_desc": (
            "Learn to assign windows to specific"
            " monitors and positions."
        ),
        "tut_monitor_level": "Intermediate",
        "tut_monitor_step_1": (
            "When creating or editing a command, enable the "
            "**Position window on open** option."
        ),
        "tut_monitor_step_2": (
            "Select the **monitor** where you want the "
            "window to appear (auto-detected)."
        ),
        "tut_monitor_step_3": (
            "Choose a predefined **position**:\n"
            "  • Maximized, left/right half\n"
            "  • Top/bottom half\n"
            "  • Corners (top-left, bottom-right, etc.)\n"
            "  • Center"
        ),
        "tut_monitor_step_4": (
            "Save the command. Next time you run it, "
            "the window will open in the chosen position."
        ),
        "tut_monitor_action": "Go to Commands",
        "tut_monitor_tip": (
            "In scenes you can position each step on a different "
            "monitor and position to create full workspaces."
        ),
        "tut_lang_title": "Change interface language",
        "tut_lang_desc": (
            "Switch between Spanish and English"
            " without losing your settings."
        ),
        "tut_lang_level": "Basic",
        "tut_lang_step_1": (
            "Go to the **Languages** page from the sidebar."
        ),
        "tut_lang_step_2": (
            "You will see two cards: **Español** and **English**. "
            "The one with the 'Active' badge is the current language."
        ),
        "tut_lang_step_3": (
            "Click on the card of the language you want to use. "
            "The entire interface will change instantly."
        ),
        "tut_lang_step_4": (
            "The change is saved automatically. "
            "When you reopen the app, it will remember your choice."
        ),
        "tut_lang_action": "Go to Languages",
        "tut_lang_tip": (
            "Command aliases work in any language. "
            "You can type 'shutdown' or 'apagar' regardless "
            "of the interface language."
        ),
        "tut_diag_title": "Diagnostics & recovery",
        "tut_diag_desc": (
            "What to do if something fails: restore settings,"
            " check logs, and troubleshoot."
        ),
        "tut_diag_level": "Advanced",
        "tut_diag_step_1": (
            "Go to the **Diagnostics** page from the sidebar."
        ),
        "tut_diag_step_2": (
            "Check the **System information** section: "
            "verify the Python version, PySide6, and OS."
        ),
        "tut_diag_step_3": (
            "If something isn't working, try **Open data folder** "
            "to inspect the configuration files "
            "(config.json, commands.json, scenes.json)."
        ),
        "tut_diag_step_4": (
            "As a last resort, use **Factory reset** "
            "to return to default settings. "
            "⚠️ This will delete your custom commands and scenes."
        ),
        "tut_diag_action": "Go to Diagnostics",
        "tut_diag_tip": (
            "Before doing a factory reset, consider exporting "
            "your configuration as a backup."
        ),
        "tut_export_title": "Export & import settings",
        "tut_export_desc": (
            "Back up your entire configuration"
            " and restore it on another computer."
        ),
        "tut_export_level": "Advanced",
        "tut_export_step_1": (
            "Go to **Diagnostics** and click "
            "**Open data folder**."
        ),
        "tut_export_step_2": (
            "Copy the files `config.json`, `commands.json` "
            "and `scenes.json` to a safe location (USB, cloud, etc.)."
        ),
        "tut_export_step_3": (
            "To restore on another computer, copy those files "
            "to RunDesk's data folder "
            "(`%LOCALAPPDATA%\\RunDesk`)."
        ),
        "tut_export_step_4": (
            "Restart the application. Your commands, scenes "
            "and settings will be available."
        ),
        "tut_export_action": "Go to Diagnostics",
        "tut_export_tip": (
            "This feature will be automatic in future versions "
            "with export and import buttons."
        ),
    },
    # === Diagnostics ===
    "diagnostics": {
        "title": "Diagnostics",
        "subtitle": "System information, health status, and support tools",
        "health_ok": "Operating system — Everything is working correctly",
        "system_info": "System information",
        "os": "Operating system",
        "architecture": "Architecture",
        "config_path": "Data directory",
        "schema_version": "Schema version",
        "commands_loaded": "Commands loaded",
        "scenes_loaded": "Scenes loaded",
        "open_data_folder": "Open data folder",
        "open_data_folder_tip": "Open the configuration directory in Explorer",
        "export_logs": "Export logs",
        "export_logs_tip": "Generate a file with recent logs",
        "factory_reset": "Factory reset",
        "factory_reset_tip": "Restore all settings to default values",
        # Health checks
        "health_warning": "Warning — Minor issues detected",
        "health_error": "Error — Corrupt or missing files detected",
        "file_ok": "OK",
        "file_missing": "Missing",
        "file_corrupt": "Corrupt",
        "file_check": "Data files",
        # Log viewer
        "log_viewer": "Activity log",
        "log_empty": "No log entries available",
        # Export
        "logs_saved": "Logs exported to: {path}",
        "logs_save_title": "Save logs",
        # Factory reset dialog
        "reset_title": "Factory reset",
        "reset_warning": (
            "This action will delete all your custom commands, "
            "scenes, and settings.\n\n"
            "Would you like to create a backup before proceeding?"
        ),
        "reset_backup_yes": "Backup and reset",
        "reset_backup_no": "Reset without backup",
        "reset_cancel": "Cancel",
        "reset_success": "Settings restored to factory defaults.",
        "reset_backup_saved": "Backup saved to: {path}",
        # Export/Import config
        "export_config": "Export config",
        "export_config_tip": "Export commands, scenes and settings to a ZIP file",
        "import_config": "Import config",
        "import_config_tip": "Import commands, scenes and settings from a ZIP file",
        "export_config_title": "Export configuration",
        "export_config_success": "Configuration exported to: {path}",
        "import_config_title": "Import configuration",
        "import_config_warning": (
            "This will replace your current commands, scenes and settings "
            "with the imported data.\n\nDo you want to continue?"
        ),
        "import_config_success": "Configuration imported successfully. Restart recommended.",
        "import_config_error": "Error importing configuration: {error}",
    },
    # === Default command names ===
    "default_cmd": {
        "cmd_shutdown": "Shut down computer",
        "cmd_restart": "Restart computer",
        "cmd_sleep": "Sleep computer",
        "cmd_lock": "Lock computer",
        "cmd_open_settings": "Open Windows settings",
        "cmd_open_explorer": "Open file explorer",
        "cmd_open_taskmgr": "Open task manager",
        "cmd_open_browser": "Open browser",
        "cmd_open_calc": "Open calculator",
        "cmd_vol_up": "Volume up",
        "cmd_vol_down": "Volume down",
        "cmd_mute": "Mute",
        "cmd_bright_up": "Brightness up",
        "cmd_bright_down": "Brightness down",
        "cmd_open_panel": "Open launcher panel",
        "cmd_pause_launcher": "Pause launcher",
        "cmd_resume_launcher": "Resume launcher",
        "cmd_lang_es": "Switch to Spanish",
        "cmd_lang_en": "Switch to English",
    },
    # === Overlay ===
    "overlay": {
        "placeholder": "Type a command...",
        "no_match": "Command not found",
        "exact": "exact",
    },
    # === General ===
    "general": {
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "error": "Error",
        "confirm": "Confirm",
        "confirm_action": "Confirm action",
        "confirm_critical": (
            "Are you sure you want to run '{name}'?"
            "\n\nThis action may be irreversible."
        ),
        "yes": "Yes",
        "no": "No",
    },
    # === Accent color names ===
    "accent": {
        "light_blue": "Light blue",
        "intense_blue": "Intense blue",
        "green": "Green",
        "purple": "Purple",
        "pink": "Pink",
        "orange": "Orange",
        "cyan": "Cyan",
        "red": "Red",
        "white": "White",
    },
    # === About ===
    "about": {
        "title": "About RunDesk",
        "subtitle": "Open source command launcher for Windows",
        "version": "Version",
        "description": (
            "RunDesk is a keyboard-driven command launcher for Windows "
            "that lets you open applications, execute system actions, and "
            "automate workflows using customizable text commands and scenes."
        ),
        "features_title": "Key Features",
        "feat_1": "Instant command execution via configurable hotkey (Ctrl+Space)",
        "feat_2": "Fuzzy matching — tolerates typos when typing commands",
        "feat_3": "Scenes — chain multiple actions in sequence with delays",
        "feat_4": "Multi-monitor support with window positioning",
        "feat_5": "Fully offline — no internet connection required",
        "feat_6": "Spanish and English interface",
        "open_source_title": "Open Source",
        "open_source_text": (
            "RunDesk is open source software. You may view, study, and "
            "fork the source code under the following conditions:"
        ),
        "license_title": "License & Usage Terms",
        "license_text": (
            "This software is provided under a source-available license. "
            "You are free to use, modify, and distribute this software for "
            "personal and non-commercial purposes, provided that:\n\n"
            "1. Any redistribution or derivative work MUST include clear "
            "and visible attribution to the original project and its author.\n\n"
            "2. You may NOT use this software, or any derivative of it, for "
            "commercial purposes without explicit written permission from the author.\n\n"
            "3. You may NOT publish a fork or copy that removes or obscures "
            "the original attribution, nor present it as your own original work.\n\n"
            "4. Contributions to the original repository are welcome and will "
            "be credited accordingly."
        ),
        "github": "GitHub Repository",
        "github_url": "https://github.com/MikeDevQH/RunDesk",
        "author": "Author",
        "author_name": "RunDesk Team",
        "tech_title": "Technology",
        "tech_text": "Built with Python and PySide6 (Qt for Python)",
        "copyright": "© 2025 RunDesk. All rights reserved.",
    },
    # === System tray ===
    "tray": {
        "open": "Open RunDesk",
        "quit": "Quit",
    },
}
