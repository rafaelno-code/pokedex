"""
tests/test_api.py
Integration tests for the Flask API endpoints.
All PokeAPI calls are mocked via the Pokedex class.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from app import app as flask_app
from pokemon import Pokemon

# ---------------------------------------------------------------------------
# Shared fake Pokemon
# ---------------------------------------------------------------------------

def _fake_pokemon():
    return Pokemon(
        name="pikachu",
        pokemon_id=25,
        weight=60,
        height=4,
        types=["electric"],
        abilities=["static", "lightning-rod"],
        stats={"hp": 35, "attack": 55, "defense": 40,
               "special-attack": 50, "special-defense": 50, "speed": 90},
        sprite_url="https://example.com/pikachu.png",
        sprite_shiny_url="https://example.com/pikachu_shiny.png",
        base_experience=112,
        species_url="https://pokeapi.co/api/v2/pokemon-species/25/",
    )


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# /api/pokemon/search/<name>
# ---------------------------------------------------------------------------

class TestSearchEndpoint:
    @patch("app.dex.search", return_value=_fake_pokemon())
    @patch("app.dex.get_species_description", return_value="An electric mouse Pokemon.")
    def test_search_success(self, _desc, _search, client):
        resp = client.get("/api/pokemon/search/pikachu")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "pikachu"
        assert data["description"] == "An electric mouse Pokemon."

    @patch("app.dex.search", side_effect=Exception("not found"))
    def test_search_not_found(self, _mock, client):
        resp = client.get("/api/pokemon/search/notapokemon")
        assert resp.status_code in (404, 500)


# ---------------------------------------------------------------------------
# /api/pokemon/random
# ---------------------------------------------------------------------------

class TestRandomEndpoint:
    @patch("app.dex.random_pokemon", return_value=_fake_pokemon())
    @patch("app.dex.get_species_description", return_value="Zap!")
    def test_random_returns_pokemon(self, _desc, _rand, client):
        resp = client.get("/api/pokemon/random")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "name" in data
        assert "types" in data


# ---------------------------------------------------------------------------
# /api/pokemon/evolution/<name>
# ---------------------------------------------------------------------------

class TestEvolutionEndpoint:
    @patch("app.dex.search", return_value=_fake_pokemon())
    @patch("app.dex.get_evolution_chain", return_value=[["pichu"], ["pikachu"], ["raichu"]])
    @patch("app.dex.get_evolution_sprites", return_value={
        "pichu": "pichu.png", "pikachu": "pikachu.png", "raichu": "raichu.png"
    })
    def test_evolution_chain(self, _sprites, _chain, _search, client):
        resp = client.get("/api/pokemon/evolution/pikachu")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "chain" in data
        assert len(data["chain"]) == 3

    @patch("app.dex.search", side_effect=Exception("not found"))
    def test_evolution_not_found(self, _mock, client):
        resp = client.get("/api/pokemon/evolution/fakemon")
        assert resp.status_code in (404, 500)


# ---------------------------------------------------------------------------
# UI route
# ---------------------------------------------------------------------------

class TestUIRoute:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"html" in resp.data.lower()
