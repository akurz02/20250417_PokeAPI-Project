"""
Pokémon Analytics — Battle Data page.

Provides a polished IV / EV reconstruction interface backed by PokéAPI
and the generalized analyzer in utils.iv_ev.
"""

import html
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.api import fetch_pokemon_data
from utils.calculations import calculate_stats
from utils.constants import (
    MAX_EV_PER_STAT,
    MAX_IV,
    MAX_TOTAL_EV,
    NATURES,
    STAT_DISPLAY_NAMES,
    STAT_NAMES,
)
from utils.iv_ev import analyze_stats
from utils.pokemon import (
    get_base_stats,
    get_pokemon_artwork,
    get_pokemon_name,
    get_pokemon_types,
)


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="Battle Data — Pokémon Analytics",
    page_icon="⚡",
    layout="wide",
)


# ------------------------------------------------------------
# GLOBAL STYLES
# ------------------------------------------------------------

def load_css():
    """Load the shared application stylesheet."""
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


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

TYPE_COLORS = {
    "normal": "#a8a878",
    "fire": "#f08030",
    "water": "#6890f0",
    "electric": "#f8d030",
    "grass": "#78c850",
    "ice": "#98d8d8",
    "fighting": "#c03028",
    "poison": "#a040a0",
    "ground": "#e0c068",
    "flying": "#a890f0",
    "psychic": "#f85888",
    "bug": "#a8b820",
    "rock": "#b8a038",
    "ghost": "#705898",
    "dragon": "#7038f8",
    "dark": "#705848",
    "steel": "#b8b8d0",
    "fairy": "#ee99ac",
}


def inject_battle_css():
    """Small page-specific additions that sit on top of main.css."""
    st.markdown(
        """
        <style>
        .battle-hero {
            padding: 0.25rem 0 1.25rem 0;
        }

        .battle-kicker {
            color: var(--accent);
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.75rem;
        }

        .battle-hero h1 {
            color: #fff;
            font-size: clamp(2.3rem, 5vw, 4.2rem);
            line-height: 0.98;
            letter-spacing: -0.045em;
            margin: 0;
        }

        .battle-hero p {
            color: var(--text-muted);
            max-width: 760px;
            line-height: 1.7;
            margin: 0.9rem 0 0;
        }

        .battle-profile {
            display: flex;
            align-items: center;
            gap: 1.25rem;
            background: linear-gradient(145deg, var(--surface), var(--bg-elevated));
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.5rem;
            margin: 1rem 0 0.5rem;
            box-shadow: var(--shadow);
        }

        .battle-profile img {
            width: 112px;
            height: 112px;
            object-fit: contain;
            flex: 0 0 auto;
        }

        .battle-profile-name {
            color: #fff;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.03em;
        }

        .battle-profile-meta {
            color: var(--text-subtle);
            font-size: 0.82rem;
            margin-top: 0.2rem;
        }

        .battle-type-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.65rem;
        }

        .battle-type {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 68px;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            color: #fff;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            border: 1px solid rgba(255,255,255,0.15);
            text-shadow: 0 1px 2px rgba(0,0,0,0.25);
        }

        .analysis-banner {
            padding: 1rem 1.1rem;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            background: var(--surface);
            margin: 1rem 0 1.25rem;
        }

        .analysis-banner strong {
            color: #fff;
        }

        .analysis-banner span {
            color: var(--text-muted);
        }

        .result-number {
            color: #fff;
            font-size: 1.6rem;
            font-weight: 800;
        }

        .result-label {
            color: var(--text-subtle);
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .range-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.35rem 0.6rem;
            min-width: 54px;
            border-radius: 999px;
            background: var(--accent-soft);
            border: 1px solid rgba(139,92,246,0.22);
            color: #ddd6fe;
            font-size: 0.78rem;
            font-weight: 750;
        }

        .known-pill {
            color: var(--success);
            background: rgba(52,211,153,0.08);
            border-color: rgba(52,211,153,0.2);
        }

        .unknown-pill {
            color: var(--text-muted);
            background: rgba(255,255,255,0.035);
            border-color: var(--border);
        }

        .battle-note {
            color: var(--text-subtle);
            font-size: 0.78rem;
            line-height: 1.55;
            margin-top: 0.65rem;
        }

        @media (max-width: 700px) {
            .battle-profile {
                align-items: flex-start;
            }

            .battle-profile img {
                width: 84px;
                height: 84px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_battle_css()


def stat_label(stat_name):
    return STAT_DISPLAY_NAMES.get(
        stat_name,
        stat_name.replace("-", " ").title(),
    )


def render_header():
    """Render the shared visual header without depending on app.py."""
    logo_path = Path("assets/logo.png")

    if logo_path.exists():
        logo_html = (
            f'<img class="logo" src="data:image/png;base64,'
            f'{__import__("base64").b64encode(logo_path.read_bytes()).decode()}">'
        )
    else:
        logo_html = '<div style="font-weight:800;font-size:1.1rem;">⚡ Pokémon Analytics</div>'

    st.markdown(
        f"""
        <div class="topbar">
            {logo_html}
            <div class="nav">
                <a href="/">Home</a>
                <a href="/Pokedex">Pokédex</a>
                <a class="active" href="/Battle_Data">Battle Data</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_profile(pokemon_data):
    """Render a compact Pokémon identity card."""
    name = html.escape(get_pokemon_name(pokemon_data))
    pokemon_id = pokemon_data.get("id", "—")
    artwork = get_pokemon_artwork(pokemon_data)
    types = get_pokemon_types(pokemon_data)

    type_html = "".join(
        f'<span class="battle-type" style="background:{TYPE_COLORS.get(t, "#555")}">'
        f"{html.escape(t.title())}</span>"
        for t in types
    )

    image_html = (
        f'<img src="{html.escape(artwork)}" alt="{name}">'
        if artwork
        else '<div style="width:112px;height:112px;"></div>'
    )

    st.markdown(
        f"""
        <div class="battle-profile">
            {image_html}
            <div>
                <div class="battle-profile-name">{name}</div>
                <div class="battle-profile-meta">National Pokédex #{pokemon_id:03d}</div>
                <div class="battle-type-row">{type_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(items):
    """Render small metric cards."""
    columns = st.columns(len(items))

    for column, (label, value) in zip(columns, items):
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{html.escape(str(label))}</div>
                    <div class="metric-value">{html.escape(str(value))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def build_stat_chart(base_stats, observed_stats, calculated_stats):
    """Create a dark Plotly comparison chart."""
    labels = [stat_label(stat) for stat in STAT_NAMES]
    base_values = [base_stats.get(stat, 0) for stat in STAT_NAMES]
    observed_values = [observed_stats.get(stat) for stat in STAT_NAMES]
    projected_values = [calculated_stats.get(stat, 0) for stat in STAT_NAMES]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Base",
            x=labels,
            y=base_values,
            marker=dict(opacity=0.45),
        )
    )

    fig.add_trace(
        go.Bar(
            name="Observed",
            x=labels,
            y=[
                value if value is not None else 0
                for value in observed_values
            ],
            marker=dict(opacity=0.95),
        )
    )

    fig.add_trace(
        go.Bar(
            name="Configured",
            x=labels,
            y=projected_values,
            marker=dict(opacity=0.75),
        )
    )

    fig.update_layout(
        barmode="group",
        height=390,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            zeroline=False,
        ),
    )

    return fig


def build_result_dataframe(analysis):
    """Turn analyzer builds into a readable table."""
    rows = []

    for index, build in enumerate(analysis["builds"], start=1):
        row = {"Build": index}

        for stat in STAT_NAMES:
            row[f"{stat_label(stat)} IV"] = build["ivs"].get(stat)
            row[f"{stat_label(stat)} EV"] = build["evs"].get(stat)

        row["Total EVs"] = build["total_evs"]
        rows.append(row)

    return pd.DataFrame(rows)


def render_ranges(analysis):
    """Render per-stat IV / EV candidate ranges."""
    ranges = analysis.get("stat_ranges", {})

    columns = st.columns(3)

    for index, stat in enumerate(STAT_NAMES):
        with columns[index % 3]:
            info = ranges.get(stat)

            if not info:
                continue

            iv_min = info.get("iv_min")
            iv_max = info.get("iv_max")
            ev_min = info.get("ev_min")
            ev_max = info.get("ev_max")

            if iv_min is None:
                iv_display = "—"
                ev_display = "—"
                iv_class = "unknown-pill"
                ev_class = "unknown-pill"
            else:
                iv_display = (
                    str(iv_min)
                    if iv_min == iv_max
                    else f"{iv_min}–{iv_max}"
                )
                ev_display = (
                    str(ev_min)
                    if ev_min == ev_max
                    else f"{ev_min}–{ev_max}"
                )
                iv_class = (
                    "range-pill known-pill"
                    if iv_min == iv_max
                    else "range-pill"
                )
                ev_class = (
                    "range-pill known-pill"
                    if ev_min == ev_max
                    else "range-pill"
                )

            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-name">{html.escape(stat_label(stat))}</div>
                    <div style="margin-top:0.65rem;">
                        <div class="stat-meta">Possible IV</div>
                        <span class="{iv_class}">{iv_display}</span>
                    </div>
                    <div style="margin-top:0.65rem;">
                        <div class="stat-meta">Possible EV</div>
                        <span class="{ev_class}">{ev_display}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ------------------------------------------------------------
# HEADER / HERO
# ------------------------------------------------------------

render_header()

st.markdown(
    """
    <div class="battle-hero">
        <div class="battle-kicker">Battle Data</div>
        <h1>Reconstruct the build.</h1>
        <p>
            Enter a Pokémon's observed battle stats and any IVs or EVs you already
            know. Pokémon Analytics searches the valid stat space and surfaces the
            builds that can actually produce those numbers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# POKÉMON SEARCH
# ------------------------------------------------------------

st.markdown('<div class="section-label">Pokémon</div>', unsafe_allow_html=True)

search_col, button_col = st.columns([5, 1])

with search_col:
    pokemon_query = st.text_input(
        "Search Pokémon",
        value=st.session_state.get("battle_pokemon_query", "gardevoir"),
        placeholder="e.g. gardevoir, garchomp, dragapult",
        label_visibility="collapsed",
    )

with button_col:
    search_clicked = st.button(
        "Load",
        use_container_width=True,
        type="primary",
    )

if search_clicked or "battle_pokemon_data" not in st.session_state:
    if not pokemon_query.strip():
        st.warning("Enter a Pokémon name to load its battle data.")
        st.stop()

    with st.spinner(f"Loading {pokemon_query.strip().title()}…"):
        loaded_data = fetch_pokemon_data(pokemon_query)

    if not loaded_data:
        st.error(
            "PokéAPI could not find that Pokémon. Check the spelling and try again."
        )
        st.stop()

    st.session_state.battle_pokemon_data = loaded_data
    st.session_state.battle_pokemon_query = pokemon_query.strip().lower()


pokemon_data = st.session_state.get("battle_pokemon_data")

if not pokemon_data:
    st.stop()

render_profile(pokemon_data)


# ------------------------------------------------------------
# ANALYSIS CONFIGURATION
# ------------------------------------------------------------

st.markdown(
    '<div class="section-label">Analysis configuration</div>',
    unsafe_allow_html=True,
)

config_left, config_right = st.columns([1, 1])

with config_left:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### Pokémon settings")

    level = st.number_input(
        "Level",
        min_value=1,
        max_value=100,
        value=100,
        step=1,
        key="battle_level",
    )

    nature = st.selectbox(
        "Nature",
        NATURES,
        index=NATURES.index("Hardy"),
        key="battle_nature",
    )

    analysis_mode = st.radio(
        "Known information",
        options=[
            "Known EVs → find possible IVs",
            "Known IVs → find possible EVs",
            "Neither known → find compatible builds",
        ],
        key="battle_analysis_mode",
    )

    max_results = st.number_input(
        "Maximum builds to return",
        min_value=1,
        max_value=5000,
        value=500,
        step=100,
        help="The analyzer stops after this many compatible builds.",
    )

    st.markdown(
        """
        <div class="battle-note">
            The analyzer uses the in-game stat formula and enforces the 510 total
            EV limit and 252 EV maximum per stat.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

with config_right:
    st.markdown('<div class="config-card">', unsafe_allow_html=True)
    st.markdown("### Stat inputs")
    st.caption(
        "Check a stat to include it in the reconstruction. "
        "Unobserved stats are ignored."
    )

    known_evs_mode = analysis_mode.startswith("Known EVs")
    known_ivs_mode = analysis_mode.startswith("Known IVs")

    observed_stats = {}
    known_ivs = {}
    known_evs = {}

    header_cols = st.columns([0.55, 1.65, 1, 1])

    with header_cols[0]:
        st.markdown("**Use**")
    with header_cols[1]:
        st.markdown("**Stat**")
    with header_cols[2]:
        st.markdown("**Observed**")
    with header_cols[3]:
        if known_evs_mode:
            st.markdown("**Known EV**")
        elif known_ivs_mode:
            st.markdown("**Known IV**")
        else:
            st.markdown("**Known**")

    for stat in STAT_NAMES:
        row = st.columns([0.55, 1.65, 1, 1])

        with row[0]:
            use_stat = st.checkbox(
                "Use",
                value=True,
                key=f"battle_use_{stat}",
                label_visibility="collapsed",
            )

        with row[1]:
            st.markdown(
                f'<div style="padding-top:0.55rem;color:#d1d5db;font-weight:650;">'
                f"{html.escape(stat_label(stat))}</div>",
                unsafe_allow_html=True,
            )

        with row[2]:
            observed = st.number_input(
                f"Observed {stat_label(stat)}",
                min_value=0,
                max_value=999,
                value=0,
                step=1,
                key=f"battle_observed_{stat}",
                label_visibility="collapsed",
                disabled=not use_stat,
            )

        with row[3]:
            if known_evs_mode:
                value = st.number_input(
                    f"EV {stat_label(stat)}",
                    min_value=0,
                    max_value=MAX_EV_PER_STAT,
                    value=0,
                    step=4,
                    key=f"battle_ev_{stat}",
                    label_visibility="collapsed",
                    disabled=not use_stat,
                )
                known_evs[stat] = value if use_stat else None

            elif known_ivs_mode:
                value = st.number_input(
                    f"IV {stat_label(stat)}",
                    min_value=0,
                    max_value=MAX_IV,
                    value=31,
                    step=1,
                    key=f"battle_iv_{stat}",
                    label_visibility="collapsed",
                    disabled=not use_stat,
                )
                known_ivs[stat] = value if use_stat else None

            else:
                st.markdown(
                    '<div style="padding-top:0.55rem;color:#737d8d;">Unknown</div>',
                    unsafe_allow_html=True,
                )

        if use_stat:
            observed_stats[stat] = observed

    known_ivs = {k: v for k, v in known_ivs.items() if v is not None}
    known_evs = {k: v for k, v in known_evs.items() if v is not None}

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# EV VALIDATION
# ------------------------------------------------------------

known_ev_total = sum(known_evs.values())

if known_evs_mode:
    if known_ev_total > MAX_TOTAL_EV:
        st.markdown(
            f"""
            <div class="status-card error">
                <strong>EV total exceeds the legal limit.</strong>
                You have entered {known_ev_total} EVs; the maximum is {MAX_TOTAL_EV}.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        remaining = MAX_TOTAL_EV - known_ev_total
        status_class = "valid" if known_ev_total <= MAX_TOTAL_EV else "invalid"
        st.markdown(
            f"""
            <div class="ev-total {status_class}" style="margin-top:1rem;">
                Known EVs: <strong>{known_ev_total}</strong> / {MAX_TOTAL_EV}
                &nbsp;·&nbsp; {remaining} remaining
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------
# ANALYZE
# ------------------------------------------------------------

st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

analyze_clicked = st.button(
    "Analyze Build",
    type="primary",
    use_container_width=True,
)

if analyze_clicked:
    if not observed_stats:
        st.warning("Select at least one observed stat before analyzing.")
    elif known_ev_total > MAX_TOTAL_EV:
        st.error("Reduce the known EVs to 510 or fewer before analyzing.")
    else:
        with st.spinner("Reconstructing compatible builds…"):
            analysis = analyze_stats(
                pokemon_data=pokemon_data,
                level=level,
                observed_stats=observed_stats,
                nature=nature,
                known_ivs=known_ivs,
                known_evs=known_evs,
                max_results=int(max_results),
            )

        st.session_state.battle_analysis = analysis
        st.session_state.battle_analysis_inputs = {
            "level": level,
            "nature": nature,
            "observed_stats": observed_stats,
            "known_ivs": known_ivs,
            "known_evs": known_evs,
        }


analysis = st.session_state.get("battle_analysis")


# ------------------------------------------------------------
# RESULTS
# ------------------------------------------------------------

if analysis:
    st.markdown(
        '<div class="section-label">Analysis results</div>',
        unsafe_allow_html=True,
    )

    status = analysis.get("status")
    solutions = analysis.get("solutions_found", 0)
    truncated = analysis.get("truncated", False)

    if status == "unique":
        title = "Unique compatible build"
        message = "The supplied information narrows the search to one complete build."
        banner_class = "success"
    elif status == "multiple":
        title = f"{solutions:,} compatible builds found"
        message = (
            "The supplied information does not uniquely determine one build."
            if not truncated
            else "The search reached the configured result limit."
        )
        banner_class = "warning"
    elif status == "no_solutions":
        title = "No compatible build"
        message = (
            "No IV / EV combination satisfies the supplied stats and constraints."
        )
        banner_class = "error"
    else:
        title = "No observations"
        message = "Provide at least one observed stat to reconstruct the build."
        banner_class = "warning"

    st.markdown(
        f"""
        <div class="analysis-banner status-card {banner_class}">
            <strong>{html.escape(title)}</strong><br>
            <span>{html.escape(message)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if status == "no_solutions":
        st.info(
            "Double-check the Pokémon, level, nature, observed stats, and any "
            "known IV/EV values. A single incorrect input can eliminate every build."
        )
        st.stop()

    render_metric_cards(
        [
            ("Status", status.replace("_", " ").title()),
            ("Compatible builds", f"{solutions:,}"),
            ("Observed stats", len(analysis.get("stat_candidates", {}))),
            ("Search limit", f"{int(max_results):,}"),
        ]
    )

    st.markdown(
        '<div class="section-title">Possible stat ranges</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Ranges are calculated from the exact IV / EV combinations that reproduce "
        "the observed values."
    )
    render_ranges(analysis)

    # --------------------------------------------------------
    # CONFIGURED STAT VIEW
    # --------------------------------------------------------

    inputs = st.session_state.get("battle_analysis_inputs", {})
    observed = inputs.get("observed_stats", {})
    known_iv_values = inputs.get("known_ivs", {})
    known_ev_values = inputs.get("known_evs", {})
    analyzed_level = inputs.get("level", level)
    analyzed_nature = inputs.get("nature", nature)

    configured_stats = calculate_stats(
        pokemon_data=pokemon_data,
        level=analyzed_level,
        ivs=known_iv_values,
        evs=known_ev_values,
        nature=analyzed_nature,
    )

    base_stats = get_base_stats(pokemon_data)

    st.markdown(
        '<div class="section-title">Stat comparison</div>',
        unsafe_allow_html=True,
    )

    fig = build_stat_chart(
        base_stats=base_stats,
        observed_stats=observed,
        calculated_stats=configured_stats,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # --------------------------------------------------------
    # BUILDS
    # --------------------------------------------------------

    if analysis.get("builds"):
        st.markdown(
            '<div class="section-title">Compatible builds</div>',
            unsafe_allow_html=True,
        )

        result_df = build_result_dataframe(analysis)

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
        )

        if truncated:
            st.warning(
                f"Only the first {int(max_results):,} compatible builds are shown. "
                "Increase the search limit if you need a larger result set."
            )

        if status == "unique":
            build = analysis["builds"][0]

            st.markdown(
                '<div class="section-title">Reconstructed build</div>',
                unsafe_allow_html=True,
            )

            cols = st.columns(6)

            for column, stat in zip(cols, STAT_NAMES):
                with column:
                    st.markdown(
                        f"""
                        <div class="stat-card">
                            <div class="stat-name">{html.escape(stat_label(stat))}</div>
                            <div class="stat-value">{build["ivs"][stat]}</div>
                            <div class="stat-meta">
                                IV &nbsp;·&nbsp; {build["evs"][stat]} EV
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown(
                f"""
                <div class="ev-total valid" style="margin-top:1rem;">
                    Total EVs: <strong>{build["total_evs"]}</strong> / {MAX_TOTAL_EV}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------
    # METHODOLOGY
    # --------------------------------------------------------

    with st.expander("How the reconstruction works"):
        st.markdown(
            """
            **1. PokéAPI supplies the Pokémon's base stats.**  
            The page does not ask you to manually enter base stats.

            **2. Your observed stats become constraints.**  
            For each selected stat, the analyzer searches IV / EV combinations
            that reproduce the exact displayed value at the selected level and nature.

            **3. Legal EV limits are enforced.**  
            Each stat is limited to 252 EVs and the complete build is limited to
            510 total EVs.

            **4. Ambiguity is preserved.**  
            If multiple builds can produce the same observed stats, the page shows
            the compatible range instead of pretending the exact build is known.

            **5. Exact integer EVs are tested.**  
            This matters because the game formula uses `EV // 4`, so multiple
            individual EV values can map to the same stat contribution.
            """
        )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Pokémon Analytics · Battle Data · Powered by PokéAPI
    </div>
    """,
    unsafe_allow_html=True,
)
