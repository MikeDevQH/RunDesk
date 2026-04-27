"""
Página de diagnóstico del sistema.
Info del sistema, health checks, log viewer y herramientas de soporte.
"""

import json
import logging
import os
import platform
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
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

logger = logging.getLogger(__name__)


class InfoRow(QFrame):
    """Fila de información clave-valor."""

    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(40)
        self.setObjectName("infoRow")
        self.setStyleSheet(f"""
            QFrame#infoRow {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {Colors.BORDER_SUBTLE};
            }}
        """)

        row = QHBoxLayout(self)
        row.setContentsMargins(Spacing.XL, 0, Spacing.XL, 0)

        lbl = QLabel(label)
        lbl.setFont(QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM))
        lbl.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        row.addWidget(lbl)

        row.addStretch()

        val = QLabel(value)
        val.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM, Fonts.WEIGHT_MEDIUM)
        )
        val.setStyleSheet(lbl_style(Colors.TEXT_PRIMARY))
        val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(val)


class FileCheckRow(QFrame):
    """Fila de verificación de archivo con estado."""

    def __init__(self, filename: str, status: str, color: str, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(36)
        self.setObjectName("fileCheckRow")
        self.setStyleSheet(f"""
            QFrame#fileCheckRow {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {Colors.BORDER_SUBTLE};
            }}
        """)

        row = QHBoxLayout(self)
        row.setContentsMargins(Spacing.XL, 0, Spacing.XL, 0)

        name_lbl = QLabel(filename)
        name_lbl.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_SM)
        )
        name_lbl.setStyleSheet(lbl_style(Colors.TEXT_SECONDARY))
        row.addWidget(name_lbl)

        row.addStretch()

        status_lbl = QLabel(status)
        status_lbl.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_SM,
                Fonts.WEIGHT_MEDIUM,
            )
        )
        status_lbl.setStyleSheet(lbl_style(color))
        row.addWidget(status_lbl)


class DiagnosticsPage(QWidget):
    """Página de diagnóstico y herramientas de soporte."""

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._setup_ui()

    def _get_data_dir(self) -> Path | None:
        """Obtiene el directorio de datos."""
        if self._bootstrap:
            config = self._bootstrap.get_config()
            if config:
                return config.data_dir
        return None

    def _check_file(self, filepath: Path) -> tuple[str, str]:
        """Verifica un archivo JSON. Retorna (status_text, color)."""
        if not filepath.exists():
            return t("diagnostics.file_missing"), Colors.WARNING
        try:
            with open(filepath, encoding="utf-8") as f:
                json.load(f)
            return t("diagnostics.file_ok"), Colors.SUCCESS
        except (json.JSONDecodeError, OSError):
            return t("diagnostics.file_corrupt"), Colors.ERROR

    def _run_health_checks(self) -> tuple[str, str, str]:
        """Ejecuta health checks. Retorna (icon, text, color)."""
        data_dir = self._get_data_dir()
        if not data_dir:
            return "🟢", t("diagnostics.health_ok"), Colors.SUCCESS

        has_error = False
        has_warning = False
        for fname in ("config.json", "commands.json", "scenes.json"):
            fpath = data_dir / fname
            if not fpath.exists():
                has_warning = True
            else:
                try:
                    with open(fpath, encoding="utf-8") as f:
                        json.load(f)
                except (json.JSONDecodeError, OSError):
                    has_error = True

        if has_error:
            return "🔴", t("diagnostics.health_error"), Colors.ERROR
        if has_warning:
            return "🟡", t("diagnostics.health_warning"), Colors.WARNING
        return "🟢", t("diagnostics.health_ok"), Colors.SUCCESS

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(scroll)

        self._container = QWidget()
        scroll.setWidget(self._container)
        self._build_content()

    def _build_content(self):
        """Construye todo el contenido de la página."""
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(
            Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL,
        )
        layout.setSpacing(Spacing.XL)

        # --- Header ---
        title = QLabel(t("diagnostics.title"))
        title.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_HERO,
                Fonts.WEIGHT_BOLD,
            )
        )
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel(t("diagnostics.subtitle"))
        subtitle.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_LG)
        )
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(subtitle)

        layout.addSpacing(Spacing.MD)

        # --- Health status ---
        h_icon, h_text, h_color = self._run_health_checks()

        health_frame = QFrame()
        health_frame.setFixedHeight(60)
        health_frame.setObjectName("healthFrame")
        health_frame.setStyleSheet(f"""
            QFrame#healthFrame {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
        """)
        health_layout = QHBoxLayout(health_frame)
        health_layout.setContentsMargins(Spacing.XL, 0, Spacing.XL, 0)

        health_icon = QLabel(h_icon)
        health_icon.setFont(
            QFont(Fonts.FAMILY.split(",")[0].strip(), Fonts.SIZE_XL)
        )
        health_icon.setStyleSheet("background: transparent;")
        health_layout.addWidget(health_icon)

        health_label = QLabel(h_text)
        health_label.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_MD,
                Fonts.WEIGHT_MEDIUM,
            )
        )
        health_label.setStyleSheet(lbl_style(h_color))
        health_layout.addWidget(health_label)

        health_layout.addStretch()
        layout.addWidget(health_frame)

        # --- System info ---
        sys_section = QFrame()
        sys_section.setObjectName("sysSection")
        sys_section.setStyleSheet(f"""
            QFrame#sysSection {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
        """)
        sys_lay = QVBoxLayout(sys_section)
        sys_lay.setContentsMargins(0, 0, 0, 0)
        sys_lay.setSpacing(0)

        sys_header = QLabel(f"  🖥️  {t('diagnostics.system_info')}")
        sys_header.setFixedHeight(48)
        sys_header.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_LG,
                Fonts.WEIGHT_SEMIBOLD,
            )
        )
        sys_header.setStyleSheet(
            f"{lbl_style(Colors.TEXT_PRIMARY)} "
            f"padding-left: {Spacing.XL}px;"
        )
        sys_lay.addWidget(sys_header)

        sys_lay.addWidget(InfoRow(t("diagnostics.os"), platform.platform()))
        sys_lay.addWidget(InfoRow("Python", sys.version.split()[0]))
        sys_lay.addWidget(
            InfoRow(t("diagnostics.architecture"), platform.machine())
        )

        try:
            import PySide6
            pyside_ver = PySide6.__version__
        except AttributeError:
            pyside_ver = "6.x"
        sys_lay.addWidget(InfoRow("PySide6", pyside_ver))

        # Config data
        data_dir = self._get_data_dir()
        data_dir_str = str(data_dir) if data_dir else "—"
        config_ver = "—"
        cmd_count = "—"
        scene_count = "—"

        if self._bootstrap:
            config = self._bootstrap.get_config()
            if config:
                config_ver = str(config.get("schema_version", "—"))
            commands = self._bootstrap.get_commands()
            if commands:
                cmd_count = str(commands.count)
            scenes = self._bootstrap.get_scenes()
            if scenes:
                scene_count = str(scenes.count)

        sys_lay.addWidget(InfoRow(t("diagnostics.config_path"), data_dir_str))
        sys_lay.addWidget(
            InfoRow(t("diagnostics.schema_version"), config_ver)
        )
        sys_lay.addWidget(
            InfoRow(t("diagnostics.commands_loaded"), cmd_count)
        )
        sys_lay.addWidget(
            InfoRow(t("diagnostics.scenes_loaded"), scene_count)
        )

        layout.addWidget(sys_section)

        # --- File health checks ---
        if data_dir:
            file_section = QFrame()
            file_section.setObjectName("fileSection")
            file_section.setStyleSheet(f"""
                QFrame#fileSection {{
                    background-color: {Colors.BG_SURFACE};
                    border: 1px solid {Colors.BORDER_SUBTLE};
                    border-radius: {Radius.LG}px;
                }}
            """)
            file_lay = QVBoxLayout(file_section)
            file_lay.setContentsMargins(0, 0, 0, 0)
            file_lay.setSpacing(0)

            file_header = QLabel(
                f"  📁  {t('diagnostics.file_check')}"
            )
            file_header.setFixedHeight(48)
            file_header.setFont(
                QFont(
                    Fonts.FAMILY.split(",")[0].strip(),
                    Fonts.SIZE_LG,
                    Fonts.WEIGHT_SEMIBOLD,
                )
            )
            file_header.setStyleSheet(
                f"{lbl_style(Colors.TEXT_PRIMARY)} "
                f"padding-left: {Spacing.XL}px;"
            )
            file_lay.addWidget(file_header)

            for fname in ("config.json", "commands.json", "scenes.json"):
                status, color = self._check_file(data_dir / fname)
                file_lay.addWidget(FileCheckRow(fname, status, color))

            layout.addWidget(file_section)

        # --- Log viewer ---
        log_section = QFrame()
        log_section.setObjectName("logSection")
        log_section.setStyleSheet(f"""
            QFrame#logSection {{
                background-color: {Colors.BG_SURFACE};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {Radius.LG}px;
            }}
        """)
        log_lay = QVBoxLayout(log_section)
        log_lay.setContentsMargins(0, 0, 0, 0)
        log_lay.setSpacing(0)

        log_header = QLabel(f"  📋  {t('diagnostics.log_viewer')}")
        log_header.setFixedHeight(48)
        log_header.setFont(
            QFont(
                Fonts.FAMILY.split(",")[0].strip(),
                Fonts.SIZE_LG,
                Fonts.WEIGHT_SEMIBOLD,
            )
        )
        log_header.setStyleSheet(
            f"{lbl_style(Colors.TEXT_PRIMARY)} "
            f"padding-left: {Spacing.XL}px;"
        )
        log_lay.addWidget(log_header)

        self._log_text = QPlainTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFixedHeight(200)
        self._log_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {Colors.BG_DARKEST};
                color: {Colors.TEXT_SECONDARY};
                border: none;
                border-top: 1px solid {Colors.BORDER_SUBTLE};
                font-family: "Cascadia Code", "Consolas", monospace;
                font-size: {Fonts.SIZE_SM}px;
                padding: {Spacing.MD}px;
            }}
        """)
        self._refresh_logs()
        log_lay.addWidget(self._log_text)

        layout.addWidget(log_section)

        # --- Action buttons ---
        actions_row = QHBoxLayout()
        actions_row.setSpacing(Spacing.MD)

        btn_open = QPushButton(t("diagnostics.open_data_folder"))
        btn_open.setStyleSheet(get_button_secondary_style())
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setToolTip(t("diagnostics.open_data_folder_tip"))
        btn_open.clicked.connect(self._on_open_data_folder)
        actions_row.addWidget(btn_open)

        btn_export_logs = QPushButton(t("diagnostics.export_logs"))
        btn_export_logs.setStyleSheet(get_button_secondary_style())
        btn_export_logs.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export_logs.setToolTip(t("diagnostics.export_logs_tip"))
        btn_export_logs.clicked.connect(self._on_export_logs)
        actions_row.addWidget(btn_export_logs)

        btn_export_cfg = QPushButton(t("diagnostics.export_config"))
        btn_export_cfg.setStyleSheet(get_button_primary_style())
        btn_export_cfg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export_cfg.setToolTip(t("diagnostics.export_config_tip"))
        btn_export_cfg.clicked.connect(self._on_export_config)
        actions_row.addWidget(btn_export_cfg)

        btn_import_cfg = QPushButton(t("diagnostics.import_config"))
        btn_import_cfg.setStyleSheet(get_button_secondary_style())
        btn_import_cfg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import_cfg.setToolTip(t("diagnostics.import_config_tip"))
        btn_import_cfg.clicked.connect(self._on_import_config)
        actions_row.addWidget(btn_import_cfg)

        btn_reset = QPushButton(t("diagnostics.factory_reset"))
        btn_reset.setStyleSheet(get_button_primary_style().replace(
            Colors.ACCENT_PRIMARY, Colors.ERROR
        ).replace(
            Colors.ACCENT_HOVER, "#FF9999"
        ).replace(
            Colors.ACCENT_PRESSED, "#CC5555"
        ))
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setToolTip(t("diagnostics.factory_reset_tip"))
        btn_reset.clicked.connect(self._on_factory_reset)
        actions_row.addWidget(btn_reset)

        actions_row.addStretch()
        layout.addLayout(actions_row)

        layout.addStretch()

    # --- Actions ---

    def _refresh_logs(self):
        """Actualiza el visor de logs con las líneas capturadas."""
        from app.core.log_capture import get_log_lines
        lines = get_log_lines()
        if lines:
            self._log_text.setPlainText("\n".join(lines))
            # Scroll al final
            sb = self._log_text.verticalScrollBar()
            sb.setValue(sb.maximum())
        else:
            self._log_text.setPlainText(t("diagnostics.log_empty"))

    def _on_open_data_folder(self):
        """Abre el directorio de datos en el explorador."""
        data_dir = self._get_data_dir()
        if data_dir and data_dir.exists():
            os.startfile(str(data_dir))

    def _on_export_logs(self):
        """Exporta los logs a un archivo de texto."""
        from app.core.log_capture import get_log_lines

        lines = get_log_lines()
        if not lines:
            return

        default_name = (
            f"app_launcher_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            t("diagnostics.logs_save_title"),
            default_name,
            "Text files (*.txt)",
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                msg = t("diagnostics.logs_saved").replace(
                    "{path}", filepath
                )
                logger.info(msg)
                QMessageBox.information(
                    self, t("diagnostics.export_logs"), msg,
                )
            except OSError as e:
                logger.error("Error exportando logs: %s", e)

    def _on_export_config(self):
        """Exporta config.json, commands.json y scenes.json a un ZIP."""
        data_dir = self._get_data_dir()
        if not data_dir:
            return

        default_name = f"rundesk_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            t("diagnostics.export_config_title"),
            default_name,
            "ZIP files (*.zip)",
        )
        if not filepath:
            return

        try:
            with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in ("config.json", "commands.json", "scenes.json"):
                    fpath = data_dir / fname
                    if fpath.exists():
                        zf.write(fpath, fname)
            msg = t("diagnostics.export_config_success").replace("{path}", filepath)
            logger.info(msg)
            QMessageBox.information(self, t("diagnostics.export_config_title"), msg)
        except OSError as e:
            logger.error("Error exportando config: %s", e)

    def _on_import_config(self):
        """Importa config.json, commands.json y scenes.json desde un ZIP."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            t("diagnostics.import_config_title"),
            "",
            "ZIP files (*.zip)",
        )
        if not filepath:
            return

        # Confirmar antes de sobreescribir
        reply = QMessageBox.warning(
            self,
            t("diagnostics.import_config_title"),
            t("diagnostics.import_config_warning"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        data_dir = self._get_data_dir()
        if not data_dir:
            return

        try:
            valid_files = {"config.json", "commands.json", "scenes.json"}
            with zipfile.ZipFile(filepath, "r") as zf:
                names = set(zf.namelist())
                to_extract = names & valid_files
                if not to_extract:
                    raise ValueError("No valid config files found in ZIP")
                for fname in to_extract:
                    zf.extract(fname, data_dir)

            msg = t("diagnostics.import_config_success")
            logger.info(msg)
            QMessageBox.information(self, t("diagnostics.import_config_title"), msg)
        except Exception as e:
            msg = t("diagnostics.import_config_error").replace("{error}", str(e))
            logger.error(msg)
            QMessageBox.critical(self, t("diagnostics.import_config_title"), msg)

    def _on_factory_reset(self):
        """Factory reset con diálogo de confirmación y respaldo opcional."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(t("diagnostics.reset_title"))
        msg_box.setText(t("diagnostics.reset_warning"))
        msg_box.setIcon(QMessageBox.Icon.Warning)

        btn_backup = msg_box.addButton(
            t("diagnostics.reset_backup_yes"),
            QMessageBox.ButtonRole.AcceptRole,
        )
        btn_no_backup = msg_box.addButton(
            t("diagnostics.reset_backup_no"),
            QMessageBox.ButtonRole.DestructiveRole,
        )
        msg_box.addButton(
            t("diagnostics.reset_cancel"),
            QMessageBox.ButtonRole.RejectRole,
        )
        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked == btn_backup:
            self._do_backup_and_reset()
        elif clicked == btn_no_backup:
            self._do_reset()

    def _do_backup_and_reset(self):
        """Crea respaldo y luego resetea."""
        data_dir = self._get_data_dir()
        if not data_dir:
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = data_dir / f"backup_{ts}"
        backup_dir.mkdir(exist_ok=True)

        for fname in ("config.json", "commands.json", "scenes.json"):
            src = data_dir / fname
            if src.exists():
                shutil.copy2(src, backup_dir / fname)

        msg = t("diagnostics.reset_backup_saved").replace(
            "{path}", str(backup_dir)
        )
        logger.info(msg)
        QMessageBox.information(
            self, t("diagnostics.reset_title"), msg,
        )
        self._do_reset()

    def _do_reset(self):
        """Ejecuta el factory reset."""
        if self._bootstrap:
            config = self._bootstrap.get_config()
            if config:
                config.reset_to_defaults()
            commands = self._bootstrap.get_commands()
            if commands:
                commands.reset_defaults()
            scenes = self._bootstrap.get_scenes()
            if scenes:
                scenes.reset()

        logger.info("Factory reset ejecutado")
        QMessageBox.information(
            self,
            t("diagnostics.reset_title"),
            t("diagnostics.reset_success"),
        )
        # Reconstruir la página
        self.on_page_shown()

    def on_page_shown(self):
        """Reconstruye la página (cambio de idioma o refresh)."""
        scroll = self.findChild(QScrollArea)
        if scroll:
            old = scroll.takeWidget()
            if old is not None:
                old.deleteLater()
        self._container = QWidget()
        if scroll:
            scroll.setWidget(self._container)
        self._build_content()
