"""
Sistema de migración de esquema para archivos JSON.
Cuando cambia schema_version, se aplican migraciones secuenciales.
"""

import logging

from app.core.config.schemas import CURRENT_SCHEMA_VERSION

logger = logging.getLogger(__name__)


# Registro de migraciones: versión destino → función que transforma el dict
MIGRATIONS: dict[int, callable] = {
    # Ejemplo para futuro:
    # 2: migrate_v1_to_v2,
}


def needs_migration(config: dict) -> bool:
    """True si la versión del config es menor que la actual."""
    return config.get("schema_version", 1) < CURRENT_SCHEMA_VERSION


def migrate(config: dict) -> dict:
    """Aplica migraciones secuenciales desde la versión actual hasta CURRENT_SCHEMA_VERSION."""
    current = config.get("schema_version", 1)

    if current >= CURRENT_SCHEMA_VERSION:
        return config

    logger.info("Migrando config de v%d a v%d", current, CURRENT_SCHEMA_VERSION)

    while current < CURRENT_SCHEMA_VERSION:
        next_version = current + 1
        if next_version in MIGRATIONS:
            try:
                config = MIGRATIONS[next_version](config)
                config["schema_version"] = next_version
                logger.info("Migración a v%d completada", next_version)
            except Exception as e:
                logger.error("Error en migración a v%d: %s", next_version, e)
                break
        else:
            # No hay migración explícita, solo subir versión
            config["schema_version"] = next_version
        current = next_version

    return config
