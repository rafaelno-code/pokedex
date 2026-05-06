class Pokemon:
    """
    Represents a Pokemon with data sourced from the PokeAPI.
    Stores identity, physical traits, battle stats, types, abilities,
    sprites, and species metadata.
    """
 
    def __init__(
        self,
        name: str,
        pokemon_id: int,
        weight: int,
        height: int,
        types: list[str],
        abilities: list[str],
        stats: dict[str, int],
        sprite_url: str,
        sprite_shiny_url: str,
        base_experience: int,
        species_url: str,
    ):
        self.name = name
        self.pokemon_id = pokemon_id
        self.weight = weight          # in hectograms (divide by 10 for kg)
        self.height = height          # in decimetres  (divide by 10 for m)
        self.types = types            # e.g. ["fire", "flying"]
        self.abilities = abilities    # e.g. ["blaze", "solar-power"]
        self.stats = stats            # e.g. {"hp": 45, "attack": 49, ...}
        self.sprite_url = sprite_url
        self.sprite_shiny_url = sprite_shiny_url
        self.base_experience = base_experience
        self.species_url = species_url
 
    # Convenience helpers
 
    @property
    def weight_kg(self) -> float:
        return self.weight / 10
 
    @property
    def height_m(self) -> float:
        return self.height / 10
 
    @property
    def total_base_stats(self) -> int:
        return sum(self.stats.values())
 
    def to_dict(self) -> dict:
        """Serialise to a plain dictionary (JSON-friendly)."""
        return {
            "name": self.name,
            "id": self.pokemon_id,
            "weight_kg": self.weight_kg,
            "height_m": self.height_m,
            "types": self.types,
            "abilities": self.abilities,
            "stats": self.stats,
            "total_base_stats": self.total_base_stats,
            "sprite_url": self.sprite_url,
            "sprite_shiny_url": self.sprite_shiny_url,
            "base_experience": self.base_experience,
            "species_url": self.species_url,
        }
 
    def __repr__(self) -> str:
        return (
            f"Pokemon(name={self.name!r}, id={self.pokemon_id}, "
            f"types={self.types}, total_stats={self.total_base_stats})"
        )
 
    # Factory
 
    @classmethod
    def from_api_response(cls, data: dict) -> "Pokemon":
        """
        Build a Pokemon instance directly from the raw PokeAPI
        /pokemon/{name} response dictionary.
        """
        name = data["name"]
        pokemon_id = data["id"]
        weight = data["weight"]
        height = data["height"]
        base_experience = data.get("base_experience") or 0
        species_url = data.get("species", {}).get("url", "")
 
        types = [t["type"]["name"] for t in data.get("types", [])]
        abilities = [a["ability"]["name"] for a in data.get("abilities", [])]
 
        stats = {
            s["stat"]["name"]: s["base_stat"]
            for s in data.get("stats", [])
        }
 
        sprites = data.get("sprites", {})
        sprite_url = sprites.get("front_default") or ""
        sprite_shiny_url = sprites.get("front_shiny") or ""
 
        return cls(
            name=name,
            pokemon_id=pokemon_id,
            weight=weight,
            height=height,
            types=types,
            abilities=abilities,
            stats=stats,
            sprite_url=sprite_url,
            sprite_shiny_url=sprite_shiny_url,
            base_experience=base_experience,
            species_url=species_url,
        )