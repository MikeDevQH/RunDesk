"""
Sistema de estilos base para RunDesk.
Define paleta de colores, tipografías, espaciado y estilos de componentes.
"""


class Colors:
    """Paleta de colores del tema profesional oscuro."""

    # Fondos
    BG_DARKEST = "#0B1019"
    BG_BASE = "#0F1722"
    BG_DEEP = "#152638"
    BG_SURFACE = "#1B2A3B"
    BG_ELEVATED = "#223447"
    BG_HOVER = "#2A3F55"

    # Acentos
    ACCENT_PRIMARY = "#6EB6FF"
    ACCENT_SECONDARY = "#4B8DFF"
    ACCENT_HOVER = "#8DC8FF"
    ACCENT_PRESSED = "#3A7AE0"

    # Texto
    TEXT_PRIMARY = "#E8EDF3"
    TEXT_SECONDARY = "#9BADBF"
    TEXT_MUTED = "#607080"
    TEXT_ON_ACCENT = "#0F1722"

    # Bordes
    BORDER_SUBTLE = "rgba(214, 228, 240, 0.08)"
    BORDER_DEFAULT = "rgba(214, 228, 240, 0.12)"
    BORDER_STRONG = "rgba(214, 228, 240, 0.20)"

    # Estados
    SUCCESS = "#4ADE80"
    ERROR = "#F87171"
    WARNING = "#FBBF24"
    INFO = "#6EB6FF"

    # Sidebar
    SIDEBAR_BG = "#0B1019"
    SIDEBAR_ITEM_HOVER = "rgba(110, 182, 255, 0.08)"
    SIDEBAR_ITEM_ACTIVE = "rgba(110, 182, 255, 0.15)"
    SIDEBAR_SEPARATOR = "rgba(214, 228, 240, 0.06)"


class Fonts:
    """Configuración de tipografía."""

    FAMILY = "Segoe UI, Inter, sans-serif"
    SIZE_XS = 11
    SIZE_SM = 12
    SIZE_MD = 13
    SIZE_LG = 15
    SIZE_XL = 18
    SIZE_XXL = 24
    SIZE_HERO = 32
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


class Spacing:
    """Sistema de espaciado consistente."""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48


class Radius:
    """Bordes redondeados (estilo Windows 11)."""

    SM = 6
    MD = 10
    LG = 14
    XL = 18
    XXL = 24
    ROUND = 9999


SIDEBAR_WIDTH = 240
SIDEBAR_COLLAPSED_WIDTH = 64

_LABEL_CLEAN = "background: transparent; border: none"


def lbl_style(color: str) -> str:
    """Inline stylesheet for a QLabel: color + transparent bg + no border."""
    return f"color: {color}; {_LABEL_CLEAN};"


def get_base_stylesheet() -> str:
    """Retorna el stylesheet global de la aplicación (estilo Windows 11)."""
    return f"""
        /* === RESET Y BASE === */
        QWidget {{
            font-family: {Fonts.FAMILY};
            font-size: {Fonts.SIZE_MD}px;
            color: {Colors.TEXT_PRIMARY};
            background-color: transparent;
        }}

        QMainWindow {{
            background-color: {Colors.BG_BASE};
        }}

        /* Prevenir herencia de bordes en labels y contenedores */
        QLabel, QScrollArea {{
            border: none;
            background: transparent;
        }}

        /* === SCROLL BARS (slim, modern) === */
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 4px 1px;
        }}
        QScrollBar::handle:vertical {{
            background: rgba(255, 255, 255, 0.08);
            min-height: 40px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
            margin: 1px 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: rgba(255, 255, 255, 0.08);
            min-width: 40px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {{
            background: transparent;
        }}

        /* === TOOLTIPS === */
        QToolTip {{
            background-color: {Colors.BG_ELEVATED};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_SUBTLE};
            border-radius: {Radius.SM}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-size: {Fonts.SIZE_SM}px;
        }}

        /* === CHECKBOXES (toggle style) === */
        QCheckBox {{
            spacing: 10px;
            color: {Colors.TEXT_SECONDARY};
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {Colors.BORDER_STRONG};
            border-radius: 6px;
            background-color: {Colors.BG_DEEP};
        }}
        QCheckBox::indicator:hover {{
            border-color: {Colors.ACCENT_PRIMARY};
            background-color: {Colors.BG_ELEVATED};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Colors.ACCENT_PRIMARY};
            border-color: {Colors.ACCENT_PRIMARY};
            image: none;
        }}

        /* === LINE EDITS (borderless at rest, accent on focus) === */
        QLineEdit {{
            background-color: {Colors.BG_DEEP};
            color: {Colors.TEXT_PRIMARY};
            border: 2px solid transparent;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            selection-background-color: {Colors.ACCENT_SECONDARY};
        }}
        QLineEdit:hover {{
            background-color: {Colors.BG_ELEVATED};
        }}
        QLineEdit:focus {{
            border-color: {Colors.ACCENT_PRIMARY};
            background-color: {Colors.BG_DEEP};
        }}

        /* === PLAIN TEXT EDIT === */
        QPlainTextEdit {{
            background-color: {Colors.BG_DEEP};
            color: {Colors.TEXT_PRIMARY};
            border: 2px solid transparent;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px;
            selection-background-color: {Colors.ACCENT_SECONDARY};
        }}
        QPlainTextEdit:focus {{
            border-color: {Colors.ACCENT_PRIMARY};
        }}

        /* === COMBO BOXES === */
        QComboBox {{
            background-color: {Colors.BG_DEEP};
            color: {Colors.TEXT_PRIMARY};
            border: 2px solid transparent;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            min-height: 30px;
        }}
        QComboBox:hover {{
            background-color: {Colors.BG_ELEVATED};
        }}
        QComboBox:focus, QComboBox:on {{
            border-color: {Colors.ACCENT_PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 28px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Colors.BG_ELEVATED};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_SUBTLE};
            border-radius: {Radius.SM}px;
            padding: 4px;
            selection-background-color: {Colors.SIDEBAR_ITEM_ACTIVE};
            selection-color: {Colors.ACCENT_PRIMARY};
            outline: none;
        }}

        /* === SPIN BOXES === */
        QSpinBox, QDoubleSpinBox {{
            background-color: {Colors.BG_DEEP};
            color: {Colors.TEXT_PRIMARY};
            border: 2px solid transparent;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            min-height: 30px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            background-color: {Colors.BG_ELEVATED};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {Colors.ACCENT_PRIMARY};
        }}

        /* === TABLES === */
        QTableWidget {{
            background-color: {Colors.BG_BASE};
            gridline-color: {Colors.BORDER_SUBTLE};
            border: none;
            border-radius: {Radius.MD}px;
            selection-background-color: {Colors.SIDEBAR_ITEM_ACTIVE};
            selection-color: {Colors.TEXT_PRIMARY};
        }}
        QHeaderView::section {{
            background-color: {Colors.BG_SURFACE};
            color: {Colors.TEXT_SECONDARY};
            border: none;
            border-bottom: 1px solid {Colors.BORDER_SUBTLE};
            padding: {Spacing.SM}px {Spacing.MD}px;
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
        }}

        /* === MESSAGE BOX === */
        QMessageBox {{
            background-color: {Colors.BG_SURFACE};
        }}
        QMessageBox QLabel {{
            color: {Colors.TEXT_PRIMARY};
        }}
        QMessageBox QPushButton {{
            min-width: 80px;
        }}
    """


def get_button_primary_style() -> str:
    """Estilo para botones primarios (Windows 11 pill style)."""
    return f"""
        QPushButton {{
            background-color: {Colors.ACCENT_PRIMARY};
            color: {Colors.TEXT_ON_ACCENT};
            border: none;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM + 2}px {Spacing.XL}px;
            font-size: {Fonts.SIZE_MD}px;
            font-weight: {Fonts.WEIGHT_SEMIBOLD};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {Colors.ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.ACCENT_PRESSED};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BG_HOVER};
            color: {Colors.TEXT_MUTED};
        }}
    """


def get_button_secondary_style() -> str:
    """Estilo para botones secundarios (ghost style)."""
    return f"""
        QPushButton {{
            background-color: {Colors.BG_ELEVATED};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_SUBTLE};
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM + 2}px {Spacing.XL}px;
            font-size: {Fonts.SIZE_MD}px;
            font-weight: {Fonts.WEIGHT_MEDIUM};
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BG_HOVER};
            border-color: {Colors.BORDER_DEFAULT};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BG_SURFACE};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BG_DEEP};
            color: {Colors.TEXT_MUTED};
            border-color: transparent;
        }}
    """


def get_card_style() -> str:
    """Estilo para cards/paneles (elevación sutil)."""
    return f"""
        QFrame {{
            background-color: {Colors.BG_SURFACE};
            border: 1px solid {Colors.BORDER_SUBTLE};
            border-radius: {Radius.LG}px;
        }}
    """


def get_section_style() -> str:
    """Estilo para secciones agrupadas con fondo elevado."""
    return f"""
        QFrame {{
            background-color: {Colors.BG_SURFACE};
            border: 1px solid {Colors.BORDER_SUBTLE};
            border-radius: {Radius.LG}px;
        }}
        QFrame:hover {{
            border-color: {Colors.BORDER_DEFAULT};
        }}
    """
