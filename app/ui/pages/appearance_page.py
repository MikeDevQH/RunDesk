"""
Página de personalización de apariencia.
Color de acento, configuración del overlay y sonidos — con persistencia real.
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QRadialGradient
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import (
    Colors,
    Fonts,
    Radius,
    Spacing,
    lbl_style,
)

logger = logging.getLogger(__name__)

# Opciones de color de acento
ACCENT_OPTIONS = [
    ("#6EB6FF", "Azul claro"),
    ("#4B8DFF", "Azul intenso"),
    ("#4ADE80", "Verde"),
    ("#FBBF24", "Ámbar"),
    ("#F87171", "Rojo suave"),
    ("#A78BFA", "Violeta"),
    ("#FB923C", "Naranja"),
    ("#E879F9", "Rosa"),
    ("#22D3EE", "Cyan"),
]

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

_SLIDER_STYLE = f"""
    QSlider::groove:horizontal {{
        height: 6px;
        background: {Colors.BG_HOVER};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        width: 18px;
        height: 18px;
        margin: -6px 0;
        background: {Colors.ACCENT_PRIMARY};
        border-radius: 9px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {Colors.ACCENT_HOVER};
    }}
    QSlider::sub-page:horizontal {{
        background: {Colors.ACCENT_SECONDARY};
        border-radius: 3px;
    }}
"""


class ColorSwatch(QFrame):
    """Muestra un color clickeable con indicador de selección."""

    selected = Signal(str)

    def __init__(self, color: str, label: str, active: bool = False, parent=None):
        super().__init__(parent)
        self._color = color
        self._active = active
        self.setFixedSize(48, 48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{label}  ({color})")
        self.setObjectName("colorSwatch")
        self._apply_style()

    def _apply_style(self):
        border = (
            f"3px solid {Colors.TEXT_PRIMARY}"
            if self._active
            else f"1px solid {Colors.BORDER_DEFAULT}"
        )
        self.setStyleSheet(f"""
            QFrame#colorSwatch {{
                background-color: {self._color};
                border: {border};
                border-radius: {Radius.MD}px;
            }}
            QFrame#colorSwatch:hover {{
                border: 2px solid {Colors.TEXT_SECONDARY};
            }}
        """)

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()

    def mousePressEvent(self, event):
        self.selected.emit(self._color)


class OverlayPreview(QFrame):
    """Preview visual interactivo del overlay del launcher."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(160)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._accent = Colors.ACCENT_PRIMARY
        self._opacity = 0.85
        self._glow = True
        self._glow_intensity = 0.6

        self.setObjectName("overlayPreview")
        self.setStyleSheet(f"""
            QFrame#overlayPreview {{
                background-color: {Colors.BG_DARKEST};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radius.XL}px;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(Spacing.SM)

        self._input_frame = QFrame()
        self._input_frame.setObjectName("inputPreview")
        self._input_frame.setFixedSize(380, 42)
        input_layout = QHBoxLayout(self._input_frame)
        input_layout.setContentsMargins(Spacing.LG, 0, Spacing.LG, 0)
        input_layout.setSpacing(Spacing.SM)

        self._icon = QLabel("✦")
        self._icon.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        self._icon.setFixedWidth(24)
        input_layout.addWidget(self._icon)

        placeholder = QLabel(t("overlay.placeholder"))
        placeholder.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD))
        placeholder.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        input_layout.addWidget(placeholder)
        input_layout.addStretch()

        esc_hint = QLabel("ESC")
        esc_hint.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 8))
        esc_hint.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: rgba(255,255,255,0.06);"
            f" border: 1px solid rgba(255,255,255,0.10);"
            f" border-radius: 4px; padding: 2px 6px;"
        )
        esc_hint.setFixedWidth(32)
        input_layout.addWidget(esc_hint)

        main_layout.addWidget(self._input_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        hint = QLabel(t("appearance.preview_hint"))
        hint.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS))
        hint.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(hint)

        self._refresh_preview()

    def update_settings(self, accent: str, opacity: float, glow: bool, glow_intensity: float = 0.6):
        self._accent = accent
        self._opacity = opacity
        self._glow = glow
        self._glow_intensity = glow_intensity
        self._refresh_preview()

    def _refresh_preview(self):
        bg_alpha = int(self._opacity * 255)
        border_color = self._accent
        self._input_frame.setStyleSheet(f"""
            QFrame#inputPreview {{
                background-color: rgba(27, 42, 59, {bg_alpha});
                border: 2px solid {border_color};
                border-radius: {Radius.LG}px;
            }}
        """)
        self._icon.setStyleSheet(lbl_style(self._accent))
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._glow:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx = self.width() / 2
        cy = self.height() / 2 - 10
        color = QColor(self._accent)
        gradient = QRadialGradient(cx, cy, 200)
        gi = self._glow_intensity
        gradient.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), int(45 * gi)))
        gradient.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), int(12 * gi)))
        gradient.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        path = QPainterPath()
        path.addRoundedRect(self.rect().toRectF(), Radius.XL, Radius.XL)
        painter.fillPath(path, gradient)
        painter.end()


class AppearancePage(QWidget):
    """Página de personalización visual con persistencia real."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._swatches: list[ColorSwatch] = []
        self._setup_ui()

    def on_page_shown(self):
        """Refresca preview al navegar a esta página."""
        self._sync_preview()

    def _get_appearance(self) -> dict:
        if self._bootstrap:
            cfg = self._bootstrap.get_config()
            if cfg:
                return cfg.get("appearance", {})
        return {}

    def _save_appearance(self, key: str, value):
        if self._bootstrap:
            cfg = self._bootstrap.get_config()
            appearance = cfg.get("appearance", {})
            appearance[key] = value
            cfg.set("appearance", appearance)
            cfg.save()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        title = QLabel(t("appearance.title"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel(t("appearance.subtitle"))
        subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        # --- Scroll ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setContentsMargins(0, Spacing.MD, 0, 0)
        clayout.setSpacing(Spacing.LG)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        appearance = self._get_appearance()

        # --- Preview ---
        self._preview = OverlayPreview()
        clayout.addWidget(self._preview)

        # === Color de acento ===
        accent_section = self._make_section()
        al = QVBoxLayout(accent_section)
        al.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        al.setSpacing(Spacing.MD)

        al.addWidget(self._section_title(f"✦  {t('appearance.accent_color')}"))

        current_accent = appearance.get("accent", Colors.ACCENT_PRIMARY).lower()
        colors_row = QHBoxLayout()
        colors_row.setSpacing(Spacing.MD)

        for color, name in ACCENT_OPTIONS:
            swatch = ColorSwatch(color, name, active=(color.lower() == current_accent))
            swatch.selected.connect(self._on_accent_selected)
            self._swatches.append(swatch)
            colors_row.addWidget(swatch)

        colors_row.addStretch()
        al.addLayout(colors_row)
        clayout.addWidget(accent_section)

        # === Overlay settings ===
        overlay_section = self._make_section()
        ol = QVBoxLayout(overlay_section)
        ol.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        ol.setSpacing(Spacing.LG)

        ol.addWidget(self._section_title(f"🔲  {t('appearance.overlay')}"))

        # Blur
        self._blur_check = QCheckBox(t("appearance.blur"))
        self._blur_check.setChecked(appearance.get("overlay_blur", True))
        self._blur_check.setStyleSheet(self._check_style())
        self._blur_check.toggled.connect(lambda v: self._save_appearance("overlay_blur", v))
        ol.addWidget(self._blur_check)

        # Glow
        self._glow_check = QCheckBox(t("appearance.glow"))
        self._glow_check.setChecked(appearance.get("overlay_glow", True))
        self._glow_check.setStyleSheet(self._check_style())
        self._glow_check.toggled.connect(self._on_glow_changed)
        ol.addWidget(self._glow_check)

        # Intensidad del glow
        glow_row = QHBoxLayout()
        glow_row.setSpacing(Spacing.MD)
        glow_row.addWidget(self._field_label(t("appearance.glow_intensity")))
        self._glow_slider = QSlider(Qt.Orientation.Horizontal)
        self._glow_slider.setRange(0, 100)
        self._glow_slider.setValue(int(appearance.get("overlay_glow_intensity", 0.6) * 100))
        self._glow_slider.setStyleSheet(_SLIDER_STYLE)
        self._glow_slider.setFixedWidth(200)
        self._glow_slider.valueChanged.connect(self._on_glow_intensity_changed)
        glow_row.addWidget(self._glow_slider)
        self._glow_int_label = QLabel(f"{self._glow_slider.value()}%")
        self._glow_int_label.setFixedWidth(40)
        self._glow_int_label.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        glow_row.addWidget(self._glow_int_label)
        glow_row.addStretch()
        ol.addLayout(glow_row)

        # Opacidad
        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(Spacing.MD)
        opacity_row.addWidget(self._field_label(t("appearance.opacity")))
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(40, 100)
        self._opacity_slider.setValue(int(appearance.get("overlay_opacity", 0.85) * 100))
        self._opacity_slider.setStyleSheet(_SLIDER_STYLE)
        self._opacity_slider.setFixedWidth(200)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_row.addWidget(self._opacity_slider)
        self._opacity_label = QLabel(f"{self._opacity_slider.value()}%")
        self._opacity_label.setFixedWidth(40)
        self._opacity_label.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        opacity_row.addWidget(self._opacity_label)
        opacity_row.addStretch()
        ol.addLayout(opacity_row)

        # Animación
        anim_row = QHBoxLayout()
        anim_row.setSpacing(Spacing.MD)
        anim_row.addWidget(self._field_label(t("appearance.animation")))
        self._anim_slider = QSlider(Qt.Orientation.Horizontal)
        self._anim_slider.setRange(50, 500)
        self._anim_slider.setValue(appearance.get("overlay_animation_ms", 300))
        self._anim_slider.setStyleSheet(_SLIDER_STYLE)
        self._anim_slider.setFixedWidth(200)
        self._anim_slider.valueChanged.connect(self._on_anim_changed)
        anim_row.addWidget(self._anim_slider)
        self._anim_label = QLabel(f"{self._anim_slider.value()} ms")
        self._anim_label.setFixedWidth(55)
        self._anim_label.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        anim_row.addWidget(self._anim_label)
        anim_row.addStretch()
        ol.addLayout(anim_row)

        clayout.addWidget(overlay_section)

        # === Sonidos ===
        sound_section = self._make_section()
        sl = QVBoxLayout(sound_section)
        sl.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        sl.setSpacing(Spacing.MD)

        sl.addWidget(self._section_title(f"🔊  {t('appearance.sounds')}"))

        sounds_cfg = {}
        if self._bootstrap:
            sounds_cfg = self._bootstrap.get_config().get("sounds", {})

        self._sound_check = QCheckBox(t("appearance.sounds_enable"))
        self._sound_check.setChecked(sounds_cfg.get("enabled", True))
        self._sound_check.setStyleSheet(self._check_style())
        self._sound_check.toggled.connect(self._on_sound_toggled)
        sl.addWidget(self._sound_check)

        sound_hint = QLabel("Reproduce un sonido al ejecutar comandos, errores y confirmaciones.")
        sound_hint.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        sound_hint.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        sl.addWidget(sound_hint)

        clayout.addWidget(sound_section)

        clayout.addStretch()

        # Init preview
        self._sync_preview()

    # --- Helpers de UI ---

    @staticmethod
    def _make_section() -> QFrame:
        section = QFrame()
        section.setObjectName("section")
        section.setStyleSheet(_SECTION_STYLE)
        return section

    @staticmethod
    def _section_title(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD)
        )
        lbl.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        return lbl

    @staticmethod
    def _field_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD))
        lbl.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        lbl.setFixedWidth(180)
        return lbl

    @staticmethod
    def _check_style() -> str:
        return f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SIZE_MD}px; spacing: 8px;"

    # --- Callbacks ---

    def _on_accent_selected(self, color: str):
        for sw in self._swatches:
            sw.set_active(sw._color.lower() == color.lower())
        self._save_appearance("accent", color)
        self._sync_preview()
        logger.info("Color de acento cambiado a %s", color)

    def _on_opacity_changed(self, value: int):
        self._opacity_label.setText(f"{value}%")
        self._save_appearance("overlay_opacity", value / 100.0)
        self._sync_preview()

    def _on_glow_changed(self, checked: bool):
        self._save_appearance("overlay_glow", checked)
        self._sync_preview()

    def _on_glow_intensity_changed(self, value: int):
        self._glow_int_label.setText(f"{value}%")
        self._save_appearance("overlay_glow_intensity", value / 100.0)
        self._sync_preview()

    def _on_anim_changed(self, value: int):
        self._anim_label.setText(f"{value} ms")
        self._save_appearance("overlay_animation_ms", value)

    def _on_sound_toggled(self, checked: bool):
        if self._bootstrap:
            cfg = self._bootstrap.get_config()
            sounds = cfg.get("sounds", {})
            sounds["enabled"] = checked
            cfg.set("sounds", sounds)
            cfg.save()

    def _sync_preview(self):
        a = self._get_appearance()
        self._preview.update_settings(
            accent=a.get("accent", Colors.ACCENT_PRIMARY),
            opacity=a.get("overlay_opacity", 0.85),
            glow=a.get("overlay_glow", True),
            glow_intensity=a.get("overlay_glow_intensity", 0.6),
        )
