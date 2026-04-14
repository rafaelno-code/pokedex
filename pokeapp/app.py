from flask import Flask
from flask_restx import Resource, Api
import requests

app = Flask(__name__)
api = Api(app)

#hardcoded for now
pokemon_name="clefairy"

#Accesses pokemon GET endpoint to give holistic pokemon information
#returns whole pokemon JSON in the form of a dictionary
@api.route('/get_pokemon_info')
class PokemonFinder(Resource):
    def get(self):
        pokemon = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        pokemon_json = pokemon.json()

        return pokemon_json

if __name__ == '__main__':
    app.run(debug=False)