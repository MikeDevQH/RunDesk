"""
Input Overlay — ventana flotante premium del launcher.
Fullscreen backdrop + floating input con blur, glow intenso, animaciones
y panel de sugerencias en tiempo real.
"""

import ctypes
import ctypes.wintypes
import logging

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QCursor,
    QFont,
    QPainter,
    QPainterPath,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import Colors, Fonts, Radius, Spacing

logger = logging.getLogger(__name__)

# --- Constantes del overlay ---

OVERLAY_WIDTH = 580
INPUT_HEIGHT = 52
SUGGESTION_ROW_HEIGHT = 38
MAX_SUGGESTIONS = 5
GLOW_MARGIN = 32


def _enable_acrylic(hwnd: int):
    """Aplica efecto acrylic/blur al fondo de la ventana usando DWM de Windows."""
    try:
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_int),
            ]

        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_ulong),
            ]

        accent = ACCENT_POLICY()
        accent.AccentState = 4
        accent.AccentFlags = 2
        accent.GradientColor = 0x991A1A2E

        data = WINCOMPATTRDATA()
        data.Attribute = 19
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)

        ctypes.windll.user32.SetWindowCompositionAttribute(
            ctypes.wintypes.HWND(hwnd), ctypes.byref(data)
        )
    except Exception:
        logger.debug("Acrylic blur no disponible, usando fallback opaco")


class GlowWidget(QWidget):
    """Widget que dibuja un halo/glow radial alrededor del input."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._color = QColor(110, 182, 255)
        self._intensity = 0.7  # 0.0 a 1.0

    def set_color(self, hex_color: str):
        """Cambia el color del glow dinámicamente."""
        self._color = QColor(hex_color)
        self.update()

    def set_intensity(self, intensity: float):
        """Cambia la intensidad/opacidad del glow (0.0 - 1.0)."""
        self._intensity = max(0.0, min(1.0, intensity))
        self.update()

    def paintEvent(self, event):
        if self._intensity <= 0.01:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        c = self._color
        i = self._intensity
        center = self.rect().center()
        radius = max(self.width(), self.height()) * 0.55
        gradient = QRadialGradient(center.x(), center.y(), radius)
        gradient.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), int(80 * i)))
        gradient.setColorAt(0.3, QColor(c.red(), c.green(), c.blue(), int(35 * i)))
        gradient.setColorAt(0.6, QColor(c.red(), c.green(), c.blue(), int(10 * i)))
        gradient.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))

        path = QPainterPath()
        path.addRoundedRect(
            self.rect().toRectF(), Radius.XL + 8, Radius.XL + 8
        )
        painter.fillPath(path, gradient)
        painter.end()


class BackdropWidget(QWidget):
    """Fondo oscuro fullscreen que difumina todo lo que hay detrás del overlay."""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self._opacity = 0.55

    def set_opacity(self, opacity: float):
        self._opacity = opacity

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(self._opacity * 255)))
        painter.end()

    def mousePressEvent(self, event):
        self.clicked.emit()


class SuggestionRow(QWidget):
    """Una fila individual de sugerencia."""

    clicked = Signal(str)  # emite el id del item

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(SUGGESTION_ROW_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._item_id = ""
        self._is_selected = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XL + 28 + Spacing.MD, 0, Spacing.XL, 0)
        layout.setSpacing(Spacing.SM)

        self._icon = QLabel()
        self._icon.setFixedWidth(18)
        self._icon.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        self._icon.setStyleSheet("border: none;")
        layout.addWidget(self._icon)

        self._name = QLabel()
        self._name.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_MEDIUM)
        )
        self._name.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; border: none;")
        layout.addWidget(self._name)

        self._alias = QLabel()
        self._alias.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        self._alias.setStyleSheet(f"color: {Colors.TEXT_MUTED}; border: none;")
        layout.addWidget(self._alias)

        layout.addStretch()

        self._score_label = QLabel()
        self._score_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS))
        self._score_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; border: none;")
        layout.addWidget(self._score_label)

    def set_data(self, suggestion: dict):
        """Actualiza con datos de sugerencia: {id, name, type, alias, score}."""
        self._item_id = suggestion["id"]
        icon = "⌨️" if suggestion["type"] == "command" else "🎬"
        self._icon.setText(icon)
        self._name.setText(suggestion["name"])
        self._alias.setText(f"({suggestion['alias']})")
        score = suggestion["score"]
        if score >= 1.0:
            self._score_label.setText("exacto")
            self._score_label.setStyleSheet(f"color: {Colors.SUCCESS}; border: none;")
        else:
            self._score_label.setText(f"{score:.0%}")
            self._score_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; border: none;")
        self.show()

    def set_selected(self, selected: bool):
        """Marca visual de selección."""
        self._is_selected = selected
        bg = "rgba(110, 182, 255, 0.12)" if selected else "transparent"
        self.setStyleSheet(f"background-color: {bg}; border: none; border-radius: 4px;")
        if selected:
            self._name.setStyleSheet(f"color: {Colors.ACCENT_PRIMARY}; border: none;")
        else:
            self._name.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; border: none;")

    def mousePressEvent(self, event):
        if self._item_id:
            self.clicked.emit(self._item_id)


class InputOverlay(QWidget):
    """Overlay flotante del launcher con backdrop fullscreen, input premium
    y sugerencias en tiempo real.

    Señales:
        command_submitted(str): texto enviado por el usuario (Enter).
        overlay_closed(): el overlay se cerró (Esc o pérdida de foco).
    """

    command_submitted = Signal(str)
    overlay_closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parser = None
        self._config = None
        self._suggestions: list[dict] = []
        self._selected_index = -1

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        # Backdrop fullscreen
        self._backdrop = BackdropWidget()
        self._backdrop.clicked.connect(self.hide_overlay)

        self._setup_ui()
        self._setup_animations()
        self._update_size()

    def set_parser(self, parser):
        """Conecta el CommandParser para sugerencias en vivo."""
        self._parser = parser

    def set_config(self, config):
        """Conecta el ConfigStore para leer apariencia."""
        self._config = config

    def _get_appearance(self) -> dict:
        if self._config:
            return self._config.get("appearance", {})
        return {}

    def _get_accent(self) -> str:
        return self._get_appearance().get("accent", Colors.ACCENT_PRIMARY)

    def _setup_ui(self):
        """Construye el layout del overlay."""
        root = QVBoxLayout(self)
        root.setContentsMargins(GLOW_MARGIN, GLOW_MARGIN, GLOW_MARGIN, GLOW_MARGIN)
        root.setSpacing(0)

        self._glow = GlowWidget(self)

        # Container principal — muy transparente, borde luminoso
        self._container = QWidget()
        self._container.setObjectName("overlayContainer")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 160))
        self._container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # --- Fila del input ---
        input_row = QWidget()
        input_row.setFixedHeight(INPUT_HEIGHT)
        input_row.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_row)
        input_layout.setContentsMargins(Spacing.XL + 4, 0, Spacing.XL, 0)
        input_layout.setSpacing(Spacing.MD)

        self._accent_icon = QLabel("✦")
        self._accent_icon.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 20))
        self._accent_icon.setStyleSheet(f"""
            color: {Colors.ACCENT_PRIMARY};
            background: transparent;
            border: none;
        """)
        self._accent_icon.setFixedWidth(30)
        input_layout.addWidget(self._accent_icon)

        self._input = QLineEdit()
        self._input.setPlaceholderText(t("overlay.placeholder"))
        self._input.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {Colors.TEXT_PRIMARY};
                padding: 0;
                selection-background-color: {Colors.ACCENT_SECONDARY};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self._input.returnPressed.connect(self._on_submit)
        self._input.textChanged.connect(self._on_text_changed)
        input_layout.addWidget(self._input)

        esc_hint = QLabel("ESC")
        esc_hint.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 9, Fonts.WEIGHT_MEDIUM))
        esc_hint.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: {Radius.SM}px;
            padding: 3px 8px;
        """)
        esc_hint.setFixedWidth(36)
        input_layout.addWidget(esc_hint)

        container_layout.addWidget(input_row)

        # --- Separador ---
        self._separator = QWidget()
        self._separator.setFixedHeight(1)
        self._separator.setStyleSheet("border: none;")
        self._separator.hide()
        container_layout.addWidget(self._separator)

        # --- Panel de sugerencias ---
        self._suggestions_panel = QWidget()
        self._suggestions_panel.setStyleSheet("background: transparent; border: none;")
        suggestions_layout = QVBoxLayout(self._suggestions_panel)
        suggestions_layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.SM)
        suggestions_layout.setSpacing(2)

        self._suggestion_rows: list[SuggestionRow] = []
        for _ in range(MAX_SUGGESTIONS):
            row = SuggestionRow()
            row.clicked.connect(self._on_suggestion_clicked)
            row.hide()
            suggestions_layout.addWidget(row)
            self._suggestion_rows.append(row)

        # No-match label
        self._no_match_label = QLabel(t("overlay.no_match"))
        self._no_match_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
        )
        self._no_match_label.setStyleSheet(
            f"color: {Colors.ERROR}; border: none; padding-left: {Spacing.XL + 30 + Spacing.MD}px;"
        )
        self._no_match_label.setFixedHeight(SUGGESTION_ROW_HEIGHT)
        self._no_match_label.hide()
        suggestions_layout.addWidget(self._no_match_label)

        self._suggestions_panel.hide()
        container_layout.addWidget(self._suggestions_panel)

        root.addWidget(self._container)

    def _setup_animations(self):
        """Configura animaciones de fade in/out."""
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in.setDuration(220)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out.setDuration(160)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self._on_fade_out_done)

        # Backdrop fade
        self._backdrop_opacity = QGraphicsOpacityEffect(self._backdrop)
        self._backdrop_opacity.setOpacity(0.0)
        self._backdrop.setGraphicsEffect(self._backdrop_opacity)

        self._backdrop_fade_in = QPropertyAnimation(self._backdrop_opacity, b"opacity")
        self._backdrop_fade_in.setDuration(250)
        self._backdrop_fade_in.setStartValue(0.0)
        self._backdrop_fade_in.setEndValue(1.0)
        self._backdrop_fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._backdrop_fade_out = QPropertyAnimation(self._backdrop_opacity, b"opacity")
        self._backdrop_fade_out.setDuration(180)
        self._backdrop_fade_out.setStartValue(1.0)
        self._backdrop_fade_out.setEndValue(0.0)
        self._backdrop_fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._backdrop_fade_out.finished.connect(self._backdrop.hide)

    # --- Tamaño dinámico ---

    def _update_size(self, num_suggestions: int = 0):
        """Recalcula el tamaño del overlay según sugerencias visibles."""
        content_h = INPUT_HEIGHT
        if num_suggestions > 0:
            content_h += 1 + Spacing.XS + num_suggestions * SUGGESTION_ROW_HEIGHT + Spacing.SM
        total_w = OVERLAY_WIDTH + GLOW_MARGIN * 2
        total_h = content_h + GLOW_MARGIN * 2
        self.setFixedSize(total_w, total_h)
        self._container.setFixedSize(OVERLAY_WIDTH, content_h)

    # --- Sugerencias ---

    def _on_text_changed(self, text: str):
        """Actualiza sugerencias en tiempo real."""
        text = text.strip()

        if not text or not self._parser:
            self._hide_suggestions()
            return

        suggestions = self._parser.get_suggestions(text, limit=MAX_SUGGESTIONS)
        self._suggestions = suggestions
        self._selected_index = 0 if suggestions else -1
        self._show_suggestions(suggestions, show_no_match=(len(text) >= 2))

    def _show_suggestions(self, suggestions: list[dict], show_no_match: bool = False):
        """Muestra las sugerencias en el panel."""
        for row in self._suggestion_rows:
            row.hide()
        self._no_match_label.hide()

        if suggestions:
            for i, sug in enumerate(suggestions):
                self._suggestion_rows[i].set_data(sug)
                self._suggestion_rows[i].set_selected(i == self._selected_index)
            self._separator.show()
            self._suggestions_panel.show()
            self._update_size(len(suggestions))
        elif show_no_match:
            self._no_match_label.show()
            self._separator.show()
            self._suggestions_panel.show()
            self._update_size(1)
        else:
            self._hide_suggestions()

    def _hide_suggestions(self):
        """Oculta el panel de sugerencias."""
        self._suggestions.clear()
        self._selected_index = -1
        for row in self._suggestion_rows:
            row.hide()
        self._no_match_label.hide()
        self._separator.hide()
        self._suggestions_panel.hide()
        self._update_size(0)

    def _on_suggestion_clicked(self, item_id: str):
        """Cuando se hace click en una sugerencia."""
        self.command_submitted.emit(item_id)
        self.hide_overlay()

    # --- Posicionamiento ---

    def _center_on_active_screen(self):
        """Centra el overlay en el monitor donde está el cursor."""
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if screen is None:
            screen = QApplication.primaryScreen()

        geo = screen.availableGeometry()

        # Backdrop cubre toda la pantalla
        self._backdrop.setGeometry(QRect(geo.x(), geo.y(), geo.width(), geo.height()))

        # Overlay centrado horizontalmente, un poco arriba del centro vertical
        total_w = self.width()
        total_h = self.height()
        x = geo.x() + (geo.width() - total_w) // 2
        y = geo.y() + int(geo.height() * 0.30) - total_h // 2
        self.move(x, y)

    # --- Show / Hide ---

    def _apply_appearance(self):
        """Aplica configuración de apariencia desde config al overlay."""
        a = self._get_appearance()
        accent = a.get("accent", Colors.ACCENT_PRIMARY)
        opacity = a.get("overlay_opacity", 0.85)
        glow_enabled = a.get("overlay_glow", True)
        anim_ms = a.get("overlay_animation_ms", 300)

        rgb = self._hex_to_rgb(accent)

        # Container — translúcido con borde luminoso grueso
        bg_alpha = max(int(opacity * 200), 80)
        self._container.setStyleSheet(f"""
            QWidget#overlayContainer {{
                background-color: rgba(10, 16, 28, {bg_alpha});
                border: 2px solid rgba({rgb}, 0.50);
                border-radius: {Radius.XL + 4}px;
            }}
        """)

        # Separador con color de acento
        self._separator.setStyleSheet(
            f"background-color: rgba({rgb}, 0.15); border: none;"
        )

        # Icono
        self._accent_icon.setStyleSheet(f"""
            color: {accent};
            background: transparent;
            border: none;
        """)

        # Input
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {Colors.TEXT_PRIMARY};
                padding: 0;
                selection-background-color: {accent};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)

        # Glow — color de acento + intensidad configurable
        glow_intensity = a.get("overlay_glow_intensity", 0.6)
        self._glow.setVisible(glow_enabled)
        self._glow.set_color(accent)
        self._glow.set_intensity(glow_intensity)

        # Shadow con color de acento
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 3)
        c = QColor(accent)
        shadow.setColor(QColor(c.red(), c.green(), c.blue(), int(50 * glow_intensity)))
        self._container.setGraphicsEffect(shadow)

        # Animación
        self._fade_in.setDuration(anim_ms)
        self._fade_out.setDuration(max(anim_ms - 60, 60))

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        """Convierte '#RRGGBB' a 'R, G, B'."""
        h = hex_color.lstrip("#")
        return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"

    def show_overlay(self):
        """Muestra el backdrop + overlay con animación."""
        self._input.clear()
        self._input.setPlaceholderText(t("overlay.placeholder"))
        self._no_match_label.setText(t("overlay.no_match"))
        self._hide_suggestions()
        self._apply_appearance()
        self._center_on_active_screen()

        # Mostrar backdrop primero
        self._backdrop.show()
        self._backdrop_fade_out.stop()
        self._backdrop_fade_in.start()

        # Mostrar overlay
        self.show()
        self.raise_()

        if self._get_appearance().get("overlay_blur", True):
            _enable_acrylic(int(self.winId()))

        self._fade_out.stop()
        self._fade_in.start()
        self._input.setFocus()
        self.activateWindow()

    def show_feedback(self, success: bool, message: str, duration_ms: int = 1200):
        """Muestra un toast de feedback breve en el overlay antes de cerrarlo."""
        self._hide_suggestions()
        self._input.setReadOnly(True)

        icon = "✓" if success else "✗"
        color = Colors.SUCCESS if success else Colors.ERROR
        # Truncar mensaje largo
        short = message[:60] + "…" if len(message) > 60 else message
        self._input.setText(f"  {icon}  {short}")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {color};
                padding: 0;
            }}
        """)

        if not self.isVisible():
            self._apply_appearance()
            self._center_on_active_screen()
            self._backdrop.show()
            self._backdrop_fade_in.start()
            self.show()
            self.raise_()
            _enable_acrylic(int(self.winId()))
            self._fade_out.stop()
            self._fade_in.start()

        QTimer.singleShot(duration_ms, self._finish_feedback)

    def _finish_feedback(self):
        """Restaura el overlay después del feedback y lo cierra."""
        self._input.setReadOnly(False)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {Colors.TEXT_PRIMARY};
                padding: 0;
                selection-background-color: {Colors.ACCENT_SECONDARY};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self.hide_overlay()

    def hide_overlay(self):
        """Oculta backdrop + overlay con animación fade out."""
        if not self.isVisible():
            return
        self._fade_in.stop()
        self._fade_out.start()
        self._backdrop_fade_in.stop()
        self._backdrop_fade_out.start()

    def toggle(self):
        """Alterna visibilidad del overlay."""
        if self.isVisible():
            self.hide_overlay()
        else:
            self.show_overlay()

    def _on_fade_out_done(self):
        """Llamado cuando termina la animación de salida."""
        self.hide()
        self.overlay_closed.emit()

    # --- Eventos ---

    def _on_submit(self):
        """Llamado cuando el usuario presiona Enter."""
        # Si hay sugerencia seleccionada, usarla por su alias/id
        if self._suggestions and 0 <= self._selected_index < len(self._suggestions):
            selected = self._suggestions[self._selected_index]
            self.command_submitted.emit(selected["alias"])
            self.hide_overlay()
            return

        text = self._input.text().strip()
        if text:
            self.command_submitted.emit(text)
        self.hide_overlay()

    def keyPressEvent(self, event):
        """Maneja Esc, flechas arriba/abajo para navegación."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_overlay()
        elif event.key() == Qt.Key.Key_Down and self._suggestions:
            self._selected_index = min(
                self._selected_index + 1, len(self._suggestions) - 1
            )
            self._refresh_selection()
        elif event.key() == Qt.Key.Key_Up and self._suggestions:
            self._selected_index = max(self._selected_index - 1, 0)
            self._refresh_selection()
        else:
            super().keyPressEvent(event)

    def _refresh_selection(self):
        """Actualiza visual de selección en las filas."""
        for i, row in enumerate(self._suggestion_rows):
            if row.isVisible():
                row.set_selected(i == self._selected_index)

    def resizeEvent(self, event):
        """Ajusta el glow al tamaño del widget."""
        super().resizeEvent(event)
        self._glow.setGeometry(self.rect())

    def focusOutEvent(self, event):
        """Cierra si pierde el foco (click fuera)."""
        super().focusOutEvent(event)
        if self.isVisible() and not self._input.hasFocus():
            self.hide_overlay()
