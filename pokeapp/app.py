from flask import Flask
from flask_restx import Resource, Api
import requests

app = Flask(__name__)
api = Api(app)

pokemon_name="clefairy"

@api.route('/get_pokemon_info')
class PokemonFinder(Resource):
    def get(self):
        pokemon = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        pokemon_json = pokemon.json()
        return pokemon_json
        
        

if __name__ == '__main__':
    app.run(debug=False)