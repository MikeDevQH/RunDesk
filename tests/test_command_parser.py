"""Tests para el pipeline de parsing: AliasResolver, FuzzyMatcher, CommandParser."""

import pytest

from app.core.input.alias_resolver import AliasResolver
from app.core.input.command_parser import CommandParser
from app.core.input.fuzzy_matcher import FuzzyMatcher

# --- Fixtures ---

SAMPLE_COMMANDS = [
    {
        "id": "cmd_youtube",
        "name": "Abrir YouTube",
        "aliases": ["youtube", "yt", "ytt"],
        "enabled": True,
        "type": "open_url",
        "category": "web",
    },
    {
        "id": "cmd_calculator",
        "name": "Abrir Calculadora",
        "aliases": ["calculadora", "calc"],
        "enabled": True,
        "type": "open_app",
        "category": "utilidades",
    },
    {
        "id": "cmd_shutdown",
        "name": "Apagar PC",
        "aliases": ["apagar", "shutdown"],
        "enabled": True,
        "type": "system",
        "category": "sistema",
    },
    {
        "id": "cmd_disabled",
        "name": "Comando desactivado",
        "aliases": ["desactivado"],
        "enabled": False,
        "type": "open_app",
        "category": "otros",
    },
]

SAMPLE_SCENES = [
    {
        "id": "scene_work",
        "name": "Modo trabajo",
        "aliases": ["trabajo", "work"],
        "enabled": True,
        "steps": [{"action": "open_app", "target": "code"}],
    },
]


@pytest.fixture
def resolver():
    r = AliasResolver()
    # Solo enabled
    enabled = [c for c in SAMPLE_COMMANDS if c.get("enabled", True)]
    r.build_index(enabled, SAMPLE_SCENES)
    return r


@pytest.fixture
def fuzzy():
    return FuzzyMatcher(threshold=0.65)


@pytest.fixture
def parser(resolver, fuzzy):
    return CommandParser(resolver, fuzzy)


# === AliasResolver ===


class TestAliasResolver:
    def test_resolve_exact_alias(self, resolver):
        result = resolver.resolve("yt")
        assert result is not None
        assert result["id"] == "cmd_youtube"

    def test_resolve_by_name(self, resolver):
        result = resolver.resolve("Abrir YouTube")
        assert result is not None
        assert result["id"] == "cmd_youtube"

    def test_resolve_case_insensitive(self, resolver):
        result = resolver.resolve("YOUTUBE")
        assert result is not None
        assert result["id"] == "cmd_youtube"

    def test_resolve_none_for_unknown(self, resolver):
        assert resolver.resolve("xyznonexistent") is None

    def test_resolve_scene(self, resolver):
        result = resolver.resolve("trabajo")
        assert result is not None
        assert result["type"] == "scene"
        assert result["id"] == "scene_work"

    def test_disabled_commands_not_indexed(self, resolver):
        assert resolver.resolve("desactivado") is None

    def test_get_all_aliases_returns_list(self, resolver):
        aliases = resolver.get_all_aliases()
        assert isinstance(aliases, list)
        assert "yt" in aliases
        assert "calculadora" in aliases
        assert "trabajo" in aliases

    def test_get_all_entries_no_duplicates(self, resolver):
        entries = resolver.get_all_entries()
        ids = [e["id"] for e in entries]
        assert len(ids) == len(set(ids))


# === FuzzyMatcher ===


class TestFuzzyMatcher:
    def test_exact_match_high_score(self, fuzzy):
        best, score = fuzzy.best_match("youtube", ["youtube", "calculadora"])
        assert best == "youtube"
        assert score >= 0.95

    def test_typo_still_matches(self, fuzzy):
        best, score = fuzzy.best_match("yuotube", ["youtube", "calculadora", "apagar"])
        assert best == "youtube"
        assert score >= 0.65

    def test_no_match_below_threshold(self):
        strict = FuzzyMatcher(threshold=0.99)
        best, score = strict.best_match("xyz", ["youtube", "calculadora"])
        assert best is None
        assert score == 0.0

    def test_empty_query_returns_none(self, fuzzy):
        best, _score = fuzzy.best_match("", ["youtube"])
        assert best is None

    def test_empty_candidates_returns_none(self, fuzzy):
        best, _score = fuzzy.best_match("youtube", [])
        assert best is None

    def test_top_matches_returns_sorted(self, fuzzy):
        results = fuzzy.top_matches(
            "calc", ["calculadora", "calc", "youtube", "apagar"], limit=3
        )
        assert len(results) > 0
        # First result should be best
        assert results[0][0] in ("calc", "calculadora")

    def test_threshold_setter_clamps(self, fuzzy):
        fuzzy.threshold = -0.5
        assert fuzzy.threshold == 0.0
        fuzzy.threshold = 2.0
        assert fuzzy.threshold == 1.0


# === CommandParser ===


class TestCommandParser:
    def test_parse_exact_alias(self, parser):
        result = parser.parse("yt")
        assert result.matched is True
        assert result.match_type == "exact"
        assert result.item["id"] == "cmd_youtube"
        assert result.score == 1.0

    def test_parse_fuzzy_typo(self, parser):
        result = parser.parse("yuotube")
        assert result.matched is True
        assert result.match_type == "fuzzy"
        assert result.item["id"] == "cmd_youtube"
        assert result.score >= 0.65

    def test_parse_no_match(self, parser):
        result = parser.parse("xyznonexistent123")
        assert result.matched is False

    def test_parse_empty(self, parser):
        result = parser.parse("")
        assert result.matched is False

    def test_parse_scene_alias(self, parser):
        result = parser.parse("trabajo")
        assert result.matched is True
        assert result.item["type"] == "scene"

    def test_suggestions_exact(self, parser):
        suggestions = parser.get_suggestions("yt")
        assert len(suggestions) == 1
        assert suggestions[0]["id"] == "cmd_youtube"
        assert suggestions[0]["score"] == 1.0

    def test_suggestions_fuzzy(self, parser):
        suggestions = parser.get_suggestions("calcu")
        assert len(suggestions) >= 1
        ids = [s["id"] for s in suggestions]
        assert "cmd_calculator" in ids

    def test_suggestions_empty_input(self, parser):
        assert parser.get_suggestions("") == []

    def test_suggestions_limit(self, parser):
        suggestions = parser.get_suggestions("a", limit=2)
        assert len(suggestions) <= 2

    def test_parse_result_repr(self, parser):
        r1 = parser.parse("yt")
        assert "matched=True" in repr(r1)
        r2 = parser.parse("xyznonexistent")
        assert "matched=False" in repr(r2)
