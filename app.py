"""
DEMON PREDICTIONS 2.1
RED EDITION

Sports Intelligence Platform

Datos deportivos: ESPN
Zona horaria: Colombia
Actualización automática: 60 segundos

Ejecutar:
streamlit run app.py
"""

import math
import re
import datetime as dt
from html import escape

import requests
import pandas as pd
import streamlit as st


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="DEMON PREDICTIONS | RED EDITION",
    page_icon="😈",
    layout="wide",
    initial_sidebar_state="expanded",
)

TZ = dt.timezone(dt.timedelta(hours=-5))

BASE = (
    "https://site.api.espn.com/apis/site/v2/"
    "sports/{sport}/{league}/scoreboard"
)

LEAGUES = {
    "NBA": ("basketball", "nba", 12.0),
    "WNBA": ("basketball", "wnba", 11.0),
    "NCAA baloncesto": (
        "basketball",
        "mens-college-basketball",
        11.0,
    ),
    "NFL": ("football", "nfl", 13.5),
    "NCAA fútbol americano": (
        "football",
        "college-football",
        14.0,
    ),
    "NHL": ("hockey", "nhl", None),
    "MLB": ("baseball", "mlb", None),
    "Premier League": ("soccer", "eng.1", None),
    "La Liga": ("soccer", "esp.1", None),
    "Serie A": ("soccer", "ita.1", None),
    "Bundesliga": ("soccer", "ger.1", None),
    "Ligue 1": ("soccer", "fra.1", None),
    "Champions League": (
        "soccer",
        "uefa.champions",
        None,
    ),
    "MLS": ("soccer", "usa.1", None),
    "Liga BetPlay": ("soccer", "col.1", None),
    "Libertadores": (
        "soccer",
        "conmebol.libertadores",
        None,
    ),
}

SPORT_ICONS = {
    "basketball": "🏀",
    "football": "🏈",
    "hockey": "🏒",
    "baseball": "⚾",
    "soccer": "⚽",
}


# =====================================================
# CSS PREMIUM
# =====================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            ellipse at top,
            rgba(185, 15, 40, 0.17),
            transparent 48%
        ),
        #08090e;
    color: #f5f5f7;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background: #101116;
    border-right: 1px solid #40202a;
}

section[data-testid="stSidebar"] * {
    color: #eeeeee;
}

.demon-hero {
    background:
        linear-gradient(
            115deg,
            #2d0a15,
            #151119 55%,
            #270b14
        );
    border: 1px solid #772033;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 25px;
    box-shadow: 0 0 35px rgba(255, 35, 65, 0.10);
}

.demon-logo {
    font-family: 'Rajdhani', sans-serif;
    font-size: clamp(35px, 5vw, 62px);
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}

.demon-logo span {
    color: #ff304b;
    text-shadow: 0 0 25px rgba(255, 48, 75, 0.4);
}

.demon-tagline {
    color: #b4b4c0;
    font-size: 12px;
    letter-spacing: 2px;
    margin-top: 12px;
}

.demon-live {
    display: inline-block;
    color: #00f29a;
    background: rgba(0, 240, 140, 0.08);
    border: 1px solid rgba(0, 240, 140, 0.35);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 11px;
    font-weight: 800;
    margin-top: 20px;
}

.demon-section {
    font-family: 'Rajdhani', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 28px;
    margin-bottom: 4px;
}

.demon-description {
    color: #999ba9;
    font-size: 12px;
    margin-bottom: 18px;
}

.stat-card {
    background: linear-gradient(145deg, #1b1b24, #111218);
    border: 1px solid #30303b;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 12px;
    min-height: 135px;
    transition: all 0.2s ease;
}

.stat-card:hover {
    border-color: #ff304b;
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(255, 30, 60, 0.12);
}

.stat-label {
    color: #aeb0bd;
    font-size: 11px;
    letter-spacing: 1px;
    font-weight: 700;
}

.stat-number {
    color: #ffffff;
    font-family: 'Rajdhani', sans-serif;
    font-size: 45px;
    font-weight: 700;
    line-height: 1.3;
}

.stat-footer {
    color: #ff4059;
    font-size: 11px;
}

.rank {
    display: inline-block;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 800;
    margin: 8px 0;
}

.rank-elite {
    color: #ffd66b;
    background: rgba(255, 214, 107, 0.12);
    border: 1px solid #78602b;
}

.rank-power {
    color: #ff5069;
    background: rgba(255, 50, 80, 0.12);
    border: 1px solid #813040;
}

.rank-edge {
    color: #ffb65c;
    background: rgba(255, 180, 75, 0.1);
    border: 1px solid #78532d;
}

.rank-balanced {
    color: #b8b9c5;
    background: #23242e;
    border: 1px solid #41424e;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 15px;
}

div[data-testid="stMetric"] {
    background: #171820;
    border: 1px solid #30313c;
    padding: 12px;
    border-radius: 12px;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #b91531, #f02b49);
    border: none;
    color: #ffffff;
    font-weight: 800;
    border-radius: 10px;
}

.stButton > button[kind="primary"]:hover {
    background: #ff3855;
    color: #ffffff;
    border: none;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #b91531, #ff4059);
}

.demon-footer {
    color: #81828f;
    border-top: 1px solid #40202a;
    text-align: center;
    padding: 25px;
    margin-top: 40px;
    font-size: 11px;
    letter-spacing: 1px;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .demon-hero {
        padding: 20px;
    }

    .demon-logo {
        font-size: 35px;
    }

    .stat-card {
        padding: 15px;
        min-height: 110px;
    }

    .stat-number {
        font-size: 34px;
    }

    .demon-section {
        font-size: 25px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# COMPONENTES VISUALES
# =====================================================

def section_title(title, description=""):
    html = (
        f'<div class="demon-section">{escape(title)}</div>'
        f'<div class="demon-description">{escape(description)}</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def stat_card(label, value, footer):
    html = (
        '<div class="stat-card">'
        f'<div class="stat-label">{escape(str(label))}</div>'
        f'<div class="stat-number">{escape(str(value))}</div>'
        f'<div class="stat-footer">{escape(str(footer))}</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)


def demon_rank(prob):
    if prob >= 80:
        return "🔥 DEMON ELITE", "rank-elite"

    if prob >= 70:
        return "🔴 DEMON POWER", "rank-power"

    if prob >= 60:
        return "⚡ DEMON EDGE", "rank-edge"

    return "⚖️ EQUILIBRADO", "rank-balanced"


def rank_badge(prob):
    title, css = demon_rank(prob)

    html = (
        f'<span class="rank {css}">'
        f'{escape(title)}'
        '</span>'
    )

    st.markdown(html, unsafe_allow_html=True)


# =====================================================
# CÁLCULOS DE PROBABILIDADES
# =====================================================

def ml_to_prob(ml):
    try:
        value = float(
            str(ml)
            .upper()
            .replace("EVEN", "100")
            .replace("+", "")
        )

    except (TypeError, ValueError):
        return None

    if value == 0:
        return None

    if value > 0:
        return 100 / (value + 100)

    return -value / (-value + 100)


def pick_ml(odds, side):
    if side == "draw":
        block = odds.get("drawOdds")
    else:
        block = odds.get(side + "TeamOdds")

    if isinstance(block, dict):
        moneyline = block.get("moneyLine")

        if moneyline is not None:
            return ml_to_prob(moneyline)

    moneyline = odds.get("moneyline", {})

    if not isinstance(moneyline, dict):
        return None

    side_block = moneyline.get(side, {})

    if not isinstance(side_block, dict):
        return None

    for key in ("close", "open"):
        item = side_block.get(key)

        if isinstance(item, dict):
            value = item.get("odds")

            if value is not None:
                return ml_to_prob(value)

    return None


def spread_prob(odds, home_abbr, away_abbr, sd):
    details = str(odds.get("details", "")).strip()

    if not details or sd is None:
        return None

    if details.upper() == "EVEN":
        return 0.5

    match = re.match(
        r"([A-Za-z.]+)\s*([+-]?\d+(?:\.\d+)?)",
        details,
    )

    if not match:
        return None

    abbr = match.group(1).upper()
    line = abs(float(match.group(2)))

    p_fav = 0.5 * (
        1 + math.erf(line / sd / math.sqrt(2))
    )

    if abbr == home_abbr.upper():
        return p_fav

    if abbr == away_abbr.upper():
        return 1 - p_fav

    return None


def probabilities(comp, home, away, sd, sport):
    odds_list = comp.get("odds") or []

    if not odds_list:
        return None

    odds = odds_list[0]

    ph = pick_ml(odds, "home")
    pa = pick_ml(odds, "away")
    pd_ = pick_ml(odds, "draw")

    # En fútbol necesitamos tres resultados:
    # local, empate y visitante.
    # No convertir cuotas de dos vías en un mercado
    # de tres resultados.

    if sport == "soccer":
        if ph is None or pa is None or pd_ is None:
            return None

        total = ph + pa + pd_

        if total <= 0:
            return None

        return (
            ph / total * 100,
            pa / total * 100,
            pd_ / total * 100,
            "Cuotas del mercado",
        )

    if ph is not None and pa is not None:
        total = ph + pa

        if total <= 0:
            return None

        return (
            ph / total * 100,
            pa / total * 100,
            None,
            "Cuotas del mercado",
        )

    p = spread_prob(
        odds,
        home["abbr"],
        away["abbr"],
        sd,
    )

    if p is not None:
        return (
            p * 100,
            (1 - p) * 100,
            None,
            "Estimación por spread",
        )

    return None


# =====================================================
# ESPN
# =====================================================

@st.cache_data(ttl=60, show_spinner=False)
def load_league(name, day):
    sport, league, sd = LEAGUES[name]

    url = BASE.format(
        sport=sport,
        league=league,
    )

    response = requests.get(
        url,
        params={
            "dates": day.strftime("%Y%m%d")
        },
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=15,
    )

    response.raise_for_status()

    events = response.json().get("events", [])

    games = []

    for event in events:
        competitions = event.get("competitions") or []

        if not competitions:
            continue

        comp = competitions[0]

        teams = {}

        for competitor in comp.get("competitors", []):
            team = competitor.get("team", {})

            logos = team.get("logos") or []

            logo = None

            if logos:
                logo = logos[0].get("href")

            if not logo:
                logo = team.get("logo")

            side = competitor.get("homeAway")

            teams[side] = {
                "name": team.get("displayName", "?"),
                "abbr": team.get("abbreviation", "?"),
                "score": competitor.get("score", "0"),
                "logo": logo,
            }

        if "home" not in teams or "away" not in teams:
            continue

        start = dt.datetime.fromisoformat(
            event["date"].replace("Z", "+00:00")
        ).astimezone(TZ)

        status = event.get("status", {}).get("type", {})

        probs = probabilities(
            comp,
            teams["home"],
            teams["away"],
            sd,
            sport,
        )

        games.append({
            "id": event.get("id"),
            "liga": name,
            "sport": sport,
            "hora": start,
            "state": status.get("state", "pre"),
            "estado": status.get("shortDetail", ""),
            "home": teams["home"],
            "away": teams["away"],
            "probs": probs,
        })

    return games


# =====================================================
# FAVORITOS
# =====================================================

def favorite(game):
    if game["probs"] is None:
        return None

    ph, pa, pd_, source = game["probs"]

    options = [
        (ph, game["home"]["name"]),
        (pa, game["away"]["name"]),
    ]

    if pd_ is not None:
        options.append((pd_, "Empate"))

    return max(options, key=lambda x: x[0])


# =====================================================
# TARJETAS DE PARTIDOS
# =====================================================

def show_logo(team):
    logo = team.get("logo")

    if logo and str(logo).startswith("https://"):
        try:
            st.image(logo, width=65)
        except Exception:
            st.markdown("🏆")
    else:
        st.markdown("🏆")


def probability_bar(name, value):
    st.markdown(f"**{name}: {value:.1f}%**")

    st.progress(
        min(max(value / 100, 0), 1)
    )


def match_card(game, featured=False):
    with st.container(border=True):
        sport_icon = SPORT_ICONS.get(
            game["sport"],
            "🏆",
        )

        left, right = st.columns([3, 1])

        with left:
            st.markdown(
                f"### {sport_icon} {game['liga']}"
            )

        with right:
            if game["state"] == "in":
                st.error("🔴 LIVE")

            elif game["state"] == "post":
                st.success("FINAL")

            else:
                st.info("PRÓXIMO")

        st.caption(
            "🕒 "
            + game["hora"].strftime("%d/%m/%Y %H:%M")
            + " · Colombia"
        )

        st.divider()

        away_col, middle_col, home_col = st.columns(
            [2, 1, 2]
        )

        with away_col:
            show_logo(game["away"])

            st.markdown(
                f"**{game['away']['name']}**"
            )

            st.caption("VISITANTE")

        with middle_col:
            st.markdown("### VS")

            if game["state"] != "pre":
                st.markdown(
                    f"### {game['away']['score']}"
                    f" - {game['home']['score']}"
                )

        with home_col:
            show_logo(game["home"])

            st.markdown(
                f"**{game['home']['name']}**"
            )

            st.caption("LOCAL")

        if game["estado"]:
            st.caption(
                f"📡 {game['estado']}"
            )

        st.divider()

        if game["probs"] is None:
            st.warning(
                "⏳ Probabilidades no disponibles."
            )
            return

        ph, pa, pd_, source = game["probs"]

        fav = favorite(game)

        if fav:
            prob, name = fav

            rank_badge(prob)

            st.markdown(
                f"🎯 **Favorito del mercado: {name}**"
            )

            st.metric(
                "Probabilidad implícita",
                f"{prob:.1f}%",
            )

        st.markdown("##### 📊 PROBABILIDADES")

        probability_bar(
            game["away"]["abbr"],
            pa,
        )

        if pd_ is not None:
            probability_bar(
                "EMPATE",
                pd_,
            )

        probability_bar(
            game["home"]["abbr"],
            ph,
        )

        st.caption(f"📡 Fuente: {source}")

        if featured:
            st.caption(
                "⭐ Destacado por favoritismo del mercado."
            )


# =====================================================
# HEADER PRINCIPAL
# =====================================================

st.markdown(
    '<div class="demon-hero">'
    '<div class="demon-logo">'
    '😈 DEMON <span>PREDICTIONS</span>'
    '</div>'
    '<div class="demon-tagline">'
    'RED EDITION · SPORTS INTELLIGENCE PLATFORM'
    '</div>'
    '<div class="demon-live">'
    '● LIVE DATA · POWERED BY ESPN'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.title("😈 DEMON")

    st.markdown("**PREDICTIONS 2.1**")

    st.caption("🔴 RED EDITION")

    st.divider()

    st.subheader("⚙️ CENTRO DE CONTROL")

    day = st.date_input(
        "📅 Fecha de partidos",
        dt.datetime.now(TZ).date(),
    )

    selected = st.multiselect(
        "🏆 Seleccionar ligas",
        list(LEAGUES.keys()),
        default=[
            "NBA",
            "NFL",
            "NHL",
            "MLB",
        ],
    )

    min_conf = st.slider(
        "🎯 Probabilidad mínima (%)",
        50,
        90,
        50,
    )

    only_live = st.checkbox(
        "🔴 Solo partidos en vivo"
    )

    search = st.text_input(
        "🔎 Buscar equipo",
        placeholder="Ej: Lakers, Madrid...",
    )

    st.divider()

    if st.button(
        "🔄 ACTUALIZAR DATOS",
        type="primary",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.markdown("**📡 ESTADO DEL SISTEMA**")

    st.success("🟢 SISTEMA ACTIVO")

    st.caption("Fuente: ESPN")
    st.caption("Actualización: 60 segundos")
    st.caption("Zona horaria: Colombia")


# =====================================================
# DASHBOARD
# =====================================================

def dashboard():
    if not selected:
        st.warning(
            "Selecciona al menos una liga."
        )
        return

    all_games = []
    errors = []

    with st.spinner("Cargando datos deportivos..."):
        for name in selected:
            try:
                all_games.extend(
                    load_league(name, day)
                )
            except requests.RequestException:
                errors.append(name)
            except (KeyError, ValueError, TypeError):
                errors.append(name)

    if errors:
        st.warning(
            "No se pudieron cargar estas ligas: "
            + ", ".join(errors)
        )

    games = all_games

    if only_live:
        games = [
            g for g in games
            if g["state"] == "in"
        ]

    if search.strip():
        term = search.lower().strip()

        games = [
            g for g in games
            if (
                term in g["home"]["name"].lower()
                or term in g["away"]["name"].lower()
            )
        ]

    with_probs = [
        g for g in games
        if g["probs"] is not None
    ]

    live_games = [
        g for g in games
        if g["state"] == "in"
    ]

    strong = [
        g for g in with_probs
        if favorite(g)
        and favorite(g)[0] >= 70
    ]

    st.caption(
        "🕒 Actualizado: "
        + dt.datetime.now(TZ).strftime("%H:%M:%S")
        + " · Colombia"
    )

    section_title(
        "📊 DEMON CONTROL CENTER",
        "Resumen de los encuentros deportivos",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        stat_card(
            "🏆 PARTIDOS",
            len(games),
            "Encuentros encontrados",
        )

    with c2:
        stat_card(
            "🎯 CON PROBABILIDADES",
            len(with_probs),
            "Datos disponibles",
        )

    with c3:
        stat_card(
            "🔥 FAVORITOS 70%+",
            len(strong),
            "Favoritos marcados",
        )

    with c4:
        stat_card(
            "🔴 EN VIVO",
            len(live_games),
            "Partidos en desarrollo",
        )

    if not games:
        st.info(
            "No hay encuentros con los filtros seleccionados."
        )
        return

    # =================================================
    # TOP PICKS
    # =================================================

    section_title(
        "🔥 DEMON TOP PICKS",
        "Los favoritos más marcados del mercado",
    )

    upcoming = [
        g for g in with_probs
        if (
            g["state"] == "pre"
            and favorite(g)
            and favorite(g)[0] >= min_conf
        )
    ]

    top_games = sorted(
        upcoming,
        key=lambda g: favorite(g)[0],
        reverse=True,
    )[:3]

    if top_games:
        cols = st.columns(len(top_games))

        for i, game in enumerate(top_games):
            with cols[i]:
                match_card(game, featured=True)
    else:
        st.info(
            "No hay TOP PICKS disponibles para estos filtros."
        )

    # =================================================
    # RANKING
    # =================================================

    section_title(
        "🎯 RANKING DE PRONÓSTICOS",
        "Probabilidades implícitas del mercado",
    )

    rows = []

    for g in with_probs:
        fav = favorite(g)

        if not fav:
            continue

        prob, name = fav

        if prob < min_conf:
            continue

        rank, _ = demon_rank(prob)

        rows.append({
            "Liga": g["liga"],
            "Hora": g["hora"].strftime("%H:%M"),
            "Partido": (
                g["away"]["name"]
                + " vs "
                + g["home"]["name"]
            ),
            "Favorito": name,
            "Probabilidad": round(prob, 1),
            "Clasificación": rank,
            "Estado": g["estado"],
        })

    if rows:
        df = pd.DataFrame(rows)

        df = df.sort_values(
            "Probabilidad",
            ascending=False,
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Probabilidad":
                    st.column_config.ProgressColumn(
                        "Probabilidad %",
                        min_value=0,
                        max_value=100,
                        format="%.1f",
                    ),
            },
        )

        csv = df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 DESCARGAR PRONÓSTICOS",
            csv,
            "demon_predictions.csv",
            "text/csv",
        )
    else:
        st.info(
            "No hay pronósticos que cumplan el filtro."
        )

    # =================================================
    # MATCH CENTER
    # =================================================

    section_title(
        "⚽ DEMON MATCH CENTER",
        "Explora todos los encuentros",
    )

    tabs = st.tabs([
        "🔥 TODOS",
        "⚽ FÚTBOL",
        "🏀 BASKET",
        "🏈 NFL / NCAA",
        "🏒 NHL",
        "⚾ MLB",
    ])

    categories = [
        None,
        "soccer",
        "basketball",
        "football",
        "hockey",
        "baseball",
    ]

    for tab, category in zip(tabs, categories):
        with tab:
            filtered = [
                g for g in games
                if (
                    category is None
                    or g["sport"] == category
                )
            ]

            filtered = [
                g for g in filtered
                if (
                    favorite(g) is None
                    or favorite(g)[0] >= min_conf
                )
            ]

            filtered = sorted(
                filtered,
                key=lambda g: (
                    g["liga"],
                    g["hora"],
                ),
            )

            if not filtered:
                st.info(
                    "No hay encuentros en esta categoría."
                )
                continue

            st.caption(
                f"🏆 {len(filtered)} encuentros"
            )

            for i in range(0, len(filtered), 2):
                cols = st.columns(2)

                for j in range(2):
                    index = i + j

                    if index < len(filtered):
                        with cols[j]:
                            match_card(filtered[index])

    # =================================================
    # ANALYTICS
    # =================================================

    section_title(
        "📈 DEMON ANALYTICS",
        "Distribución de encuentros por liga",
    )

    league_counts = {}

    for g in games:
        league_counts[g["liga"]] = (
            league_counts.get(g["liga"], 0) + 1
        )

    if league_counts:
        stats_df = pd.DataFrame({
            "Liga": list(league_counts.keys()),
            "Partidos": list(league_counts.values()),
        })

        st.bar_chart(
            stats_df.set_index("Liga"),
            color="#ff304b",
        )

    st.divider()

    st.info(
        "📊 Las probabilidades proceden de cuotas "
        "del mercado o de estimaciones basadas en spread. "
        "No garantizan resultados y no representan "
        "necesariamente oportunidades de apuesta rentables."
    )


# =====================================================
# ACTUALIZACIÓN AUTOMÁTICA
# =====================================================

@st.fragment(run_every=60)
def live_dashboard():
    dashboard()


live_dashboard()


# =====================================================
# FOOTER
# =====================================================

st.markdown(
    '<div class="demon-footer">'
    '😈 DEMON PREDICTIONS 2.1'
    '<br><br>'
    'RED EDITION · SPORTS INTELLIGENCE'
    '<br><br>'
    'DATOS DE ESPN · ACTUALIZACIÓN AUTOMÁTICA'
    '<br><br>'
    '© 2026 DEMON PREDICTIONS'
    '</div>',
    unsafe_allow_html=True,
)
