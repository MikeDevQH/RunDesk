"""
Fuzzy Matcher — tolerancia a errores tipográficos.
Usa rapidfuzz para encontrar coincidencias aproximadas
entre el input del usuario y los aliases/nombres de comandos.
"""

from rapidfuzz import fuzz, process


class FuzzyMatcher:
    """Resuelve texto con tolerancia a typos contra un catálogo de strings."""

    def __init__(self, threshold: float = 0.65):
        self._threshold = threshold

    @property
    def threshold(self) -> float:
        return self._threshold

    @threshold.setter
    def threshold(self, value: float):
        self._threshold = max(0.0, min(1.0, value))

    def best_match(self, query: str, candidates: list[str]) -> tuple[str | None, float]:
        """Retorna el mejor match y su score (0-1). None si está por debajo del threshold.

        Args:
            query: texto del usuario
            candidates: lista de strings contra los que comparar

        Returns:
            (mejor_candidate, score) o (None, 0.0) si no hay match
        """
        if not query or not candidates:
            return None, 0.0

        result = process.extractOne(
            query.lower(),
            [c.lower() for c in candidates],
            scorer=fuzz.WRatio,
            score_cutoff=self._threshold * 100,
        )

        if result is None:
            return None, 0.0

        _matched_text, score, index = result
        return candidates[index], score / 100.0

    def top_matches(
        self, query: str, candidates: list[str], limit: int = 5
    ) -> list[tuple[str, float]]:
        """Retorna los mejores N matches con score >= threshold.

        Args:
            query: texto del usuario
            candidates: lista de strings
            limit: máximo de resultados

        Returns:
            Lista de (candidate, score) ordenada por score descendente
        """
        if not query or not candidates:
            return []

        results = process.extract(
            query.lower(),
            [c.lower() for c in candidates],
            scorer=fuzz.WRatio,
            limit=limit,
            score_cutoff=self._threshold * 100,
        )

        return [(candidates[idx], score / 100.0) for _, score, idx in results]
