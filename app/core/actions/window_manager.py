"""
Window Manager — posiciona ventanas en monitores específicos.
Usa la API de Windows (user32) para mover y redimensionar ventanas.
"""

import ctypes
import ctypes.wintypes
import logging
import threading
import time

logger = logging.getLogger(__name__)

# Constantes Win32
SW_RESTORE = 9
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

user32 = ctypes.windll.user32


def get_monitors() -> list[dict]:
    """Detecta monitores conectados usando EnumDisplayMonitors.

    Returns:
        Lista de dicts con: index, name, x, y, width, height, primary, work_area
    """
    monitors = []
    CCHDEVICENAME = 32

    class MONITORINFOEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("rcMonitor", ctypes.wintypes.RECT),
            ("rcWork", ctypes.wintypes.RECT),
            ("dwFlags", ctypes.c_ulong),
            ("szDevice", ctypes.c_wchar * CCHDEVICENAME),
        ]

    def callback(hMonitor, _hdcMonitor, _lprcMonitor, _dwData):
        info = MONITORINFOEX()
        info.cbSize = ctypes.sizeof(MONITORINFOEX)
        user32.GetMonitorInfoW(hMonitor, ctypes.byref(info))
        rc = info.rcMonitor
        wa = info.rcWork
        monitors.append({
            "index": len(monitors),
            "name": info.szDevice.strip("\x00"),
            "x": rc.left,
            "y": rc.top,
            "width": rc.right - rc.left,
            "height": rc.bottom - rc.top,
            "primary": bool(info.dwFlags & 1),
            "work_area": {
                "x": wa.left,
                "y": wa.top,
                "width": wa.right - wa.left,
                "height": wa.bottom - wa.top,
            },
        })
        return True

    MONITORENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.wintypes.RECT),
        ctypes.c_double,
    )
    try:
        user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)
    except Exception:
        logger.exception("Error enumerando monitores")

    return monitors


def _calc_position(position: str, wa: dict) -> tuple[int, int, int, int]:
    """Calcula x, y, width, height según la posición predefinida y el work area.

    Args:
        position: nombre de la posición (left-half, right-half, etc.)
        wa: dict con x, y, width, height del work area del monitor

    Returns:
        (x, y, width, height)
    """
    x, y, w, h = wa["x"], wa["y"], wa["width"], wa["height"]
    half_w = w // 2
    half_h = h // 2

    positions = {
        "maximized": (x, y, w, h),
        "left-half": (x, y, half_w, h),
        "right-half": (x + half_w, y, half_w, h),
        "top-half": (x, y, w, half_h),
        "bottom-half": (x, y + half_h, w, half_h),
        "top-left": (x, y, half_w, half_h),
        "top-right": (x + half_w, y, half_w, half_h),
        "bottom-left": (x, y + half_h, half_w, half_h),
        "bottom-right": (x + half_w, y + half_h, half_w, half_h),
        "center": (x + w // 4, y + h // 4, half_w, half_h),
        "minimized": (x, y, w, h),  # se minimizará después
    }
    return positions.get(position, (x, y, w, h))


def _get_all_visible_windows() -> set[int]:
    """Retorna un set con todos los HWNDs de ventanas visibles con título."""
    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
    )
    windows = set()

    def enum_callback(hwnd, _lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                windows.add(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return windows


def find_window_by_pid(pid: int, timeout: float = 3.0) -> int | None:
    """Busca el HWND principal de un proceso por su PID.

    Args:
        pid: Process ID
        timeout: segundos máximos de espera

    Returns:
        HWND o None
    """
    WNDENUMPROC = ctypes.WINFUNCTYPE(
        ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM
    )
    result = []

    def enum_callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        window_pid = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
        if window_pid.value == pid:
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                result.append(hwnd)
                return False
        return True

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result.clear()
        user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
        if result:
            return result[0]
        time.sleep(0.15)

    return None


def find_new_window(before_hwnds: set[int], timeout: float = 5.0) -> int | None:
    """Detecta una ventana nueva que no existía antes.

    Compara las ventanas visibles actuales contra un snapshot previo.
    Más confiable que buscar por PID, ya que en Windows muchas apps
    lanzan procesos hijos y la ventana pertenece a otro PID.

    Args:
        before_hwnds: set de HWNDs capturados ANTES de lanzar la app
        timeout: segundos máximos de espera

    Returns:
        HWND de la nueva ventana o None
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        current = _get_all_visible_windows()
        new_windows = current - before_hwnds
        if new_windows:
            # Retornar la ventana nueva más reciente (la de mayor HWND suele ser la última)
            hwnd = max(new_windows)
            logger.debug("Nueva ventana detectada: HWND=%d", hwnd)
            return hwnd
        time.sleep(0.2)

    logger.warning("No se detectó ventana nueva en %0.1fs", timeout)
    return None


def launch_and_position(
    launch_fn: callable,
    monitor_index: int,
    position: str,
    timeout: float = 5.0,
):
    """Lanza una app y posiciona su ventana en un hilo de fondo.

    Args:
        launch_fn: función que lanza la app (sin argumentos)
        monitor_index: índice del monitor destino
        position: posición predefinida
        timeout: tiempo máximo de espera para detectar la ventana
    """
    def _worker():
        # Snapshot de ventanas ANTES de lanzar
        before = _get_all_visible_windows()
        logger.debug("Snapshot: %d ventanas antes de lanzar", len(before))

        # Lanzar la app
        launch_fn()

        # Esperar un momento para que el proceso arranque
        time.sleep(0.3)

        # Buscar ventana nueva
        hwnd = find_new_window(before, timeout=timeout)
        if hwnd:
            position_window(hwnd, monitor_index, position)
            logger.info("Ventana posicionada: monitor=%d, pos=%s", monitor_index, position)
        else:
            logger.warning("No se pudo posicionar: ventana no encontrada")

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()


def position_window(hwnd: int, monitor_index: int, position: str) -> bool:
    """Posiciona una ventana en un monitor y posición específica.

    Args:
        hwnd: handle de la ventana
        monitor_index: índice del monitor (0-based)
        position: posición predefinida o "custom"

    Returns:
        True si se posicionó correctamente
    """
    monitors = get_monitors()
    if not monitors:
        logger.warning("No se detectaron monitores")
        return False

    if monitor_index < 0 or monitor_index >= len(monitors):
        logger.warning("Monitor %d no existe, usando monitor 0", monitor_index)
        monitor_index = 0

    monitor = monitors[monitor_index]
    wa = monitor["work_area"]

    if position == "minimized":
        user32.ShowWindow(hwnd, SW_MINIMIZE)
        return True

    # Restaurar si está minimizada o maximizada
    user32.ShowWindow(hwnd, SW_RESTORE)

    if position == "maximized":
        # Mover al monitor correcto primero, luego maximizar
        x, y, w, h = _calc_position("center", wa)
        user32.SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOZORDER)
        time.sleep(0.05)
        user32.ShowWindow(hwnd, SW_MAXIMIZE)
        return True

    x, y, w, h = _calc_position(position, wa)
    result = user32.SetWindowPos(hwnd, 0, x, y, w, h, SWP_NOZORDER)
    return bool(result)


def position_window_custom(hwnd: int, x: int, y: int, width: int, height: int) -> bool:
    """Posiciona una ventana con coordenadas absolutas."""
    user32.ShowWindow(hwnd, SW_RESTORE)
    result = user32.SetWindowPos(hwnd, 0, x, y, width, height, SWP_NOZORDER)
    return bool(result)
