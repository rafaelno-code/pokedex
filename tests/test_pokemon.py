"""
tests/test_pokemon.py
Unit tests for the Pokemon class and its factory method.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pokemon import Pokemon

# ---------------------------------------------------------------------------
# Minimal fake API payload (mirrors real PokeAPI shape)
# ---------------------------------------------------------------------------
FAKE_API_DATA = {
    "id": 4,
    "name": "charmander",
    "weight": 85,
    "height": 6,
    "base_experience": 62,
    "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/4/"},
    "types": [{"type": {"name": "fire"}}],
    "abilities": [
        {"ability": {"name": "blaze"}},
        {"ability": {"name": "solar-power"}},
    ],
    "stats": [
        {"stat": {"name": "hp"}, "base_stat": 39},
        {"stat": {"name": "attack"}, "base_stat": 52},
        {"stat": {"name": "defense"}, "base_stat": 43},
        {"stat": {"name": "special-attack"}, "base_stat": 60},
        {"stat": {"name": "special-defense"}, "base_stat": 50},
        {"stat": {"name": "speed"}, "base_stat": 65},
    ],
    "sprites": {
        "front_default": "https://example.com/charmander.png",
        "front_shiny": "https://example.com/charmander_shiny.png",
    },
}


@pytest.fixture
def charmander() -> Pokemon:
    return Pokemon.from_api_response(FAKE_API_DATA)


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------

class TestPokemonFactory:
    def test_name(self, charmander):
        assert charmander.name == "charmander"

    def test_id(self, charmander):
        assert charmander.pokemon_id == 4

    def test_types(self, charmander):
        assert charmander.types == ["fire"]

    def test_abilities(self, charmander):
        assert "blaze" in charmander.abilities
        assert "solar-power" in charmander.abilities

    def test_stats_keys(self, charmander):
        expected = {"hp", "attack", "defense", "special-attack", "special-defense", "speed"}
        assert set(charmander.stats.keys()) == expected

    def test_sprites(self, charmander):
        assert "charmander.png" in charmander.sprite_url
        assert "shiny" in charmander.sprite_shiny_url

    def test_species_url(self, charmander):
        assert "pokemon-species/4" in charmander.species_url


# ---------------------------------------------------------------------------
# Property / helper tests
# ---------------------------------------------------------------------------

class TestPokemonProperties:
    def test_weight_kg(self, charmander):
        assert charmander.weight_kg == pytest.approx(8.5)

    def test_height_m(self, charmander):
        assert charmander.height_m == pytest.approx(0.6)

    def test_total_base_stats(self, charmander):
        assert charmander.total_base_stats == 39 + 52 + 43 + 60 + 50 + 65

    def test_to_dict_keys(self, charmander):
        d = charmander.to_dict()
        for key in ("name", "id", "types", "abilities", "stats", "total_base_stats"):
            assert key in d

    def test_repr(self, charmander):
        assert "charmander" in repr(charmander)
        assert "fire" in repr(charmander)


# ---------------------------------------------------------------------------
# Edge-case construction
# ---------------------------------------------------------------------------

class TestPokemonEdgeCases:
    def test_missing_base_experience(self):
        data = dict(FAKE_API_DATA)
        data["base_experience"] = None
        poke = Pokemon.from_api_response(data)
        assert poke.base_experience == 0

    def test_no_species_url(self):
        data = dict(FAKE_API_DATA)
        data["species"] = {}
        poke = Pokemon.from_api_response(data)
        assert poke.species_url == ""

    def test_empty_types(self):
        data = dict(FAKE_API_DATA)
        data["types"] = []
        poke = Pokemon.from_api_response(data)
        assert poke.types == []
