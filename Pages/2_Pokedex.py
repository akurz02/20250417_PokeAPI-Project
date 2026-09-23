"""
Pokémon Analytics — Pokédex page.

Search and explore Pokémon using PokéAPI, with base-stat analysis,
level projections, and regional origin information.
"""

import base64
import html
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.api import fetch_pokemon_data, fetch_species_data
from utils.calculations import calculate_level_projection, calculate_stats
from utils.constants import (
    GEN_TO_LOCATION,
    GENERATION_REGIONS,
    NATURE_MODIFIERS,
    NATURES,
    STAT_DISPLAY_NAMES,
    STAT_NAMES,
)
from utils.pokemon import (
    get_base_stats,
    get_generation_number,
    get_height_meters,
    get_pokemon_abilities,
    get_pokemon_artwork,
    get_pokemon_id,
    get_pokemon_name,
    get_pokemon_types,
    get_species_url,
    get_weight_kg,
)


st.set_page_config(
    page_title="Pokédex — Pokémon Analytics",
    page_icon="⚡",
    layout="wide",
)


def load_css():
    candidates = [
        Path("styles/main.css"),
        Path("main.css"),
        Path(__file__).resolve().parents[1] / "styles" / "main.css",
        Path(__file__).resolve().parents[1] / "main.css",
    ]
    for css_path in candidates:
        if css_path.exists():
            st.markdown(
                f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True,
            )
            return


load_css()


def inject_page_css():
    st.markdown(
        """
        <style>
        .pokedex-hero {
            padding: 0.25rem 0 1.35rem;
        }
        .pokedex-kicker {
            color: var(--accent);
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }
        .pokedex-hero h1 {
            color: #fff;
            font-size: clamp(2.3rem, 5vw, 4.2rem);
            line-height: 0.98;
            letter-spacing: -0.045em;
            margin: 0;
        }
        .pokedex-hero p {
            color: var(--text-muted);
            max-width: 760px;
            line-height: 1.7;
            margin: 0.9rem 0 0;
        }
        .pokedex-search {
            margin: 0.5rem 0 1.25rem;
        }
        .pokedex-profile {
            background: linear-gradient(145deg, var(--surface), var(--bg-elevated));
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            box-shadow: var(--shadow);
            margin-bottom: 1.5rem;
        }
        .pokedex-id {
            color: var(--text-subtle);
            font-size: 0.85rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }
        .pokedex-name {
            color: #fff;
            font-size: clamp(2rem, 4vw, 3.25rem);
            font-weight: 850;
            letter-spacing: -0.045em;
            line-height: 1;
            margin: 0.2rem 0 0.8rem;
        }
        .type-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-bottom: 1.15rem;
        }
        .type-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 72px;
            padding: 0.38rem 0.75rem;
            border-radius: 999px;
            color: #fff;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            text-shadow: 0 1px 2px rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.14);
        }
        .ability-chip {
            display: inline-block;
            padding: 0.5rem 0.7rem;
            margin: 0 0.4rem 0.4rem 0;
            border-radius: 0.55rem;
            background: rgba(255,255,255,0.045);
            border: 1px solid var(--border);
            color: #d7dbe4;
            font-size: 0.82rem;
            font-weight: 650;
        }
        .stat-bar {
            margin: 0.55rem 0 0.9rem;
        }
        .stat-bar-label {
            display: flex;
            justify-content: space-between;
            color: #d7dbe4;
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .stat-track {
            height: 8px;
            border-radius: 999px;
            background: rgba(255,255,255,0.07);
            overflow: hidden;
        }
        .stat-fill {
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, var(--accent), #a78bfa);
        }
        .generation-card {
            min-height: 180px;
        }
        .empty-state {
            text-align: center;
            padding: 4rem 1rem;
            border: 1px dashed var(--border);
            border-radius: var(--radius-lg);
            background: rgba(255,255,255,0.018);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_page_css()


TYPE_COLORS = {
    "normal": "#a8a878", "fire": "#f08030", "water": "#6890f0",
    "electric": "#f8d030", "grass": "#78c850", "ice": "#98d8d8",
    "fighting": "#c03028", "poison": "#a040a0", "ground": "#e0c068",
    "flying": "#a890f0", "psychic": "#f85888", "bug": "#a8b820",
    "rock": "#b8a038", "ghost": "#705898", "dragon": "#7038f8",
    "dark": "#705848", "steel": "#b8b8d0", "fairy": "#ee99ac",
}


def render_header():
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        encoded = base64.b64encode(logo_path.read_bytes()).decode()
        logo_html = f'<img class="logo" src="data:image/png;base64,{encoded}">'
    else:
        logo_html = '<div style="font-weight:800;font-size:1.1rem;">⚡ Pokémon Analytics</div>'

    st.markdown(
        f"""
        <div class="topbar">
            {logo_html}
            <div class="nav">
                <a href="/">Home</a>
                <a class="active" href="/Pokedex">Pokédex</a>
                <a href="/Battle_Data">Battle Data</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def type_badges(types):
    return "".join(
        f'<span class="type-badge" style="background:{TYPE_COLORS.get(t, "#555")}">'
        f"{html.escape(t.replace('-', ' ').title())}</span>"
        for t in types
    )


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_base_stat_bars(base_stats):
    max_display = 255
    for stat in STAT_NAMES:
        value = base_stats.get(stat, 0)
        pct = min(100, (value / max_display) * 100)
        st.markdown(
            f"""
            <div class="stat-bar">
                <div class="stat-bar-label">
                    <span>{html.escape(STAT_DISPLAY_NAMES.get(stat, stat.title()))}</span>
                    <span>{value}</span>
                </div>
                <div class="stat-track">
                    <div class="stat-fill" style="width:{pct:.1f}%"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_stat_chart(base_stats, projected_stats):
    labels = [STAT_DISPLAY_NAMES[s] for s in STAT_NAMES]
    base_values = [base_stats.get(s, 0) for s in STAT_NAMES]
    projected_values = [projected_stats.get(s, 0) for s in STAT_NAMES]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Base", x=labels, y=base_values, opacity=0.55))
    fig.add_trace(go.Bar(name="Projected", x=labels, y=projected_values, opacity=0.9))

    fig.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
        ),
    )
    return fig


render_header()

st.markdown(
    """
    <div class="pokedex-hero">
        <div class="pokedex-kicker">Pokédex</div>
        <h1>Explore every Pokémon.</h1>
        <p>
            Search PokéAPI for a Pokémon and explore its official artwork, typing,
            abilities, physical data, base stats, projected stats, and regional origin.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------

st.markdown('<div class="section-label">Search Pokémon</div>', unsafe_allow_html=True)

search_col, button_col = st.columns([5, 1])

with search_col:
    query = st.text_input(
        "Pokémon name",
        value=st.session_state.get("pokedex_query", ""),
        placeholder="Try Pikachu, Gardevoir, Gengar, Lucario…",
        label_visibility="collapsed",
    )

with button_col:
    search_clicked = st.button(
        "Search",
        type="primary",
        use_container_width=True,
    )

if search_clicked:
    if not query.strip():
        st.warning("Enter a Pokémon name to search.")
        st.stop()

    with st.spinner(f"Loading {query.strip().title()}…"):
        data = fetch_pokemon_data(query)

    if not data:
        st.session_state.pop("pokedex_data", None)
        st.error(
            "Pokémon not found. Try an English Pokémon name such as "
            "pikachu, gardevoir, or garchomp."
        )
        st.stop()

    st.session_state.pokedex_data = data
    st.session_state.pokedex_query = query.strip().lower()

pokemon_data = st.session_state.get("pokedex_data")

if not pokemon_data:
    st.markdown(
        """
        <div class="empty-state">
            <div style="font-size:2.5rem;">⚡</div>
            <h3 style="color:#fff;margin:0.75rem 0 0.4rem;">Start exploring</h3>
            <div style="color:#8992a2;">
                Search for a Pokémon above to load its analytics profile.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ------------------------------------------------------------
# PROFILE
# ------------------------------------------------------------

pokemon_id = get_pokemon_id(pokemon_data)
name = get_pokemon_name(pokemon_data)
types = get_pokemon_types(pokemon_data)
artwork = get_pokemon_artwork(pokemon_data)
abilities = get_pokemon_abilities(pokemon_data)
base_stats = get_base_stats(pokemon_data)

st.markdown('<div class="section-label">Pokémon profile</div>', unsafe_allow_html=True)

st.markdown('<div class="pokedex-profile">', unsafe_allow_html=True)

left, right = st.columns([1, 1.55])

with left:
    if artwork:
        st.image(artwork, use_container_width=True)
    else:
        st.markdown(
            '<div class="empty-state">Artwork unavailable</div>',
            unsafe_allow_html=True,
        )

with right:
    st.markdown(
        f"""
        <div class="pokedex-id">#{pokemon_id:03d}</div>
        <div class="pokedex-name">{html.escape(name)}</div>
        <div class="type-row">{type_badges(types)}</div>
        <div class="section-label">ABILITIES</div>
        <div>
            {''.join(f'<span class="ability-chip">{html.escape(a)}</span>' for a in abilities)}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# OVERVIEW
# ------------------------------------------------------------

st.markdown('<div class="section-label">Pokémon overview</div>', unsafe_allow_html=True)

height = get_height_meters(pokemon_data)
weight = get_weight_kg(pokemon_data)
base_xp = pokemon_data.get("base_experience")

cols = st.columns(3)
with cols[0]:
    metric_card("HEIGHT", f"{height:.1f} m" if height is not None else "—")
with cols[1]:
    metric_card("WEIGHT", f"{weight:.1f} kg" if weight is not None else "—")
with cols[2]:
    metric_card("BASE XP", base_xp if base_xp is not None else "—")


# ------------------------------------------------------------
# BASE STATS
# ------------------------------------------------------------

st.markdown('<div class="section-label">Base stats</div>', unsafe_allow_html=True)

stats_col, chart_col = st.columns([1, 1.55])

with stats_col:
    render_base_stat_bars(base_stats)

with chart_col:
    base_fig = go.Figure(
        go.Bar(
            x=[STAT_DISPLAY_NAMES[s] for s in STAT_NAMES],
            y=[base_stats.get(s, 0) for s in STAT_NAMES],
            opacity=0.9,
        )
    )
    base_fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
        ),
    )
    st.plotly_chart(
        base_fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ------------------------------------------------------------
# LEVEL PROJECTION
# ------------------------------------------------------------

st.markdown('<div class="section-label">Level projection</div>', unsafe_allow_html=True)

level = st.slider(
    "Select Pokémon level",
    min_value=1,
    max_value=100,
    value=50,
    step=1,
    key="pokedex_level_projection",
)

st.caption(
    "Projected stats use 31 IVs, 0 EVs, and a neutral Hardy nature. "
    "This is a baseline projection, not a competitive build."
)

projected_stats = calculate_level_projection(pokemon_data, level)

projection_rows = [
    {
        "Stat": STAT_DISPLAY_NAMES.get(stat, stat.replace("-", " ").title()),
        "Base": base_stats.get(stat, 0),
        "Projected": projected_stats.get(stat, 0),
    }
    for stat in STAT_NAMES
]

projection_df = pd.DataFrame(projection_rows)

chart_col, table_col = st.columns([1.35, 1])

with chart_col:
    st.plotly_chart(
        render_stat_chart(base_stats, projected_stats),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with table_col:
    st.dataframe(
        projection_df,
        use_container_width=True,
        hide_index=True,
    )


# ------------------------------------------------------------
# STAT PROJECTOR
# ------------------------------------------------------------

st.markdown('<div class="section-label">Stat projector</div>', unsafe_allow_html=True)

st.caption(
    "Experiment with a level, nature, IVs, and EVs. For reverse-engineering a "
    "real Pokémon, use the Battle Data page."
)

projector_col, result_col = st.columns([1, 1.35])

with projector_col:
    projector_level = st.slider(
        "Level",
        1,
        100,
        50,
        key="pokedex_projector_level",
    )

    projector_nature = st.selectbox(
        "Nature",
        NATURES,
        index=NATURES.index("Hardy"),
        key="pokedex_projector_nature",
    )

    ivs = {}
    evs = {}

    for stat in STAT_NAMES:
        label = STAT_DISPLAY_NAMES[stat]
        row = st.columns([1, 1])

        with row[0]:
            ivs[stat] = st.number_input(
                f"{label} IV",
                min_value=0,
                max_value=31,
                value=31,
                step=1,
                key=f"pokedex_iv_{stat}",
            )

        with row[1]:
            evs[stat] = st.number_input(
                f"{label} EV",
                min_value=0,
                max_value=252,
                value=0,
                step=4,
                key=f"pokedex_ev_{stat}",
            )

    total_evs = sum(evs.values())
    if total_evs > 510:
        st.warning(f"Total EVs: {total_evs} / 510 — over the standard limit.")
    else:
        st.caption(f"Total EVs: {total_evs} / 510")

with result_col:
    projected_custom = calculate_stats(
        pokemon_data=pokemon_data,
        level=projector_level,
        ivs=ivs,
        evs=evs,
        nature=projector_nature,
    )

    custom_rows = [
        {
            "Stat": STAT_DISPLAY_NAMES.get(stat, stat.replace("-", " ").title()),
            "Base": base_stats.get(stat, 0),
            "Projected": projected_custom.get(stat, 0),
        }
        for stat in STAT_NAMES
    ]

    st.dataframe(
        pd.DataFrame(custom_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.plotly_chart(
    render_stat_chart(base_stats, projected_custom),
    use_container_width=True,
    config={"displayModeBar": False},
    key="pokedex_stat_chart",
)


# ------------------------------------------------------------
# REGIONAL ORIGIN
# ------------------------------------------------------------

st.markdown('<div class="section-label">Regional origin</div>', unsafe_allow_html=True)

species_url = get_species_url(pokemon_data)

if species_url:
    with st.spinner("Loading regional origin…"):
        species_data = fetch_species_data(species_url)

    if species_data:
        generation = get_generation_number(species_data)
        location = GEN_TO_LOCATION.get(generation)

        if generation and location:
            region_col, map_col = st.columns([1, 2])

            with region_col:
                st.markdown(
                    f"""
                    <div class="info-card generation-card">
                        <div class="info-label">GENERATION INTRODUCED:</div>
                        <div class="info-value">Gen. {generation}</div>
                        <br>
                        <div class="info-label">REGION:</div>
                        <div class="info-value">{html.escape(GENERATION_REGIONS[generation])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with map_col:
                map_df = pd.DataFrame(
                    [{"lat": location["lat"], "lon": location["lon"]}]
                )
                st.map(
                    map_df,
                    latitude="lat",
                    longitude="lon",
                    zoom=2,
                )
        else:
            st.info("Regional origin data is not available for this Pokémon.")
    else:
        st.info("Regional origin data could not be loaded.")
else:
    st.info("Regional origin data is not available.")


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Pokémon Analytics · Pokédex · Powered by PokéAPI
    </div>
    """,
    unsafe_allow_html=True,
)
