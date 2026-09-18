"""Helpers for extracting and formatting Pokémon data returned by PokéAPI."""


def get_pokemon_name(pokemon_data):
    """Return the Pokémon's display name."""
    return pokemon_data["name"].capitalize()


def get_pokemon_id(pokemon_data):
    """Return the Pokédex ID."""
    return pokemon_data["id"]


def get_pokemon_types(pokemon_data):
    """Return Pokémon type names in API order."""
    return [
        item["type"]["name"]
        for item in pokemon_data["types"]
    ]


def get_pokemon_type_labels(pokemon_data):
    """Return Pokémon type names formatted for display."""
    return [
        pokemon_type.replace("-", " ").title()
        for pokemon_type in get_pokemon_types(pokemon_data)
    ]


def get_pokemon_abilities(pokemon_data):
    """Return formatted ability names."""
    return [
        item["ability"]["name"]
        .replace("-", " ")
        .title()
        for item in pokemon_data["abilities"]
    ]


def get_pokemon_artwork(pokemon_data):
    """Return the official artwork URL, if available."""
    return (
        pokemon_data
        .get("sprites", {})
        .get("other", {})
        .get("official-artwork", {})
        .get("front_default")
    )


def get_base_stats(pokemon_data):
    """Return base stats as a simple stat-name/value dictionary."""
    return {
        item["stat"]["name"]: item["base_stat"]
        for item in pokemon_data["stats"]
    }


def get_stat_names(pokemon_data):
    """Return the stat names supplied by PokéAPI."""
    return [
        item["stat"]["name"]
        for item in pokemon_data["stats"]
    ]


def get_species_url(pokemon_data):
    """Return the species endpoint URL."""
    return pokemon_data.get("species", {}).get("url")


def get_generation_number(species_data):
    """Extract a numeric generation from a species response.

    Example:
        'https://pokeapi.co/api/v2/generation/6/' -> 6
    """
    generation = species_data.get("generation", {})
    generation_url = generation.get("url", "")

    try:
        return int(generation_url.rstrip("/").split("/")[-1])
    except (ValueError, IndexError):
        return None


def get_generation_name(species_data):
    """Return the API generation identifier, such as 'generation-vi'."""
    return species_data.get("generation", {}).get("name")


def get_height_meters(pokemon_data):
    """Convert PokéAPI height (decimeters) to meters."""
    height = pokemon_data.get("height")
    return height / 10 if height is not None else None


def get_weight_kg(pokemon_data):
    """Convert PokéAPI weight (hectograms) to kilograms."""
    weight = pokemon_data.get("weight")
    return weight / 10 if weight is not None else None


def get_default_stats(pokemon_data):
    """Return stats in the same structure used by the calculation layer."""
    return {
        item["stat"]["name"]: item["base_stat"]
        for item in pokemon_data["stats"]
    }
