"""
Página de gestión de comandos.
Lista completa con filtros, estados, acciones CRUD y diálogo de edición.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.i18n import t
from app.ui.components.command_dialog import CommandDialog
from app.ui.styles import (
    Colors,
    Fonts,
    Radius,
    Spacing,
    get_button_primary_style,
    get_button_secondary_style,
    lbl_style,
)

logger = logging.getLogger(__name__)


class CommandsPage(QWidget):
    """Página de catálogo de comandos con tabla interactiva y CRUD completo."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._current_filter = "all"  # "all", "system", "custom"
        self._all_cmds: list[dict] = []
        self._setup_ui()
        self._refresh()

    # === UI ===

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        header_row = QHBoxLayout()
        header_col = QVBoxLayout()

        title = QLabel(t("commands.title"))
        title.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_HERO, Fonts.WEIGHT_BOLD)
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header_col.addWidget(title)

        subtitle = QLabel(t("commands.subtitle"))
        subtitle.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG))
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        header_col.addWidget(subtitle)

        header_row.addLayout(header_col)
        header_row.addStretch()

        add_btn = QPushButton(f"+ {t('commands.add')}")
        add_btn.setStyleSheet(get_button_primary_style())
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._on_add)
        header_row.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header_row)

        # --- Stats bar ---
        self._stats_frame = QFrame()
        self._stats_frame.setFixedHeight(50)
        self._stats_frame.setObjectName("statsFrame")
        self._stats_frame.setStyleSheet(f"""
            QFrame#statsFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.MD}px;
            }}
        """)
        self._stats_layout = QHBoxLayout(self._stats_frame)
        self._stats_layout.setContentsMargins(Spacing.XL, 0, Spacing.XL, 0)
        layout.addWidget(self._stats_frame)

        # --- Search + filter ---
        filter_row = QHBoxLayout()
        filter_row.setSpacing(Spacing.MD)

        self._search = QLineEdit()
        self._search.setPlaceholderText(t("commands.search"))
        self._search.setFixedHeight(38)
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {Radius.MD}px;
                padding: 0 {Spacing.MD}px;
                color: {Colors.TEXT_PRIMARY};
                font-size: {Fonts.SIZE_MD}px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """)
        self._search.textChanged.connect(self._apply_filters)
        filter_row.addWidget(self._search)

        self._filter_buttons: dict[str, QPushButton] = {}
        for key, label in [
            ("all", t("commands.all")),
            ("system", t("commands.system")),
            ("custom", t("commands.custom")),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(get_button_secondary_style())
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumWidth(90)
            btn.clicked.connect(lambda checked, k=key: self._set_filter(k))
            filter_row.addWidget(btn)
            self._filter_buttons[key] = btn

        layout.addLayout(filter_row)

        # --- Action buttons row ---
        action_row = QHBoxLayout()
        action_row.setSpacing(Spacing.SM)

        for label, slot, tooltip in [
            (t("commands.edit"), self._on_edit, t("commands.edit_tip")),
            (t("commands.duplicate"), self._on_duplicate, t("commands.duplicate_tip")),
            (t("commands.toggle"), self._on_toggle, t("commands.toggle_tip")),
            (t("commands.delete"), self._on_delete, t("commands.delete_tip")),
            (t("commands.test"), self._on_test, t("commands.test_tip")),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(get_button_secondary_style())
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.clicked.connect(slot)
            action_row.addWidget(btn)

        action_row.addStretch()
        layout.addLayout(action_row)

        # --- Tabla de comandos ---
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels([
            t("commands.col_status"), t("commands.col_name"), t("commands.col_aliases"),
            t("commands.col_category"), t("commands.col_type"), t("commands.locked"),
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 60)
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(5, 90)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.setShowGrid(False)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: {Spacing.SM}px {Spacing.MD}px;
                border-bottom: 1px solid {Colors.BORDER_SUBTLE};
                color: {Colors.TEXT_PRIMARY};
            }}
            QTableWidget::item:selected {{
                background-color: {Colors.SIDEBAR_ITEM_ACTIVE};
                color: {Colors.TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: {Colors.BG_ELEVATED};
                color: {Colors.TEXT_SECONDARY};
                font-size: {Fonts.SIZE_SM}px;
                font-weight: {Fonts.WEIGHT_SEMIBOLD};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border: none;
                border-bottom: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        self._table.setMinimumHeight(300)
        self._table.doubleClicked.connect(self._on_edit)
        layout.addWidget(self._table)

        layout.addStretch()

    # === Data ===

    def _get_store(self):
        if self._bootstrap:
            return self._bootstrap.get_commands()
        return None

    def _refresh(self):
        """Recarga datos del store y refresca tabla, stats e índice del parser."""
        store = self._get_store()
        self._all_cmds = store.get_all() if store else []
        self._update_stats()
        self._populate_table()
        self._update_filter_style()
        # Reconstruir índice del parser para que el overlay vea los cambios
        if self._bootstrap:
            self._bootstrap.rebuild_parser_index()

    def _update_stats(self):
        """Actualiza la barra de estadísticas."""
        # Limpiar
        while self._stats_layout.count():
            item = self._stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total = len(self._all_cmds)
        enabled = sum(1 for c in self._all_cmds if c.get("enabled", True))
        default_count = sum(1 for c in self._all_cmds if c.get("default"))
        custom_count = total - default_count

        for label, value, color in [
            ("Total", str(total), Colors.TEXT_PRIMARY),
            (t("commands.enabled"), str(enabled), Colors.SUCCESS),
            (t("commands.system"), str(default_count), Colors.ACCENT_PRIMARY),
            (t("commands.custom"), str(custom_count), Colors.WARNING),
        ]:
            stat = QLabel(f"{label}: ")
            stat.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
            stat.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
            self._stats_layout.addWidget(stat)

            val = QLabel(value)
            val.setFont(
                QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_MD, Fonts.WEIGHT_BOLD)
            )
            val.setStyleSheet(lbl_style(color))
            self._stats_layout.addWidget(val)

            self._stats_layout.addSpacing(Spacing.XL)

        self._stats_layout.addStretch()

    def _populate_table(self):
        """Llena la tabla con datos filtrados."""
        cmds = self._filtered_commands()
        self._table.setRowCount(len(cmds))

        for row, cmd in enumerate(cmds):
            status = "🟢" if cmd.get("enabled", True) else "🔴"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setData(Qt.ItemDataRole.UserRole, cmd["id"])
            self._table.setItem(row, 0, status_item)

            # Use translated name for default commands
            display_name = cmd.get("name", "")
            if cmd.get("default"):
                translated = t(f"default_cmd.{cmd['id']}")
                if translated != f"default_cmd.{cmd['id']}":
                    display_name = translated
            self._table.setItem(row, 1, QTableWidgetItem(display_name))
            self._table.setItem(row, 2, QTableWidgetItem(", ".join(cmd.get("aliases", []))))
            self._table.setItem(row, 3, QTableWidgetItem(cmd.get("category", "").capitalize()))
            self._table.setItem(row, 4, QTableWidgetItem(cmd.get("type", "").capitalize()))

            locked = "🔒" if cmd.get("locked") else "—"
            locked_item = QTableWidgetItem(locked)
            locked_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 5, locked_item)

            self._table.setRowHeight(row, 42)

    def _filtered_commands(self) -> list[dict]:
        """Retorna comandos filtrados por categoría y búsqueda."""
        cmds = self._all_cmds

        if self._current_filter == "system":
            cmds = [c for c in cmds if c.get("default")]
        elif self._current_filter == "custom":
            cmds = [c for c in cmds if not c.get("default")]

        text = self._search.text().lower().strip()
        if text:
            cmds = [
                c for c in cmds
                if text in c.get("name", "").lower()
                or text in " ".join(c.get("aliases", [])).lower()
            ]
        return cmds

    def _selected_cmd_id(self) -> str | None:
        """Retorna el ID del comando seleccionado en la tabla."""
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    # === Filtros ===

    def _set_filter(self, key: str):
        self._current_filter = key
        self._update_filter_style()
        self._populate_table()

    def _update_filter_style(self):
        for key, btn in self._filter_buttons.items():
            if key == self._current_filter:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.ACCENT_PRIMARY};
                        color: {Colors.TEXT_ON_ACCENT};
                        border: none;
                        border-radius: {Radius.MD}px;
                        padding: {Spacing.SM}px {Spacing.LG}px;
                        font-size: {Fonts.SIZE_MD}px;
                        font-weight: {Fonts.WEIGHT_SEMIBOLD};
                        min-height: 36px;
                    }}
                """)
            else:
                btn.setStyleSheet(get_button_secondary_style())

    def _apply_filters(self):
        self._populate_table()

    # === CRUD ===

    def _on_add(self):
        """Abre diálogo para crear un comando nuevo."""
        dialog = CommandDialog(parent=self)
        if dialog.exec() == CommandDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                store = self._get_store()
                if store:
                    # Validar que no exista un comando con el mismo ID
                    if store.get_by_id(data["id"]):
                        QMessageBox.warning(
                            self, t("cmd_dialog.error"),
                            t("cmd_dialog.err_id_exists"),
                        )
                        return
                    ok, msg = store.add(data)
                    if ok:
                        logger.info("Comando creado: %s", data["id"])
                        self._refresh()
                    else:
                        QMessageBox.warning(self, "Error", msg)

    def _on_edit(self):
        """Abre diálogo para editar el comando seleccionado."""
        cmd_id = self._selected_cmd_id()
        if not cmd_id:
            return

        store = self._get_store()
        if not store:
            return

        cmd = store.get_by_id(cmd_id)
        if not cmd:
            return

        if cmd.get("locked"):
            QMessageBox.information(
                self, t("commands.locked"),
                t("commands.locked_edit_msg"),
            )
            return
        if cmd.get("default") and not cmd.get("locked"):
            dialog = CommandDialog(command=cmd, parent=self)
            if dialog.exec() == CommandDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data:
                    ok, msg = store.update(cmd_id, data)
                    if ok:
                        self._refresh()
                    else:
                        QMessageBox.warning(self, "Error", msg)

    def _on_duplicate(self):
        """Duplica el comando seleccionado."""
        cmd_id = self._selected_cmd_id()
        if not cmd_id:
            return

        store = self._get_store()
        if not store:
            return

        new_id = f"{cmd_id}_copy"
        ok, msg = store.duplicate(cmd_id, new_id)
        if ok:
            logger.info("Comando duplicado: %s → %s", cmd_id, new_id)
            self._refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_toggle(self):
        """Activa/desactiva el comando seleccionado."""
        cmd_id = self._selected_cmd_id()
        if not cmd_id:
            return

        store = self._get_store()
        if not store:
            return

        ok, msg = store.toggle_enabled(cmd_id)
        if ok:
            self._refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_delete(self):
        """Elimina el comando seleccionado (solo custom)."""
        cmd_id = self._selected_cmd_id()
        if not cmd_id:
            return

        store = self._get_store()
        if not store:
            return

        cmd = store.get_by_id(cmd_id)
        if cmd and (cmd.get("locked") or cmd.get("default")):
            QMessageBox.information(
                self, t("commands.locked"),
                t("commands.locked")
            )
            return

        reply = QMessageBox.question(
            self, t("commands.confirm_title"),
            t("commands.confirm_delete").replace("{name}", cmd.get('name', cmd_id)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = store.delete(cmd_id)
            if ok:
                logger.info("Comando eliminado: %s", cmd_id)
                self._refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_test(self):
        """Ejecuta el comando seleccionado para probarlo (sin popup)."""
        cmd_id = self._selected_cmd_id()
        if not cmd_id:
            return

        store = self._get_store()
        if not store:
            return

        cmd = store.get_by_id(cmd_id)
        if not cmd:
            return

        try:
            from app.core.actions.action_executor import ActionExecutor
            executor = ActionExecutor()
            result = executor.execute(cmd)
            if result.success:
                logger.info("Test comando '%s': %s", cmd_id, result.message)
            else:
                logger.warning("Test comando '%s' falló: %s", cmd_id, result.message)
        except Exception:
            logger.exception("Error ejecutando test de comando '%s'", cmd_id)
