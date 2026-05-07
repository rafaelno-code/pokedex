import random
import requests
from pokemon import Pokemon

BASE_URL = "https://pokeapi.co/api/v2"
TOTAL_POKEMON = 1025   # Gen 1-9 national dex ceiling (as of API v2)


class PokedexError(Exception):
    """Raised when a Pokedex operation fails (not-found, network, etc.)."""


class Pokedex:
    """
    Provides lookup and navigation utilities backed by the PokeAPI.

    All network calls raise PokedexError on failure so callers never
    need to handle raw requests exceptions.
    """

    # Internal helpers

    @staticmethod
    def _get(url: str) -> dict:
        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as exc:
            raise PokedexError(f"Network error: {exc}") from exc

        if response.status_code == 404:
            raise PokedexError(f"Resource not found: {url}")
        if not response.ok:
            raise PokedexError(
                f"API returned {response.status_code} for {url}"
            )
        return response.json()

    # Public API

    def search(self, name_or_id: str | int) -> Pokemon:
        """
        Fetch a Pokemon by name (case-insensitive) or national dex ID.

        Returns a fully populated Pokemon instance.
        Raises PokedexError if the Pokemon is not found.
        """
        query = str(name_or_id).strip().lower()
        if not query:
            raise PokedexError("Search query cannot be empty.")

        url = f"{BASE_URL}/pokemon/{query}/"
        data = self._get(url)
        return Pokemon.from_api_response(data)

    def random_pokemon(self) -> Pokemon:
        """Return a randomly selected Pokemon from the national dex."""
        dex_number = random.randint(1, TOTAL_POKEMON)
        return self.search(dex_number)

    def get_evolution_chain(self, pokemon: Pokemon) -> list[list[str]]:
        """
        Return the evolution chain for the given Pokemon as a list of
        stages, where each stage is a list of names (for branching evos).

        Example — Eevee:
            [["eevee"], ["vaporeon", "jolteon", "flareon", ...]]

        Example — Bulbasaur:
            [["bulbasaur"], ["ivysaur"], ["venusaur"]]
        """
        species_data = self._get(pokemon.species_url)
        chain_url = species_data["evolution_chain"]["url"]
        chain_data = self._get(chain_url)

        stages: list[list[str]] = []
        self._walk_chain(chain_data["chain"], stages)
        return stages

    def _walk_chain(self, node: dict, stages: list[list[str]]) -> None:
        """
        Recursively walk the evolution chain tree, collapsing each
        depth-level into a single stage list to handle branching.
        """
        depth = len(stages)
        name = node["chain_link"] if "chain_link" in node else node.get("species", {}).get("name", "")

        # PokeAPI uses 'species' at each node
        name = node.get("species", {}).get("name", "")

        if depth >= len(stages):
            stages.append([])
        if name:
            stages[depth].append(name)

        for evolution in node.get("evolves_to", []):
            self._walk_chain(evolution, stages)

    def get_species_description(self, pokemon: Pokemon) -> str:
        """
        Return the first English Pokedex flavour text for the Pokemon.
        Falls back to an empty string when none is available.
        """
        species_data = self._get(pokemon.species_url)
        for entry in species_data.get("flavor_text_entries", []):
            if entry.get("language", {}).get("name") == "en":
                # Replace awkward whitespace / form-feed chars
                return (
                    entry["flavor_text"]
                    .replace("\n", " ")
                    .replace("\f", " ")
                    .strip()
                )
        return ""

    def get_evolution_sprites(self, stages: list[list[str]]) -> dict[str, str]:
        """
        Given a list of evolution stages (from get_evolution_chain),
        return a mapping of pokemon_name -> sprite_url for each member.
        """
        sprites: dict[str, str] = {}
        for stage in stages:
            for name in stage:
                try:
                    poke = self.search(name)
                    sprites[name] = poke.sprite_url
                except PokedexError:
                    sprites[name] = ""
        return sprites
