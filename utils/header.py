"""Shared Pokémon Analytics header and branding."""

import base64
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
# LOGO_PATH = ROOT / "Media" / "20260911_Kirisuto-Logo.png"


def _logo_html() -> str:
    """Return the project logo as an embedded image, with a text fallback."""
#    if LOGO_PATH.exists():
#        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
#        return (
#            '<img class="logo" '
#            'alt="Pokémon Analytics" '
#            f'src="data:image/png;base64,{encoded}">'
#        )

    return '<div class="logo-fallback">⚡ Pokémon Analytics</div>'

def render_header(active: str = "") -> None:
    """Render the shared branded header used by all application pages."""
    active = active.strip().lower()

    links = [
        ("Home", "/", "home"),
        ("Pokédex", "/Pokedex", "pokedex"),
        ("Battle Data", "/Battle_Data", "battle"),
    ]

    nav_html = "".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
        for label, href, key in links
    )

    st.markdown(
        f"""
        <div class="topbar">
            <a class="brand-link" href="/" aria-label="Pokémon Analytics home">
                {_logo_html()}
            </a>
            <nav class="nav" aria-label="Primary navigation">
                {nav_html}
            </nav>
        </div>
        """,
        unsafe_allow_html=True,
    )
