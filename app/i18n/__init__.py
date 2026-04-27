"""
Sistema de internacionalización (i18n) para RunDesk.
Provee función t() para obtener traducciones por clave.
"""

from app.i18n.translator import get_language, set_language, t

__all__ = ["get_language", "set_language", "t"]
