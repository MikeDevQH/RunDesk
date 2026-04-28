"""
Página de configuración del Launcher.
Hotkey (fijo), overlay, fuzzy matching, comportamiento general.
Los ajustes editables se guardan en tiempo real.
"""

import logging

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import Colors, Fonts, Radius, Spacing, lbl_style

logger = logging.getLogger(__name__)

_FF = Fonts.FAMILY.split(",")[0].strip()

# ─── Styles ───────────────────────────────────────────────────────

_SECTION_STYLE = f"""
    QFrame#section {{
        background-color: {Colors.BG_SURFACE};
        border: 1px solid {Colors.BORDER_SUBTLE};
        border-radius: {Radius.LG}px;
    }}
    QFrame#section:hover {{
        border-color: {Colors.BORDER_DEFAULT};
    }}
"""

_ROW_STYLE = f"""
    QWidget#settingRow {{
        background: transparent;
        border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    }}
    QWidget#settingRow:hover {{
        background-color: rgba(110, 182, 255, 0.03);
    }}
"""

_ROW_LAST_STYLE = f"""
    QWidget#settingRow {{
        background: transparent;
    }}
    QWidget#settingRow:hover {{
        background-color: rgba(110, 182, 255, 0.03);
    }}
"""

_HOTKEY_BADGE_STYLE = f"""
    QLabel#hotkeyBadge {{
        background-color: {Colors.BG_DEEP};
        color: {Colors.ACCENT_PRIMARY};
        border: 2px solid {Colors.BORDER_DEFAULT};
        border-radius: {Radius.MD}px;
        padding: 6px 18px;
        font-size: {Fonts.SIZE_MD}px;
        font-weight: {Fonts.WEIGHT_SEMIBOLD};
    }}
"""


# ─── Toggle Switch (painted) ─────────────────────────────────────

class ToggleSwitch(QWidget):
    """Toggle switch moderno renderizado con QPainter."""

    toggled = Signal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self._anim_pos = 1.0 if checked else 0.0
        self.setFixedSize(46, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, val: bool):
        self._checked = val
        self._anim_pos = 1.0 if val else 0.0
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._anim_pos = 1.0 if self._checked else 0.0
        self.update()
        self.toggled.emit(self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        r = h / 2

        # Track
        track_color = QColor(Colors.ACCENT_PRIMARY) if self._checked else QColor(Colors.BG_HOVER)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(track_color)
        p.drawRoundedRect(0, 0, w, h, r, r)

        # Thumb
        margin = 3
        thumb_r = h - margin * 2
        x = margin + self._anim_pos * (w - thumb_r - margin * 2)
        thumb_color = QColor("#FFFFFF") if self._checked else QColor(Colors.TEXT_MUTED)
        p.setBrush(thumb_color)
        p.drawEllipse(int(x), margin, int(thumb_r), int(thumb_r))

        p.end()


# ─── Setting Section ─────────────────────────────────────────────

class SettingSection(QFrame):
    """Sección agrupada con header y filas de configuración."""

    def __init__(self, title: str, icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("section")
        self.setStyleSheet(_SECTION_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._row_count = 0

        header = QWidget()
        header.setFixedHeight(48)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(Spacing.XL, Spacing.MD, Spacing.XL, Spacing.SM)

        lbl = QLabel(f"{icon}  {title}" if icon else title)
        lbl.setFont(QFont(_FF, Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD))
        lbl.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        hl.addWidget(lbl)
        self._layout.addWidget(header)

    def add_row(self, label: str, widget: QWidget, description: str = "",
                is_last: bool = False):
        """Agrega una fila con label + widget a la derecha."""
        row = QWidget()
        row.setObjectName("settingRow")
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        row.setFixedHeight(60)
        row.setStyleSheet(_ROW_LAST_STYLE if is_last else _ROW_STYLE)

        h = QHBoxLayout(row)
        h.setContentsMargins(Spacing.XL, Spacing.SM, Spacing.XL, Spacing.SM)

        col = QVBoxLayout()
        col.setSpacing(1)

        name = QLabel(label)
        name.setFont(QFont(_FF, Fonts.SIZE_MD, Fonts.WEIGHT_MEDIUM))
        name.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        col.addWidget(name)

        if description:
            desc = QLabel(description)
            desc.setFont(QFont(_FF, Fonts.SIZE_XS))
            desc.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
            col.addWidget(desc)

        h.addLayout(col, 1)
        h.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(row)
        self._row_count += 1


# ─── Saved Toast ──────────────────────────────────────────────────

class SavedToast(QLabel):
    """Notificación breve de guardado exitoso."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont(_FF, Fonts.SIZE_SM, Fonts.WEIGHT_SEMIBOLD))
        self.setStyleSheet(
            f"color: {Colors.SUCCESS}; background: transparent; border: none;"
            f" padding: 4px 12px; border-radius: {Radius.SM}px;"
        )
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.hide()

    def flash(self):
        self.setText(f"✓  {t('launcher.saved')}")
        self.show()
        QTimer.singleShot(2000, self.hide)


# ─── Main Page ────────────────────────────────────────────────────

class LauncherSettingsPage(QWidget):
    """Página de ajustes del launcher — totalmente editable."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._config = bootstrap.get_config() if bootstrap else None
        self._setup_ui()

    def _save(self, key, value):
        if self._config:
            self._config.set(key, value)
            logger.info("Config: %s = %s", key, value)
            self._toast.flash()

    def _save_nested(self, *kv):
        if self._config:
            self._config.set_nested(*kv)
            logger.info("Config: %s", kv)
            self._toast.flash()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        lay = QVBoxLayout(container)
        lay.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        lay.setSpacing(Spacing.XL)

        # Header
        title = QLabel(t("launcher.title"))
        title.setFont(QFont(_FF, Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD))
        title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        lay.addWidget(title)

        hdr = QHBoxLayout()
        sub = QLabel(t("launcher.subtitle"))
        sub.setFont(QFont(_FF, Fonts.SIZE_LG))
        sub.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        hdr.addWidget(sub, 1)
        self._toast = SavedToast()
        hdr.addWidget(self._toast)
        lay.addLayout(hdr)
        lay.addSpacing(Spacing.SM)

        # Valores actuales
        cfg = self._config
        om = cfg.get("overlay_monitor", "active") if cfg else "active"
        fm = cfg.get("fuzzy_matching", {}) if cfg else {}
        f_on = fm.get("enabled", True)
        f_thr = fm.get("threshold", 0.65)
        sw = cfg.get("start_with_windows", True) if cfg else True
        sm = cfg.get("start_minimized", True) if cfg else True
        to = cfg.get("execution_timeout_ms", 10000) if cfg else 10000
        hm = cfg.get("history_max_items", 50) if cfg else 50

        # ── Activación ──
        s1 = SettingSection(t("launcher.section_activation"), "⌨️")

        hotkey_badge = QLabel("Ctrl + Space")
        hotkey_badge.setObjectName("hotkeyBadge")
        hotkey_badge.setFixedHeight(34)
        hotkey_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hotkey_badge.setStyleSheet(_HOTKEY_BADGE_STYLE)
        s1.add_row(t("launcher.hotkey"), hotkey_badge, t("launcher.hotkey_desc"))

        self._monitor_combo = QComboBox()
        self._monitor_combo.setFixedWidth(200)
        self._monitor_combo.setFixedHeight(34)
        self._monitor_combo.addItem(t("launcher.monitor_active"), "active")
        try:
            from screeninfo import get_monitors
            for i, m in enumerate(get_monitors()):
                self._monitor_combo.addItem(
                    f"Monitor {i + 1}  ({m.width}×{m.height})", str(i)
                )
        except Exception:
            pass
        idx = self._monitor_combo.findData(str(om))
        if idx >= 0:
            self._monitor_combo.setCurrentIndex(idx)
        self._monitor_combo.currentIndexChanged.connect(self._on_monitor_changed)
        s1.add_row(
            t("launcher.overlay_monitor"), self._monitor_combo,
            t("launcher.overlay_monitor_desc"), is_last=True,
        )
        lay.addWidget(s1)

        # ── Fuzzy Matching ──
        s2 = SettingSection(t("launcher.section_fuzzy"), "🔍")

        self._fuzzy_toggle = ToggleSwitch(f_on)
        self._fuzzy_toggle.toggled.connect(self._on_fuzzy_toggled)
        s2.add_row(
            t("launcher.fuzzy_enabled"), self._fuzzy_toggle,
            t("launcher.fuzzy_enabled_desc"),
        )

        self._fuzzy_spin = QDoubleSpinBox()
        self._fuzzy_spin.setFixedWidth(110)
        self._fuzzy_spin.setFixedHeight(34)
        self._fuzzy_spin.setRange(0.0, 1.0)
        self._fuzzy_spin.setSingleStep(0.05)
        self._fuzzy_spin.setDecimals(2)
        self._fuzzy_spin.setValue(f_thr)
        self._fuzzy_spin.valueChanged.connect(self._on_fuzzy_threshold_changed)
        s2.add_row(
            t("launcher.fuzzy_threshold"), self._fuzzy_spin,
            t("launcher.fuzzy_threshold_desc"), is_last=True,
        )
        lay.addWidget(s2)

        # ── Comportamiento ──
        s3 = SettingSection(t("launcher.section_behavior"), "⚙️")

        self._sw_toggle = ToggleSwitch(sw)
        self._sw_toggle.toggled.connect(self._on_start_windows_toggled)
        s3.add_row(
            t("launcher.start_windows"), self._sw_toggle,
            t("launcher.start_windows_desc"),
        )

        self._sm_toggle = ToggleSwitch(sm)
        self._sm_toggle.toggled.connect(self._on_start_minimized_toggled)
        s3.add_row(
            t("launcher.start_minimized"), self._sm_toggle,
            t("launcher.start_minimized_desc"),
        )

        self._timeout_spin = QSpinBox()
        self._timeout_spin.setFixedWidth(130)
        self._timeout_spin.setFixedHeight(34)
        self._timeout_spin.setRange(1000, 60000)
        self._timeout_spin.setSingleStep(1000)
        self._timeout_spin.setSuffix(" ms")
        self._timeout_spin.setValue(to)
        self._timeout_spin.valueChanged.connect(self._on_timeout_changed)
        s3.add_row(t("launcher.timeout"), self._timeout_spin, t("launcher.timeout_desc"))

        self._history_spin = QSpinBox()
        self._history_spin.setFixedWidth(130)
        self._history_spin.setFixedHeight(34)
        self._history_spin.setRange(10, 500)
        self._history_spin.setSingleStep(10)
        self._history_spin.setValue(hm)
        self._history_spin.valueChanged.connect(self._on_history_changed)
        s3.add_row(
            t("launcher.history_max"), self._history_spin,
            t("launcher.history_max_desc"), is_last=True,
        )
        lay.addWidget(s3)

        # Hint
        hint = QLabel(t("launcher.restart_hint"))
        hint.setFont(QFont(_FF, Fonts.SIZE_XS))
        hint.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        lay.addWidget(hint)
        lay.addStretch()

    # ── Callbacks ──

    def _on_monitor_changed(self, index: int):
        val = self._monitor_combo.currentData()
        if val is not None:
            self._save("overlay_monitor", val)

    def _on_fuzzy_toggled(self, checked: bool):
        self._save_nested("fuzzy_matching", "enabled", checked)

    def _on_fuzzy_threshold_changed(self, value: float):
        self._save_nested("fuzzy_matching", "threshold", round(value, 2))

    def _on_start_windows_toggled(self, checked: bool):
        self._save("start_with_windows", checked)
        try:
            from app.core.startup_manager import sync_startup
            sync_startup(checked)
        except Exception as e:
            logger.warning("No se pudo sincronizar startup: %s", e)

    def _on_start_minimized_toggled(self, checked: bool):
        self._save("start_minimized", checked)

    def _on_timeout_changed(self, value: int):
        self._save("execution_timeout_ms", value)

    def _on_history_changed(self, value: int):
        self._save("history_max_items", value)
