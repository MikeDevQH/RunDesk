"""
Diálogo para crear/editar comandos.
Formulario completo con todos los campos editables.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.core.actions.window_manager import get_monitors
from app.core.config.schemas import WINDOW_POSITIONS
from app.i18n import t
from app.ui.styles import (
    Colors,
    Fonts,
    Radius,
    Spacing,
    get_button_primary_style,
    get_button_secondary_style,
)

COMMAND_TYPES = ["program", "folder", "url", "system", "shortcut", "script"]
CATEGORIES = ["system", "productivity", "audio", "screen", "launcher", "languages", "custom"]

_INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {Colors.BG_ELEVATED};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: {Radius.SM}px;
        padding: 6px {Spacing.MD}px;
        color: {Colors.TEXT_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
        min-height: 30px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border-color: {Colors.ACCENT_PRIMARY};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        selection-background-color: {Colors.SIDEBAR_ITEM_ACTIVE};
    }}
"""


class CommandDialog(QDialog):
    """Diálogo modal para crear o editar un comando."""

    def __init__(self, command: dict | None = None, parent=None):
        super().__init__(parent)
        self._command = command or {}
        self._is_edit = bool(command and command.get("id"))
        self._result_data: dict | None = None

        win_title = t("cmd_dialog.title_edit") if self._is_edit else t("cmd_dialog.title_new")
        self.setWindowTitle(win_title)
        self.setFixedSize(540, 620)
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
        layout.setSpacing(Spacing.LG)

        # Título
        title = QLabel(t("cmd_dialog.title_edit") if self._is_edit else t("cmd_dialog.title_new"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)

        # Formulario
        form = QFormLayout()
        form.setSpacing(Spacing.MD)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        label_style = f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SIZE_SM}px;"

        # ID
        self._id_input = QLineEdit(self._command.get("id", ""))
        self._id_input.setPlaceholderText(t("cmd_dialog.id_hint"))
        self._id_input.setStyleSheet(_INPUT_STYLE)
        if self._is_edit:
            self._id_input.setReadOnly(True)
            self._id_input.setStyleSheet(
                _INPUT_STYLE + f"QLineEdit {{ color: {Colors.TEXT_MUTED}; }}"
            )
        id_label = QLabel(f"{t('cmd_dialog.id')}:")
        id_label.setStyleSheet(label_style)
        form.addRow(id_label, self._id_input)

        # Nombre
        self._name_input = QLineEdit(self._command.get("name", ""))
        self._name_input.setPlaceholderText(t("cmd_dialog.name_hint"))
        self._name_input.setStyleSheet(_INPUT_STYLE)
        name_label = QLabel(f"{t('cmd_dialog.name')}:")
        name_label.setStyleSheet(label_style)
        form.addRow(name_label, self._name_input)

        # Aliases
        aliases = ", ".join(self._command.get("aliases", []))
        self._aliases_input = QLineEdit(aliases)
        self._aliases_input.setPlaceholderText(t("cmd_dialog.aliases_hint"))
        self._aliases_input.setStyleSheet(_INPUT_STYLE)
        aliases_label = QLabel(f"{t('cmd_dialog.aliases')}:")
        aliases_label.setStyleSheet(label_style)
        form.addRow(aliases_label, self._aliases_input)

        # Tipo
        self._type_combo = QComboBox()
        self._type_combo.addItems(COMMAND_TYPES)
        self._type_combo.setStyleSheet(_INPUT_STYLE)
        current_type = self._command.get("type", "program")
        if current_type in COMMAND_TYPES:
            self._type_combo.setCurrentText(current_type)
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        type_label = QLabel(f"{t('cmd_dialog.type')}:")
        type_label.setStyleSheet(label_style)
        form.addRow(type_label, self._type_combo)

        # Categoría
        self._category_combo = QComboBox()
        self._category_combo.addItems(CATEGORIES)
        self._category_combo.setStyleSheet(_INPUT_STYLE)
        current_cat = self._command.get("category", "custom")
        if current_cat in CATEGORIES:
            self._category_combo.setCurrentText(current_cat)
        cat_label = QLabel(f"{t('cmd_dialog.category')}:")
        cat_label.setStyleSheet(label_style)
        form.addRow(cat_label, self._category_combo)

        # Path (para program, folder)
        self._path_input = QLineEdit(self._command.get("path") or "")
        self._path_input.setPlaceholderText("C:\\ruta\\al\\programa.exe")
        self._path_input.setStyleSheet(_INPUT_STYLE)
        path_label = QLabel(f"{t('cmd_dialog.path')}:")
        path_label.setStyleSheet(label_style)
        form.addRow(path_label, self._path_input)

        # URL (para url)
        self._url_input = QLineEdit(self._command.get("url") or "")
        self._url_input.setPlaceholderText("https://ejemplo.com")
        self._url_input.setStyleSheet(_INPUT_STYLE)
        url_label = QLabel(f"{t('cmd_dialog.url')}:")
        url_label.setStyleSheet(label_style)
        form.addRow(url_label, self._url_input)

        # Shell (para script)
        self._shell_input = QLineEdit(self._command.get("shell") or "")
        self._shell_input.setPlaceholderText("comando a ejecutar en shell")
        self._shell_input.setStyleSheet(_INPUT_STYLE)
        shell_label = QLabel(f"{t('cmd_dialog.shell')}:")
        shell_label.setStyleSheet(label_style)
        form.addRow(shell_label, self._shell_input)

        # --- Sección Window (monitor + posición) ---
        window_cfg = self._command.get("window") or {}

        self._window_check = QCheckBox(t("cmd_dialog.window_position"))
        self._window_check.setChecked(bool(window_cfg))
        self._window_check.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Fonts.SIZE_SM}px;"
        )
        self._window_check.toggled.connect(self._on_window_toggled)
        form.addRow(QLabel(""), self._window_check)

        # Monitor
        self._monitor_combo = QComboBox()
        self._monitor_combo.setStyleSheet(_INPUT_STYLE)
        monitors = get_monitors()
        if monitors:
            for m in monitors:
                tag = " (principal)" if m["primary"] else ""
                self._monitor_combo.addItem(
                    f"Monitor {m['index']}: {m['width']}x{m['height']}{tag}",
                    m["index"],
                )
        else:
            self._monitor_combo.addItem("Monitor 0 (por defecto)", 0)
        cur_mon = window_cfg.get("monitor", 0)
        for i in range(self._monitor_combo.count()):
            if self._monitor_combo.itemData(i) == cur_mon:
                self._monitor_combo.setCurrentIndex(i)
                break
        monitor_label = QLabel(f"{t('cmd_dialog.monitor')}:")
        monitor_label.setStyleSheet(label_style)
        form.addRow(monitor_label, self._monitor_combo)

        # Posición
        self._position_combo = QComboBox()
        self._position_combo.setStyleSheet(_INPUT_STYLE)
        for pos in WINDOW_POSITIONS:
            self._position_combo.addItem(pos)
        cur_pos = window_cfg.get("position", "maximized")
        if cur_pos in WINDOW_POSITIONS:
            self._position_combo.setCurrentText(cur_pos)
        position_label = QLabel(f"{t('cmd_dialog.position')}:")
        position_label.setStyleSheet(label_style)
        form.addRow(position_label, self._position_combo)

        self._monitor_label = monitor_label
        self._position_label = position_label

        layout.addLayout(form)

        # Mostrar/ocultar campos según tipo
        self._path_label = path_label
        self._url_label = url_label
        self._shell_label = shell_label
        self._on_type_changed(self._type_combo.currentText())
        self._on_window_toggled(self._window_check.isChecked())

        layout.addStretch()

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton(t("cmd_dialog.cancel"))
        cancel_btn.setStyleSheet(get_button_secondary_style())
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton(t("cmd_dialog.save"))
        save_btn.setStyleSheet(get_button_primary_style())
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

    def _on_type_changed(self, cmd_type: str):
        """Muestra/oculta campos según el tipo de comando."""
        show_path = cmd_type in ("program", "folder")
        show_url = cmd_type == "url"
        show_shell = cmd_type == "script"

        self._path_input.setVisible(show_path)
        self._path_label.setVisible(show_path)
        self._url_input.setVisible(show_url)
        self._url_label.setVisible(show_url)
        self._shell_input.setVisible(show_shell)
        self._shell_label.setVisible(show_shell)

    def _on_window_toggled(self, checked: bool):
        """Muestra/oculta selector de monitor y posición."""
        self._monitor_combo.setVisible(checked)
        self._monitor_label.setVisible(checked)
        self._position_combo.setVisible(checked)
        self._position_label.setVisible(checked)

    def _on_save(self):
        """Valida y guarda los datos."""
        cmd_id = self._id_input.text().strip()
        name = self._name_input.text().strip()

        if not cmd_id:
            QMessageBox.warning(self, t("cmd_dialog.error"), t("cmd_dialog.err_id_required"))
            return
        if " " in cmd_id:
            QMessageBox.warning(self, t("cmd_dialog.error"), t("cmd_dialog.err_id_spaces"))
            return
        if not name:
            QMessageBox.warning(self, t("cmd_dialog.error"), t("cmd_dialog.err_name_required"))
            return

        aliases_raw = self._aliases_input.text().strip()
        aliases = [a.strip() for a in aliases_raw.split(",") if a.strip()] if aliases_raw else []

        # Construir window config si está habilitado
        window_cfg = None
        if self._window_check.isChecked():
            window_cfg = {
                "monitor": self._monitor_combo.currentData(),
                "position": self._position_combo.currentText(),
            }

        self._result_data = {
            "id": cmd_id,
            "name": name,
            "aliases": aliases,
            "type": self._type_combo.currentText(),
            "category": self._category_combo.currentText(),
            "path": self._path_input.text().strip() or None,
            "url": self._url_input.text().strip() or None,
            "shell": self._shell_input.text().strip() or None,
            "window": window_cfg,
        }
        self.accept()

    def get_data(self) -> dict | None:
        """Retorna los datos del formulario si se guardó, None si se canceló."""
        return self._result_data
