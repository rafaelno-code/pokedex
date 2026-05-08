# Pokédex

A web app that lets you look up any Pokémon using the [PokeAPI](https://pokeapi.co/). Search by name or Pokédex number, discover a random Pokémon, and explore full evolution chains — complete with stats, type badges, abilities, shiny sprites, and Pokédex descriptions.

## Prerequisites

- Python 3.10+
- pip

## Setup & Running

```bash
# Install dependencies (from project root)
pip install -r requirements.txt

# Start the app (from inside pokeapp/)
python app.py
```

Then open your browser to `http://localhost:5000`.

## Running Tests

```bash
# From inside pokeapp/
pytest tests/ -v
```
