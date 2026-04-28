"""Catálogo de traducciones — Español."""

CATALOG_ES = {
    # === Sidebar ===
    "sidebar": {
        "dashboard": "Dashboard",
        "commands": "Comandos",
        "scenes": "Escenas",
        "launcher": "Launcher",
        "appearance": "Apariencia",
        "languages": "Idiomas",
        "tutorials": "Ayuda",
        "diagnostics": "Diagnóstico",
        "about": "Acerca de",
    },
    # === Dashboard ===
    "dashboard": {
        "title": "Dashboard",
        "subtitle": "Vista general del estado de RunDesk",
        "status": "Estado",
        "active": "Activo",
        "running": "Launcher en ejecución",
        "hotkey": "Atajo",
        "hotkey_sub": "Hotkey de activación",
        "commands": "Comandos",
        "commands_sub": "Comandos registrados",
        "scenes": "Escenas",
        "scenes_sub": "Escenas configuradas",
        "language": "Idioma",
        "language_sub": "Idioma activo de la UI",
        "monitors": "Monitores",
        "monitors_sub": "Detección automática",
        "monitors_fallback": "No se pudo detectar",
        "primary": "principal",
        "active_count": "{n} activos",
        "quick_actions": "Acciones rápidas",
        "quick_hint": "Las acciones rápidas estarán disponibles en fases posteriores.",
        "total_executions": "Ejecuciones totales",
        "top_commands": "Comandos más usados",
        "recent_activity": "Actividad reciente",
        "no_activity": "Sin actividad aún. ¡Usa Ctrl+Espacio para ejecutar tu primer comando!",
        "times": "{n} veces",
        "success": "Éxito",
        "failed": "Falló",
        "today": "Hoy",
        "yesterday": "Ayer",
        "days_ago": "Hace {n} días",
    },
    # === Commands ===
    "commands": {
        "title": "Comandos",
        "subtitle": "Gestiona los comandos disponibles del launcher",
        "search": "Buscar comandos...",
        "add": "Nuevo comando",
        "all": "Todos",
        "system": "Sistema",
        "custom": "Personalizados",
        "col_name": "Nombre",
        "col_type": "Tipo",
        "col_category": "Categoría",
        "col_aliases": "Aliases",
        "col_status": "Estado",
        "col_actions": "Acciones",
        "enabled": "Activo",
        "disabled": "Inactivo",
        "edit": "Editar",
        "duplicate": "Duplicar",
        "delete": "Eliminar",
        "enable": "Habilitar",
        "disable": "Deshabilitar",
        "locked": "Bloqueado",
        "locked_edit_msg": "Este comando está bloqueado y no se puede editar.",
        "toggle": "Activar/Desactivar",
        "test": "Probar",
        "edit_tip": "Editar comando seleccionado",
        "duplicate_tip": "Duplicar comando seleccionado",
        "toggle_tip": "Cambiar estado del comando",
        "delete_tip": "Eliminar comando custom",
        "test_tip": "Ejecutar comando para probar",
        "empty": "No se encontraron comandos con este filtro.",
        "confirm_delete": "¿Estás seguro de eliminar el comando '{name}'?",
        "confirm_title": "Confirmar eliminación",
    },
    # === Command Dialog ===
    "cmd_dialog": {
        "title_new": "Nuevo comando",
        "title_edit": "Editar comando",
        "id": "ID único",
        "id_hint": "Identificador sin espacios (ej: abrir_chrome)",
        "name": "Nombre",
        "name_hint": "Nombre descriptivo del comando",
        "aliases": "Aliases",
        "aliases_hint": "Separados por coma (ej: chrome, navegar)",
        "type": "Tipo",
        "category": "Categoría",
        "path": "Ruta del programa",
        "url": "URL",
        "shell": "Comando shell",
        "window_position": "Posicionar ventana al abrir",
        "monitor": "Monitor",
        "position": "Posición",
        "save": "Guardar",
        "cancel": "Cancelar",
        "error": "Error",
        "err_id_required": "El ID es obligatorio.",
        "err_id_spaces": "El ID no puede contener espacios.",
        "err_name_required": "El nombre es obligatorio.",
        "err_id_exists": "Ya existe un comando con este ID.",
    },
    # === Scenes ===
    "scenes": {
        "title": "Escenas",
        "subtitle": "Crea rutinas que ejecuten múltiples acciones en secuencia",
        "add": "Nueva escena",
        "edit": "Editar",
        "toggle_disable": "Deshabilitar",
        "toggle_enable": "Habilitar",
        "delete": "Eliminar",
        "steps_count": "{n} pasos",
        "aliases_label": "Aliases: {aliases}",
        "empty": "No hay escenas creadas. Crea una para automatizar tareas.",
        "confirm_delete": "¿Eliminar la escena '{name}'?",
        "confirm_title": "Confirmar eliminación",
    },
    # === Scene Dialog ===
    "scene_dialog": {
        "title_new": "Nueva escena",
        "title_edit": "Editar escena",
        "id": "ID único",
        "name": "Nombre",
        "aliases": "Aliases (separados por coma)",
        "steps": "Pasos de la escena",
        "add_step": "+ Agregar paso",
        "add_delay": "Delay",
        "step": "Paso {n}",
        "step_type": "Tipo",
        "step_target": "Destino/Valor",
        "step_delay": "Delay (ms)",
        "delete_step": "Eliminar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "error": "Error",
        "err_id_required": "El ID es obligatorio.",
        "err_id_spaces": "El ID no puede contener espacios.",
        "err_name_required": "El nombre es obligatorio.",
        "err_no_steps": "La escena necesita al menos un paso.",
    },
    # === Appearance ===
    "appearance": {
        "title": "Apariencia",
        "subtitle": "Personaliza colores, estilo del overlay y sonidos",
        "accent_color": "Color de acento",
        "overlay": "Overlay",
        "blur": "Efecto blur/acrylic",
        "glow": "Halo/glow alrededor del input",
        "glow_intensity": "Intensidad del glow",
        "opacity": "Opacidad del fondo",
        "animation": "Velocidad de animación",
        "sounds": "Sonidos",
        "sounds_enable": "Sonidos de feedback activados",
        "preview_hint": "Vista previa del overlay",
    },
    # === Launcher Settings ===
    "launcher": {
        "title": "Configuración del Launcher",
        "subtitle": "Ajustes del atajo de teclado, overlay, fuzzy matching y comportamiento",
        "section_activation": "Activación",
        "hotkey": "Atajo de teclado",
        "hotkey_desc": "Atajo fijo para mostrar el overlay",
        "overlay_monitor": "Monitor del overlay",
        "overlay_monitor_desc": "Dónde aparece el input flotante",
        "monitor_active": "Monitor activo",
        "section_fuzzy": "Fuzzy Matching",
        "fuzzy_enabled": "Activado",
        "fuzzy_enabled_desc": "Tolerar errores tipográficos al escribir comandos",
        "fuzzy_threshold": "Umbral",
        "fuzzy_threshold_desc": "Sensibilidad (0.0 = muy permisivo, 1.0 = exacto)",
        "section_behavior": "Comportamiento",
        "start_windows": "Iniciar con Windows",
        "start_windows_desc": "Arrancar automáticamente al encender",
        "start_minimized": "Iniciar minimizado",
        "start_minimized_desc": "Iniciar directamente en la bandeja",
        "timeout": "Timeout de ejecución",
        "timeout_desc": "Tiempo máximo de espera por acción",
        "history_max": "Historial máximo",
        "history_max_desc": "Comandos recientes a recordar",
        "history_max_value": "{n} comandos",
        "yes": "Sí",
        "no": "No",
        "saved": "Guardado",
        "restart_hint": "Algunos cambios pueden requerir reiniciar para aplicarse completamente.",
    },
    # === Languages ===
    "languages": {
        "title": "Idiomas",
        "subtitle": "Selecciona el idioma de la interfaz de RunDesk",
        "active_badge": "Activo",
        "es_name": "Español",
        "es_native": "Interfaz en español",
        "en_name": "English",
        "en_native": "Interface in English",
        "info_title": "Sobre el cambio de idioma",
        "info_1": "Cambia todos los textos de la interfaz al idioma seleccionado.",
        "info_2": "Los aliases de comandos funcionan en cualquier idioma independientemente.",
        "info_3": "Los comandos personalizados mantienen el idioma en que fueron creados.",
        "info_4": "El cambio es instantáneo, no requiere reiniciar la aplicación.",
    },
    # === Tutorials ===
    "tutorials": {
        "title": "Ayuda y tutoriales",
        "subtitle": "Aprende a usar RunDesk paso a paso",
        "getting_started": "Primeros pasos",
        "advanced": "Uso avanzado",
        "maintenance": "Mantenimiento",
        "back": "← Volver a tutoriales",
        "tut_first_title": "Tu primer comando personalizado",
        "tut_first_desc": (
            "Aprende a crear un comando que abra tu aplicación"
            " favorita con un alias simple."
        ),
        "tut_first_level": "Básico",
        "tut_first_step_1": (
            "Abre la página **Comandos** haciendo click en la barra lateral."
        ),
        "tut_first_step_2": (
            "Haz click en el botón **Nuevo comando** en la parte superior."
        ),
        "tut_first_step_3": (
            "Rellena el formulario:\n"
            "  • **ID**: un identificador único sin espacios (ej: `abrir_chrome`)\n"
            "  • **Nombre**: un nombre descriptivo (ej: Abrir Chrome)\n"
            "  • **Aliases**: palabras cortas para invocar el comando (ej: chrome, nav)\n"
            "  • **Tipo**: selecciona el tipo de acción (programa, URL, carpeta…)\n"
            "  • **Ruta/URL**: la ruta del programa o URL a abrir"
        ),
        "tut_first_step_4": (
            "Haz click en **Guardar** para crear el comando."
        ),
        "tut_first_step_5": (
            "¡Pruébalo! Presiona **Ctrl+Space** para abrir el overlay "
            "y escribe uno de los aliases que configuraste."
        ),
        "tut_first_action": "Ir a Comandos",
        "tut_first_tip": (
            "Los comandos del sistema (apagar, reiniciar, etc.) ya vienen "
            "preconfigurados y no se pueden eliminar."
        ),
        "tut_alias_title": "Usar aliases y atajos",
        "tut_alias_desc": (
            "Configura múltiples aliases para acceder"
            " rápidamente a tus comandos."
        ),
        "tut_alias_level": "Básico",
        "tut_alias_step_1": (
            "Ve a la página **Comandos** y selecciona un comando existente."
        ),
        "tut_alias_step_2": (
            "Haz click en **Editar** para abrir el formulario de edición."
        ),
        "tut_alias_step_3": (
            "En el campo **Aliases**, escribe varias palabras "
            "separadas por comas.\n"
            "  • Ejemplo: `chrome, navegador, browser, nav`\n"
            "  • Cada alias es una forma distinta de invocar el mismo comando."
        ),
        "tut_alias_step_4": (
            "Guarda los cambios. Ahora puedes usar cualquiera "
            "de esos aliases en el overlay."
        ),
        "tut_alias_step_5": (
            "El **fuzzy matching** tolera errores tipográficos: "
            "si escribes `crhome` en vez de `chrome`, igual lo encontrará."
        ),
        "tut_alias_action": "Ir a Comandos",
        "tut_alias_tip": (
            "Los aliases funcionan en cualquier idioma. "
            "Puedes mezclar aliases en español e inglés."
        ),
        "tut_scene_title": "Crear una escena desde plantilla",
        "tut_scene_desc": (
            "Configura rutinas que abran múltiples apps"
            " en posiciones específicas."
        ),
        "tut_scene_level": "Intermedio",
        "tut_scene_step_1": (
            "Ve a la página **Escenas** desde la barra lateral."
        ),
        "tut_scene_step_2": (
            "Haz click en **Nueva escena** para crear una rutina."
        ),
        "tut_scene_step_3": (
            "Rellena los datos básicos:\n"
            "  • **ID**: identificador único (ej: `modo_trabajo`)\n"
            "  • **Nombre**: nombre descriptivo (ej: Modo Trabajo)\n"
            "  • **Aliases**: palabras para invocarla (ej: trabajo, work)"
        ),
        "tut_scene_step_4": (
            "Agrega pasos con **+ Añadir paso**. Cada paso puede ser:\n"
            "  • **Programa**: abre una aplicación\n"
            "  • **URL**: abre una web en el navegador\n"
            "  • **Delay**: espera antes del siguiente paso\n"
            "  • Activa **Posicionar** para elegir monitor y posición"
        ),
        "tut_scene_step_5": (
            "Guarda la escena y pruébala desde el overlay "
            "escribiendo uno de sus aliases."
        ),
        "tut_scene_action": "Ir a Escenas",
        "tut_scene_tip": (
            "Usa delays entre pasos para dar tiempo a que las "
            "aplicaciones se abran antes de posicionarlas."
        ),
        "tut_monitor_title": "Posicionamiento multi-monitor",
        "tut_monitor_desc": (
            "Aprende a asignar ventanas a monitores"
            " y posiciones predefinidas."
        ),
        "tut_monitor_level": "Intermedio",
        "tut_monitor_step_1": (
            "Al crear o editar un comando, activa la opción "
            "**Posicionar ventana al abrir**."
        ),
        "tut_monitor_step_2": (
            "Selecciona el **monitor** donde quieres que "
            "aparezca la ventana (se detectan automáticamente)."
        ),
        "tut_monitor_step_3": (
            "Elige una **posición** predefinida:\n"
            "  • Maximizada, mitad izquierda/derecha\n"
            "  • Mitad superior/inferior\n"
            "  • Esquinas (superior-izquierda, inferior-derecha, etc.)\n"
            "  • Centro"
        ),
        "tut_monitor_step_4": (
            "Guarda el comando. La próxima vez que lo ejecutes, "
            "la ventana se abrirá en la posición elegida."
        ),
        "tut_monitor_action": "Ir a Comandos",
        "tut_monitor_tip": (
            "En escenas puedes posicionar cada paso en un monitor "
            "y posición diferente para crear workspaces completos."
        ),
        "tut_lang_title": "Cambiar idioma de la interfaz",
        "tut_lang_desc": (
            "Alterna entre español e inglés"
            " sin perder tu configuración."
        ),
        "tut_lang_level": "Básico",
        "tut_lang_step_1": (
            "Ve a la página **Idiomas** desde la barra lateral."
        ),
        "tut_lang_step_2": (
            "Verás dos tarjetas: **Español** e **English**. "
            "La que tiene la etiqueta 'Activo' es el idioma actual."
        ),
        "tut_lang_step_3": (
            "Haz click en la tarjeta del idioma que quieras usar. "
            "Toda la interfaz cambiará al instante."
        ),
        "tut_lang_step_4": (
            "El cambio se guarda automáticamente. "
            "Al reabrir la app, recordará tu elección."
        ),
        "tut_lang_action": "Ir a Idiomas",
        "tut_lang_tip": (
            "Los aliases de comandos funcionan en cualquier idioma. "
            "Puedes escribir 'shutdown' o 'apagar' sin importar "
            "el idioma de la interfaz."
        ),
        "tut_diag_title": "Diagnóstico y recuperación",
        "tut_diag_desc": (
            "Qué hacer si algo falla: restaurar configuración,"
            " revisar logs y solucionar problemas."
        ),
        "tut_diag_level": "Avanzado",
        "tut_diag_step_1": (
            "Ve a la página **Diagnóstico** desde la barra lateral."
        ),
        "tut_diag_step_2": (
            "Revisa la sección **Información del sistema**: "
            "verifica la versión de Python, PySide6 y el SO."
        ),
        "tut_diag_step_3": (
            "Si algo no funciona, prueba **Abrir carpeta de datos** "
            "para inspeccionar los archivos de configuración "
            "(config.json, commands.json, scenes.json)."
        ),
        "tut_diag_step_4": (
            "Como último recurso, usa **Restaurar fábrica** "
            "para volver a la configuración por defecto. "
            "⚠️ Esto borrará tus comandos y escenas personalizadas."
        ),
        "tut_diag_action": "Ir a Diagnóstico",
        "tut_diag_tip": (
            "Antes de restaurar fábrica, considera exportar "
            "tu configuración como respaldo."
        ),
        "tut_export_title": "Export e import de configuración",
        "tut_export_desc": (
            "Respalda tu configuración completa"
            " y recupérala en otro equipo."
        ),
        "tut_export_level": "Avanzado",
        "tut_export_step_1": (
            "Ve a **Diagnóstico** y haz click en "
            "**Abrir carpeta de datos**."
        ),
        "tut_export_step_2": (
            "Copia los archivos `config.json`, `commands.json` "
            "y `scenes.json` a una ubicación segura (USB, nube, etc.)."
        ),
        "tut_export_step_3": (
            "Para restaurar en otro equipo, copia esos archivos "
            "a la carpeta de datos de RunDesk "
            "(`%LOCALAPPDATA%\\RunDesk`)."
        ),
        "tut_export_step_4": (
            "Reinicia la aplicación. Tus comandos, escenas "
            "y configuración estarán disponibles."
        ),
        "tut_export_action": "Ir a Diagnóstico",
        "tut_export_tip": (
            "Esta funcionalidad será automática en futuras versiones "
            "con botones de exportar e importar."
        ),
    },
    # === Diagnostics ===
    "diagnostics": {
        "title": "Diagnóstico",
        "subtitle": "Información del sistema, estado de salud y herramientas de soporte",
        "health_ok": "Sistema operativo — Todo funciona correctamente",
        "system_info": "Información del sistema",
        "os": "Sistema operativo",
        "architecture": "Arquitectura",
        "config_path": "Directorio de datos",
        "schema_version": "Schema version",
        "commands_loaded": "Comandos cargados",
        "scenes_loaded": "Escenas cargadas",
        "open_data_folder": "Abrir carpeta de datos",
        "open_data_folder_tip": "Abre el directorio de configuración en Explorer",
        "export_logs": "Exportar logs",
        "export_logs_tip": "Genera un archivo con los logs recientes",
        "factory_reset": "Restaurar fábrica",
        "factory_reset_tip": "Restaurar toda la configuración a valores por defecto",
        # Health checks
        "health_warning": "Advertencia — Se detectaron problemas menores",
        "health_error": "Error — Hay archivos corruptos o faltantes",
        "file_ok": "OK",
        "file_missing": "Faltante",
        "file_corrupt": "Corrupto",
        "file_check": "Archivos de datos",
        # Log viewer
        "log_viewer": "Registro de actividad",
        "log_empty": "No hay registros disponibles",
        # Export
        "logs_saved": "Logs exportados a: {path}",
        "logs_save_title": "Guardar logs",
        # Factory reset dialog
        "reset_title": "Restaurar fábrica",
        "reset_warning": (
            "Esta acción eliminará todos tus comandos personalizados, "
            "escenas y configuración.\n\n"
            "¿Deseas crear un respaldo antes de continuar?"
        ),
        "reset_backup_yes": "Respaldar y restaurar",
        "reset_backup_no": "Restaurar sin respaldo",
        "reset_cancel": "Cancelar",
        "reset_success": "Configuración restaurada a valores de fábrica.",
        "reset_backup_saved": "Respaldo guardado en: {path}",
        # Export/Import config
        "export_config": "Exportar config",
        "export_config_tip": "Exportar comandos, escenas y ajustes a un archivo ZIP",
        "import_config": "Importar config",
        "import_config_tip": "Importar comandos, escenas y ajustes desde un archivo ZIP",
        "export_config_title": "Exportar configuración",
        "export_config_success": "Configuración exportada a: {path}",
        "import_config_title": "Importar configuración",
        "import_config_warning": (
            "Esto reemplazará tus comandos, escenas y ajustes actuales "
            "con los datos importados.\n\n¿Deseas continuar?"
        ),
        "import_config_success": "Configuración importada correctamente. Se recomienda reiniciar.",
        "import_config_error": "Error al importar configuración: {error}",
    },
    # === Default command names ===
    "default_cmd": {
        "cmd_shutdown": "Apagar equipo",
        "cmd_restart": "Reiniciar equipo",
        "cmd_sleep": "Suspender equipo",
        "cmd_lock": "Bloquear equipo",
        "cmd_open_settings": "Abrir configuración Windows",
        "cmd_open_explorer": "Abrir explorador",
        "cmd_open_taskmgr": "Abrir administrador de tareas",
        "cmd_open_browser": "Abrir navegador",
        "cmd_open_calc": "Abrir calculadora",
        "cmd_vol_up": "Subir volumen",
        "cmd_vol_down": "Bajar volumen",
        "cmd_mute": "Silenciar",
        "cmd_bright_up": "Subir brillo",
        "cmd_bright_down": "Bajar brillo",
        "cmd_open_panel": "Abrir panel del launcher",
        "cmd_pause_launcher": "Pausar launcher",
        "cmd_resume_launcher": "Reanudar launcher",
        "cmd_lang_es": "Cambiar a español",
        "cmd_lang_en": "Cambiar a inglés",
    },
    # === Overlay ===
    "overlay": {
        "placeholder": "Escribe un comando...",
        "no_match": "No se encontró el comando",
        "exact": "exacto",
    },
    # === General ===
    "general": {
        "save": "Guardar",
        "cancel": "Cancelar",
        "delete": "Eliminar",
        "edit": "Editar",
        "error": "Error",
        "confirm": "Confirmar",
        "confirm_action": "Confirmar acción",
        "confirm_critical": (
            "¿Estás seguro de ejecutar '{name}'?"
            "\n\nEsta acción puede ser irreversible."
        ),
        "yes": "Sí",
        "no": "No",
    },
    # === Accent color names ===
    "accent": {
        "light_blue": "Azul claro",
        "intense_blue": "Azul intenso",
        "green": "Verde",
        "purple": "Morado",
        "pink": "Rosa",
        "orange": "Naranja",
        "cyan": "Cian",
        "red": "Rojo",
        "white": "Blanco",
    },
    # === About ===
    "about": {
        "title": "Acerca de RunDesk",
        "subtitle": "Launcher de comandos de código abierto para Windows",
        "version": "Versión",
        "description": (
            "RunDesk es un launcher de comandos por teclado para Windows "
            "que permite abrir aplicaciones, ejecutar acciones del sistema y "
            "automatizar flujos de trabajo usando comandos de texto y escenas personalizables."
        ),
        "features_title": "Características principales",
        "feat_1": "Ejecución instantánea de comandos mediante hotkey configurable (Ctrl+Espacio)",
        "feat_2": "Fuzzy matching — tolera errores tipográficos al escribir comandos",
        "feat_3": "Escenas — encadena múltiples acciones en secuencia con delays",
        "feat_4": "Soporte multi-monitor con posicionamiento de ventanas",
        "feat_5": "Completamente offline — no requiere conexión a internet",
        "feat_6": "Interfaz en español e inglés",
        "open_source_title": "Código Abierto",
        "open_source_text": (
            "RunDesk es software de código abierto. Puedes ver, estudiar y "
            "hacer fork del código fuente bajo las siguientes condiciones:"
        ),
        "license_title": "Licencia y Términos de Uso",
        "license_text": (
            "Este software se proporciona bajo una licencia source-available. "
            "Eres libre de usar, modificar y distribuir este software para "
            "fines personales y no comerciales, siempre que:\n\n"
            "1. Cualquier redistribución o trabajo derivado DEBE incluir una "
            "atribución clara y visible al proyecto original y su autor.\n\n"
            "2. NO puedes usar este software, ni ningún derivado, con "
            "fines comerciales sin permiso escrito explícito del autor.\n\n"
            "3. NO puedes publicar un fork o copia que elimine u oculte "
            "la atribución original, ni presentarlo como trabajo propio original.\n\n"
            "4. Las contribuciones al repositorio original son bienvenidas y "
            "serán acreditadas correspondientemente."
        ),
        "github": "Repositorio en GitHub",
        "github_url": "https://github.com/MikeDevQH/RunDesk",
        "author": "Autor",
        "author_name": "RunDesk Team",
        "tech_title": "Tecnología",
        "tech_text": "Desarrollado con Python y PySide6 (Qt para Python)",
        "copyright": "© 2025 RunDesk. Todos los derechos reservados.",
    },
    # === System tray ===
    "tray": {
        "open": "Abrir RunDesk",
        "quit": "Salir",
    },
}
