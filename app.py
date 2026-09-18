"""
Pokémon Analytics — Application shell.

This is the single Streamlit entry point. It owns the navigation and
loads the three application pages:
    - Home
    - Pokédex
    - Battle Data
"""

from pathlib import Path

import streamlit as st


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="Pokémon Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# SHARED CSS
# ------------------------------------------------------------

def load_css():
    candidates = [
        Path("styles/main.css"),
        Path("main.css"),
        Path(__file__).resolve().parent / "styles" / "main.css",
        Path(__file__).resolve().parent / "main.css",
    ]

    for css_path in candidates:
        if css_path.exists():
            st.markdown(
                f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True,
            )
            return


load_css()


# ------------------------------------------------------------
# APP BRANDING
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    /* Streamlit's native navigation is intentionally used here.
       These styles make it fit the existing dark dashboard. */

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #f8fafc;
    }

    .app-shell-brand {
        padding: 0.25rem 0 1.25rem;
    }

    .app-shell-brand-title {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 850;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .app-shell-brand-subtitle {
        color: #8b8fa3;
        font-size: 0.72rem;
        margin-top: 0.2rem;
    }

    /* Keep Streamlit's page navigation visible and clickable. */
    [data-testid="stSidebarNav"] {
        padding-top: 0.25rem;
    }

    [data-testid="stSidebarNav"] a {
        border-radius: 10px;
    }

    /* Hide Streamlit's automatic page list only if the navigation
       API is not available. This is intentionally not used when
       st.navigation is active. */

    .shell-footer {
        color: #71778a;
        font-size: 0.7rem;
        line-height: 1.5;
        padding: 1.5rem 0 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# PAGE DEFINITIONS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent

home_page = st.Page(
    str(ROOT / "Pages" / "1_Home.py"),
    title="Home",
    icon="🏠",
    default=True,
)

pokedex_page = st.Page(
    str(ROOT / "Pages" / "2_Pokedex.py"),
    title="Pokédex",
    icon="📖",
)

battle_data_page = st.Page(
    str(ROOT / "Pages" / "3_Battle_Data.py"),
    title="Battle Data",
    icon="⚔️",
)


# ------------------------------------------------------------
# NAVIGATION
# ------------------------------------------------------------

pg = st.navigation(
    {
        "Pokémon Analytics": [
            home_page,
            pokedex_page,
            battle_data_page,
        ]
    },
    position="sidebar",
)


# ------------------------------------------------------------
# SIDEBAR BRANDING
# ------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="app-shell-brand">
            <div class="app-shell-brand-title">⚡ Pokémon Analytics</div>
            <div class="app-shell-brand-subtitle">
                Explore · Analyze · Understand
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="shell-footer">
            Pokémon data powered by PokéAPI.<br>
            Built with Python · Streamlit · Plotly
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# RUN SELECTED PAGE
# ------------------------------------------------------------

pg.run()
