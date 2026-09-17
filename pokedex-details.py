import base64
import math
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PokéData",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# LOGO
# ============================================================

def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None


logo = get_image_base64("/workspaces/20250417_PokeAPI-Project/Media/20260911_Kirisuto-Logo.png")


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

    /* -----------------------------
       GLOBAL
    ----------------------------- */

    .stApp {
        background: #0b0f17;
        color: #f5f7fa;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* -----------------------------
       HEADER
    ----------------------------- */

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0 2rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 3rem;
    }

    .logo {
        max-height: 48px;
        max-width: 180px;
        object-fit: contain;
    }

    .nav {
        display: flex;
        gap: 2rem;
        color: #9ca3af;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* -----------------------------
       HERO
    ----------------------------- */

    .hero {
        padding: 1rem 0 2rem 0;
    }

    .eyebrow {
        color: #8b5cf6;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        margin-bottom: 1rem;
    }

    .hero h1 {
        font-size: clamp(2.8rem, 6vw, 5.5rem);
        line-height: 0.95;
        letter-spacing: -0.05em;
        margin: 0 0 1.5rem 0;
        color: #ffffff;
    }

    .hero p {
        max-width: 700px;
        color: #9ca3af;
        font-size: 1.1rem;
        line-height: 1.7;
        margin-bottom: 2rem;
    }

    /* -----------------------------
       SEARCH
    ----------------------------- */

    div[data-testid="stTextInput"] input {
        background: #151a24;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        color: #ffffff;
        padding: 0.8rem 1rem;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 1px #8b5cf6;
    }

    .stButton > button {
        background: #8b5cf6;
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        min-height: 44px;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: #7c3aed;
        border: none;
    }

    /* -----------------------------
       EMPTY STATE
    ----------------------------- */

    .empty-state {
        margin-top: 2rem;
        padding: 5rem 2rem;
        text-align: center;
        border: 1px dashed rgba(255,255,255,0.14);
        border-radius: 24px;
        background: rgba(255,255,255,0.02);
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .empty-state h2 {
        color: #ffffff;
        margin-bottom: 0.75rem;
    }

    .empty-state p {
        color: #8f98a8;
        max-width: 650px;
        margin: 0.5rem auto;
        line-height: 1.6;
    }

    /* -----------------------------
       POKÉMON CARD
    ----------------------------- */

    .pokemon-card {
        background: linear-gradient(
            145deg,
            #151a24,
            #10151e
        );
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 24px;
        padding: 2rem;
        margin-top: 2rem;
    }

    .pokemon-name {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }

    .pokemon-id {
        color: #737d8d;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    /* -----------------------------
       TYPE BADGES
    ----------------------------- */

    .type-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 999px;
        background: rgba(139,92,246,0.16);
        border: 1px solid rgba(139,92,246,0.35);
        color: #c4b5fd;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    /* -----------------------------
       METRIC CARDS
    ----------------------------- */

    .metric-card {
        background: #151a24;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.25rem;
        min-height: 105px;
    }

    .metric-label {
        color: #737d8d;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.55rem;
        font-weight: 800;
    }

    /* -----------------------------
       SECTION HEADINGS
    ----------------------------- */

    .section-label {
        color: #737d8d;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin-top: 2.5rem;
        margin-bottom: 0.75rem;
    }

    /* -----------------------------
       INFO CARDS
    ----------------------------- */

    .info-card {
        background: #151a24;
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 16px;
        padding: 1.25rem;
        margin-top: 1rem;
    }

    .info-label {
        color: #737d8d;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }

    .info-value {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 600;
    }

    /* -----------------------------
       FOOTER
    ----------------------------- */

    .footer {
        text-align: center;
        padding: 3rem 0 1rem 0;
        margin-top: 4rem;
        border-top: 1px solid rgba(255,255,255,0.07);
        color: #667085;
        font-size: 0.8rem;
    }

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# API FUNCTIONS
# ============================================================

@st.cache_data(ttl=3600)
def fetch_pokemon_data(name):

    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower().strip()}"

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

    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:
        return None

# ============================================================
# REGION / GENERATION DATA
# ============================================================

gen_to_location = {

    1: {
        "lat": 35.875,
        "lon": 139.65,
        "region": "Kanto, Japan"
    },

    2: {
        "lat": 34.675,
        "lon": 135.65,
        "region": "Kansai, Japan"
    },

    3: {
        "lat": 33.8394,
        "lon": 130.7383,
        "region": "Kyushu, Japan"
    },

    4: {
        "lat": 43.2207,
        "lon": 142.8636,
        "region": "Hokkaido, Japan"
    },

    5: {
        "lat": 40.7128,
        "lon": -74.0060,
        "region": "New York, USA"
    },

    6: {
        "lat": 46.2276,
        "lon": 2.2137,
        "region": "France"
    },

    7: {
        "lat": 21.2894,
        "lon": -157.5177,
        "region": "Hawaii, USA"
    },

    8: {
        "lat": 54.0000,
        "lon": -2.0000,
        "region": "United Kingdom"
    },

    9: {
        "lat": 40.4637,
        "lon": -3.7492,
        "region": "Spain"
    }
}


# ============================================================
# STAT CALCULATION
# ============================================================

def calculate_stats(pokemon_data, level, ivs, evs, nature_modifiers):
    calculated_stats = {}

    for stat in pokemon_data["stats"]:
        base_stat = stat["base_stat"]
        stat_name = stat["stat"]["name"]

        iv = ivs.get(stat_name, 31)
        ev = evs.get(stat_name, 0)
        nature_modifier = nature_modifiers.get(stat_name, 1.0)

        # HP has a different formula from the other stats
        if stat_name == "hp":
            stat_value = (
                math.floor(
                    ((2 * base_stat + iv + (ev // 4)) * level) / 100
                )
                + level
                + 10
            )

        # Attack, Defense, Sp. Atk, Sp. Def, Speed
        else:
            base_value = (
                math.floor(
                    ((2 * base_stat + iv + (ev // 4)) * level) / 100
                )
                + 5
            )

            stat_value = math.floor(
                base_value * nature_modifier
            )

        calculated_stats[stat_name] = stat_value

    return calculated_stats


# ============================================================
# LEVEL PROJECTION CALCULATION
# ============================================================

def calculate_level_projection(pokemon_data, level):
    """Calculate a simplified level projection using 31 IVs and 0 EVs."""
    projected_stats = {}

    for stat in pokemon_data["stats"]:
        base_stat = stat["base_stat"]
        stat_name = stat["stat"]["name"]
        iv = 31
        ev = 0

        if stat_name == "hp":
            stat_value = (
                math.floor(
                    ((2 * base_stat + iv + (ev // 4)) * level) / 100
                )
                + level
                + 10
            )
        else:
            stat_value = (
                math.floor(
                    ((2 * base_stat + iv + (ev // 4)) * level) / 100
                )
                + 5
            )

        projected_stats[stat_name] = stat_value

    return projected_stats


# ============================================================
# POKÉMON NATURE MODIFIERS
# ============================================================

nature_modifiers = {
    "Hardy": {},
    "Lonely": {"attack": 1.1, "defense": 0.9},
    "Brave": {"attack": 1.1, "speed": 0.9},
    "Adamant": {"attack": 1.1, "special-attack": 0.9},
    "Naughty": {"attack": 1.1, "special-defense": 0.9},
    "Bold": {"defense": 1.1, "attack": 0.9},
    "Docile": {},
    "Relaxed": {"defense": 1.1, "speed": 0.9},
    "Impish": {"defense": 1.1, "special-attack": 0.9},
    "Lax": {"defense": 1.1, "special-defense": 0.9},
    "Timid": {"speed": 1.1, "attack": 0.9},
    "Hasty": {"speed": 1.1, "defense": 0.9},
    "Serious": {},
    "Jolly": {"speed": 1.1, "special-attack": 0.9},
    "Naive": {"speed": 1.1, "special-defense": 0.9},
    "Bashful": {},
    "Rash": {"special-attack": 1.1, "special-defense": 0.9},
    "Quiet": {"special-attack": 1.1, "speed": 0.9},
    "Quirky": {},
    "Modest": {"special-attack": 1.1, "attack": 0.9},
    "Mild": {"special-attack": 1.1, "defense": 0.9},
    "Calm": {"special-defense": 1.1, "attack": 0.9},
    "Gentle": {"special-defense": 1.1, "defense": 0.9},
    "Sassy": {"special-defense": 1.1, "speed": 0.9},
    "Careful": {"special-defense": 1.1, "special-attack": 0.9},
}


# ============================================================
# UI HELPERS
# ============================================================

def metric_card(label, value):

    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
</div>
""",
        unsafe_allow_html=True
    )


def type_badges(types):

    badges = ""

    for pokemon_type in types:

        badges += (
            f'<span class="type-badge">'
            f'{pokemon_type.upper()}'
            f'</span>'
        )

    return badges


# ============================================================
# SESSION STATE
# ============================================================

if "pokemon_data" not in st.session_state:

    st.session_state["pokemon_data"] = None


pokemon_data = st.session_state["pokemon_data"]

# ============================================================
# HEADER
# ============================================================

if logo:
    st.markdown(
        f"""<div class="topbar">
<img src="data:image/png;base64,{logo}" class="logo">

<div class="nav">
    <span>Dashboard</span>
    <span>Analytics</span>
    <span>About</span>
</div>

</div>""",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """<div class="topbar">

<div class="nav">
    <span>Dashboard</span>
    <span>Analytics</span>
    <span>About</span>
</div>

</div>""",
        unsafe_allow_html=True
    )

# ============================================================
# HERO
# ============================================================

st.markdown(
    """<div class="hero">

<div class="eyebrow">
    INTERACTIVE DATA EXPLORER
</div>

<h1>
    Explore Pokémon<br>
    like never before.
</h1>

<p>
    Analyze statistics, project performance across levels,
    and explore regional origins through an interactive dashboard.
</p>

</div>""",
    unsafe_allow_html=True
)


# ============================================================
# SEARCH
# ============================================================

search_col, button_col = st.columns(
    [5, 1]
)


with search_col:

    pokemon_name = st.text_input(
        "Pokémon",
        placeholder="Search Pokémon...",
        label_visibility="collapsed"
    )


with button_col:

    fetch_data_button = st.button(
        "Analyze",
        use_container_width=True
    )


# ============================================================
# FETCH DATA
# ============================================================

if fetch_data_button and pokemon_name:

    with st.spinner(
        "Analyzing Pokémon data..."
    ):

        data = fetch_pokemon_data(
            pokemon_name
        )

    if data:

        st.session_state["pokemon_data"] = data

        pokemon_data = data

    else:

        st.error(
            f'We couldn\'t find "{pokemon_name}". '
            "Try another Pokémon."
        )


# ============================================================
# EMPTY STATE
# ============================================================

# ============================================================
# EMPTY STATE
# ============================================================

if pokemon_data is None:

    st.markdown(
        """<div class="empty-state">

<div class="empty-icon">⚡</div>

<h2>Ready to explore?</h2>

<p>
Search for a Pokémon above to see its statistics,
level projections, and regional information.
</p>

<p>
Try <strong>Pikachu</strong>,
<strong>Gardevoir</strong>,
<strong>Gengar</strong>, 
<strong>Lucario</strong>, or
<strong>Lilligant</strong>.
</p>

</div>""",
        unsafe_allow_html=True
    )


# ============================================================
# POKÉMON DASHBOARD
# ============================================================

if pokemon_data:

    # --------------------------------------------------------
    # BASIC DATA
    # --------------------------------------------------------

    pokemon_id = pokemon_data["id"]

    name = pokemon_data["name"].capitalize()

    types = [
        item["type"]["name"]
        for item in pokemon_data["types"]
    ]

    artwork = (
        pokemon_data["sprites"]
        ["other"]
        ["official-artwork"]
        ["front_default"]
    )

    abilities = [
        item["ability"]["name"]
        .replace("-", " ")
        .title()
        for item in pokemon_data["abilities"]
    ]


    # --------------------------------------------------------
    # MAIN POKÉMON CARD
    # --------------------------------------------------------

    st.markdown(
        '<div class="pokemon-card">',
        unsafe_allow_html=True
    )


    left, right = st.columns(
        [1, 1.5]
    )


    # --------------------------------------------------------
    # LEFT SIDE
    # --------------------------------------------------------

    with left:

        if artwork:

            st.image(
                artwork,
                use_container_width=True
            )


    # --------------------------------------------------------
    # RIGHT SIDE
    # --------------------------------------------------------

    with right:

        st.markdown(
            f"""
<div class="pokemon-id">
    #{pokemon_id:03d}
</div>

<div class="pokemon-name">
    {name}
</div>
""",
            unsafe_allow_html=True
        )

        st.markdown(
            type_badges(types),
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-label">ABILITIES</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
<div class="info-card">
    <div class="info-value">
        {", ".join(abilities)}
    </div>
</div>
""",
            unsafe_allow_html=True
        )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # METRICS
    # ========================================================

    st.markdown(
        '<div class="section-label">POKÉMON OVERVIEW</div>',
        unsafe_allow_html=True
    )


    metric_col1, metric_col2, metric_col3 = st.columns(3)


    with metric_col1:

        metric_card(
            "HEIGHT",
            f"{pokemon_data['height'] / 10:.1f} m"
        )


    with metric_col2:

        metric_card(
            "WEIGHT",
            f"{pokemon_data['weight'] / 10:.1f} kg"
        )


    with metric_col3:

        metric_card(
            "BASE XP",
            pokemon_data["base_experience"]
        )


    # ========================================================
    # LEVEL PROJECTION
    # ========================================================

    st.markdown(
        '<div class="section-label">LEVEL PROJECTION</div>',
        unsafe_allow_html=True
    )

    level = st.slider(
        "Select Pokémon Level",
        min_value=1,
        max_value=100,
        value=50,
        step=1,
        key="level_projection"
    )

    st.caption(
        "Estimated stats use a simplified projection with "
        "31 IVs and 0 EVs for demonstration purposes."
    )

    projected_stats = calculate_level_projection(
        pokemon_data,
        level
    )

    projection_rows = []

    for stat in pokemon_data["stats"]:
        stat_name = stat["stat"]["name"]
        projection_rows.append({
            "Stat": stat_name.replace("-", " ").title(),
            "Base": stat["base_stat"],
            "Estimated": projected_stats[stat_name]
        })

    projection_df = pd.DataFrame(projection_rows)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=projection_df["Stat"],
            x=projection_df["Base"],
            name="Base",
            orientation="h"
        )
    )

    fig.add_trace(
        go.Bar(
            y=projection_df["Stat"],
            x=projection_df["Estimated"],
            name=f"Level {level}",
            orientation="h"
        )
    )

    fig.update_layout(
        barmode="group",
        height=430,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Stat Value",
        yaxis_title="",
        legend_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.dataframe(
        projection_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # STAT CONFIGURATION
    # ========================================================

    st.markdown(
        '<div class="section-label">STAT CONFIGURATION</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Customize the Pokémon's Nature, IVs, and EVs for detailed stat calculations."
    )

    nature = st.selectbox(
        "Nature",
        list(nature_modifiers.keys()),
        key="nature_selection"
    )

    stat_names = [
        "hp",
        "attack",
        "defense",
        "special-attack",
        "special-defense",
        "speed"
    ]

    ivs = {}
    evs = {}

    st.markdown("### IVs & EVs")

    for stat_name in stat_names:
        display_name = stat_name.replace("-", " ").title()
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(display_name)

        with col2:
            ivs[stat_name] = st.number_input(
                "IV",
                min_value=0,
                max_value=31,
                value=31,
                step=1,
                key=f"iv_{stat_name}"
            )

        with col3:
            evs[stat_name] = st.number_input(
                "EV",
                min_value=0,
                max_value=252,
                value=0,
                step=4,
                key=f"ev_{stat_name}"
            )

    total_evs = sum(evs.values())

    st.caption(
        f"Total EVs: {total_evs} / 510"
    )

    if total_evs > 510:
        st.warning(
            "Total EVs exceed the standard 510 EV limit."
        )

    selected_nature_modifiers = {
        stat_name: nature_modifiers[nature].get(stat_name, 1.0)
        for stat_name in [
            "attack",
            "defense",
            "special-attack",
            "special-defense",
            "speed"
        ]
    }

    estimated_stats = calculate_stats(
        pokemon_data,
        level,
        ivs,
        evs,
        selected_nature_modifiers
    )

    detailed_rows = []

    for stat in pokemon_data["stats"]:
        stat_name = stat["stat"]["name"]
        detailed_rows.append({
            "Stat": stat_name.replace("-", " ").title(),
            "Base": stat["base_stat"],
            "Projected": estimated_stats[stat_name]
        })

    detailed_df = pd.DataFrame(detailed_rows)

    st.markdown("### Projected Stats")

    st.dataframe(
        detailed_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # REGIONAL ORIGIN
    # ========================================================

    st.markdown(
        '<div class="section-label">REGIONAL ORIGIN</div>',
        unsafe_allow_html=True
    )

    species_data = fetch_species_data(
        pokemon_data["species"]["url"]
    )

    if species_data:
        generation_url = species_data["generation"]["url"]

        generation = int(
            generation_url.strip("/").split("/")[-1]
        )

        location = gen_to_location.get(generation)

        if location:
            region_col1, region_col2 = st.columns([1, 2])

            with region_col1:
                st.markdown(
                    f"""
<div class="info-card">

    <div class="info-label">
        GENERATION
    </div>

    <div class="info-value">
        Generation {generation}
    </div>

    <br>

    <div class="info-label">
        REGION
    </div>

    <div class="info-value">
        {location["region"]}
    </div>

</div>
""",
                    unsafe_allow_html=True
                )

            with region_col2:
                map_df = pd.DataFrame(
                    [{
                        "lat": location["lat"],
                        "lon": location["lon"]
                    }]
                )

                st.map(
                    map_df,
                    latitude="lat",
                    longitude="lon",
                    zoom=2
                )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
<div class="footer">

    Built with Python · Streamlit · PokéAPI

</div>
""",
    unsafe_allow_html=True
)