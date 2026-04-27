"""
Alias Resolver — mapea aliases a comandos y escenas.
Construye un índice invertido de alias → item para resolución rápida.
"""


class AliasResolver:
    """Resuelve un alias de texto al comando o escena correspondiente.

    El índice se construye a partir de las listas de comandos y escenas,
    usando el campo 'aliases' de cada item. También indexa por 'name'.
    """

    def __init__(self):
        self._index: dict[str, dict] = {}

    def build_index(self, commands: list[dict], scenes: list[dict] | None = None):
        """Reconstruye el índice de aliases.

        Args:
            commands: lista de comandos (solo enabled)
            scenes: lista de escenas (solo enabled)
        """
        self._index.clear()

        for cmd in commands:
            item = {
                "type": "command",
                "id": cmd["id"],
                "name": cmd.get("name", ""),
                "data": cmd,
            }
            # Indexar por cada alias
            for alias in cmd.get("aliases", []):
                self._index[alias.lower().strip()] = item
            # Indexar por nombre completo
            name = cmd.get("name", "").lower().strip()
            if name and name not in self._index:
                self._index[name] = item

        for scene in scenes or []:
            item = {
                "type": "scene",
                "id": scene["id"],
                "name": scene.get("name", ""),
                "data": scene,
            }
            for alias in scene.get("aliases", []):
                self._index[alias.lower().strip()] = item
            name = scene.get("name", "").lower().strip()
            if name and name not in self._index:
                self._index[name] = item

    def resolve(self, text: str) -> dict | None:
        """Busca coincidencia exacta por alias o nombre.

        Returns:
            Dict con {type, id, name, data} o None si no hay match exacto.
        """
        return self._index.get(text.lower().strip())

    def get_all_aliases(self) -> list[str]:
        """Retorna todas las claves del índice (aliases + nombres)."""
        return list(self._index.keys())

    def get_all_entries(self) -> list[dict]:
        """Retorna todos los entries únicos del índice (sin duplicados por alias)."""
        seen = set()
        entries = []
        for entry in self._index.values():
            if entry["id"] not in seen:
                seen.add(entry["id"])
                entries.append(entry)
        return entries
