"""
Diálogo para crear/editar escenas con pasos.
Editor completo: metadatos de escena + lista de pasos con tipo, config y window.
"""

import copy

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.core.actions.window_manager import get_monitors
from app.core.config.schemas import SCENE_STEP_TEMPLATE, WINDOW_POSITIONS
from app.i18n import t
from app.ui.styles import (
    Colors,
    Fonts,
    Radius,
    Spacing,
    get_button_primary_style,
    get_button_secondary_style,
)

STEP_TYPES = ["program", "url", "folder", "script", "delay"]

_INPUT_STYLE = f"""
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {Colors.BG_ELEVATED};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: {Radius.SM}px;
        padding: 4px {Spacing.SM}px;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_SM}px;
        min-height: 26px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border-color: {Colors.ACCENT_PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        selection-background-color: {Colors.SIDEBAR_ITEM_ACTIVE};
    }}
"""

_STEP_FRAME_STYLE = f"""
    QFrame#stepFrame {{
        background-color: {Colors.BG_ELEVATED};
        border: 1px solid {Colors.BORDER_SUBTLE};
        border-radius: {Radius.MD}px;
    }}
    QFrame#stepFrame:hover {{
        border-color: {Colors.BORDER_DEFAULT};
    }}
"""

_MONITORS_CACHE: list[dict] | None = None


def _get_monitors_cached() -> list[dict]:
    global _MONITORS_CACHE
    if _MONITORS_CACHE is None:
        _MONITORS_CACHE = get_monitors()
    return _MONITORS_CACHE


class StepWidget(QFrame):
    """Widget para un paso individual de la escena."""

    def __init__(self, step_data: dict, step_number: int, on_delete_cb=None, parent=None):
        super().__init__(parent)
        self._on_delete_cb = on_delete_cb
        self.setObjectName("stepFrame")
        self.setStyleSheet(_STEP_FRAME_STYLE)
        self._setup_ui(step_data, step_number)

    def _setup_ui(self, step: dict, num: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.setSpacing(Spacing.SM)

        # --- Fila 1: número + tipo + enabled + eliminar ---
        row1 = QHBoxLayout()
        row1.setSpacing(Spacing.SM)

        self._num_label = QLabel(f"#{num}")
        self._num_label.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM, Fonts.WEIGHT_BOLD)
        )
        self._num_label.setStyleSheet(f"color: {Colors.ACCENT_PRIMARY};")
        self._num_label.setFixedWidth(28)
        row1.addWidget(self._num_label)

        self._type_combo = QComboBox()
        self._type_combo.addItems(STEP_TYPES)
        self._type_combo.setStyleSheet(_INPUT_STYLE)
        self._type_combo.setFixedWidth(100)
        cur_type = step.get("type", "program")
        if cur_type in STEP_TYPES:
            self._type_combo.setCurrentText(cur_type)
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        row1.addWidget(self._type_combo)

        row1.addStretch()

        self._enabled_check = QCheckBox("Activo")
        self._enabled_check.setChecked(step.get("enabled", True))
        self._enabled_check.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SIZE_SM}px;"
        )
        row1.addWidget(self._enabled_check)

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(24, 24)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_MUTED};
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: #FF6B6B;
            }}
        """)
        del_btn.setToolTip("Eliminar paso")
        del_btn.clicked.connect(self._request_delete)
        row1.addWidget(del_btn)

        layout.addLayout(row1)

        # --- Fila 2: campos según tipo ---
        row2 = QHBoxLayout()
        row2.setSpacing(Spacing.SM)

        # Path (program, folder)
        self._path_input = QLineEdit(step.get("path") or "")
        self._path_input.setPlaceholderText("C:\\ruta\\programa.exe")
        self._path_input.setStyleSheet(_INPUT_STYLE)
        row2.addWidget(self._path_input)

        # URL
        self._url_input = QLineEdit(step.get("url") or "")
        self._url_input.setPlaceholderText("https://ejemplo.com")
        self._url_input.setStyleSheet(_INPUT_STYLE)
        row2.addWidget(self._url_input)

        # Shell
        self._shell_input = QLineEdit(step.get("shell") or step.get("command") or "")
        self._shell_input.setPlaceholderText("comando shell")
        self._shell_input.setStyleSheet(_INPUT_STYLE)
        row2.addWidget(self._shell_input)

        # Delay (ms)
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(100, 30000)
        self._delay_spin.setSingleStep(100)
        self._delay_spin.setSuffix(" ms")
        self._delay_spin.setValue(step.get("milliseconds") or 500)
        self._delay_spin.setStyleSheet(_INPUT_STYLE)
        self._delay_spin.setFixedWidth(120)
        row2.addWidget(self._delay_spin)

        layout.addLayout(row2)

        # --- Fila 3: window positioning (para tipos no-delay) ---
        row3 = QHBoxLayout()
        row3.setSpacing(Spacing.SM)

        self._window_check = QCheckBox("Posicionar")
        self._window_check.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SIZE_SM}px;"
        )
        window_cfg = step.get("window") or {}
        self._window_check.setChecked(bool(window_cfg))
        self._window_check.toggled.connect(self._on_window_toggled)
        row3.addWidget(self._window_check)

        self._monitor_combo = QComboBox()
        self._monitor_combo.setStyleSheet(_INPUT_STYLE)
        self._monitor_combo.setFixedWidth(180)
        monitors = _get_monitors_cached()
        if monitors:
            for m in monitors:
                tag = " (principal)" if m["primary"] else ""
                self._monitor_combo.addItem(
                    f"Monitor {m['index']}: {m['width']}x{m['height']}{tag}",
                    m["index"],
                )
        else:
            self._monitor_combo.addItem("Monitor 0", 0)
        cur_mon = window_cfg.get("monitor", 0)
        for i in range(self._monitor_combo.count()):
            if self._monitor_combo.itemData(i) == cur_mon:
                self._monitor_combo.setCurrentIndex(i)
                break
        row3.addWidget(self._monitor_combo)

        self._position_combo = QComboBox()
        self._position_combo.setStyleSheet(_INPUT_STYLE)
        self._position_combo.setFixedWidth(130)
        for pos in WINDOW_POSITIONS:
            self._position_combo.addItem(pos)
        cur_pos = window_cfg.get("position", "maximized")
        if cur_pos in WINDOW_POSITIONS:
            self._position_combo.setCurrentText(cur_pos)
        row3.addWidget(self._position_combo)

        row3.addStretch()
        layout.addLayout(row3)

        # Mostrar/ocultar según tipo
        self._on_type_changed(self._type_combo.currentText())
        self._on_window_toggled(self._window_check.isChecked())

    def _on_type_changed(self, step_type: str):
        is_delay = step_type == "delay"
        show_path = step_type in ("program", "folder")
        show_url = step_type == "url"
        show_shell = step_type == "script"

        self._path_input.setVisible(show_path)
        self._url_input.setVisible(show_url)
        self._shell_input.setVisible(show_shell)
        self._delay_spin.setVisible(is_delay)

        self._window_check.setVisible(not is_delay)
        self._monitor_combo.setVisible(not is_delay and self._window_check.isChecked())
        self._position_combo.setVisible(not is_delay and self._window_check.isChecked())

    def _on_window_toggled(self, checked: bool):
        is_delay = self._type_combo.currentText() == "delay"
        self._monitor_combo.setVisible(checked and not is_delay)
        self._position_combo.setVisible(checked and not is_delay)

    def set_number(self, num: int):
        """Actualiza el número mostrado del paso."""
        self._num_label.setText(f"#{num}")

    def _request_delete(self):
        self.setProperty("_deleted", True)
        self.setVisible(False)
        if self._on_delete_cb:
            self._on_delete_cb()

    def is_deleted(self) -> bool:
        return self.property("_deleted") is True

    def get_step_data(self) -> dict:
        """Retorna los datos del paso."""
        step = copy.deepcopy(SCENE_STEP_TEMPLATE)
        step["type"] = self._type_combo.currentText()
        step["enabled"] = self._enabled_check.isChecked()

        if step["type"] == "delay":
            step["milliseconds"] = self._delay_spin.value()
            step["window"] = None
        else:
            step["path"] = self._path_input.text().strip() or None
            step["url"] = self._url_input.text().strip() or None
            step["shell"] = self._shell_input.text().strip() or None
            step["milliseconds"] = None

            if self._window_check.isChecked():
                step["window"] = {
                    "monitor": self._monitor_combo.currentData(),
                    "position": self._position_combo.currentText(),
                }
            else:
                step["window"] = None

        return step


class SceneDialog(QDialog):
    """Diálogo modal para crear o editar una escena con pasos."""

    def __init__(self, scene: dict | None = None, parent=None):
        super().__init__(parent)
        self._scene = scene or {}
        self._is_edit = bool(scene and scene.get("id"))
        self._result_data: dict | None = None
        self._step_widgets: list[StepWidget] = []

        win_title = t("scene_dialog.title_edit") if self._is_edit else t("scene_dialog.title_new")
        self.setWindowTitle(win_title)
        self.setFixedSize(620, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_BASE};
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.MD)

        # Título
        dlg_title = t("scene_dialog.title_edit") if self._is_edit else t("scene_dialog.title_new")
        title = QLabel(dlg_title)
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)

        # --- Metadatos ---
        form = QFormLayout()
        form.setSpacing(Spacing.SM)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        label_style = f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SIZE_SM}px;"

        self._id_input = QLineEdit(self._scene.get("id", ""))
        self._id_input.setPlaceholderText(t("scene_dialog.id"))
        self._id_input.setStyleSheet(_INPUT_STYLE)
        if self._is_edit:
            self._id_input.setReadOnly(True)
            self._id_input.setStyleSheet(
                _INPUT_STYLE + f"QLineEdit {{ color: {Colors.TEXT_MUTED}; }}"
            )
        id_label = QLabel(f"{t('scene_dialog.id')}:")
        id_label.setStyleSheet(label_style)
        form.addRow(id_label, self._id_input)

        self._name_input = QLineEdit(self._scene.get("name", ""))
        self._name_input.setPlaceholderText(t("scene_dialog.name"))
        self._name_input.setStyleSheet(_INPUT_STYLE)
        name_label = QLabel(f"{t('scene_dialog.name')}:")
        name_label.setStyleSheet(label_style)
        form.addRow(name_label, self._name_input)

        aliases = ", ".join(self._scene.get("aliases", []))
        self._aliases_input = QLineEdit(aliases)
        self._aliases_input.setPlaceholderText(t("scene_dialog.aliases"))
        self._aliases_input.setStyleSheet(_INPUT_STYLE)
        aliases_label = QLabel(f"{t('scene_dialog.aliases')}:")
        aliases_label.setStyleSheet(label_style)
        form.addRow(aliases_label, self._aliases_input)

        layout.addLayout(form)

        # --- Pasos ---
        steps_header = QHBoxLayout()
        steps_title = QLabel(t("scene_dialog.steps"))
        steps_title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_SEMIBOLD)
        )
        steps_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        steps_header.addWidget(steps_title)
        steps_header.addStretch()

        add_step_btn = QPushButton(t("scene_dialog.add_step"))
        add_step_btn.setStyleSheet(get_button_secondary_style())
        add_step_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_step_btn.setMinimumWidth(100)
        add_step_btn.clicked.connect(self._add_empty_step)
        steps_header.addWidget(add_step_btn)

        add_delay_btn = QPushButton(f"+ {t('scene_dialog.add_delay')}")
        add_delay_btn.setStyleSheet(get_button_secondary_style())
        add_delay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_delay_btn.setMinimumWidth(100)
        add_delay_btn.clicked.connect(self._add_delay_step)
        steps_header.addWidget(add_delay_btn)

        layout.addLayout(steps_header)

        # Scroll area para pasos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.SM}px;
                background: transparent;
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: {Colors.BORDER_DEFAULT};
                border-radius: 3px;
            }}
        """)
        self._steps_container = QWidget()
        self._steps_layout = QVBoxLayout(self._steps_container)
        self._steps_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        self._steps_layout.setSpacing(Spacing.SM)
        self._steps_layout.addStretch()
        scroll.setWidget(self._steps_container)
        layout.addWidget(scroll, 1)

        # Cargar pasos existentes
        for step in self._scene.get("steps", []):
            self._add_step_widget(step)

        # --- Botones ---
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton(t("scene_dialog.cancel"))
        cancel_btn.setStyleSheet(get_button_secondary_style())
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton(t("scene_dialog.save"))
        save_btn.setStyleSheet(get_button_primary_style())
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _add_step_widget(self, step_data: dict):
        visible_count = sum(1 for sw in self._step_widgets if not sw.is_deleted())
        num = visible_count + 1
        widget = StepWidget(step_data, num, on_delete_cb=self._renumber_steps)
        self._step_widgets.append(widget)
        # Insertar antes del stretch
        self._steps_layout.insertWidget(self._steps_layout.count() - 1, widget)

    def _renumber_steps(self):
        """Renumera los pasos visibles secuencialmente."""
        num = 1
        for sw in self._step_widgets:
            if not sw.is_deleted():
                sw.set_number(num)
                num += 1

    def _add_empty_step(self):
        step = copy.deepcopy(SCENE_STEP_TEMPLATE)
        step["type"] = "program"
        self._add_step_widget(step)

    def _add_delay_step(self):
        step = copy.deepcopy(SCENE_STEP_TEMPLATE)
        step["type"] = "delay"
        step["milliseconds"] = 500
        self._add_step_widget(step)

    def _on_save(self):
        scene_id = self._id_input.text().strip()
        name = self._name_input.text().strip()

        if not scene_id:
            QMessageBox.warning(self, t("scene_dialog.error"), t("scene_dialog.err_id_required"))
            return
        if " " in scene_id:
            QMessageBox.warning(self, t("scene_dialog.error"), t("scene_dialog.err_id_spaces"))
            return
        if not name:
            QMessageBox.warning(self, t("scene_dialog.error"), t("scene_dialog.err_name_required"))
            return

        aliases_raw = self._aliases_input.text().strip()
        aliases = [a.strip() for a in aliases_raw.split(",") if a.strip()] if aliases_raw else []

        steps = []
        for sw in self._step_widgets:
            if not sw.is_deleted():
                steps.append(sw.get_step_data())

        if not steps:
            QMessageBox.warning(self, t("scene_dialog.error"), t("scene_dialog.err_no_steps"))
            return

        self._result_data = {
            "id": scene_id,
            "name": name,
            "aliases": aliases,
            "steps": steps,
            "enabled": True,
        }
        self.accept()

    def get_data(self) -> dict | None:
        """Retorna los datos de la escena si se guardó, None si se canceló."""
        return self._result_data
