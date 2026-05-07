from flask import Flask, render_template, jsonify
from flask_restx import Resource, Api
from pokedex import Pokedex, PokedexError

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Pokédex API",
    description="REST API backed by the PokeAPI",
    doc="/api/docs",
    prefix="/api",
)
 
dex = Pokedex()
 
ns = api.namespace("pokemon", description="Pokemon operations")
 
# Helper

def _error(message: str, code: int = 404):
    return {"error": message}, code
 
# Routes
 
@ns.route("/search/<string:name_or_id>")
@ns.doc(params={"name_or_id": "Pokemon name (e.g. pikachu) or national dex number"})
class PokemonSearch(Resource):
    def get(self, name_or_id):
        """Fetch a Pokemon by name or dex number."""
        try:
            pokemon = dex.search(name_or_id)
            result = pokemon.to_dict()
            result["description"] = dex.get_species_description(pokemon)
            return result
        except PokedexError as exc:
            return _error(str(exc))
 
 
@ns.route("/random")
class PokemonRandom(Resource):
    def get(self):
        """Fetch a completely random Pokemon."""
        try:
            pokemon = dex.random_pokemon()
            result = pokemon.to_dict()
            result["description"] = dex.get_species_description(pokemon)
            return result
        except PokedexError as exc:
            return _error(str(exc), 500)
 
 
@ns.route("/evolution/<string:name_or_id>")
@ns.doc(params={"name_or_id": "Pokemon name or dex number"})
class PokemonEvolution(Resource):
    def get(self, name_or_id):
        """
        Return the evolution chain for a Pokemon.
        Each stage is an object with name and sprite_url.
        """
        try:
            pokemon = dex.search(name_or_id)
            stages = dex.get_evolution_chain(pokemon)
            sprites = dex.get_evolution_sprites(stages)
 
            chain = [
                [{"name": name, "sprite_url": sprites.get(name, "")} for name in stage]
                for stage in stages
            ]
            return {"chain": chain}
        except PokedexError as exc:
            return _error(str(exc))
 
# UI routes (served by Flask templates)
 
@app.route("/")
def index():
    return render_template("index.html")
 
 
if __name__ == "__main__":
    app.run(debug=False)