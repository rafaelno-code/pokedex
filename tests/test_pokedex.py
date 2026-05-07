"""
tests/test_pokedex.py
Unit tests for the Pokedex class — all HTTP calls are mocked.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from pokedex import Pokedex, PokedexError
from pokemon import Pokemon

# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

BULBASAUR_DATA = {
    "id": 1, "name": "bulbasaur", "weight": 69, "height": 7,
    "base_experience": 64,
    "species": {"url": "https://pokeapi.co/api/v2/pokemon-species/1/"},
    "types": [{"type": {"name": "grass"}}, {"type": {"name": "poison"}}],
    "abilities": [{"ability": {"name": "overgrow"}}],
    "stats": [
        {"stat": {"name": "hp"}, "base_stat": 45},
        {"stat": {"name": "attack"}, "base_stat": 49},
        {"stat": {"name": "defense"}, "base_stat": 49},
        {"stat": {"name": "special-attack"}, "base_stat": 65},
        {"stat": {"name": "special-defense"}, "base_stat": 65},
        {"stat": {"name": "speed"}, "base_stat": 45},
    ],
    "sprites": {"front_default": "https://example.com/bulbasaur.png", "front_shiny": ""},
}

SPECIES_DATA = {
    "evolution_chain": {"url": "https://pokeapi.co/api/v2/evolution-chain/1/"},
    "flavor_text_entries": [
        {"flavor_text": "A strange seed\nwas planted.", "language": {"name": "en"}},
        {"flavor_text": "Un étrange graine.", "language": {"name": "fr"}},
    ],
}

CHAIN_DATA = {
    "chain": {
        "species": {"name": "bulbasaur"},
        "evolves_to": [{
            "species": {"name": "ivysaur"},
            "evolves_to": [{
                "species": {"name": "venusaur"},
                "evolves_to": [],
            }],
        }],
    }
}


def _mock_get(url, timeout=10):
    resp = MagicMock()
    resp.ok = True
    resp.status_code = 200
    if "pokemon/bulbasaur" in url or "pokemon/1" in url:
        resp.json.return_value = BULBASAUR_DATA
    elif "pokemon-species" in url:
        resp.json.return_value = SPECIES_DATA
    elif "evolution-chain" in url:
        resp.json.return_value = CHAIN_DATA
    else:
        resp.json.return_value = BULBASAUR_DATA
    return resp


@pytest.fixture
def dex():
    return Pokedex()


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------

class TestPokedexSearch:
    @patch("requests.get", side_effect=_mock_get)
    def test_search_by_name(self, _mock, dex):
        poke = dex.search("bulbasaur")
        assert isinstance(poke, Pokemon)
        assert poke.name == "bulbasaur"

    @patch("requests.get", side_effect=_mock_get)
    def test_search_by_id(self, _mock, dex):
        poke = dex.search(1)
        assert poke.pokemon_id == 1

    @patch("requests.get", side_effect=_mock_get)
    def test_search_case_insensitive(self, _mock, dex):
        poke = dex.search("BULBASAUR")
        assert poke.name == "bulbasaur"

    def test_search_empty_raises(self, dex):
        with pytest.raises(PokedexError, match="empty"):
            dex.search("   ")

    @patch("requests.get")
    def test_search_not_found_raises(self, mock_get, dex):
        mock_get.return_value = MagicMock(ok=False, status_code=404)
        with pytest.raises(PokedexError):
            dex.search("notapokemon")


# ---------------------------------------------------------------------------
# random_pokemon()
# ---------------------------------------------------------------------------

class TestPokedexRandom:
    @patch("requests.get", side_effect=_mock_get)
    @patch("random.randint", return_value=1)
    def test_returns_pokemon(self, _rand, _get, dex):
        poke = dex.random_pokemon()
        assert isinstance(poke, Pokemon)

    @patch("requests.get", side_effect=_mock_get)
    def test_called_multiple_times(self, _mock, dex):
        results = [dex.random_pokemon() for _ in range(5)]
        assert all(isinstance(p, Pokemon) for p in results)


# ---------------------------------------------------------------------------
# get_evolution_chain()
# ---------------------------------------------------------------------------

class TestPokedexEvolution:
    @patch("requests.get", side_effect=_mock_get)
    def test_chain_structure(self, _mock, dex):
        poke = dex.search("bulbasaur")
        stages = dex.get_evolution_chain(poke)
        # Bulbasaur → Ivysaur → Venusaur = 3 stages
        assert len(stages) == 3
        assert stages[0] == ["bulbasaur"]
        assert stages[1] == ["ivysaur"]
        assert stages[2] == ["venusaur"]

    @patch("requests.get", side_effect=_mock_get)
    def test_chain_names_are_strings(self, _mock, dex):
        poke = dex.search("bulbasaur")
        stages = dex.get_evolution_chain(poke)
        for stage in stages:
            for name in stage:
                assert isinstance(name, str)


# ---------------------------------------------------------------------------
# get_species_description()
# ---------------------------------------------------------------------------

class TestPokedexDescription:
    @patch("requests.get", side_effect=_mock_get)
    def test_returns_english(self, _mock, dex):
        poke = dex.search("bulbasaur")
        desc = dex.get_species_description(poke)
        assert "strange seed" in desc.lower()

    @patch("requests.get", side_effect=_mock_get)
    def test_no_newlines(self, _mock, dex):
        poke = dex.search("bulbasaur")
        desc = dex.get_species_description(poke)
        assert "\n" not in desc
        assert "\f" not in desc
