"""
Command Router — orquesta el flujo completo:
texto del usuario → parser → confirmación (si aplica) → ejecución → resultado.
"""

import logging
import time

from app.core.actions.action_executor import ActionExecutor, ActionResult
from app.core.input.command_parser import CommandParser

logger = logging.getLogger(__name__)


class CommandRouter:
    """Conecta el parser de comandos con el executor de acciones.

    Flujo:
        1. Recibe texto raw del overlay
        2. Parsea con CommandParser (alias + fuzzy)
        3. Verifica si requiere confirmación → pregunta al usuario
        4. Ejecuta con ActionExecutor
        5. Retorna resultado
    """

    def __init__(self, parser: CommandParser, executor: ActionExecutor):
        self._parser = parser
        self._executor = executor
        self._confirm_callback: callable | None = None

    def set_confirm_callback(self, callback: callable):
        """Registra un callback para confirmar acciones críticas.

        callback(cmd_name: str) -> bool: retorna True si el usuario confirma.
        """
        self._confirm_callback = callback

    def route(self, text: str) -> ActionResult:
        """Procesa un texto de entrada y ejecuta la acción correspondiente.

        Args:
            text: texto crudo del usuario desde el overlay

        Returns:
            ActionResult con éxito/error y mensaje
        """
        result = self._parser.parse(text)

        if not result.matched:
            logger.info("Sin match para: '%s'", text)
            return ActionResult(False, f"Comando no encontrado: {text}")

        command_data = result.item["data"]
        cmd_name = result.item["name"]
        cmd_type = result.item["type"]

        # Verificar confirmación requerida
        if command_data.get("confirm_required"):
            if self._confirm_callback:
                confirmed = self._confirm_callback(cmd_name)
                if not confirmed:
                    return ActionResult(False, f"Cancelado: {cmd_name}")
            else:
                logger.warning("Ejecutando '%s' sin confirmación (no hay callback)", cmd_name)

        # Ejecutar según tipo
        if cmd_type == "command":
            action_result = self._executor.execute(command_data)
        elif cmd_type == "scene":
            action_result = self._execute_scene(command_data)
        else:
            action_result = ActionResult(False, f"Tipo desconocido: {cmd_type}")

        # Log
        if action_result.success:
            logger.info("✓ %s — %s", cmd_name, action_result.message)
        else:
            logger.warning("✗ %s — %s", cmd_name, action_result.message)

        return action_result

    def _execute_scene(self, scene_data: dict) -> ActionResult:
        """Ejecuta los pasos de una escena en secuencia.

        Soporta:
        - Pasos normales (program, url, folder, etc.) con window positioning
        - Pasos de delay (type: "delay") con milliseconds
        - Pasos deshabilitados (enabled: False) se omiten
        """
        steps = scene_data.get("steps", [])
        if not steps:
            return ActionResult(False, "Escena sin pasos definidos")

        executed = 0
        errors = []

        for i, step in enumerate(steps, 1):
            # Omitir pasos deshabilitados
            if not step.get("enabled", True):
                continue

            # Paso de delay
            if step.get("type") == "delay":
                ms = step.get("milliseconds", 500)
                time.sleep(ms / 1000.0)
                executed += 1
                continue

            result = self._executor.execute(step)
            if result.success:
                executed += 1
            else:
                errors.append(f"Paso {i}: {result.message}")

        if errors:
            return ActionResult(
                False,
                f"Escena parcial: {executed}/{len(steps)} pasos. Errores: {'; '.join(errors)}",
            )
        return ActionResult(True, f"Escena completada: {executed} pasos ejecutados")

    @property
    def parser(self) -> CommandParser:
        """Acceso al parser para uso externo (sugerencias)."""
        return self._parser
