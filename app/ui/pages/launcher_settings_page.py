"""
Página de configuración del Launcher.
Hotkey, overlay, fuzzy matching, comportamiento general.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import Colors, Fonts, Radius, Spacing, lbl_style


class SettingRow(QWidget):
    """Fila de configuración con label, valor actual y descripción."""

    def __init__(self, label: str, value: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(56)

        row = QHBoxLayout(self)
        row.setContentsMargins(Spacing.XL, Spacing.SM, Spacing.XL, Spacing.SM)

        col = QVBoxLayout()
        col.setSpacing(2)

        lbl = QLabel(label)
        lbl.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_SEMIBOLD)
        )
        lbl.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        col.addWidget(lbl)

        if description:
            desc = QLabel(description)
            desc.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS))
            desc.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
            col.addWidget(desc)

        row.addLayout(col, 1)

        val = QLabel(value)
        val.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_MEDIUM)
        )
        val.setStyleSheet(lbl_style(Colors.ACCENT_PRIMARY))
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(val)


class SettingSection(QFrame):
    """Sección agrupada de settings con título y filas."""

    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("settingSection")
        self.setStyleSheet(f"""
            QFrame#settingSection {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
            QFrame#settingSection QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, Spacing.MD, 0, Spacing.SM)
        self._layout.setSpacing(0)

        # Header de sección
        header_text = QLabel(f"{icon}  {title}" if icon else title)
        header_text.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD)
        )
        header_text.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        header_text.setContentsMargins(Spacing.XL, 0, Spacing.XL, Spacing.SM)
        self._layout.addWidget(header_text)

    def add_row(self, label: str, value: str, description: str = ""):
        """Agrega una fila de configuración a esta sección."""
        self._layout.addWidget(SettingRow(label, value, description))


class LauncherSettingsPage(QWidget):
    """Página de ajustes del launcher."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        title = QLabel(t("launcher.title"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel(t("launcher.subtitle"))
        subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(Spacing.MD)

        # Cargar datos
        hotkey = "Ctrl+Space"
        overlay_monitor = t("launcher.monitor_active")
        timeout = "10000 ms"
        history_max = "50"
        fuzzy_enabled = t("launcher.yes")
        fuzzy_threshold = "0.65"
        start_windows = t("launcher.yes")
        start_minimized = t("launcher.yes")

        if self._bootstrap:
            config = self._bootstrap.get_config()
            if config:
                hotkey = config.get("hotkey", "ctrl+space").replace("+", " + ").title()
                om = config.get("overlay_monitor", "active")
                overlay_monitor = (
                    t("launcher.monitor_active") if om == "active"
                    else f"Monitor {om}"
                )
                timeout = f"{config.get('execution_timeout_ms', 10000)} ms"
                history_max = str(config.get("history_max_items", 50))
                fm = config.get("fuzzy_matching", {})
                fuzzy_enabled = (
                    t("launcher.yes") if fm.get("enabled", True)
                    else t("launcher.no")
                )
                fuzzy_threshold = str(fm.get("threshold", 0.65))
                start_windows = (
                    t("launcher.yes") if config.get("start_with_windows", True)
                    else t("launcher.no")
                )
                start_minimized = (
                    t("launcher.yes") if config.get("start_minimized", True)
                    else t("launcher.no")
                )

        # --- Sección: Activación ---
        s1 = SettingSection(t("launcher.section_activation"), "⌨️")
        s1.add_row(t("launcher.hotkey"), hotkey, t("launcher.hotkey_desc"))
        s1.add_row(
            t("launcher.overlay_monitor"), overlay_monitor,
            t("launcher.overlay_monitor_desc"),
        )
        layout.addWidget(s1)

        # --- Sección: Fuzzy Matching ---
        s2 = SettingSection(t("launcher.section_fuzzy"), "🔍")
        s2.add_row(
            t("launcher.fuzzy_enabled"), fuzzy_enabled,
            t("launcher.fuzzy_enabled_desc"),
        )
        s2.add_row(
            t("launcher.fuzzy_threshold"), fuzzy_threshold,
            t("launcher.fuzzy_threshold_desc"),
        )
        layout.addWidget(s2)

        # --- Sección: Comportamiento ---
        s3 = SettingSection(t("launcher.section_behavior"), "⚙️")
        s3.add_row(
            t("launcher.start_windows"), start_windows,
            t("launcher.start_windows_desc"),
        )
        s3.add_row(
            t("launcher.start_minimized"), start_minimized,
            t("launcher.start_minimized_desc"),
        )
        s3.add_row(t("launcher.timeout"), timeout, t("launcher.timeout_desc"))
        history_val = t("launcher.history_max_value").replace("{n}", history_max)
        s3.add_row(
            t("launcher.history_max"), history_val,
            t("launcher.history_max_desc"),
        )
        layout.addWidget(s3)

        # --- Nota ---
        note = QLabel(t("launcher.note"))
        note.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        note.setStyleSheet(f"color: {Colors.TEXT_MUTED};")
        layout.addWidget(note)

        layout.addStretch()
