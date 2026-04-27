"""
Página de gestión de escenas/rutinas.
Lista de escenas con CRUD completo, plantillas y acciones.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.components.scene_dialog import SceneDialog
from app.ui.styles import (
    Colors,
    Fonts,
    Radius,
    Spacing,
    get_button_primary_style,
    lbl_style,
)

logger = logging.getLogger(__name__)

_ACTION_BTN = f"""
    QPushButton {{
        background: transparent;
        color: {Colors.TEXT_MUTED};
        border: none;
        padding: 2px 6px;
        font-size: {Fonts.SIZE_SM}px;
    }}
    QPushButton:hover {{
        color: {Colors.ACCENT_PRIMARY};
    }}
"""

_DEL_BTN = f"""
    QPushButton {{
        background: transparent;
        color: {Colors.TEXT_MUTED};
        border: none;
        padding: 2px 6px;
        font-size: {Fonts.SIZE_SM}px;
    }}
    QPushButton:hover {{
        color: #FF6B6B;
    }}
"""


class SceneCard(QFrame):
    """Card visual para representar una escena con acciones."""

    def __init__(self, scene: dict, parent=None):
        super().__init__(parent)
        self.scene_id = scene.get("id", "")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(90)
        self.setObjectName("sceneCard")
        self.setStyleSheet(f"""
            QFrame#sceneCard {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
            QFrame#sceneCard:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.MD, Spacing.XL, Spacing.MD)
        layout.setSpacing(Spacing.LG)

        # Icono de estado
        enabled = scene.get("enabled", True)
        status_icon = QLabel("🟢" if enabled else "🔴")
        status_icon.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL))
        status_icon.setStyleSheet("background: transparent;")
        status_icon.setFixedWidth(32)
        layout.addWidget(status_icon)

        # Info
        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        name_label = QLabel(scene.get("name", ""))
        name_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG, Fonts.WEIGHT_SEMIBOLD)
        )
        name_label.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        info_col.addWidget(name_label)

        aliases = scene.get("aliases", [])
        alias_text = ", ".join(aliases) if aliases else "—"
        steps_count = len(scene.get("steps", []))
        steps_str = t("scenes.steps_count").replace("{n}", str(steps_count))
        meta_label = QLabel(f"{alias_text}  ·  {steps_str}")
        meta_label.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        meta_label.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
        info_col.addWidget(meta_label)

        layout.addLayout(info_col, 1)

        # Botones de acción
        btn_col = QVBoxLayout()
        btn_col.setSpacing(2)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self.edit_btn = QPushButton(t("scenes.edit"))
        self.edit_btn.setStyleSheet(_ACTION_BTN)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.edit_btn)

        toggle_text = t("scenes.toggle_disable") if enabled else t("scenes.toggle_enable")
        self.toggle_btn = QPushButton(toggle_text)
        self.toggle_btn.setStyleSheet(_ACTION_BTN)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.toggle_btn)

        self.del_btn = QPushButton(t("scenes.delete"))
        self.del_btn.setStyleSheet(_DEL_BTN)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.del_btn)

        btn_col.addLayout(btn_row)
        layout.addLayout(btn_col)


class ScenesPage(QWidget):
    """Página de gestión de escenas/rutinas con CRUD completo."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._setup_ui()

    def on_page_shown(self):
        """Llamado por el shell al navegar a esta página."""
        self._refresh_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        header_row = QHBoxLayout()
        header_col = QVBoxLayout()

        title = QLabel(t("scenes.title"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header_col.addWidget(title)

        subtitle = QLabel(t("scenes.subtitle"))
        subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        header_col.addWidget(subtitle)

        header_row.addLayout(header_col)
        header_row.addStretch()

        add_btn = QPushButton(f"+ {t('scenes.add')}")
        add_btn.setStyleSheet(get_button_primary_style())
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._on_add_scene)
        header_row.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header_row)

        # --- Scroll para contenido dinámico ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(Spacing.MD)
        scroll.setWidget(self._content_widget)
        layout.addWidget(scroll, 1)

        self._refresh_list()

    def _refresh_list(self):
        """Reconstruye la lista de escenas y plantillas."""
        # Limpiar
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        scenes_list = []
        if self._bootstrap:
            store = self._bootstrap.get_scenes()
            if store:
                scenes_list = store.get_all()

        # --- Escenas existentes ---
        if scenes_list:
            for scene in scenes_list:
                card = SceneCard(scene)
                card.edit_btn.clicked.connect(
                    lambda _checked, sid=scene["id"]: self._on_edit_scene(sid)
                )
                card.toggle_btn.clicked.connect(
                    lambda _checked, sid=scene["id"]: self._on_toggle_scene(sid)
                )
                card.del_btn.clicked.connect(
                    lambda _checked, sid=scene["id"]: self._on_delete_scene(sid)
                )
                self._content_layout.addWidget(card)
        else:
            empty = QFrame()
            empty.setFixedHeight(100)
            empty.setObjectName("emptyState")
            empty.setStyleSheet(f"""
                QFrame#emptyState {{
                    background-color: {Colors.BG_SURFACE};
                    border: 1px solid {Colors.BORDER_SUBTLE};
                    border-radius: {Radius.LG}px;
                }}
            """)
            empty_layout = QVBoxLayout(empty)
            empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_icon = QLabel("🎬")
            empty_icon.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), 24))
            empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_icon.setStyleSheet("background: transparent;")
            empty_layout.addWidget(empty_icon)
            empty_text = QLabel(t("scenes.empty"))
            empty_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_text.setStyleSheet(lbl_style(Colors.TEXT_MUTED))
            empty_layout.addWidget(empty_text)
            self._content_layout.addWidget(empty)

        self._content_layout.addStretch()

    # --- Acciones ---

    def _on_add_scene(self):
        dialog = SceneDialog(parent=self)
        if dialog.exec() == SceneDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data and self._bootstrap:
                store = self._bootstrap.get_scenes()
                ok, msg = store.add(data)
                if ok:
                    self._rebuild_alias_index()
                    self._refresh_list()
                else:
                    QMessageBox.warning(self, "Error", msg)

    def _on_edit_scene(self, scene_id: str):
        if not self._bootstrap:
            return
        store = self._bootstrap.get_scenes()
        scene = store.get_by_id(scene_id)
        if not scene:
            return

        dialog = SceneDialog(scene=scene, parent=self)
        if dialog.exec() == SceneDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                ok, msg = store.update(scene_id, data)
                if ok:
                    self._rebuild_alias_index()
                    self._refresh_list()
                else:
                    QMessageBox.warning(self, "Error", msg)

    def _on_toggle_scene(self, scene_id: str):
        if not self._bootstrap:
            return
        store = self._bootstrap.get_scenes()
        scene = store.get_by_id(scene_id)
        if not scene:
            return
        new_enabled = not scene.get("enabled", True)
        store.update(scene_id, {"enabled": new_enabled})
        self._rebuild_alias_index()
        self._refresh_list()

    def _on_delete_scene(self, scene_id: str):
        reply = QMessageBox.question(
            self,
            t("scenes.confirm_title"),
            t("scenes.confirm_delete").replace("{name}", scene_id),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes and self._bootstrap:
            store = self._bootstrap.get_scenes()
            ok, msg = store.delete(scene_id)
            if ok:
                self._rebuild_alias_index()
                self._refresh_list()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _rebuild_alias_index(self):
        """Reconstruye el índice del parser tras cambios en escenas."""
        if self._bootstrap:
            self._bootstrap.rebuild_parser_index()
