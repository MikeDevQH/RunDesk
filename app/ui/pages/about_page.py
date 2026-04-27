"""
Página "Acerca de" — información del proyecto, licencia, créditos y links.
"""

import os
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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

APP_VERSION = "0.1.0"


class AboutPage(QWidget):
    """Página de información, licencia y créditos."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._setup_ui()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
        )
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL
        )
        layout.setSpacing(Spacing.XL)

        # --- Header with logo ---
        header_row = QHBoxLayout()
        header_row.setSpacing(Spacing.LG)

        icon_path = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))
                )
            ),
            "assets",
            "icon.png",
        )
        logo = QLabel()
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(
                64,
                64,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
        logo.setFixedSize(64, 64)
        logo.setStyleSheet("background: transparent; border: none;")
        header_row.addWidget(logo)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel(t("about.title"))
        title.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_HERO,
                Fonts.WEIGHT_BOLD,
            )
        )
        title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        title_col.addWidget(title)

        subtitle = QLabel(t("about.subtitle"))
        subtitle.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG)
        )
        subtitle.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        title_col.addWidget(subtitle)

        version = QLabel(f"{t('about.version')} {APP_VERSION}")
        version.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
        )
        version.setStyleSheet(lbl_style(Colors.ACCENT_PRIMARY))
        title_col.addWidget(version)

        header_row.addLayout(title_col, 1)
        layout.addLayout(header_row)

        # --- Description ---
        desc_section = self._make_section()
        desc_lay = QVBoxLayout(desc_section)
        desc_lay.setContentsMargins(
            Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG
        )
        desc_lay.setSpacing(Spacing.MD)

        desc = QLabel(t("about.description"))
        desc.setWordWrap(True)
        desc.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
        )
        desc.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        desc_lay.addWidget(desc)

        layout.addWidget(desc_section)

        # --- Features ---
        feat_section = self._make_section()
        feat_lay = QVBoxLayout(feat_section)
        feat_lay.setContentsMargins(
            Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG
        )
        feat_lay.setSpacing(Spacing.SM)

        feat_title = QLabel(t("about.features_title"))
        feat_title.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_LG,
                Fonts.WEIGHT_SEMIBOLD,
            )
        )
        feat_title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        feat_lay.addWidget(feat_title)

        for i in range(1, 7):
            feat = QLabel(f"  •  {t(f'about.feat_{i}')}")
            feat.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
            )
            feat.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
            feat.setWordWrap(True)
            feat_lay.addWidget(feat)

        layout.addWidget(feat_section)

        # --- Open Source + License ---
        license_section = self._make_section()
        lic_lay = QVBoxLayout(license_section)
        lic_lay.setContentsMargins(
            Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG
        )
        lic_lay.setSpacing(Spacing.MD)

        oss_title = QLabel(t("about.open_source_title"))
        oss_title.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_LG,
                Fonts.WEIGHT_SEMIBOLD,
            )
        )
        oss_title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        lic_lay.addWidget(oss_title)

        oss_text = QLabel(t("about.open_source_text"))
        oss_text.setWordWrap(True)
        oss_text.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
        )
        oss_text.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        lic_lay.addWidget(oss_text)

        # License terms
        lic_title = QLabel(t("about.license_title"))
        lic_title.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_MD,
                Fonts.WEIGHT_SEMIBOLD,
            )
        )
        lic_title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        lic_lay.addWidget(lic_title)

        lic_text = QLabel(t("about.license_text"))
        lic_text.setWordWrap(True)
        lic_text.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
        )
        lic_text.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        lic_text.setTextFormat(Qt.TextFormat.PlainText)
        lic_lay.addWidget(lic_text)

        layout.addWidget(license_section)

        # --- Tech + Credits ---
        credits_section = self._make_section()
        cred_lay = QVBoxLayout(credits_section)
        cred_lay.setContentsMargins(
            Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG
        )
        cred_lay.setSpacing(Spacing.MD)

        tech_title = QLabel(t("about.tech_title"))
        tech_title.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_LG,
                Fonts.WEIGHT_SEMIBOLD,
            )
        )
        tech_title.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        cred_lay.addWidget(tech_title)

        tech = QLabel(t("about.tech_text"))
        tech.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
        )
        tech.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        cred_lay.addWidget(tech)

        # Author
        author_row = QHBoxLayout()
        author_lbl = QLabel(f"{t('about.author')}:")
        author_lbl.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_MD,
                Fonts.WEIGHT_MEDIUM,
            )
        )
        author_lbl.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        author_row.addWidget(author_lbl)

        author_val = QLabel(t("about.author_name"))
        author_val.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD)
        )
        author_val.setStyleSheet(lbl_style(Colors.ACCENT_PRIMARY))
        author_row.addWidget(author_val)
        author_row.addStretch()
        cred_lay.addLayout(author_row)

        layout.addWidget(credits_section)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(Spacing.MD)

        github_btn = QPushButton(f"  {t('about.github')}")
        github_btn.setStyleSheet(get_button_primary_style())
        github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        github_btn.clicked.connect(self._open_github)
        btn_row.addWidget(github_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # --- Copyright ---
        copy_lbl = QLabel(t("about.copyright"))
        copy_lbl.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XS)
        )
        copy_lbl.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        copy_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copy_lbl)

        layout.addStretch()

    @staticmethod
    def _make_section() -> QFrame:
        section = QFrame()
        section.setObjectName("aboutSection")
        section.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        section.setStyleSheet(f"""
            QFrame#aboutSection {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
            QFrame#aboutSection QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        return section

    @staticmethod
    def _open_github():
        url = t("about.github_url")
        webbrowser.open(url)
