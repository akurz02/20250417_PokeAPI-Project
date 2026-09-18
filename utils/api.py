import requests
import streamlit as st


POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


@st.cache_data(ttl=3600)
def fetch_pokemon_data(name):
    """Fetch Pokémon data from PokéAPI."""

    url = f"{POKEAPI_BASE_URL}/pokemon/{name.lower().strip()}"

    try:
        response = requests.get(
            url,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return None


@st.cache_data(ttl=3600)
def fetch_species_data(url):
    """Fetch Pokémon species data from PokéAPI."""

    try:
        response = requests.get(
            url,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return None