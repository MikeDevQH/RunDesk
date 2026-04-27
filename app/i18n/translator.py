"""
Motor de traducciones simple basado en diccionarios.
Soporta claves con punto: t("sidebar.dashboard") → "Dashboard"
"""

import logging

from app.i18n.catalog_en import CATALOG_EN
from app.i18n.catalog_es import CATALOG_ES

logger = logging.getLogger(__name__)

_CATALOGS = {
    "es": CATALOG_ES,
    "en": CATALOG_EN,
}

_current_language = "es"


def set_language(lang: str):
    """Cambia el idioma activo."""
    global _current_language
    if lang in _CATALOGS:
        _current_language = lang
        logger.info("Idioma cambiado a: %s", lang)
    else:
        logger.warning("Idioma no soportado: %s", lang)


def get_language() -> str:
    """Retorna el idioma activo."""
    return _current_language


def t(key: str) -> str:
    """Busca una traducción por clave dotted. Retorna la clave si no existe."""
    catalog = _CATALOGS.get(_current_language, CATALOG_ES)
    parts = key.split(".")
    node = catalog
    for part in parts:
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return key
    return node if isinstance(node, str) else key
