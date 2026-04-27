"""
Página de configuración de idioma.
Selector de idioma activo con preview.
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.i18n import get_language, set_language, t
from app.ui.styles import Colors, Fonts, Radius, Spacing, lbl_style

logger = logging.getLogger(__name__)


class LanguageCard(QFrame):
    """Card seleccionable para un idioma."""

    clicked = Signal()

    def __init__(self, flag: str, name: str, native: str, active: bool = False, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("langCard")
        self._set_active(active)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        layout.setSpacing(Spacing.XL)

        # Flag
        flag_label = QLabel(flag)
        flag_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 32))
        flag_label.setStyleSheet("background: transparent;")
        flag_label.setFixedWidth(48)
        layout.addWidget(flag_label)

        # Nombres
        col = QVBoxLayout()
        col.setSpacing(Spacing.XS)

        self._name_label = QLabel(name)
        self._name_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD)
        )
        color = Colors.ACCENT_PRIMARY if active else Colors.TEXT_PRIMARY
        self._name_label.setStyleSheet(lbl_style(color))
        col.addWidget(self._name_label)

        self._native_label = QLabel(native)
        self._native_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        self._native_label.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        col.addWidget(self._native_label)

        layout.addLayout(col, 1)

        # Badge activo
        self._badge = QLabel(t("languages.active_badge"))
        self._badge.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM, Fonts.WEIGHT_SEMIBOLD)
        )
        self._badge.setStyleSheet(f"""
            color: {Colors.SUCCESS};
            border: 1px solid {Colors.SUCCESS};
            border-radius: {Radius.SM}px;
            padding: 2px 8px;
        """)
        self._badge.setVisible(active)
        layout.addWidget(self._badge)

    def _set_active(self, active: bool):
        border = (
            f"2px solid {Colors.ACCENT_PRIMARY}" if active
            else f"1px solid {Colors.BORDER_SUBTLE}"
        )
        bg = Colors.SIDEBAR_ITEM_ACTIVE if active else Colors.BG_SURFACE
        self.setStyleSheet(f"""
            QFrame#langCard {{
                background-color: {bg};
                border: {border};
                border-radius: {Radius.LG}px;
            }}
            QFrame#langCard:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """)

    def set_active(self, active: bool):
        """Actualiza visualmente el estado activo."""
        self._set_active(active)
        color = Colors.ACCENT_PRIMARY if active else Colors.TEXT_PRIMARY
        self._name_label.setStyleSheet(lbl_style(color))
        self._badge.setText(t("languages.active_badge"))
        self._badge.setVisible(active)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class LanguagesPage(QWidget):
    """Página de selección de idioma con cambio en vivo."""

    language_changed = Signal(str)  # Emite el nuevo código de idioma

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._cards: dict[str, LanguageCard] = {}
        self._info_labels: list[QLabel] = []
        self._setup_ui()

    def on_page_shown(self):
        """Refresca labels al mostrar la página."""
        self._refresh_labels()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        self._title = QLabel(t("languages.title"))
        self._title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        self._title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(self._title)

        self._subtitle = QLabel(t("languages.subtitle"))
        self._subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        self._subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self._subtitle)

        layout.addSpacing(Spacing.MD)

        # Detectar idioma activo
        current_lang = get_language()

        # --- Cards de idioma ---
        self._cards["es"] = LanguageCard(
            "🇪🇸", t("languages.es_name"), t("languages.es_native"),
            active=(current_lang == "es"),
        )
        self._cards["es"].clicked.connect(lambda: self._switch_language("es"))
        layout.addWidget(self._cards["es"])

        self._cards["en"] = LanguageCard(
            "�🇸", t("languages.en_name"), t("languages.en_native"),
            active=(current_lang == "en"),
        )
        self._cards["en"].clicked.connect(lambda: self._switch_language("en"))
        layout.addWidget(self._cards["en"])

        # --- Info ---
        layout.addSpacing(Spacing.LG)

        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_frame.setStyleSheet(f"""
            QFrame#infoFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        info_layout.setSpacing(Spacing.SM)

        self._info_title = QLabel(f"ℹ️  {t('languages.info_title')}")
        self._info_title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_SEMIBOLD)
        )
        self._info_title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        info_layout.addWidget(self._info_title)

        for key in ("info_1", "info_2", "info_3", "info_4"):
            line = QLabel(f"• {t(f'languages.{key}')}")
            line.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
            line.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
            line.setWordWrap(True)
            info_layout.addWidget(line)
            self._info_labels.append(line)

        layout.addWidget(info_frame)
        layout.addStretch()

    def _switch_language(self, lang: str):
        """Cambia el idioma activo, persiste y emite señal."""
        if lang == get_language():
            return

        set_language(lang)

        # Persistir en config
        if self._bootstrap:
            config = self._bootstrap.get_config()
            if config:
                config.set("ui_language", lang)
                config.save()

        logger.info("Idioma cambiado a: %s", lang)

        # Actualizar cards
        for lid, card in self._cards.items():
            card.set_active(lid == lang)

        # Refrescar textos propios
        self._refresh_labels()

        # Emitir señal para que el shell refresque toda la UI
        self.language_changed.emit(lang)

    def _refresh_labels(self):
        """Actualiza textos de esta página al idioma activo."""
        self._title.setText(t("languages.title"))
        self._subtitle.setText(t("languages.subtitle"))
        self._info_title.setText(f"ℹ️  {t('languages.info_title')}")
        keys = ("info_1", "info_2", "info_3", "info_4")
        for label, key in zip(self._info_labels, keys, strict=False):
            label.setText(f"• {t(f'languages.{key}')}")
        for lid, card in self._cards.items():
            card.set_active(lid == get_language())
