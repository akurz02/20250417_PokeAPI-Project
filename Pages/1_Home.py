"""
Pokémon Analytics — Home page.

Landing page for the multi-page Pokémon analytics dashboard.
Navigation is owned by app.py; this page only renders Home content.
"""

from pathlib import Path

import streamlit as st


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

# app.py owns the global page config when launched through st.navigation.
# This fallback keeps the page usable if someone runs it directly.
if st.runtime.exists():
    pass


# ------------------------------------------------------------
# SHARED CSS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# PAGE-SPECIFIC CSS
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    .home-hero {
        padding: 2.5rem 0 2.25rem;
    }

    .home-kicker {
        color: var(--accent);
        font-size: 0.76rem;
        font-weight: 850;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    .home-hero-title {
        color: var(--text);
        max-width: 900px;
        font-size: clamp(2.8rem, 7vw, 5.6rem);
        line-height: 0.95;
        letter-spacing: -0.065em;
        font-weight: 850;
        margin: 0;
    }

    .home-hero-accent {
        color: var(--accent);
    }

    .home-hero-copy {
        color: var(--text-muted);
        max-width: 720px;
        font-size: 1.05rem;
        line-height: 1.75;
        margin: 1.2rem 0 0;
    }

    .home-feature-card {
        min-height: 285px;
        padding: 1.6rem;
        border: 1px solid var(--border-strong);
        border-radius: 22px;
        background: linear-gradient(145deg, var(--surface), var(--bg-elevated));
    }

    .home-feature-icon {
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: var(--accent-soft);
        color: var(--accent);
        font-size: 1.25rem;
        margin-bottom: 1.15rem;
    }

    .home-feature-title {
        color: var(--text);
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.55rem;
    }

    .home-feature-copy {
        color: var(--text-muted);
        line-height: 1.65;
        font-size: 0.9rem;
        min-height: 82px;
    }

    .home-step {
        min-height: 165px;
        padding: 1.35rem;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: var(--surface-2);
    }

    .home-step-number {
        color: var(--accent);
        font-size: 0.72rem;
        font-weight: 850;
        letter-spacing: 0.12em;
        margin-bottom: 0.65rem;
    }

    .home-step-title {
        color: var(--text);
        font-weight: 750;
        margin-bottom: 0.4rem;
    }

    .home-step-copy {
        color: var(--text-subtle);
        font-size: 0.82rem;
        line-height: 1.6;
    }

    .home-capability {
        padding: 1rem 0;
        border-top: 1px solid var(--border);
    }

    .home-capability-title {
        color: var(--text);
        font-weight: 750;
    }

    .home-capability-copy {
        color: var(--text-subtle);
        font-size: 0.82rem;
        line-height: 1.55;
        margin-top: 0.25rem;
    }

    .home-callout {
        padding: 2rem;
        margin-top: 2rem;
        border: 1px solid var(--accent-glow);
        border-radius: 22px;
        background:
            radial-gradient(
                circle at 100% 0%,
                var(--accent-soft),
                transparent 45%
            ),
            var(--surface);
        text-align: center;
    }

    .home-callout-title {
        color: var(--text);
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.035em;
    }

    .home-callout-copy {
        color: var(--text-muted);
        max-width: 650px;
        margin: 0.6rem auto 0;
        line-height: 1.65;
    }

    .home-tech {
        color: var(--text-subtle);
        text-align: center;
        font-size: 0.76rem;
        margin-top: 1rem;
    }

    /* Native Streamlit navigation/action controls */
    .home-actions .stPageLink a {
        min-height: 44px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# HERO
# ------------------------------------------------------------

st.markdown(
    """
    <div class="home-hero">
        <div class="home-kicker">Pokémon Analytics</div>
        <div class="home-hero-title">
            Explore the data.<br>
            <span class="home-hero-accent">Understand the build.</span>
        </div>
        <div class="home-hero-copy">
            A focused Pokémon analytics dashboard for exploring Pokémon data,
            projecting stats, and reconstructing the IV / EV combinations
            behind real battle stats.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# REAL PAGE NAVIGATION
# ------------------------------------------------------------

st.markdown(
    '<div class="section-label">EXPLORE</div>',
    unsafe_allow_html=True,
)

action_col_1, action_col_2 = st.columns(2)

with action_col_1:
    st.page_link(
        "pages/2_Pokedex.py",
        label="📖  Explore the Pokédex",
        icon="📖",
        use_container_width=True,
    )

with action_col_2:
    st.page_link(
        "pages/3_Battle_Data.py",
        label="⚔️  Analyze Battle Data",
        icon="⚔️",
        use_container_width=True,
    )


# ------------------------------------------------------------
# FEATURE CARDS
# ------------------------------------------------------------

st.markdown(
    '<div class="section-label">WHAT YOU CAN DO</div>',
    unsafe_allow_html=True,
)

feature_col_1, feature_col_2 = st.columns(2)

with feature_col_1:
    st.markdown(
        """
        <div class="home-feature-card">
            <div class="home-feature-icon">◈</div>
            <div class="home-feature-title">Pokédex</div>
            <div class="home-feature-copy">
                Search Pokémon and explore official artwork, typing,
                abilities, physical data, base stats, level projections,
                and regional origins.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with feature_col_2:
    st.markdown(
        """
        <div class="home-feature-card">
            <div class="home-feature-icon">◇</div>
            <div class="home-feature-title">Battle Data</div>
            <div class="home-feature-copy">
                Enter observed battle stats and any IVs or EVs you know.
                The analyzer searches for legal builds that can reproduce
                those exact values.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# WORKFLOW
# ------------------------------------------------------------

st.markdown(
    '<div class="section-label">HOW IT WORKS</div>',
    unsafe_allow_html=True,
)

workflow_cols = st.columns(3)

workflow = [
    (
        "01",
        "Find a Pokémon",
        "Search the Pokédex and load its data directly from PokéAPI.",
    ),
    (
        "02",
        "Explore the stats",
        "Inspect base stats or experiment with levels, natures, IVs, and EVs.",
    ),
    (
        "03",
        "Reconstruct the build",
        "Work backward from observed stats to compatible IV / EV builds.",
    ),
]

for column, (number, title, description) in zip(workflow_cols, workflow):
    with column:
        st.markdown(
            f"""
            <div class="home-step">
                <div class="home-step-number">{number}</div>
                <div class="home-step-title">{title}</div>
                <div class="home-step-copy">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------
# CAPABILITIES
# ------------------------------------------------------------

st.markdown(
    '<div class="section-label">BUILT FOR ANALYSIS</div>',
    unsafe_allow_html=True,
)

cap_left, cap_right = st.columns(2)

with cap_left:
    capabilities = [
        (
            "PokéAPI data",
            "Live Pokémon data with cached requests for a responsive experience.",
        ),
        (
            "Stat projection",
            "Project stats across levels with configurable IVs, EVs, and natures.",
        ),
        (
            "Build reconstruction",
            "Search the valid IV / EV space instead of guessing from a single stat.",
        ),
    ]

    for title, description in capabilities:
        st.markdown(
            f"""
            <div class="home-capability">
                <div class="home-capability-title">{title}</div>
                <div class="home-capability-copy">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with cap_right:
    capabilities = [
        (
            "Legal EV constraints",
            "The reconstruction engine respects 252 EVs per stat and 510 total EVs.",
        ),
        (
            "Ambiguity-aware results",
            "When multiple builds fit the evidence, the analyzer preserves that uncertainty.",
        ),
        (
            "Modular architecture",
            "API, calculations, reconstruction, and presentation are separated into focused modules.",
        ),
    ]

    for title, description in capabilities:
        st.markdown(
            f"""
            <div class="home-capability">
                <div class="home-capability-title">{title}</div>
                <div class="home-capability-copy">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------
# CALL TO ACTION
# ------------------------------------------------------------

st.markdown(
    """
    <div class="home-callout">
        <div class="home-callout-title">Ready to inspect a Pokémon?</div>
        <div class="home-callout-copy">
            Start with the Pokédex for discovery, or jump directly into
            Battle Data if you already have a Pokémon's stats.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-tech">
        Python · Streamlit · Plotly · PokéAPI
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Pokémon Analytics · Explore · Analyze · Understand
    </div>
    """,
    unsafe_allow_html=True,
)
