"""
Gestión del inicio automático de RunDesk con Windows.
Usa el registro de Windows (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
para agregar o quitar RunDesk del arranque del sistema.
"""

import logging
import sys
import winreg

log = logging.getLogger(__name__)

_REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "RunDesk"


def _get_exe_path() -> str:
    """Retorna la ruta del ejecutable actual."""
    return sys.executable if getattr(sys, "frozen", False) else ""


def is_startup_enabled() -> bool:
    """Verifica si RunDesk está registrado en el inicio de Windows."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, _APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except OSError:
        return False


def enable_startup() -> bool:
    """Agrega RunDesk al inicio de Windows."""
    exe_path = _get_exe_path()
    if not exe_path:
        log.warning("No se puede registrar startup: no es un ejecutable empaquetado")
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_PATH, 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
        winreg.CloseKey(key)
        log.info("RunDesk registrado en el inicio de Windows: %s", exe_path)
        return True
    except OSError as e:
        log.error("Error al registrar startup: %s", e)
        return False


def disable_startup() -> bool:
    """Quita RunDesk del inicio de Windows."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_PATH, 0, winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, _APP_NAME)
            log.info("RunDesk removido del inicio de Windows")
        except FileNotFoundError:
            pass  # Ya no estaba registrado
        finally:
            winreg.CloseKey(key)
        return True
    except OSError as e:
        log.error("Error al remover startup: %s", e)
        return False


def sync_startup(enabled: bool) -> bool:
    """Sincroniza el estado de startup con la configuración."""
    if enabled:
        return enable_startup()
    else:
        return disable_startup()
