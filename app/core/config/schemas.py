"""
Schemas y defaults para config.json, commands.json y scenes.json.
Incluye validación básica y constantes de esquema.
"""

CURRENT_SCHEMA_VERSION = 1

# ============================================================
# CONFIG SCHEMA
# ============================================================

DEFAULT_CONFIG = {
    "schema_version": CURRENT_SCHEMA_VERSION,
    "app_name": "RunDesk",
    "hotkey": "ctrl+space",
    "ui_language": "es",
    "start_with_windows": True,
    "start_minimized": True,
    "overlay_monitor": "active",
    "execution_timeout_ms": 10000,
    "history_max_items": 50,
    "fuzzy_matching": {
        "enabled": True,
        "threshold": 0.65,
    },
    "monitors": {
        "default_monitor": 0,
        "remember_layout": True,
    },
    "sounds": {
        "enabled": True,
        "activation": "default_beep.wav",
        "error": "default_error.wav",
        "confirm": "default_confirm.wav",
    },
    "appearance": {
        "theme": "professional_dark",
        "accent": "#6EB6FF",
        "overlay_blur": True,
        "overlay_opacity": 0.85,
        "overlay_glow": True,
        "overlay_glow_intensity": 0.6,
        "overlay_animation_ms": 300,
    },
    "safety": {
        "factory_reset_requires_phrase": True,
        "critical_commands_require_confirmation": True,
    },
}

CONFIG_REQUIRED_KEYS = [
    "schema_version", "hotkey", "ui_language",
]

# ============================================================
# COMMAND SCHEMA
# ============================================================

COMMAND_CATEGORIES = [
    "system", "productivity", "audio", "screen", "launcher", "languages", "custom",
]

COMMAND_TYPES = [
    "program", "folder", "url", "system", "shortcut", "script", "scene",
]

WINDOW_POSITIONS = [
    "maximized", "left-half", "right-half", "top-half", "bottom-half",
    "top-left", "top-right", "bottom-left", "bottom-right",
    "center", "minimized", "custom",
]

COMMAND_TEMPLATE = {
    "id": "",
    "name": "",
    "aliases": [],
    "language": "es",
    "type": "program",
    "enabled": True,
    "default": False,
    "locked": False,
    "confirm_required": False,
    "category": "custom",
    "window": None,
    # Campos específicos por tipo (opcionales)
    "path": None,
    "args": None,
    "url": None,
    "command_id": None,
    "keys": None,
    "shell": None,
    "command": None,
    "scene_id": None,
}

DEFAULT_COMMANDS = [
    {
        "id": "cmd_shutdown",
        "name": "Apagar equipo",
        "aliases": ["apagar", "shutdown"],
        "language": "es",
        "type": "system",
        "command_id": "shutdown",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": True,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_restart",
        "name": "Reiniciar equipo",
        "aliases": ["reiniciar", "restart"],
        "language": "es",
        "type": "system",
        "command_id": "restart",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": True,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_sleep",
        "name": "Suspender equipo",
        "aliases": ["suspender", "sleep"],
        "language": "es",
        "type": "system",
        "command_id": "sleep",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": True,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_lock",
        "name": "Bloquear equipo",
        "aliases": ["bloquear", "lock"],
        "language": "es",
        "type": "system",
        "command_id": "lock",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_open_settings",
        "name": "Abrir configuración Windows",
        "aliases": ["config", "settings", "configuracion"],
        "language": "es",
        "type": "system",
        "command_id": "open_settings",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_open_explorer",
        "name": "Abrir explorador",
        "aliases": ["exp", "explorador", "explorer"],
        "language": "es",
        "type": "system",
        "command_id": "open_explorer",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_open_taskmgr",
        "name": "Abrir administrador de tareas",
        "aliases": ["tasks", "tareas", "taskmgr"],
        "language": "es",
        "type": "system",
        "command_id": "open_taskmgr",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "system",
        "window": None,
    },
    {
        "id": "cmd_open_browser",
        "name": "Abrir navegador",
        "aliases": ["chrome", "browser", "nav", "navegador"],
        "language": "es",
        "type": "system",
        "command_id": "open_browser",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "productivity",
        "window": None,
    },
    {
        "id": "cmd_open_calc",
        "name": "Abrir calculadora",
        "aliases": ["calc", "calculadora", "calculator"],
        "language": "es",
        "type": "system",
        "command_id": "open_calc",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "productivity",
        "window": None,
    },
    {
        "id": "cmd_vol_up",
        "name": "Subir volumen",
        "aliases": ["vol+", "volup", "subir volumen", "volume up"],
        "language": "es",
        "type": "system",
        "command_id": "vol_up",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "audio",
        "window": None,
    },
    {
        "id": "cmd_vol_down",
        "name": "Bajar volumen",
        "aliases": ["vol-", "voldown", "bajar volumen", "volume down"],
        "language": "es",
        "type": "system",
        "command_id": "vol_down",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "audio",
        "window": None,
    },
    {
        "id": "cmd_mute",
        "name": "Silenciar",
        "aliases": ["mute", "silencio", "silenciar"],
        "language": "es",
        "type": "system",
        "command_id": "mute",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "audio",
        "window": None,
    },
    {
        "id": "cmd_bright_up",
        "name": "Subir brillo",
        "aliases": ["brillo+", "brightup", "subir brillo", "brightness up"],
        "language": "es",
        "type": "system",
        "command_id": "bright_up",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "screen",
        "window": None,
    },
    {
        "id": "cmd_bright_down",
        "name": "Bajar brillo",
        "aliases": ["brillo-", "brightdown", "bajar brillo", "brightness down"],
        "language": "es",
        "type": "system",
        "command_id": "bright_down",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "screen",
        "window": None,
    },
    {
        "id": "cmd_open_panel",
        "name": "Abrir panel del launcher",
        "aliases": ["panel", "launcher", "abrir panel", "open panel"],
        "language": "es",
        "type": "system",
        "command_id": "open_panel",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "launcher",
        "window": None,
    },
    {
        "id": "cmd_pause_launcher",
        "name": "Pausar launcher",
        "aliases": ["pausar", "pause"],
        "language": "es",
        "type": "system",
        "command_id": "pause_launcher",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "launcher",
        "window": None,
    },
    {
        "id": "cmd_resume_launcher",
        "name": "Reanudar launcher",
        "aliases": ["reanudar", "resume"],
        "language": "es",
        "type": "system",
        "command_id": "resume_launcher",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": False,
        "category": "launcher",
        "window": None,
    },
    {
        "id": "cmd_lang_es",
        "name": "Cambiar a español",
        "aliases": ["español", "spanish"],
        "language": "es",
        "type": "system",
        "command_id": "lang_es",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": True,
        "category": "languages",
        "window": None,
    },
    {
        "id": "cmd_lang_en",
        "name": "Cambiar a inglés",
        "aliases": ["inglés", "english", "ingles"],
        "language": "es",
        "type": "system",
        "command_id": "lang_en",
        "enabled": True,
        "default": True,
        "locked": True,
        "confirm_required": True,
        "category": "languages",
        "window": None,
    },
]

# ============================================================
# SCENE SCHEMA
# ============================================================

SCENE_STEP_TYPES = [
    "program", "folder", "url", "system", "shortcut", "script", "delay",
]

SCENE_TEMPLATE = {
    "id": "",
    "name": "",
    "aliases": [],
    "language": "es",
    "enabled": True,
    "default": False,
    "locked": False,
    "steps": [],
}

SCENE_STEP_TEMPLATE = {
    "type": "program",
    "enabled": True,
    # Campos opcionales según tipo
    "path": None,
    "args": None,
    "url": None,
    "command_id": None,
    "keys": None,
    "shell": None,
    "command": None,
    "milliseconds": None,
    "window": None,
}

DEFAULT_SCENES = []  # Sin escenas por defecto en V1, solo plantillas

SCENE_TEMPLATES = [
    {
        "id": "tpl_programming",
        "name": "Modo Programación",
        "aliases": ["programar", "dev", "code"],
        "language": "es",
        "enabled": False,
        "default": False,
        "locked": False,
        "steps": [
            {
                "type": "program", "path": "", "args": None,
                "enabled": True, "window": {"monitor": 0, "position": "left-half"},
            },
            {"type": "delay", "milliseconds": 500, "enabled": True},
            {
                "type": "program", "path": "", "args": None,
                "enabled": True, "window": {"monitor": 0, "position": "right-half"},
            },
        ],
    },
    {
        "id": "tpl_study",
        "name": "Modo Estudio",
        "aliases": ["estudio", "study"],
        "language": "es",
        "enabled": False,
        "default": False,
        "locked": False,
        "steps": [
            {
                "type": "url", "url": "", "enabled": True,
                "window": {"monitor": 0, "position": "left-half"},
            },
            {"type": "delay", "milliseconds": 500, "enabled": True},
            {
                "type": "program", "path": "", "args": None,
                "enabled": True, "window": {"monitor": 0, "position": "right-half"},
            },
        ],
    },
]


# ============================================================
# VALIDACIÓN
# ============================================================

def validate_config(config: dict) -> list[str]:
    """Valida un config.json y retorna lista de errores (vacía si OK)."""
    errors = []
    for key in CONFIG_REQUIRED_KEYS:
        if key not in config:
            errors.append(f"Falta clave requerida: {key}")
    if "schema_version" in config and not isinstance(config["schema_version"], int):
        errors.append("schema_version debe ser un entero")
    if "hotkey" in config and (
        not isinstance(config["hotkey"], str) or not config["hotkey"].strip()
    ):
        errors.append("hotkey debe ser un string no vacío")
    if "ui_language" in config and config["ui_language"] not in ("es", "en"):
        errors.append("ui_language debe ser 'es' o 'en'")
    if "fuzzy_matching" in config:
        fm = config["fuzzy_matching"]
        if isinstance(fm, dict) and "threshold" in fm:
            t = fm["threshold"]
            if not isinstance(t, (int, float)) or not (0.0 <= t <= 1.0):
                errors.append("fuzzy_matching.threshold debe estar entre 0.0 y 1.0")
    return errors


def validate_command(cmd: dict) -> list[str]:
    """Valida un comando individual y retorna lista de errores."""
    errors = []
    if not cmd.get("id"):
        errors.append("Comando sin id")
    if not cmd.get("name"):
        errors.append(f"Comando {cmd.get('id', '?')} sin nombre")
    if not isinstance(cmd.get("aliases"), list):
        errors.append(f"Comando {cmd.get('id', '?')}: aliases debe ser una lista")
    if cmd.get("type") and cmd["type"] not in COMMAND_TYPES:
        errors.append(f"Comando {cmd.get('id', '?')}: tipo '{cmd['type']}' no válido")
    if cmd.get("category") and cmd["category"] not in COMMAND_CATEGORIES:
        errors.append(f"Comando {cmd.get('id', '?')}: categoría '{cmd['category']}' no válida")
    if cmd.get("window"):
        w = cmd["window"]
        if isinstance(w, dict) and "position" in w and w["position"] not in WINDOW_POSITIONS:
            errors.append(f"Comando {cmd.get('id', '?')}: posición '{w['position']}' no válida")
    return errors


def validate_scene(scene: dict) -> list[str]:
    """Valida una escena individual y retorna lista de errores."""
    errors = []
    if not scene.get("id"):
        errors.append("Escena sin id")
    if not scene.get("name"):
        errors.append(f"Escena {scene.get('id', '?')} sin nombre")
    if not isinstance(scene.get("steps"), list):
        errors.append(f"Escena {scene.get('id', '?')}: steps debe ser una lista")
    else:
        for i, step in enumerate(scene["steps"]):
            if step.get("type") and step["type"] not in SCENE_STEP_TYPES:
                errors.append(
                    f"Escena {scene.get('id', '?')}, paso {i}: "
                    f"tipo '{step['type']}' no válido"
                )
    return errors
