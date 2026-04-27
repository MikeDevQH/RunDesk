"""
Motor de acciones — ejecuta las acciones asociadas a comandos.
Cada command_id del sistema se mapea a una función concreta.
Los comandos custom usan el campo type + path/url/shell.
"""

import ctypes
import logging
import os
import subprocess
import webbrowser

logger = logging.getLogger(__name__)


class ActionResult:
    """Resultado de ejecutar una acción."""

    def __init__(self, success: bool, message: str = ""):
        self.success = success
        self.message = message

    def __repr__(self):
        status = "OK" if self.success else "ERROR"
        return f"ActionResult({status}, '{self.message}')"


class ActionExecutor:
    """Ejecuta acciones reales del sistema operativo.

    Soporta:
    - Comandos de sistema con command_id (shutdown, lock, etc.)
    - Abrir programas por path
    - Abrir URLs en navegador
    - Abrir carpetas en Explorer
    - Ejecutar scripts/shell commands
    """

    def __init__(self):
        self._system_actions: dict[str, callable] = {
            "shutdown": self._shutdown,
            "restart": self._restart,
            "sleep": self._sleep,
            "lock": self._lock,
            "open_settings": self._open_settings,
            "open_explorer": self._open_explorer,
            "open_taskmgr": self._open_taskmgr,
            "open_browser": self._open_browser,
            "open_calc": self._open_calc,
            "vol_up": self._vol_up,
            "vol_down": self._vol_down,
            "mute": self._mute,
            "bright_up": self._bright_up,
            "bright_down": self._bright_down,
        }
        # Acciones internas del launcher (se registran externamente)
        self._launcher_actions: dict[str, callable] = {}

    def register_launcher_action(self, action_id: str, callback: callable):
        """Registra una acción interna del launcher (open_panel, pause, etc.)."""
        self._launcher_actions[action_id] = callback

    def execute(self, command: dict) -> ActionResult:
        """Ejecuta un comando según su tipo y datos.

        Args:
            command: dict con los datos del comando (type, command_id, path, url, etc.)

        Returns:
            ActionResult con éxito/error y mensaje
        """
        cmd_type = command.get("type", "")
        command_id = command.get("command_id", "")

        try:
            # Comandos de sistema con command_id
            if cmd_type == "system" and command_id:
                # Primero verificar si es acción del launcher
                if command_id in self._launcher_actions:
                    self._launcher_actions[command_id]()
                    return ActionResult(True, f"Acción launcher: {command_id}")

                # Luego verificar si es acción de sistema
                action = self._system_actions.get(command_id)
                if action:
                    return action()
                return ActionResult(False, f"Acción de sistema desconocida: {command_id}")

            # Abrir programa
            if cmd_type == "program":
                return self._open_program(command)

            # Abrir URL
            if cmd_type == "url":
                return self._open_url(command)

            # Abrir carpeta
            if cmd_type == "folder":
                return self._open_folder(command)

            # Ejecutar script/shell
            if cmd_type == "script":
                return self._run_script(command)

            # Shortcut (atajo de teclado simulado)
            if cmd_type == "shortcut":
                return self._send_keys(command)

            return ActionResult(False, f"Tipo de comando no soportado: {cmd_type}")

        except Exception as e:
            logger.exception("Error ejecutando comando %s", command.get("id", "?"))
            return ActionResult(False, f"Error: {e}")

    # === Acciones de sistema ===

    def _shutdown(self) -> ActionResult:
        subprocess.Popen(["shutdown", "/s", "/t", "5"], shell=True)
        return ActionResult(True, "Apagando en 5 segundos...")

    def _restart(self) -> ActionResult:
        subprocess.Popen(["shutdown", "/r", "/t", "5"], shell=True)
        return ActionResult(True, "Reiniciando en 5 segundos...")

    def _sleep(self) -> ActionResult:
        # rundll32 para suspender
        subprocess.Popen(
            ["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"],
            shell=True,
        )
        return ActionResult(True, "Suspendiendo equipo...")

    def _lock(self) -> ActionResult:
        ctypes.windll.user32.LockWorkStation()
        return ActionResult(True, "Equipo bloqueado")

    def _open_settings(self) -> ActionResult:
        os.startfile("ms-settings:")
        return ActionResult(True, "Configuración de Windows abierta")

    def _open_explorer(self) -> ActionResult:
        os.startfile("explorer.exe")
        return ActionResult(True, "Explorador abierto")

    def _open_taskmgr(self) -> ActionResult:
        subprocess.Popen(["taskmgr.exe"])
        return ActionResult(True, "Administrador de tareas abierto")

    def _open_browser(self) -> ActionResult:
        webbrowser.open("https://www.google.com")
        return ActionResult(True, "Navegador abierto")

    def _open_calc(self) -> ActionResult:
        subprocess.Popen(["calc.exe"])
        return ActionResult(True, "Calculadora abierta")

    def _vol_up(self) -> ActionResult:
        return self._send_vk(0xAF, "Volumen subido")  # VK_VOLUME_UP

    def _vol_down(self) -> ActionResult:
        return self._send_vk(0xAE, "Volumen bajado")  # VK_VOLUME_DOWN

    def _mute(self) -> ActionResult:
        return self._send_vk(0xAD, "Silenciado/desilenciado")  # VK_VOLUME_MUTE

    def _bright_up(self) -> ActionResult:
        # No hay VK directo, usar WMI/powershell
        subprocess.Popen(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
             ".WmiSetBrightness(1, [Math]::Min(100, "
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness)"
             ".CurrentBrightness + 10))"],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return ActionResult(True, "Brillo subido")

    def _bright_down(self) -> ActionResult:
        subprocess.Popen(
            ["powershell", "-Command",
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
             ".WmiSetBrightness(1, [Math]::Max(0, "
             "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness)"
             ".CurrentBrightness - 10))"],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return ActionResult(True, "Brillo bajado")

    # === Acciones genéricas ===

    def _open_program(self, cmd: dict) -> ActionResult:
        path = cmd.get("path")
        if not path:
            return ActionResult(False, "Comando sin path definido")
        args = cmd.get("args") or []
        if isinstance(args, str):
            args = args.split()

        window_cfg = cmd.get("window")
        if window_cfg:
            from app.core.actions.window_manager import launch_and_position

            monitor = window_cfg.get("monitor", 0)
            position = window_cfg.get("position", "maximized")
            launch_and_position(
                launch_fn=lambda: subprocess.Popen([path, *args]),
                monitor_index=monitor,
                position=position,
            )
            return ActionResult(True, f"Programa abierto: {path} → monitor {monitor}, {position}")

        try:
            subprocess.Popen([path, *args])
            return ActionResult(True, f"Programa abierto: {path}")
        except FileNotFoundError:
            return ActionResult(False, f"No se encontró: {path}")

    def _open_url(self, cmd: dict) -> ActionResult:
        url = cmd.get("url")
        if not url:
            return ActionResult(False, "Comando sin URL definida")

        window_cfg = cmd.get("window")
        if window_cfg:
            from app.core.actions.window_manager import launch_and_position

            monitor = window_cfg.get("monitor", 0)
            position = window_cfg.get("position", "maximized")
            launch_and_position(
                launch_fn=lambda: webbrowser.open(url),
                monitor_index=monitor,
                position=position,
            )
            return ActionResult(True, f"URL abierta: {url} → monitor {monitor}, {position}")

        webbrowser.open(url)
        return ActionResult(True, f"URL abierta: {url}")

    def _open_folder(self, cmd: dict) -> ActionResult:
        path = cmd.get("path")
        if not path:
            return ActionResult(False, "Comando sin path definido")
        if not os.path.isdir(path):
            return ActionResult(False, f"Carpeta no encontrada: {path}")
        os.startfile(path)
        return ActionResult(True, f"Carpeta abierta: {path}")

    def _run_script(self, cmd: dict) -> ActionResult:
        shell_cmd = cmd.get("shell") or cmd.get("command")
        if not shell_cmd:
            return ActionResult(False, "Comando sin shell/command definido")
        subprocess.Popen(shell_cmd, shell=True)
        return ActionResult(True, f"Script ejecutado: {shell_cmd}")

    def _send_keys(self, cmd: dict) -> ActionResult:
        keys = cmd.get("keys")
        if not keys:
            return ActionResult(False, "Shortcut sin keys definido")
        # En fases posteriores: simular combinación con keyboard lib
        return ActionResult(False, f"Envío de teclas pendiente de implementar: {keys}")

    # === Helpers ===

    @staticmethod
    def _send_vk(vk_code: int, message: str) -> ActionResult:
        """Simula presionar y soltar una tecla virtual de Windows."""
        KEYEVENTF_KEYUP = 0x0002
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
        return ActionResult(True, message)
