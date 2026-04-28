<p align="center">
  <img src="assets/icon.png" alt="RunDesk Logo" width="120" />
</p>

<h1 align="center">RunDesk</h1>

<p align="center">
  <strong>A fast, offline text-based command launcher for Windows 10/11</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue?style=flat-square" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.13%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/license-Source--Available-green?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/tests-152%20passing-brightgreen?style=flat-square" alt="Tests" />
</p>

---

## Overview

**RunDesk** is a keyboard-driven command launcher that lives in your system tray. Press `Ctrl+Space` anywhere to summon a sleek floating input overlay, type a command or alias, and RunDesk takes care of the rest — opening apps, running system actions, executing scenes (multi-step routines), and more.

Built with **PySide6**, fully **offline**, and designed for power users who want speed without the bloat.

---

## Features

| Category | Details |
|---|---|
| **Global Hotkey** | Fixed `Ctrl+Space` shortcut to summon the overlay instantly |
| **Floating Overlay** | Translucent input with blur, glow effects, and smooth animations |
| **Smart Matching** | Alias-based lookup with fuzzy matching — tolerates typos |
| **Scenes & Routines** | Chain multiple commands into sequential workflows with optional delays |
| **Multi-Monitor** | Detects all connected monitors; position windows on any screen |
| **Configuration UI** | Full settings panel: appearance, hotkey, commands, scenes, diagnostics |
| **Dashboard** | Usage statistics, most-used commands chart, and recent activity feed |
| **Export / Import** | Backup and restore your entire configuration as a ZIP file |
| **Bilingual** | English and Spanish — switch languages on the fly, UI rebuilds instantly |
| **System Tray** | Runs quietly in the background; right-click tray icon for quick actions |
| **100% Offline** | No internet required, no telemetry, no cloud dependencies |

---

## Download

Pre-built `.exe` installers are available on the [**Releases**](https://github.com/MikeDevQH/RunDesk/releases) page. Each release includes:

- **`RunDeskSetup_x.x.x.exe`** — Windows installer (recommended)
- **`RunDesk.exe`** — Standalone portable executable
- **Changelog** with a summary of new features, fixes, and improvements

> No Python installation required — just download, install, and run.

---

## Quick Start

### Prerequisites

- **Windows 10 or 11**
- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/MikeDevQH/RunDesk.git
cd RunDesk
uv sync
```

### Running

```bash
uv run python -m app
```

RunDesk will start minimized in the system tray. Press **Ctrl+Space** to open the overlay.

---

## Usage

### Basic Commands

| Action | Type in overlay |
|---|---|
| Open browser | `chrome`, `browser`, `nav` |
| Open file explorer | `explorer`, `files` |
| Open calculator | `calc`, `calculadora` |
| Lock computer | `lock`, `bloquear` |
| Shutdown | `shutdown`, `apagar` |
| Open Windows settings | `settings`, `config` |

### Custom Commands

1. Open the **Commands** page in the settings panel
2. Click **New command**
3. Fill in the ID, name, aliases, type, and path/URL
4. Save — your command is immediately available in the overlay

### Scenes (Routines)

Scenes let you chain multiple actions in sequence. For example, a "Work Setup" scene could:
1. Open VS Code
2. Open Chrome to your project management tool
3. Open Spotify

Configure scenes from the **Scenes** page in settings.

---

## Project Structure

```
rundesk/
├── app/
│   ├── core/               # Business logic
│   │   ├── actions/         # Command execution & routing
│   │   ├── config/          # Configuration store & schemas
│   │   ├── hotkey/          # Global hotkey management
│   │   ├── input/           # Command parsing & fuzzy matching
│   │   ├── scenes/          # Scene/routine management
│   │   └── sounds/          # Audio feedback
│   ├── i18n/                # Internationalization (EN/ES catalogs)
│   ├── ui/
│   │   ├── components/      # Reusable UI components (sidebar, dialogs)
│   │   ├── overlay/         # Floating input overlay
│   │   └── pages/           # Settings pages (dashboard, commands, etc.)
│   ├── bootstrap.py         # Application initialization
│   └── main.py              # Entry point
├── assets/                  # Icons and resources
├── tests/                   # Test suite (152 tests)
├── installer.iss            # Inno Setup installer script
├── rundesk.spec             # PyInstaller build spec
├── build.bat                # One-click build script
├── LICENSE.txt              # Source-Available License
└── pyproject.toml           # Project metadata & dependencies
```

---

## Building

### Executable (PyInstaller)

```bash
# Build standalone .exe
pyinstaller rundesk.spec
```

Output: `dist/RunDesk.exe`

### Installer (Inno Setup)

1. Build the `.exe` first (see above)
2. Open `installer.iss` in [Inno Setup Compiler](https://jrsoftware.org/isinfo.php)
3. Compile to generate `installer_output/RunDeskSetup_0.1.0.exe`

Or use the all-in-one build script:

```bash
build.bat
```

---

## Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_app_state.py
```

**152 tests** covering: config store, command store, scene store, command parser, action executor, i18n, sound player, window manager, app state & usage tracking, export/import.

---

## Configuration

All data is stored in `%LOCALAPPDATA%\RunDesk\`:

| File | Purpose |
|---|---|
| `config.json` | App settings (hotkey, language, appearance, fuzzy matching) |
| `commands.json` | Registered commands (default + custom) |
| `scenes.json` | Configured scenes/routines |
| `app_state.json` | Window geometry, usage statistics, recent activity |

### Export & Import

From the **Diagnostics** page you can:
- **Export** your entire configuration to a `.zip` file
- **Import** a previously exported `.zip` to restore settings
- **Factory reset** with optional backup

---

## Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.13 |
| **UI Framework** | PySide6 (Qt 6) |
| **Fuzzy Matching** | RapidFuzz |
| **Global Hotkey** | keyboard |
| **Window Management** | pywin32 |
| **Monitor Detection** | Win32 API (ctypes) |
| **Build** | PyInstaller + Inno Setup |
| **Package Manager** | uv + hatchling |
| **Testing** | pytest |
| **Linting** | Ruff |

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

Please ensure all tests pass before submitting.

---

## Roadmap

- [ ] Visual drag-and-drop editor for window positioning
- [ ] Plugin system for third-party command packs
- [ ] Command history with search
- [ ] Auto-updater
- [ ] Theming support (custom color palettes)

---

## License

This project is released under a **Source-Available License**. See [`LICENSE.txt`](LICENSE.txt) for full terms.

**TL;DR:** Free for personal use. Attribution required for forks. No commercial use without permission.

---

## Acknowledgements

- [PySide6](https://doc.qt.io/qtforpython/) — Qt for Python
- [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) — Fast fuzzy string matching
- [keyboard](https://github.com/boppreh/keyboard) — Global hotkey hooks
- [Inno Setup](https://jrsoftware.org/isinfo.php) — Windows installer framework

---

<p align="center">
  <sub>Made with focus and precision. Built for speed.</sub>
</p>
