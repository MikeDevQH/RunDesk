"""
Command Parser — coordina resolución de texto a comando/escena.
Pipeline: texto → alias exacto → fuzzy match → resultado.
"""

import logging

from app.core.input.alias_resolver import AliasResolver
from app.core.input.fuzzy_matcher import FuzzyMatcher

logger = logging.getLogger(__name__)


class ParseResult:
    """Resultado de parsear un input del usuario."""

    def __init__(
        self,
        matched: bool,
        match_type: str = "",
        item: dict | None = None,
        score: float = 0.0,
        original_text: str = "",
    ):
        self.matched = matched
        self.match_type = match_type  # "exact", "fuzzy", ""
        self.item = item  # {type, id, name, data}
        self.score = score  # 0.0-1.0
        self.original_text = original_text

    def __repr__(self):
        if self.matched:
            return (
                f"ParseResult(matched=True, type={self.match_type}, "
                f"id={self.item['id']}, score={self.score:.2f})"
            )
        return f"ParseResult(matched=False, text='{self.original_text}')"


class CommandParser:
    """Parsea el input del usuario y resuelve a comando o escena.

    Pipeline:
        1. Normalizar texto (strip, lowercase)
        2. Intentar resolución exacta por alias
        3. Si no hay exacto, intentar fuzzy matching
        4. Retornar ParseResult con el mejor match
    """

    def __init__(self, alias_resolver: AliasResolver, fuzzy_matcher: FuzzyMatcher):
        self._resolver = alias_resolver
        self._fuzzy = fuzzy_matcher

    def parse(self, text: str) -> ParseResult:
        """Resuelve texto a comando o escena.

        Args:
            text: input raw del usuario

        Returns:
            ParseResult con match o sin match
        """
        normalized = text.strip()
        if not normalized:
            return ParseResult(matched=False, original_text=text)

        # 1. Match exacto por alias
        exact = self._resolver.resolve(normalized)
        if exact:
            logger.info("Match exacto: '%s' → %s", normalized, exact["id"])
            return ParseResult(
                matched=True,
                match_type="exact",
                item=exact,
                score=1.0,
                original_text=text,
            )

        # 2. Fuzzy match
        candidates = self._resolver.get_all_aliases()
        best_alias, score = self._fuzzy.best_match(normalized, candidates)
        if best_alias:
            item = self._resolver.resolve(best_alias)
            if item:
                logger.info(
                    "Match fuzzy: '%s' → '%s' → %s (score=%.2f)",
                    normalized, best_alias, item["id"], score,
                )
                return ParseResult(
                    matched=True,
                    match_type="fuzzy",
                    item=item,
                    score=score,
                    original_text=text,
                )

        logger.info("Sin match para: '%s'", normalized)
        return ParseResult(matched=False, original_text=text)

    def get_suggestions(self, text: str, limit: int = 5) -> list[dict]:
        """Retorna sugerencias en tiempo real mientras el usuario escribe.

        Returns:
            Lista de dicts: [{id, name, type, alias, score}]
        """
        normalized = text.strip()
        if not normalized:
            return []

        # Match exacto primero
        exact = self._resolver.resolve(normalized)
        if exact:
            return [{
                "id": exact["id"],
                "name": exact["name"],
                "type": exact["type"],
                "alias": normalized,
                "score": 1.0,
            }]

        # Fuzzy top matches
        candidates = self._resolver.get_all_aliases()
        top = self._fuzzy.top_matches(normalized, candidates, limit=limit)

        suggestions = []
        seen_ids = set()
        for alias, score in top:
            item = self._resolver.resolve(alias)
            if item and item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                suggestions.append({
                    "id": item["id"],
                    "name": item["name"],
                    "type": item["type"],
                    "alias": alias,
                    "score": score,
                })

        return suggestions
