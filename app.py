"""
DEMON PREDICTIONS 2.0
RED EDITION

Plataforma de probabilidades deportivas.

Datos: ESPN
Actualización: 60 segundos
Zona horaria: Colombia

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


# =========================================================
# CONFIGURACIÓN
# =========================================================

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


# =========================================================
# DISEÑO PREMIUM
# =========================================================

st.markdown(
    """
<style>

/* FUENTE */

@import url(
'https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap'
);


/* FONDO */

.stApp {
    background:
        radial-gradient(
            ellipse at 50% -10%,
            rgba(220,20,40,0.16),
            transparent 50%
        ),
        #08090d;

    color: #f5f5f5;
    font-family: 'Inter', sans-serif;
}


/* CONTENEDOR */

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #101116;
    border-right: 1px solid #352027;
}

section[data-testid="stSidebar"] * {
    color: #eeeeee;
}


/* TITULOS */

h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
}

h1 {
    color: #ffffff;
}

h2 {
    color: #ffffff;
}

h3 {
    color: #ff344e;
}


/* HEADER PRINCIPAL */

.demon-header {
    background:
        linear-gradient(
            120deg,
            #230b12,
            #111117 55%,
            #210910
        );

    border: 1px solid #60202e;
    border-radius: 18px;

    padding: 30px;
    margin-bottom: 25px;

    box-shadow:
        0 0 35px rgba(255,30,60,0.10);

    position: relative;
    overflow: hidden;
}

.demon-title {
    font-family: 'Rajdhani', sans-serif;

    font-size: clamp(34px, 5vw, 62px);
    font-weight: 700;

    color: #ffffff;

    letter-spacing: 2px;
    line-height: 1.05;
}

.demon-title span {
    color: #ff304b;
    text-shadow:
        0 0 25px rgba(255,30,60,0.45);
}

.demon-subtitle {
    color: #aeb0bb;
    font-size: 12px;
    letter-spacing: 3px;
    margin-top: 10px;
}

.live-badge {
    display: inline-block;

    background: rgba(0,255,140,0.10);
    color: #00ef91;

    border: 1px solid rgba(0,255,140,0.35);
    border-radius: 20px;

    padding: 6px 14px;
    margin-top: 18px;

    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}


/* TARJETAS DASHBOARD */

.stat-card {
    background:
        linear-gradient(
            145deg,
            #181920,
            #101116
        );

    border: 1px solid #2b2d36;
    border-radius: 15px;

    padding: 22px 18px;

    min-height: 135px;
    margin-bottom: 12px;

    transition: all 0.25s ease;
}

.stat-card:hover {
    border-color: #ff304b;

    transform: translateY(-3px);

    box-shadow:
        0 8px 25px rgba(255,30,60,0.12);
}

.stat-label {
    font-size: 11px;
    font-weight: 700;

    color: #a5a5b0;
    letter-spacing: 1.3px;
}

.stat-value {
    font-family: 'Rajdhani', sans-serif;

    font-size: 43px;
    font-weight: 700;

    color: #ffffff;
    line-height: 1.3;
}

.stat-footer {
    font-size: 11px;
    color: #ff4059;
}


/* TITULOS DE SECCION */

.section-title {
    font-family: 'Rajdhani', sans-serif;

    font-size: 29px;
    font-weight: 700;

    margin-top: 28px;
    margin-bottom: 8px;

    color: #ffffff;
}

.section-title span {
    color: #ff344e;
}

.section-description {
    font-size: 12px;
    color: #999ba7;

    margin-bottom: 18px;
}


/* CONTENEDORES STREAMLIT */

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 15px;
}


/* METRICAS */

div[data-testid="stMetric"] {
    background: #15161c;

    padding: 15px;

    border-radius: 12px;
    border: 1px solid #292b34;
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
    font-family: 'Rajdhani', sans-serif;
}

div[data-testid="stMetricLabel"] {
    color: #aeb0bb;
}


/* BOTONES */

.stButton > button {
    background:
        linear-gradient(
            90deg,
            #a9142c,
            #ef2343
        );

    color: white;

    border: none;
    border-radius: 9px;

    font-weight: 700;
}

.stButton > button:hover {
    background: #ff344e;
    color: white;

    border: none;

    box-shadow:
        0 0 18px rgba(255,30,60,0.35);
}


/* PROGRESS */

.stProgress > div > div > div {
    background:
        linear-gradient(
            90deg,
            #a9142c,
            #ff344e
        );
}


/* TABS */

button[data-baseweb="tab"] {
    font-weight: 700;
}


/* DATAFRAME */

div[data-testid="stDataFrame"] {
    border: 1px solid #292b34;
    border-radius: 12px;
}


/* BADGES */

.demon-badge {
    display: inline-block;

    padding: 5px 11px;
    border-radius: 7px;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 0.5px;
}

.badge-elite {
    color: #ffcc55;
    background: rgba(255,204,85,0.12);
    border: 1px solid #80612a;
}

.badge-power {
    color: #ff4059;
    background: rgba(255,40,70,0.12);
    border: 1px solid #743040;
}

.badge-edge {
    color: #ffae45;
    background: rgba(255,174,69,0.10);
    border: 1px solid #70502c;
}

.badge-balanced {
    color: #aeb3c0;
    background: #20222b;
    border: 1px solid #353844;
}


/* FOOTER */

.demon-footer {
    margin-top: 45px;

    padding: 25px;

    text-align: center;

    border-top: 1px solid #342029;

    color: #858692;

    font-size: 11px;
    letter-spacing: 1px;
}


/* MOBILE */

@media (max-width: 768px) {

    .block-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .demon-header {
        padding: 20px;
    }

    .demon-title {
        font-size: 35px;
    }

    .stat-card {
        padding: 14px;
        min-height: 110px;
    }

    .stat-value {
        font-size: 32px;
    }

    .stat-label {
        font-size: 10px;
    }

    .section-title {
        font-size: 25px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# FUNCIONES DE PROBABILIDAD
# =========================================================

def ml_to_prob(ml):
    """Convierte cuota americana a probabilidad implícita."""

    try:
        ml = float(
            str(ml)
            .upper()
            .replace("EVEN", "100")
            .replace("+", "")
        )

    except (TypeError, ValueError):
        return None

    if ml == 0:
        return None

    if ml > 0:
        return 100 / (ml + 100)

    return -ml / (-ml + 100)


def pick_ml(odds, side):
    """Obtiene moneyline en los formatos de ESPN."""

    if side == "draw":
        block = odds.get("drawOdds")
    else:
        block = odds.get(side + "TeamOdds")

    if isinstance(block, dict):
        value = block.get("moneyLine")

        if value is not None:
            return ml_to_prob(value)

    ml = odds.get("moneyline", {})

    if not isinstance(ml, dict):
        return None

    side_block = ml.get(side, {})

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
    """Estima probabilidad usando el spread."""

    details = str(
        odds.get("details", "")
    ).strip()

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
        1 + math.erf(
            line / sd / math.sqrt(2)
        )
    )

    if abbr == home_abbr.upper():
        return p_fav

    if abbr == away_abbr.upper():
        return 1 - p_fav

    return None


def probabilities(comp, home, away, sd):
    """Calcula probabilidades implícitas normalizadas."""

    odds_list = comp.get("odds") or []

    if not odds_list:
        return None

    odds = odds_list[0]

    ph = pick_ml(odds, "home")
    pa = pick_ml(odds, "away")
    pd_ = pick_ml(odds, "draw")

    if ph is not None and pa is not None:

        total = ph + pa + (pd_ or 0)

        if total <= 0:
            return None

        return (
            ph / total * 100,
            pa / total * 100,
            pd_ / total * 100 if pd_ is not None else None,
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


# =========================================================
# CARGA DE ESPN
# =========================================================

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
        timeout=15,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    response.raise_for_status()

    events = response.json().get("events", [])

    games = []

    for ev in events:

        competitions = ev.get("competitions", [])

        if not competitions:
            continue

        comp = competitions[0]

        teams = {}

        for c in comp.get("competitors", []):

            t = c.get("team", {})

            logos = t.get("logos") or []

            logo = (
                logos[0].get("href")
                if logos else None
            )

            teams[c.get("homeAway")] = {
                "name": t.get(
                    "displayName",
                    "Desconocido",
                ),
                "abbr": t.get(
                    "abbreviation",
                    "?",
                ),
                "score": c.get("score", "0"),
                "logo": logo,
            }

        if (
            "home" not in teams
            or "away" not in teams
        ):
            continue

        start = dt.datetime.fromisoformat(
            ev["date"].replace("Z", "+00:00")
        ).astimezone(TZ)

        status = ev.get(
            "status", {}
        ).get("type", {})

        probs = probabilities(
            comp,
            teams["home"],
            teams["away"],
            sd,
        )

        games.append({
            "id": ev.get("id"),
            "liga": name,
            "sport": sport,
            "hora": start,
            "state": status.get(
                "state",
                "pre",
            ),
            "estado": status.get(
                "shortDetail",
                "",
            ),
            "home": teams["home"],
            "away": teams["away"],
            "probs": probs,
        })

    return games


# =========================================================
# CLASIFICACIÓN DEMON
# =========================================================

def demon_rank(prob):

    if prob >= 80:
        return (
            "🔥 DEMON ELITE",
            "badge-elite",
        )

    if prob >= 70:
        return (
            "🔴 DEMON POWER",
            "badge-power",
        )

    if prob >= 60:
        return (
            "⚡ DEMON EDGE",
            "badge-edge",
        )

    return (
        "⚖️ EQUILIBRADO",
        "badge-balanced",
    )


def favorite(game):

    if game["probs"] is None:
        return None

    ph, pa, pd_, source = game["probs"]

    options = [
        (ph, game["home"]["name"]),
        (pa, game["away"]["name"]),
    ]

    if pd_ is not None:
        options.append(
            (pd_, "Empate")
        )

    return max(
        options,
        key=lambda x: x[0],
    )


# =========================================================
# COMPONENTES VISUALES
# =========================================================

def section_title(title, description=""):

    st.markdown(
        f"""
        <div class="section-title">
            {escape(title)}
        </div>

        <div class="section-description">
            {escape(description)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label, value, footer):

    st.markdown(
        f"""
        <div class="stat-card">

            <div class="stat-label">
                {escape(str(label))}
            </div>

            <div class="stat-value">
                {escape(str(value))}
            </div>

            <div class="stat-footer">
                {escape(str(footer))}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def show_logo(team):

    logo = team.get("logo")

    if logo:
        st.image(
            logo,
            width=65,
        )
    else:
        st.markdown("🏆")


def probability_bar(label, value):

    st.markdown(
        f"**{label}: {value:.1f}%**"
    )

    st.progress(
        min(
            max(value / 100, 0),
            1,
        )
    )


# =========================================================
# TARJETA DE PARTIDO
# =========================================================

def match_card(game, featured=False):

    fav = favorite(game)

    with st.container(border=True):

        header_left, header_right = st.columns(
            [3, 1]
        )

        sport_icon = SPORT_ICONS.get(
            game["sport"],
            "🏆",
        )

        header_left.markdown(
            f"### {sport_icon} {game['liga']}"
        )

        if game["state"] == "in":

            header_right.error("🔴 LIVE")

        elif game["state"] == "post":

            header_right.success("FINAL")

        else:

            header_right.info("PRÓXIMO")

        st.caption(
            f"🕒 {game['hora'].strftime('%d/%m/%Y %H:%M')}"
            " · Hora Colombia"
        )

        st.divider()

        away_col, vs_col, home_col = st.columns(
            [2, 1, 2]
        )

        with away_col:

            show_logo(game["away"])

            st.markdown(
                f"**{game['away']['name']}**"
            )

            st.caption("VISITANTE")

        with vs_col:

            st.markdown(
                "### VS"
            )

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

        st.divider()

        if game["estado"]:
            st.caption(
                f"📡 {game['estado']}"
            )

        if game["probs"] is None:

            st.warning(
                "⏳ Probabilidades no disponibles "
                "para este encuentro."
            )

            return

        ph, pa, pd_, source = game["probs"]

        if fav:

            prob, name = fav

            rank, css = demon_rank(prob)

            st.markdown(
                f"""
                <div style="margin-bottom:12px;">

                    <span class="demon-badge {css}">
                        {escape(rank)}
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"🎯 **Favorito del mercado: {name}**"
            )

            st.markdown(
                f"### 🔥 {prob:.1f}%"
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

        st.caption(
            f"📡 Fuente: {source}"
        )

        if featured:

            st.caption(
                "⭐ Partido destacado por favoritismo "
                "del mercado."
            )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div class="demon-header">

    <div class="demon-title">
        😈 DEMON
        <span>PREDICTIONS</span>
    </div>

    <div class="demon-subtitle">
        RED EDITION · SPORTS INTELLIGENCE PLATFORM
    </div>

    <div class="live-badge">
        ● LIVE DATA · POWERED BY ESPN
    </div>

</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        # 😈 DEMON

        **PREDICTIONS 2.0**

        🔴 RED EDITION
        """
    )

    st.divider()

    st.markdown("### ⚙️ CENTRO DE CONTROL")

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
        "🔴 Solo partidos en vivo",
        value=False,
    )

    search = st.text_input(
        "🔎 Buscar equipo",
        placeholder="Ej: Lakers, Madrid...",
    )

    st.divider()

    if st.button(
        "🔄 ACTUALIZAR DATOS",
        use_container_width=True,
    ):

        st.cache_data.clear()

        st.rerun()

    st.divider()

    st.markdown(
        """
        **📡 SISTEMA**

        🟢 ESPN DATA

        🔄 Actualización: 60 segundos

        🌎 Zona horaria: Colombia

        🔐 Sin clave de API
        """
    )

    st.caption(
        "DEMON PREDICTIONS 2.0"
    )


# =========================================================
# DASHBOARD PRINCIPAL
# =========================================================

def dashboard():

    if not selected:

        st.warning(
            "Selecciona al menos una liga."
        )

        return

    all_games = []

    errors = []

    with st.spinner(
        "😈 DEMON está analizando los partidos..."
    ):

        for name in selected:

            try:

                games = load_league(
                    name,
                    day,
                )

                all_games.extend(games)

            except Exception as e:

                errors.append(
                    f"{name}: {e}"
                )

    for error in errors:

        st.warning(
            f"⚠️ Error cargando {error}"
        )

    # Aplicar filtros generales

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

    # Estadísticas

    total = len(games)

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
        "🕒 Última actualización: "
        f"{dt.datetime.now(TZ).strftime('%H:%M:%S')}"
        " · Colombia"
    )

    section_title(
        "📊 DEMON CONTROL CENTER",
        "Resumen de los encuentros deportivos",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        stat_card(
            "🏆 PARTIDOS",
            total,
            "Encuentros encontrados",
        )

    with c2:

        stat_card(
            "🎯 CON CUOTAS",
            len(with_probs),
            "Probabilidades disponibles",
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
            "No hay partidos disponibles "
            "con los filtros seleccionados."
        )

        return

    # =====================================================
    # TOP PICKS
    # =====================================================

    section_title(
        "🔥 DEMON TOP PICKS",
        "Los favoritos más marcados del mercado",
    )

    # Solo partidos programados con probabilidades.

    upcoming = [
        g for g in with_probs
        if g["state"] == "pre"
        and favorite(g)
        and favorite(g)[0] >= min_conf
    ]

    top_games = sorted(
        upcoming,
        key=lambda g: favorite(g)[0],
        reverse=True,
    )[:3]

    if top_games:

        columns = st.columns(
            len(top_games)
        )

        for i, game in enumerate(top_games):

            with columns[i]:

                match_card(
                    game,
                    featured=True,
                )

    else:

        st.info(
            "No hay favoritos disponibles "
            "para los filtros actuales."
        )

    # =====================================================
    # TABLA DE PRONÓSTICOS
    # =====================================================

    section_title(
        "🎯 RANKING DE PRONÓSTICOS",
        "Ordenados por probabilidad implícita",
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
            "No hay pronósticos que cumplan "
            "la probabilidad mínima."
        )

    # =====================================================
    # MATCH CENTER
    # =====================================================

    section_title(
        "⚽ DEMON MATCH CENTER",
        "Todos los encuentros por categoría",
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

    for tab, category in zip(
        tabs,
        categories,
    ):

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
                    "No hay partidos disponibles "
                    "en esta categoría."
                )

                continue

            st.caption(
                f"🏆 {len(filtered)} encuentros"
            )

            for i in range(
                0,
                len(filtered),
                2,
            ):

                cols = st.columns(2)

                for j in range(2):

                    index = i + j

                    if index < len(filtered):

                        with cols[j]:

                            match_card(
                                filtered[index]
                            )

    # =====================================================
    # ESTADÍSTICAS
    # =====================================================

    section_title(
        "📈 DEMON ANALYTICS",
        "Distribución de partidos por liga",
    )

    if games:

        league_counts = {}

        for g in games:

            league_counts[g["liga"]] = (
                league_counts.get(
                    g["liga"],
                    0,
                ) + 1
            )

        stats_df = pd.DataFrame(
            {
                "Liga": list(
                    league_counts.keys()
                ),
                "Partidos": list(
                    league_counts.values()
                ),
            }
        )

        st.bar_chart(
            stats_df.set_index("Liga"),
            color="#ff304b",
        )

    # =====================================================
    # AVISO
    # =====================================================

    st.divider()

    st.info(
        "📊 Las probabilidades mostradas se "
        "obtienen de cuotas del mercado o "
        "estimaciones basadas en spread. "
        "No garantizan resultados deportivos. "
        "Una probabilidad alta no significa "
        "necesariamente que una apuesta tenga valor."
    )


# =========================================================
# ACTUALIZACIÓN AUTOMÁTICA
# =========================================================

@st.fragment(run_every=60)
def live_dashboard():

    dashboard()


live_dashboard()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
<div class="demon-footer">

    😈 DEMON PREDICTIONS 2.0

    <br><br>

    RED EDITION · SPORTS INTELLIGENCE

    <br><br>

    POWERED BY ESPN PUBLIC DATA

    <br><br>

    © 2026 DEMON PREDICTIONS

</div>
""",
    unsafe_allow_html=True,
)
