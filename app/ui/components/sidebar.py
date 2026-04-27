"""
Sidebar de navegación principal.
Muestra los items de navegación con iconos, estados activos y hover.
"""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import SIDEBAR_WIDTH, Colors, Fonts, Spacing, lbl_style

# Definición de las páginas de navegación (id + icono; label viene de i18n)
NAV_ITEMS = [
    {"id": "dashboard",   "icon": "📊"},
    {"id": "commands",    "icon": "⌨️"},
    {"id": "scenes",      "icon": "🎬"},
    {"id": "launcher",    "icon": "🚀"},
    {"id": "appearance",  "icon": "🎨"},
    {"id": "languages",   "icon": "🌐"},
    {"id": "tutorials",   "icon": "❓"},
    {"id": "diagnostics", "icon": "🔧"},
    {"id": "about",       "icon": "ℹ️"},
]


class SidebarButton(QPushButton):
    """Botón individual del sidebar con estado activo/hover."""

    def __init__(self, item_id: str, label: str, icon_text: str, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self._icon_text = icon_text
        self._is_active = False

        self.setText(f"  {icon_text}   {label}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(44)
        self.setCheckable(True)
        self.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD))

        self._update_style()

    def set_active(self, active: bool):
        """Marca este botón como activo o inactivo."""
        self._is_active = active
        self.setChecked(active)
        self._update_style()

    def _update_style(self):
        """Aplica estilos según estado activo (pill style)."""
        if self._is_active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.SIDEBAR_ITEM_ACTIVE};
                    color: {Colors.ACCENT_PRIMARY};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: {Spacing.XL}px;
                    margin: 2px {Spacing.SM}px;
                    font-weight: {Fonts.WEIGHT_SEMIBOLD};
                    font-size: {Fonts.SIZE_MD}px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: {Spacing.XL}px;
                    margin: 2px {Spacing.SM}px;
                    font-weight: {Fonts.WEIGHT_NORMAL};
                    font-size: {Fonts.SIZE_MD}px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.SIDEBAR_ITEM_HOVER};
                    color: {Colors.TEXT_PRIMARY};
                }}
            """)


class Sidebar(QWidget):
    """Sidebar de navegación con logo, items y separadores."""

    navigation_requested = Signal(str)  # Emite el id de la página

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setStyleSheet(f"background-color: {Colors.SIDEBAR_BG};")

        self._buttons: dict[str, SidebarButton] = {}
        self._current_page = ""

        self._setup_ui()

    def _setup_ui(self):
        """Construye el layout del sidebar."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Logo / Título ---
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet(f"background-color: {Colors.SIDEBAR_BG};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(
            Spacing.LG, Spacing.LG, Spacing.LG, Spacing.SM
        )
        header_layout.setSpacing(Spacing.MD)

        # Logo icon
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "assets", "icon.png",
        )
        logo = QLabel()
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(
                54, 54, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
        else:
            logo.setText("⚡")
            logo.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 26))
        logo.setFixedSize(54, 54)
        logo.setStyleSheet("background: transparent; border: none;")
        header_layout.addWidget(logo)

        title = QLabel("RunDesk")
        title.setStyleSheet(
            f"color: {Colors.ACCENT_PRIMARY}; background: transparent; border: none;"
            f" font-size: 22px; font-weight: bold;"
        )
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addWidget(header)

        # --- Separador ---
        layout.addWidget(self._create_separator())

        # --- Items de navegación ---
        layout.addSpacing(Spacing.SM)
        for item in NAV_ITEMS:
            label = t(f"sidebar.{item['id']}")
            btn = SidebarButton(item["id"], label, item["icon"])
            btn.clicked.connect(lambda checked=False, pid=item["id"]: self._on_item_clicked(pid))
            self._buttons[item["id"]] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # --- Footer ---
        layout.addWidget(self._create_separator())

        version_label = QLabel("v0.1.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: {Fonts.SIZE_XS}px; "
            f"padding: {Spacing.SM}px; background: transparent;"
        )
        layout.addWidget(version_label)

    def _create_separator(self) -> QFrame:
        """Crea un separador horizontal sutil."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {Colors.SIDEBAR_SEPARATOR}; border: none;")
        return sep

    def _on_item_clicked(self, page_id: str):
        """Maneja el click en un item de navegación."""
        if page_id != self._current_page:
            self.set_active_page(page_id)
            self.navigation_requested.emit(page_id)

    def set_active_page(self, page_id: str):
        """Actualiza visualmente el item activo."""
        self._current_page = page_id
        for bid, btn in self._buttons.items():
            btn.set_active(bid == page_id)

    def refresh_labels(self):
        """Actualiza las etiquetas del sidebar con el idioma activo."""
        for bid, btn in self._buttons.items():
            label = t(f"sidebar.{bid}")
            btn.setText(f"  {btn._icon_text}   {label}")
