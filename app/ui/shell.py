"""
Shell principal de la aplicación.
Ventana con sidebar de navegación y área de contenido intercambiable.
"""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)

from app.ui.components.sidebar import Sidebar
from app.ui.pages.about_page import AboutPage
from app.ui.pages.appearance_page import AppearancePage
from app.ui.pages.commands_page import CommandsPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.diagnostics_page import DiagnosticsPage
from app.ui.pages.languages_page import LanguagesPage
from app.ui.pages.launcher_settings_page import LauncherSettingsPage
from app.ui.pages.scenes_page import ScenesPage
from app.ui.pages.tutorials_page import TutorialsPage
from app.ui.styles import Colors, get_base_stylesheet


class AppShell(QMainWindow):
    """Ventana principal con sidebar y contenido dinámico."""

    MIN_WIDTH = 1100
    MIN_HEIGHT = 700

    def __init__(self, bootstrap=None, parent=None):
        super().__init__(parent)
        self._bootstrap = bootstrap
        self._app_state = bootstrap.get_app_state() if bootstrap else None

        # Lazy import to avoid circular
        if self._app_state is None:
            from app.core.app_state import AppState
            self._app_state = AppState()

        self._allow_quit = False
        self.setWindowTitle("RunDesk")
        self.setMinimumSize(QSize(self.MIN_WIDTH, self.MIN_HEIGHT))

        self.setStyleSheet(get_base_stylesheet())

        self._pages: dict[str, QWidget] = {}

        self._setup_ui()
        self._register_pages()
        self._restore_window_geometry()

        # Página inicial
        self._sidebar.set_active_page("dashboard")
        self._navigate_to("dashboard")

    def _setup_ui(self):
        """Construye el layout principal: sidebar + contenido."""
        central = QWidget()
        central.setStyleSheet(f"background-color: {Colors.BG_BASE};")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.navigation_requested.connect(self._navigate_to)
        main_layout.addWidget(self._sidebar)

        # Área de contenido
        self._content_stack = QStackedWidget()
        self._content_stack.setStyleSheet(f"background-color: {Colors.BG_BASE};")
        self._content_stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self._content_stack)

    def _register_pages(self):
        """Registra todas las páginas disponibles."""
        self._add_page("dashboard", DashboardPage(bootstrap=self._bootstrap))
        self._add_page("commands", CommandsPage(bootstrap=self._bootstrap))
        self._add_page("scenes", ScenesPage(bootstrap=self._bootstrap))
        self._add_page("launcher", LauncherSettingsPage(bootstrap=self._bootstrap))
        self._add_page("appearance", AppearancePage(bootstrap=self._bootstrap))
        lang_page = LanguagesPage(bootstrap=self._bootstrap)
        lang_page.language_changed.connect(self._on_language_changed)
        self._add_page("languages", lang_page)
        tut_page = TutorialsPage(bootstrap=self._bootstrap)
        tut_page.navigate_requested.connect(self._navigate_to)
        self._add_page("tutorials", tut_page)
        self._add_page("diagnostics", DiagnosticsPage(bootstrap=self._bootstrap))
        self._add_page("about", AboutPage(bootstrap=self._bootstrap))

    def _add_page(self, page_id: str, widget: QWidget):
        """Agrega una página al stack de contenido."""
        self._pages[page_id] = widget
        self._content_stack.addWidget(widget)

    def _navigate_to(self, page_id: str):
        """Navega a una página por su id."""
        if page_id in self._pages:
            widget = self._pages[page_id]
            self._content_stack.setCurrentWidget(widget)
            self._sidebar.set_active_page(page_id)
            # Notificar a la página para que refresque sus datos
            if hasattr(widget, "on_page_shown"):
                widget.on_page_shown()

    # --- Persistencia de geometría de ventana ---

    def _restore_window_geometry(self):
        """Restaura tamaño y posición. Primera vez: maximizada."""
        if self._app_state.is_first_run():
            self.showMaximized()
            return

        geom = self._app_state.get_window_geometry()
        width = geom.get("width") or 1280
        height = geom.get("height") or 800
        x = geom.get("x")
        y = geom.get("y")

        self.resize(width, height)

        if x is not None and y is not None:
            self.move(x, y)
        else:
            # Centrar en pantalla si no hay posición guardada
            screen = self.screen().availableGeometry()
            self.move(
                (screen.width() - width) // 2,
                (screen.height() - height) // 2,
            )

        if geom.get("maximized", False):
            self.showMaximized()

    def _save_window_geometry(self):
        """Guarda la geometría actual (posición normal, no maximizada)."""
        is_max = self.isMaximized()
        # Guardar la geometría normal (no maximizada) para restaurarla bien
        geo = self.normalGeometry()
        self._app_state.save_window_geometry(
            x=geo.x(),
            y=geo.y(),
            width=geo.width(),
            height=geo.height(),
            maximized=is_max,
        )

    def _on_language_changed(self, lang: str):
        """Reconstruye toda la UI al cambiar de idioma."""
        self._sidebar.refresh_labels()
        # Destruir y re-crear todas las páginas para que tomen el nuevo idioma
        current_id = None
        for pid, w in self._pages.items():
            if w is self._content_stack.currentWidget():
                current_id = pid
                break
        self._rebuild_all_pages()
        if current_id and current_id in self._pages:
            self._navigate_to(current_id)

    def _rebuild_all_pages(self):
        """Destruye y recrea todas las páginas para reflejar el idioma actual."""
        for pid in list(self._pages):
            old = self._pages.pop(pid)
            self._content_stack.removeWidget(old)
            old.deleteLater()
        self._register_pages()

    def closeEvent(self, event):
        """Minimiza a bandeja en vez de cerrar. Usa quit_app() para salir."""
        if self._allow_quit:
            self._save_window_geometry()
            super().closeEvent(event)
        else:
            event.ignore()
            self.hide_to_tray()

    def hide_to_tray(self):
        """Oculta la ventana y la esconde de la barra de tareas."""
        self._save_window_geometry()
        self.hide()

    def show_from_tray(self):
        """Restaura la ventana desde la bandeja del sistema."""
        self.show()
        self.setWindowState(
            self.windowState() & ~Qt.WindowState.WindowMinimized
        )
        self.activateWindow()
        self.raise_()

    def quit_app(self):
        """Cierre real de la aplicación."""
        self._allow_quit = True
        self._save_window_geometry()
        self.close()
