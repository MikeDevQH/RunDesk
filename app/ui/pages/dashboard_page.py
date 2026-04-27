"""
Página Dashboard principal.
Muestra estado del launcher, estadísticas, comandos más usados y actividad reciente.
Se refresca dinámicamente cada vez que se navega a esta página.
"""

import ctypes
import ctypes.wintypes
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import Colors, Fonts, Radius, Spacing, lbl_style


class StatusCard(QFrame):
    """Card individual para mostrar una métrica o estado."""

    def __init__(self, icon: str, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("statusCard")
        self.setStyleSheet(f"""
            QFrame#statusCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
            QFrame#statusCard:hover {{
                border-color: {Colors.BORDER_DEFAULT};
            }}
            #cardIcon, #cardTitle, #cardValue, #cardSub {{
                background: transparent;
                border: none;
            }}
            #cardTitle {{ color: {Colors.TEXT_SECONDARY}; }}
            #cardValue {{ color: {Colors.TEXT_PRIMARY}; }}
            #cardSub   {{ color: {Colors.TEXT_MUTED}; }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        layout.setSpacing(Spacing.SM)

        # Header con icono y título
        header = QHBoxLayout()
        header.setSpacing(Spacing.SM)

        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        icon_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL))
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM, Fonts.WEIGHT_MEDIUM)
        )
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        # Valor principal
        self._value_label = QLabel(value)
        self._value_label.setObjectName("cardValue")
        self._value_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XXL, Fonts.WEIGHT_BOLD)
        )
        layout.addWidget(self._value_label)

        # Subtítulo
        self._sub_label = QLabel(subtitle)
        self._sub_label.setObjectName("cardSub")
        self._sub_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS))
        layout.addWidget(self._sub_label)

    def set_value(self, value: str, subtitle: str | None = None):
        """Actualiza el valor y opcionalmente el subtítulo."""
        self._value_label.setText(value)
        if subtitle is not None:
            self._sub_label.setText(subtitle)


def _detect_monitors() -> list[dict]:
    """Detecta monitores conectados usando la API de Windows."""
    monitors = []
    try:
        user32 = ctypes.windll.user32
        CCHDEVICENAME = 32

        class MONITORINFOEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("rcMonitor", ctypes.wintypes.RECT),
                ("rcWork", ctypes.wintypes.RECT),
                ("dwFlags", ctypes.c_ulong),
                ("szDevice", ctypes.c_wchar * CCHDEVICENAME),
            ]

        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            info = MONITORINFOEX()
            info.cbSize = ctypes.sizeof(MONITORINFOEX)
            user32.GetMonitorInfoW(hMonitor, ctypes.byref(info))
            rc = info.rcMonitor
            monitors.append({
                "name": info.szDevice.strip("\x00"),
                "x": rc.left,
                "y": rc.top,
                "width": rc.right - rc.left,
                "height": rc.bottom - rc.top,
                "primary": bool(info.dwFlags & 1),
            })
            return True

        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.wintypes.RECT),
            ctypes.c_double,
        )
        user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
    except Exception:
        pass
    return monitors


class DashboardPage(QWidget):
    """Página principal del dashboard con datos dinámicos."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._cards: dict[str, StatusCard] = {}
        self._setup_ui()
        self._refresh()

    def on_page_shown(self):
        """Llamado al navegar a esta página — refresca datos."""
        self._refresh()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        outer.addWidget(scroll)

        self._container = QWidget()
        scroll.setWidget(self._container)

        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        self._title = QLabel(t("dashboard.title"))
        self._title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        self._title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(self._title)

        self._subtitle = QLabel(t("dashboard.subtitle"))
        self._subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        self._subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self._subtitle)

        layout.addSpacing(Spacing.MD)

        # --- Grid de cards ---
        grid = QGridLayout()
        grid.setSpacing(Spacing.LG)

        self._cards["status"] = StatusCard(
            "🟢", t("dashboard.status"), t("dashboard.active"),
            t("dashboard.running"),
        )
        self._cards["hotkey"] = StatusCard(
            "⌨️", t("dashboard.hotkey"), "—", t("dashboard.hotkey_sub"),
        )
        self._cards["commands"] = StatusCard(
            "📋", t("dashboard.commands"), "0", t("dashboard.commands_sub"),
        )
        self._cards["scenes"] = StatusCard(
            "🎬", t("dashboard.scenes"), "0", t("dashboard.scenes_sub"),
        )
        self._cards["language"] = StatusCard(
            "🌐", t("dashboard.language"), "—", t("dashboard.language_sub"),
        )
        self._cards["monitors"] = StatusCard(
            "🖥️", t("dashboard.monitors"), "—", t("dashboard.monitors_sub"),
        )

        grid.addWidget(self._cards["status"], 0, 0)
        grid.addWidget(self._cards["hotkey"], 0, 1)
        grid.addWidget(self._cards["commands"], 0, 2)
        grid.addWidget(self._cards["scenes"], 1, 0)
        grid.addWidget(self._cards["language"], 1, 1)
        grid.addWidget(self._cards["monitors"], 1, 2)

        layout.addLayout(grid)

        # --- Sección de uso ---
        layout.addSpacing(Spacing.LG)

        # Top commands + Recent activity side by side
        stats_row = QHBoxLayout()
        stats_row.setSpacing(Spacing.LG)

        # --- Top Commands panel ---
        self._top_frame = QFrame()
        self._top_frame.setObjectName("topFrame")
        self._top_frame.setStyleSheet(f"""
            QFrame#topFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
        """)
        self._top_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._top_layout = QVBoxLayout(self._top_frame)
        self._top_layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        self._top_layout.setSpacing(Spacing.SM)
        stats_row.addWidget(self._top_frame)

        # --- Recent Activity panel ---
        self._activity_frame = QFrame()
        self._activity_frame.setObjectName("activityFrame")
        self._activity_frame.setStyleSheet(f"""
            QFrame#activityFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
        """)
        self._activity_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._activity_layout = QVBoxLayout(self._activity_frame)
        self._activity_layout.setContentsMargins(
            Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG
        )
        self._activity_layout.setSpacing(Spacing.SM)
        stats_row.addWidget(self._activity_frame)

        layout.addLayout(stats_row)
        layout.addStretch()

    def _refresh(self):
        """Actualiza todos los valores de las cards con datos actuales."""
        hotkey = "Ctrl+Space"
        cmd_count = "0"
        cmd_enabled = 0
        scene_count = "0"
        language = "Español"

        if self._bootstrap:
            config = self._bootstrap.get_config()
            if config:
                hotkey = config.get("hotkey", "ctrl+space").replace("+", " + ").title()
                lang = config.get("ui_language", "es")
                language = "Español" if lang == "es" else "English"
            commands = self._bootstrap.get_commands()
            if commands:
                cmd_count = str(commands.count)
                cmd_enabled = commands.enabled_count
            scenes = self._bootstrap.get_scenes()
            if scenes:
                scene_count = str(scenes.count)

        self._title.setText(t("dashboard.title"))
        self._subtitle.setText(t("dashboard.subtitle"))

        self._cards["hotkey"].set_value(hotkey)
        active_sub = t("dashboard.active_count").replace("{n}", str(cmd_enabled))
        self._cards["commands"].set_value(cmd_count, active_sub)
        self._cards["scenes"].set_value(scene_count, t("dashboard.scenes_sub"))
        self._cards["language"].set_value(language)

        # Detectar monitores
        monitors = _detect_monitors()
        if monitors:
            count = len(monitors)
            resolutions = []
            for m in monitors:
                tag = f" ({t('dashboard.primary')})" if m["primary"] else ""
                resolutions.append(f"{m['width']}x{m['height']}{tag}")
            self._cards["monitors"].set_value(str(count), " | ".join(resolutions))
        else:
            self._cards["monitors"].set_value("1", t("dashboard.monitors_fallback"))

        # --- Actualizar paneles de uso ---
        self._refresh_top_commands()
        self._refresh_recent_activity()

    def _clear_layout(self, layout):
        """Elimina todos los widgets de un layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _refresh_top_commands(self):
        """Actualiza el panel de comandos más usados."""
        self._clear_layout(self._top_layout)

        header = QLabel(f"🏆  {t('dashboard.top_commands')}")
        header.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD)
        )
        header.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        self._top_layout.addWidget(header)

        app_state = self._bootstrap.get_app_state() if self._bootstrap else None
        top_commands = app_state.get_top_commands(5) if app_state else []
        stats = app_state.get_usage_stats() if app_state else {}
        total = stats.get("total_executions", 0)

        if not top_commands:
            hint = QLabel(t("dashboard.no_activity"))
            hint.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
            hint.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
            hint.setWordWrap(True)
            self._top_layout.addWidget(hint)
        else:
            # Total executions
            total_lbl = QLabel(
                f"{t('dashboard.total_executions')}: {total}"
            )
            total_lbl.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
            )
            total_lbl.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
            self._top_layout.addWidget(total_lbl)
            self._top_layout.addSpacing(Spacing.SM)

            # Bar chart rows
            max_count = top_commands[0][1] if top_commands else 1
            for cmd_id, count in top_commands:
                row = QHBoxLayout()
                row.setSpacing(Spacing.SM)

                name_lbl = QLabel(cmd_id)
                name_lbl.setFixedWidth(120)
                name_lbl.setFont(
                    QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
                )
                name_lbl.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
                row.addWidget(name_lbl)

                # Visual bar
                bar_container = QFrame()
                bar_container.setFixedHeight(16)
                bar_container.setStyleSheet(
                    f"background-color: {Colors.BG_DARKEST};"
                    f" border-radius: 4px;"
                )
                bar_container.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                bar_inner = QFrame(bar_container)
                pct = int((count / max_count) * 100) if max_count else 0
                bar_inner.setFixedHeight(16)
                bar_inner.setStyleSheet(
                    f"background-color: {Colors.ACCENT_PRIMARY};"
                    f" border-radius: 4px;"
                )
                bar_inner.setFixedWidth(max(4, int(pct * 1.5)))
                row.addWidget(bar_container)

                count_lbl = QLabel(t("dashboard.times").replace("{n}", str(count)))
                count_lbl.setFont(
                    QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS)
                )
                count_lbl.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
                row.addWidget(count_lbl)

                row_widget = QWidget()
                row_widget.setLayout(row)
                self._top_layout.addWidget(row_widget)

        self._top_layout.addStretch()

    def _refresh_recent_activity(self):
        """Actualiza el panel de actividad reciente."""
        self._clear_layout(self._activity_layout)

        header = QLabel(f"📊  {t('dashboard.recent_activity')}")
        header.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD)
        )
        header.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        self._activity_layout.addWidget(header)

        app_state = self._bootstrap.get_app_state() if self._bootstrap else None
        activity = app_state.get_recent_activity(8) if app_state else []

        if not activity:
            hint = QLabel(t("dashboard.no_activity"))
            hint.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
            hint.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
            hint.setWordWrap(True)
            self._activity_layout.addWidget(hint)
        else:
            for entry in activity:
                row = QHBoxLayout()
                row.setSpacing(Spacing.SM)

                # Status icon
                icon = "✓" if entry.get("success") else "✗"
                icon_color = Colors.SUCCESS if entry.get("success") else Colors.ERROR
                icon_lbl = QLabel(icon)
                icon_lbl.setFont(
                    QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_BOLD)
                )
                icon_lbl.setStyleSheet(lbl_style(icon_color))
                icon_lbl.setFixedWidth(20)
                row.addWidget(icon_lbl)

                # Command name
                name_lbl = QLabel(entry.get("name", entry.get("id", "?")))
                name_lbl.setFont(
                    QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
                )
                name_lbl.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
                row.addWidget(name_lbl)

                row.addStretch()

                # Timestamp
                time_str = self._format_time(entry.get("timestamp", ""))
                time_lbl = QLabel(time_str)
                time_lbl.setFont(
                    QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS)
                )
                time_lbl.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
                row.addWidget(time_lbl)

                row_widget = QWidget()
                row_widget.setLayout(row)
                self._activity_layout.addWidget(row_widget)

        self._activity_layout.addStretch()

    @staticmethod
    def _format_time(iso_str: str) -> str:
        """Formatea un timestamp ISO a texto relativo."""
        if not iso_str:
            return ""
        try:
            ts = datetime.fromisoformat(iso_str)
            now = datetime.now()
            diff = now - ts
            if diff.days == 0:
                return f"{ts.strftime('%H:%M')} — {t('dashboard.today')}"
            elif diff.days == 1:
                return f"{ts.strftime('%H:%M')} — {t('dashboard.yesterday')}"
            else:
                return t("dashboard.days_ago").replace("{n}", str(diff.days))
        except (ValueError, TypeError):
            return ""
