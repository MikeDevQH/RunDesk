"""
Página de ayuda y tutoriales.
Guías paso a paso interactivas para el usuario.
"""

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.styles import (
    Colors,
    Fonts,
    Radius,
    Spacing,
    get_button_primary_style,
    get_button_secondary_style,
    lbl_style,
)

# Tutorial definitions: id, icon, section, step_count, action_page
TUTORIAL_DEFS = [
    {
        "id": "first",
        "icon": "🚀",
        "section": "getting_started",
        "step_count": 5,
        "action_page": "commands",
    },
    {
        "id": "alias",
        "icon": "⌨️",
        "section": "getting_started",
        "step_count": 5,
        "action_page": "commands",
    },
    {
        "id": "scene",
        "icon": "🎬",
        "section": "advanced",
        "step_count": 5,
        "action_page": "scenes",
    },
    {
        "id": "monitor",
        "icon": "🖥️",
        "section": "advanced",
        "step_count": 4,
        "action_page": "commands",
    },
    {
        "id": "lang",
        "icon": "🌐",
        "section": "advanced",
        "step_count": 4,
        "action_page": "languages",
    },
    {
        "id": "diag",
        "icon": "🔧",
        "section": "maintenance",
        "step_count": 4,
        "action_page": "diagnostics",
    },
    {
        "id": "export",
        "icon": "💾",
        "section": "maintenance",
        "step_count": 4,
        "action_page": "diagnostics",
    },
]


def _md_to_rich(text: str) -> str:
    """Convierte markdown ligero (**bold**, `code`, bullets) a HTML."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", rf'<code style="color:{Colors.ACCENT_PRIMARY}">\1</code>', text)
    text = text.replace("\n", "<br>")
    text = text.replace("  •", "&nbsp;&nbsp;•")
    return text


class TutorialCard(QFrame):
    """Card clickable para un tutorial."""

    clicked = Signal(str)

    def __init__(
        self, tutorial_id: str, icon: str, title: str,
        description: str, tag: str = "", parent=None,
    ):
        super().__init__(parent)
        self._tutorial_id = tutorial_id
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("tutCard")
        self.setStyleSheet(f"""
            QFrame#tutCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
            QFrame#tutCard:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
                background-color: {Colors.BG_ELEVATED};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        layout.setSpacing(Spacing.XL)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 24))
        icon_label.setStyleSheet("background: transparent;")
        icon_label.setFixedWidth(40)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(icon_label)

        col = QVBoxLayout()
        col.setSpacing(Spacing.XS)

        title_label = QLabel(title)
        title_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_SEMIBOLD)
        )
        title_label.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        col.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        desc_label.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        desc_label.setWordWrap(True)
        desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        col.addWidget(desc_label)

        layout.addLayout(col, 1)

        if tag:
            tag_label = QLabel(tag)
            tag_label.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS, Fonts.WEIGHT_MEDIUM)
            )
            tag_label.setStyleSheet(f"""
                color: {Colors.ACCENT_PRIMARY};
                border: 1px solid {Colors.ACCENT_PRIMARY};
                border-radius: {Radius.SM}px;
                padding: 2px 8px;
            """)
            tag_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(tag_label)

        # Arrow indicator
        arrow = QLabel("→")
        arrow.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL))
        arrow.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(arrow)

    def mousePressEvent(self, event):
        self.clicked.emit(self._tutorial_id)
        super().mousePressEvent(event)


class TutorialDetailView(QWidget):
    """Vista de detalle de un tutorial con pasos numerados."""

    back_requested = Signal()
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(self._scroll)

    def show_tutorial(self, tut_def: dict):
        """Construye la vista de detalle para un tutorial."""
        # Reemplazar el container entero (evita leak de sub-layouts)
        container = QWidget()
        self._scroll.setWidget(container)

        lay = QVBoxLayout(container)
        lay.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        lay.setSpacing(Spacing.LG)

        tid = tut_def["id"]
        prefix = f"tutorials.tut_{tid}"

        # --- Back button ---
        back_btn = QPushButton(t("tutorials.back"))
        back_btn.setStyleSheet(get_button_secondary_style())
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFixedWidth(220)
        back_btn.clicked.connect(self.back_requested.emit)
        lay.addWidget(back_btn)

        lay.addSpacing(Spacing.SM)

        # --- Icon + Title ---
        header_row = QHBoxLayout()
        header_row.setSpacing(Spacing.LG)

        icon_label = QLabel(tut_def["icon"])
        icon_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 32))
        header_row.addWidget(icon_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(Spacing.XS)

        title = QLabel(t(f"{prefix}_title"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XXL, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        title_col.addWidget(title)

        desc = QLabel(t(f"{prefix}_desc"))
        desc.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        desc.setWordWrap(True)
        title_col.addWidget(desc)

        header_row.addLayout(title_col, 1)

        level = QLabel(t(f"{prefix}_level"))
        level.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM, Fonts.WEIGHT_MEDIUM)
        )
        level.setStyleSheet(f"""
            color: {Colors.ACCENT_PRIMARY};
            border: 1px solid {Colors.ACCENT_PRIMARY};
            border-radius: {Radius.SM}px;
            padding: 4px 12px;
        """)
        level.setFixedHeight(28)
        header_row.addWidget(level, alignment=Qt.AlignmentFlag.AlignTop)

        lay.addLayout(header_row)
        lay.addSpacing(Spacing.MD)

        # --- Steps ---
        for i in range(1, tut_def["step_count"] + 1):
            step_text = t(f"{prefix}_step_{i}")
            step_frame = QFrame()
            step_frame.setObjectName("stepFrame")
            step_frame.setStyleSheet(f"""
                QFrame#stepFrame {{
                    background-color: {Colors.BG_SURFACE};
                    border: 1px solid {Colors.BORDER_SUBTLE};
                    border-radius: {Radius.LG}px;
                }}
            """)
            step_lay = QHBoxLayout(step_frame)
            step_lay.setContentsMargins(
                Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG,
            )
            step_lay.setSpacing(Spacing.LG)

            # Step number badge
            num_label = QLabel(str(i))
            num_label.setFixedSize(32, 32)
            num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num_label.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_BOLD)
            )
            num_label.setStyleSheet(f"""
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.TEXT_ON_ACCENT};
                border-radius: 16px;
                border: none;
            """)
            step_lay.addWidget(num_label, alignment=Qt.AlignmentFlag.AlignTop)

            # Step text (rich HTML)
            text_label = QLabel(_md_to_rich(step_text))
            text_label.setTextFormat(Qt.TextFormat.RichText)
            text_label.setWordWrap(True)
            text_label.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
            )
            text_label.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
            step_lay.addWidget(text_label, 1)

            lay.addWidget(step_frame)

        lay.addSpacing(Spacing.SM)

        # --- Tip box ---
        tip_text = t(f"{prefix}_tip")
        if tip_text != f"{prefix}_tip":
            tip_frame = QFrame()
            tip_frame.setObjectName("tipFrame")
            tip_frame.setStyleSheet(f"""
                QFrame#tipFrame {{
                    background-color: rgba(110, 182, 255, 0.08);
                    border: 1px solid {Colors.ACCENT_PRIMARY};
                    border-radius: {Radius.LG}px;
                }}
            """)
            tip_lay = QHBoxLayout(tip_frame)
            tip_lay.setContentsMargins(
                Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG,
            )
            tip_lay.setSpacing(Spacing.MD)

            tip_icon = QLabel("💡")
            tip_icon.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 18))
            tip_icon.setStyleSheet("background: transparent;")
            tip_lay.addWidget(tip_icon, alignment=Qt.AlignmentFlag.AlignTop)

            tip_label = QLabel(_md_to_rich(tip_text))
            tip_label.setTextFormat(Qt.TextFormat.RichText)
            tip_label.setWordWrap(True)
            tip_label.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
            )
            tip_label.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
            tip_lay.addWidget(tip_label, 1)

            lay.addWidget(tip_frame)

        # --- Action button ---
        action_text = t(f"{prefix}_action")
        if action_text != f"{prefix}_action":
            action_btn = QPushButton(f"  {action_text}  →")
            action_btn.setStyleSheet(get_button_primary_style())
            action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            action_btn.setFixedHeight(40)
            action_btn.clicked.connect(
                lambda _, p=tut_def["action_page"]: self.navigate_requested.emit(p)
            )
            btn_row = QHBoxLayout()
            btn_row.addWidget(action_btn)
            btn_row.addStretch()
            lay.addLayout(btn_row)

        lay.addStretch()


class TutorialsPage(QWidget):
    """Página de ayuda y tutoriales guiados con vista lista y detalle."""

    navigate_requested = Signal(str)

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        # View 0: List view
        self._list_view = QWidget()
        self._stack.addWidget(self._list_view)
        self._build_list_view()

        # View 1: Detail view
        self._detail_view = TutorialDetailView()
        self._detail_view.back_requested.connect(self._show_list)
        self._detail_view.navigate_requested.connect(self.navigate_requested.emit)
        self._stack.addWidget(self._detail_view)

        self._stack.setCurrentIndex(0)

    def _build_list_view(self):
        """Construye la vista de lista de tutoriales."""
        outer = QVBoxLayout(self._list_view)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        title = QLabel(t("tutorials.title"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel(t("tutorials.subtitle"))
        subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(Spacing.MD)

        # Group tutorials by section
        sections = {
            "getting_started": ("tutorials.getting_started", []),
            "advanced": ("tutorials.advanced", []),
            "maintenance": ("tutorials.maintenance", []),
        }
        for tdef in TUTORIAL_DEFS:
            sections[tdef["section"]][1].append(tdef)

        for section_key, (label_key, tutorials) in sections.items():
            if not tutorials:
                continue

            if section_key != "getting_started":
                layout.addSpacing(Spacing.MD)

            section_label = QLabel(t(label_key))
            section_label.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL, Fonts.WEIGHT_SEMIBOLD)
            )
            section_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
            layout.addWidget(section_label)

            for tdef in tutorials:
                tid = tdef["id"]
                prefix = f"tutorials.tut_{tid}"
                card = TutorialCard(
                    tid, tdef["icon"],
                    t(f"{prefix}_title"),
                    t(f"{prefix}_desc"),
                    t(f"{prefix}_level"),
                )
                card.clicked.connect(self._on_card_clicked)
                layout.addWidget(card)

        layout.addStretch()

    def _on_card_clicked(self, tutorial_id: str):
        """Abre la vista de detalle del tutorial seleccionado."""
        tut_def = next((td for td in TUTORIAL_DEFS if td["id"] == tutorial_id), None)
        if tut_def:
            self._detail_view.show_tutorial(tut_def)
            self._stack.setCurrentIndex(1)

    def _show_list(self):
        """Vuelve a la vista de lista."""
        self._stack.setCurrentIndex(0)

    def on_page_shown(self):
        """Reconstruye la vista lista al cambiar idioma."""
        # Reconstruir la lista
        old_list = self._list_view
        self._list_view = QWidget()
        self._stack.insertWidget(0, self._list_view)
        self._stack.removeWidget(old_list)
        old_list.deleteLater()
        self._build_list_view()
        self._stack.setCurrentIndex(0)
