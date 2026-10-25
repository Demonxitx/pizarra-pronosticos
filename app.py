"""
DEMON PREDICTIONS 4.0
PERFORMANCE EDITION

Sports Intelligence
Supabase Authentication
Persistent Combo History

Fuente deportiva: ESPN
Zona horaria: Colombia
Actualización: 60 segundos
"""

import math
import re
import datetime as dt
from html import escape

import pandas as pd
import requests
import streamlit as st

from supabase import create_client


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="DEMON PREDICTIONS 4.0",
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
# DISEÑO DEMON RED
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(
            ellipse at 50% -10%,
            rgba(195,20,50,.17),
            transparent 50%
        ),
        #08090e;
    color: #f5f5f7;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif;
}

section[data-testid="stSidebar"] {
    background: #101116;
    border-right: 1px solid #47202c;
}

.hero {
    background: linear-gradient(
        115deg,
        #310b17,
        #151119 55%,
        #290b15
    );
    border: 1px solid #812238;
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 25px;
    box-shadow: 0 0 35px rgba(255,35,65,.10);
}

.hero-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: clamp(35px,5vw,62px);
    font-weight: 700;
    line-height: 1.1;
    color: white;
}

.hero-title span {
    color: #ff304b;
    text-shadow: 0 0 25px rgba(255,48,75,.4);
}

.hero-subtitle {
    color: #b4b4c0;
    font-size: 12px;
    letter-spacing: 2px;
    margin-top: 12px;
}

.live-pill {
    display: inline-block;
    color: #00f29a;
    background: rgba(0,240,140,.08);
    border: 1px solid rgba(0,240,140,.35);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 11px;
    font-weight: 800;
    margin-top: 20px;
}

.section-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: white;
    margin-top: 28px;
    margin-bottom: 4px;
}

.section-description {
    color: #999ba9;
    font-size: 12px;
    margin-bottom: 18px;
}

.stat-card {
    background: linear-gradient(145deg,#1b1b24,#111218);
    border: 1px solid #30303b;
    border-radius: 16px;
    padding: 22px;
    min-height: 135px;
    margin-bottom: 12px;
}

.stat-label {
    color: #aeb0bd;
    font-size: 11px;
    letter-spacing: 1px;
    font-weight: 700;
}

.stat-number {
    color: white;
    font-family: 'Rajdhani', sans-serif;
    font-size: 45px;
    font-weight: 700;
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
    background: rgba(255,214,107,.12);
    border: 1px solid #78602b;
}

.rank-power {
    color: #ff5069;
    background: rgba(255,50,80,.12);
    border: 1px solid #813040;
}

.rank-edge {
    color: #ffb65c;
    background: rgba(255,180,75,.1);
    border: 1px solid #78532d;
}

.rank-balanced {
    color: #b8b9c5;
    background: #23242e;
    border: 1px solid #41424e;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#b91531,#f02b49);
    border: none;
    color: white;
    font-weight: 800;
    border-radius: 10px;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg,#b91531,#ff4059);
}

.footer {
    color: #81828f;
    border-top: 1px solid #40202a;
    text-align: center;
    padding: 25px;
    margin-top: 40px;
    font-size: 11px;
    letter-spacing: 1px;
}

@media (max-width:768px) {
    .block-container {
        padding-left: 12px;
        padding-right: 12px;
    }

    .hero {
        padding: 20px;
    }

    .hero-title {
        font-size: 35px;
    }

    .stat-card {
        padding: 15px;
        min-height: 110px;
    }

    .stat-number {
        font-size: 34px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# COMPONENTES
# =========================================================

def section_title(title, description=""):
    st.markdown(
        f'<div class="section-title">{escape(title)}</div>'
        f'<div class="section-description">'
        f'{escape(description)}</div>',
        unsafe_allow_html=True,
    )


def stat_card(label, value, footer):
    st.markdown(
        '<div class="stat-card">'
        f'<div class="stat-label">{escape(str(label))}</div>'
        f'<div class="stat-number">{escape(str(value))}</div>'
        f'<div class="stat-footer">{escape(str(footer))}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


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

    st.markdown(
        f'<span class="rank {css}">{escape(title)}</span>',
        unsafe_allow_html=True,
    )


# =========================================================
# SUPABASE
# =========================================================

def get_supabase():
    """
    Cada sesión de Streamlit utiliza su propio cliente.

    No se comparte un cliente autenticado mediante
    cache_resource entre diferentes usuarios.
    """

    if "supabase_client" not in st.session_state:
        config = st.secrets["supabase"]

        st.session_state.supabase_client = create_client(
            config["url"],
            config["key"],
        )

    return st.session_state.supabase_client


def clear_auth():
    st.session_state.pop("demon_session", None)
    st.session_state.pop("demon_user", None)
    st.session_state.pop("supabase_client", None)


def ensure_auth():
    """
    Comprueba la sesión y utiliza los tokens
    del usuario para respetar las políticas RLS.
    """

    session = st.session_state.get("demon_session")

    if not session:
        return None

    try:
        client = get_supabase()

        response = client.auth.set_session(
            session["access_token"],
            session["refresh_token"],
        )

        if not response.session or not response.user:
            clear_auth()
            return None

        st.session_state.demon_session = {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }

        st.session_state.demon_user = {
            "id": response.user.id,
            "email": response.user.email,
        }

        return st.session_state.demon_user

    except Exception:
        clear_auth()
        return None


def login_screen():
    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">'
        '😈 DEMON <span>PREDICTIONS</span>'
        '</div>'
        '<div class="hero-subtitle">'
        '4.0 PERFORMANCE EDITION · PRIVATE ACCESS'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    section_title(
        "🔐 DEMON PRIVATE ACCESS",
        "Acceso exclusivo para usuarios autorizados",
    )

    left, center, right = st.columns([1, 1.5, 1])

    with center:
        with st.container(border=True):
            st.markdown("### 😈 INICIAR SESIÓN")

            with st.form("demon_login"):
                email = st.text_input(
                    "Correo electrónico",
                    placeholder="correo@ejemplo.com",
                )

                password = st.text_input(
                    "Contraseña",
                    type="password",
                )

                submitted = st.form_submit_button(
                    "🔴 ENTRAR A DEMON",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not email.strip() or not password:
                    st.warning(
                        "Introduce tu correo y contraseña."
                    )
                    return

                try:
                    client = get_supabase()

                    response = (
                        client.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password,
                        })
                    )

                    if response.session and response.user:
                        st.session_state.demon_session = {
                            "access_token":
                                response.session.access_token,
                            "refresh_token":
                                response.session.refresh_token,
                        }

                        st.session_state.demon_user = {
                            "id": response.user.id,
                            "email": response.user.email,
                        }

                        st.rerun()

                    else:
                        st.error(
                            "No se pudo iniciar sesión."
                        )

                except Exception:
                    st.error(
                        "No se pudo iniciar sesión. "
                        "Comprueba tus credenciales "
                        "y vuelve a intentarlo."
                    )

            st.caption(
                "Las cuentas son creadas por el "
                "administrador de DEMON PREDICTIONS."
            )


def save_combo(name, chosen_items, combined_pct):
    """
    Guarda la combinada y sus selecciones.

    Si falla el guardado de selecciones, intenta
    eliminar el encabezado. La eliminación requiere
    permisos RLS adicionales, por lo que también
    se informa cuando hay un guardado parcial.
    """

    user = ensure_auth()

    if not user:
        raise RuntimeError(
            "La sesión ha caducado. Inicia sesión nuevamente."
        )

    client = get_supabase()

    combo_data = {
        "user_id": user["id"],
        "nombre": name,
        "probabilidad_conjunta": round(combined_pct, 4),
        "estado": "pendiente",
    }

    response = (
        client.table("demon_combos")
        .insert(combo_data)
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "No se pudo crear la combinada."
        )

    combo_id = response.data[0]["id"]

    picks = []

    for item in chosen_items:
        game = item["game"]

        picks.append({
            "combo_id": combo_id,
            "espn_event_id": game["espn_id"],
            "liga": game["liga"],
            "equipo_local": game["home"]["name"],
            "equipo_visitante": game["away"]["name"],
            "seleccion": item["team"],
            "probabilidad": round(item["prob"], 4),
            "fecha_partido": (
                game["hora"].isoformat()
            ),
            "mercado": (
    "ganador_partido_incluye_prorroga"
    if game["liga"] in ("NBA", "NHL")
    else None
),
            "estado": "pendiente",
        })

    try:
        result = (
            client.table("demon_combo_picks")
            .insert(picks)
            .execute()
        )

        if len(result.data or []) != len(picks):
            raise RuntimeError(
                "No se confirmaron todas las selecciones."
            )

    except Exception as exc:
        raise RuntimeError(
            "Se creó el registro de la combinada, "
            "pero no se pudieron guardar todas sus "
            "selecciones. No vuelvas a guardar "
            "sin revisar primero el historial. "
            f"ID: {combo_id}"
        ) from exc

    return combo_id


def load_history():
    user = ensure_auth()

    if not user:
        return [], []

    client = get_supabase()

    combos_response = (
        client.table("demon_combos")
        .select("*")
        .eq("user_id", user["id"])
        .order("fecha_creacion", desc=True)
        .limit(100)
        .execute()
    )

    combos = combos_response.data or []

    if not combos:
        return [], []

    ids = [combo["id"] for combo in combos]

    picks_response = (
        client.table("demon_combo_picks")
        .select("*")
        .in_("combo_id", ids)
        .execute()
    )

    return combos, picks_response.data or []


# =========================================================
# PROBABILIDADES
# =========================================================

def ml_to_prob(ml):
    try:
        value = float(
            str(ml).upper()
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
    key = (
        "drawOdds"
        if side == "draw"
        else side + "TeamOdds"
    )

    block = odds.get(key)

    if isinstance(block, dict):
        value = block.get("moneyLine")

        if value is not None:
            return ml_to_prob(value)

    moneyline = odds.get("moneyline", {})

    if not isinstance(moneyline, dict):
        return None

    side_block = moneyline.get(side, {})

    if not isinstance(side_block, dict):
        return None

    for period in ("close", "open"):
        item = side_block.get(period)

        if (
            isinstance(item, dict)
            and item.get("odds") is not None
        ):
            return ml_to_prob(item["odds"])

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


# =========================================================
# ESPN
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
            "dates": day.strftime("%Y%m%d"),
        },
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        timeout=15,
    )

    response.raise_for_status()

    games = []

    for event in response.json().get("events", []):
        competitions = event.get("competitions") or []

        if not competitions:
            continue

        comp = competitions[0]

        teams = {}

        for competitor in comp.get("competitors", []):
            team = competitor.get("team", {})
            logos = team.get("logos") or []

            logo = (
                logos[0].get("href")
                if logos
                else None
            )

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

        status = (
            event.get("status", {})
            .get("type", {})
        )

        probs = probabilities(
            comp,
            teams["home"],
            teams["away"],
            sd,
            sport,
        )

        games.append({
            "id": f"{name}-{event.get('id')}",
            "espn_id": str(event.get("id", "")),
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


# =========================================================
# FAVORITOS
# =========================================================

def favorite(game):
    if game["probs"] is None:
        return None

    ph, pa, pd_, _ = game["probs"]

    choices = [
        (ph, game["home"]["name"]),
        (pa, game["away"]["name"]),
    ]

    if pd_ is not None:
        choices.append((pd_, "Empate"))

    return max(
        choices,
        key=lambda item: item[0],
    )


def upcoming_favorites(games, min_conf):
    result = []

    for game in games:
        if game["state"] != "pre":
            continue

        fav = favorite(game)

        if fav and fav[0] >= min_conf:
            result.append(game)

    return sorted(
        result,
        key=lambda game: favorite(game)[0],
        reverse=True,
    )


# =========================================================
# TARJETAS DE PARTIDOS
# =========================================================

def show_logo(team):
    logo = team.get("logo")

    if logo and str(logo).startswith("https://"):
        st.image(logo, width=65)
    else:
        st.markdown("🏆")


def probability_bar(name, value):
    st.markdown(
        f"**{name}: {value:.1f}%**"
    )

    st.progress(
        min(max(value / 100, 0), 1)
    )


def match_card(game, featured=False):
    with st.container(border=True):
        left, right = st.columns([3, 1])

        with left:
            icon = SPORT_ICONS.get(
                game["sport"],
                "🏆",
            )

            st.markdown(
                f"### {icon} {game['liga']}"
            )

        with right:
            if game["state"] == "in":
                st.error("LIVE")

            elif game["state"] == "post":
                st.success("FINAL")

            else:
                st.caption("PRÓXIMO")

        st.caption(
            "🕒 "
            + game["hora"].strftime("%d/%m/%Y %H:%M")
            + " · Colombia"
        )

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
            st.caption(game["estado"])

        st.divider()

        if game["probs"] is None:
            st.warning(
                "Probabilidades no disponibles."
            )
            return

        ph, pa, pd_, source = game["probs"]

        fav = favorite(game)

        if fav:
            prob, name = fav

            rank_badge(prob)

            st.markdown(
                f"🎯 **Favorito: {name}**"
            )

            st.metric(
                "Probabilidad implícita",
                f"{prob:.1f}%",
            )

        st.markdown(
            "##### 📊 PROBABILIDADES"
        )

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
            f"Fuente: {source}"
        )

        if featured:
            st.caption(
                "⭐ Destacado por favoritismo del mercado."
            )


# =========================================================
# CABECERA
# =========================================================

def hero():
    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">'
        '😈 DEMON <span>PREDICTIONS</span>'
        '</div>'
        '<div class="hero-subtitle">'
        '4.0 PERFORMANCE EDITION · SPORTS INTELLIGENCE'
        '</div>'
        '<div class="live-pill">'
        '● LIVE DATA · POWERED BY ESPN'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# HISTORIAL
# =========================================================

def combo_history():
    section_title(
        "💾 DEMON COMBO HISTORY",
        "Historial permanente de tus combinadas",
    )

    if st.button(
        "🔄 ACTUALIZAR HISTORIAL",
        key="refresh_history",
    ):
        st.rerun()

    try:
        combos, picks = load_history()

    except Exception:
        st.error(
            "No se pudo consultar el historial. "
            "Comprueba la conexión con Supabase."
        )
        return

    if not combos:
        st.info(
            "Todavía no tienes combinadas guardadas. "
            "Crea tu primera combinada en DEMON COMBO BUILDER."
        )
        return

    total = len(combos)

    pending = sum(
        1
        for combo in combos
        if combo["estado"] == "pendiente"
    )

    c1, c2 = st.columns(2)

    with c1:
        stat_card(
            "🎰 COMBINADAS",
            total,
            "Últimas 100 combinadas",
        )

    with c2:
        stat_card(
            "⏳ PENDIENTES",
            pending,
            "En espera de verificación",
        )

    for combo in combos:
        combo_picks = [
            pick
            for pick in picks
            if pick["combo_id"] == combo["id"]
        ]

        title = (
            f"🎰 {combo['nombre']} "
            f"· {combo['estado'].upper()}"
        )

        with st.expander(title):
            st.caption(
                "📅 Creada: "
                + str(combo["fecha_creacion"])[:19]
                .replace("T", " ")
                + " UTC"
            )

            probability = (
                combo.get("probabilidad_conjunta")
            )

            if probability is not None:
                st.metric(
                    "🎯 Probabilidad conjunta estimada",
                    f"{float(probability):.2f}%",
                )

            if combo_picks:
                rows = []

                for pick in combo_picks:
                    rows.append({
                        "Liga": pick["liga"],
                        "Partido": (
                            pick["equipo_visitante"]
                            + " vs "
                            + pick["equipo_local"]
                        ),
                        "Selección": pick["seleccion"],
                        "Probabilidad %": (
                            float(pick["probabilidad"])
                            if pick["probabilidad"] is not None
                            else None
                        ),
                        "Estado": pick["estado"],
                    })

                st.dataframe(
                    pd.DataFrame(rows),
                    hide_index=True,
                    use_container_width=True,
                )

            else:
                st.warning(
                    "Esta combinada no tiene selecciones "
                    "registradas. Puede tratarse de un "
                    "guardado incompleto."
                )

            st.caption(
                "Los resultados todavía no se actualizan "
                "automáticamente. Las selecciones "
                "permanecerán pendientes hasta implementar "
                "el verificador de resultados."
            )


# =========================================================
# CONSTRUCTOR DE COMBINADAS
# =========================================================

def combo_builder(games, min_conf):
    section_title(
        "🎰 DEMON COMBO BUILDER",
        "Construye, analiza y guarda tus combinadas",
    )

    candidates = upcoming_favorites(
        games,
        min_conf,
    )

    if not candidates:
        st.info(
            "No hay partidos próximos con probabilidades "
            "suficientes para construir una combinada."
        )
        return

    lookup = {}

    for game in candidates:
        fav = favorite(game)

        if not fav:
            continue

        prob, team = fav

        label = (
            f"{game['liga']} | "
            f"{game['away']['name']} vs "
            f"{game['home']['name']} | "
            f"{team} ({prob:.1f}%)"
        )

        lookup[game["id"]] = {
            "label": label,
            "game": game,
            "team": team,
            "prob": prob,
        }

    chosen = st.multiselect(
        "🏆 Selecciona los favoritos",
        list(lookup),
        format_func=lambda key: lookup[key]["label"],
        max_selections=12,
        key="combo_selections",
    )

    if not chosen:
        st.info(
            "Selecciona al menos un partido para "
            "construir tu combinada."
        )
        return

    combined_probability = 1.0

    rows = []
    chosen_items = []

    for key in chosen:
        item = lookup[key]

        combined_probability *= (
            item["prob"] / 100
        )

        chosen_items.append(item)

        rows.append({
            "Liga": item["game"]["liga"],
            "Selección": item["team"],
            "Probabilidad %": round(
                item["prob"],
                1,
            ),
        })

    combined_pct = (
        combined_probability * 100
    )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        stat_card(
            "🎯 PROBABILIDAD CONJUNTA",
            f"{combined_pct:.2f}%",
            "Supone independencia",
        )

    with c2:
        stat_card(
            "🏆 SELECCIONES",
            len(chosen),
            "Equipos seleccionados",
        )

    with c3:
        stat_card(
            "⚠️ PROBABILIDAD DE FALLO",
            f"{100 - combined_pct:.2f}%",
            "Estimación complementaria",
        )

    st.progress(
        min(
            max(combined_probability, 0),
            1,
        )
    )

    section_title(
        "⚠️ DEMON RISK ANALYZER",
        "Análisis aproximado del riesgo acumulado",
    )

    if combined_pct >= 70:
        st.success(
            "Probabilidad conjunta estimada elevada "
            "bajo los supuestos del cálculo."
        )

    elif combined_pct >= 40:
        st.warning(
            "Probabilidad conjunta intermedia. "
            "Existe un riesgo considerable de fallo."
        )

    else:
        st.error(
            "Probabilidad conjunta estimada baja. "
            "Es difícil acertar todas las selecciones."
        )

    st.caption(
        "La probabilidad conjunta se calcula "
        "multiplicando probabilidades individuales. "
        "Esto supone independencia y puede ser "
        "incorrecto cuando los resultados están "
        "correlacionados."
    )

    evolution = []
    running = 1.0

    for index, key in enumerate(
        chosen,
        start=1,
    ):
        running *= (
            lookup[key]["prob"] / 100
        )

        evolution.append({
            "Selecciones": index,
            "Probabilidad %": running * 100,
        })

    st.line_chart(
        pd.DataFrame(evolution).set_index(
            "Selecciones"
        ),
        color="#ff304b",
    )

    st.divider()

    st.markdown(
        "### 💾 GUARDAR COMBINADA"
    )

    st.caption(
        "Tu combinada se guardará permanentemente "
        "en Supabase y estará asociada a tu cuenta."
    )

    with st.form("save_combo_form"):
        name = st.text_input(
            "Nombre de la combinada",
            value=(
                "DEMON COMBO "
                + dt.datetime.now(TZ).strftime(
                    "%d/%m/%Y"
                )
            ),
            max_chars=100,
        )
        requiere_confirmacion = any(
            item["game"]["liga"] in ("NBA", "NHL")
            for item in chosen_items
        )

        mercado_confirmado = st.checkbox(
            "Confirmo que mis selecciones NBA/NHL "
            "son al ganador del partido, "
            "incluyendo prórroga.",
            value=False,
            disabled=not requiere_confirmacion,
        )
        submitted = st.form_submit_button(
            "💾 GUARDAR COMBINADA",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not name.strip():
            st.warning(
                "Introduce un nombre para la combinada."
            )

        elif requiere_confirmacion and not mercado_confirmado:
            st.warning(
                "Debes confirmar que tus selecciones "
                "NBA/NHL son al ganador del partido "
                "incluyendo prórroga."
            )

        else:
            try:
                combo_id = save_combo(
                    name.strip(),
                    chosen_items,
                    combined_pct,
                )

                st.success(
                    "✅ ¡Combinada guardada correctamente!"
                )

                st.caption(
                    f"ID del registro: {combo_id}"
                )

                st.info(
                    "Abre DEMON COMBO HISTORY para "
                    "consultar tu combinada guardada."
                )

            except Exception as exc:
                st.error(
                    "No se pudo completar el guardado."
                )

                st.warning(str(exc))


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(day, selected, min_conf, only_live, search):
    if not selected:
        st.warning(
            "Selecciona al menos una liga."
        )
        return

    all_games = []
    errors = []

    with st.spinner(
        "😈 Cargando encuentros..."
    ):
        for name in selected:
            try:
                all_games.extend(
                    load_league(name, day)
                )

            except (
                requests.RequestException,
                ValueError,
                KeyError,
                TypeError,
            ):
                errors.append(name)

    if errors:
        st.warning(
            "No se pudieron cargar: "
            + ", ".join(errors)
        )

    games = all_games

    if only_live:
        games = [
            g
            for g in games
            if g["state"] == "in"
        ]

    if search.strip():
        term = search.strip().lower()

        games = [
            g
            for g in games
            if (
                term in g["home"]["name"].lower()
                or term in g["away"]["name"].lower()
            )
        ]

    with_probs = [
        g
        for g in games
        if g["probs"] is not None
    ]

    live_games = [
        g
        for g in games
        if g["state"] == "in"
    ]

    strong = [
        g
        for g in with_probs
        if (
            favorite(g)
            and favorite(g)[0] >= 70
        )
    ]

    st.caption(
        "🕒 Actualizado: "
        + dt.datetime.now(TZ).strftime(
            "%H:%M:%S"
        )
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
            "Encontrados",
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
            "Favoritos destacados",
        )

    with c4:
        stat_card(
            "🔴 EN VIVO",
            len(live_games),
            "Partidos en desarrollo",
        )

    if not games:
        st.info(
            "No hay encuentros disponibles."
        )
        return

    # TOP PICKS

    section_title(
        "🔥 DEMON TOP PICKS PRO",
        "Favoritos destacados del mercado",
    )

    top_games = upcoming_favorites(
        games,
        min_conf,
    )[:3]

    if top_games:
        cols = st.columns(
            len(top_games)
        )

        for i, game in enumerate(top_games):
            with cols[i]:
                match_card(
                    game,
                    featured=True,
                )

    else:
        st.info(
            "No hay favoritos próximos disponibles."
        )

    # CONSTRUCTOR

    combo_builder(
        games,
        min_conf,
    )

    # HISTORIAL

    combo_history()

    # RANKING

    section_title(
        "🏆 DEMON POWER RANKING",
        "Favoritos ordenados por probabilidad",
    )

    rows = []

    for game in games:
        fav = favorite(game)

        if (
            fav is None
            or fav[0] < min_conf
        ):
            continue

        prob, team = fav

        rank, _ = demon_rank(prob)

        rows.append({
            "Liga": game["liga"],
            "Hora": game["hora"].strftime(
                "%H:%M"
            ),
            "Partido": (
                game["away"]["name"]
                + " vs "
                + game["home"]["name"]
            ),
            "Favorito": team,
            "Probabilidad": round(
                prob,
                1,
            ),
            "Clasificación": rank,
            "Estado": game["estado"],
        })

    if rows:
        df = pd.DataFrame(
            rows
        ).sort_values(
            "Probabilidad",
            ascending=False,
        )

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
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

        st.download_button(
            "📥 DESCARGAR RANKING",
            df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            "demon_ranking.csv",
            "text/csv",
        )

    else:
        st.info(
            "No hay favoritos para este filtro."
        )

    # MATCH CENTER

    section_title(
        "⚽ DEMON MATCH CENTER",
        "Todos los encuentros por deporte",
    )

    tabs = st.tabs([
        "🔥 TODOS",
        "⚽ FÚTBOL",
        "🏀 BASKET",
        "🏈 NFL/NCAA",
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
                g
                for g in games
                if (
                    category is None
                    or g["sport"] == category
                )
            ]

            filtered = [
                g
                for g in filtered
                if (
                    favorite(g) is None
                    or favorite(g)[0] >= min_conf
                )
            ]

            filtered.sort(
                key=lambda g: (
                    g["liga"],
                    g["hora"],
                )
            )

            if not filtered:
                st.info(
                    "No hay partidos en esta categoría."
                )
                continue

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

    # AI LAB

    section_title(
        "🧠 DEMON AI LAB",
        "Centro de desarrollo del modelo predictivo",
    )

    with st.container(border=True):
        st.markdown(
            "### 🤖 ESTADO DEL MOTOR DE IA"
        )

        st.info(
            "El modelo predictivo independiente "
            "todavía no está entrenado. "
            "Las probabilidades actuales provienen "
            "de cuotas del mercado o estimaciones "
            "basadas en spreads."
        )

        st.markdown(
            "**Próxima etapa:** recopilar resultados "
            "históricos de NBA y fútbol, construir "
            "variables estadísticas y entrenar "
            "modelos específicos para cada deporte."
        )

        st.caption(
            "Los futuros modelos se evaluarán "
            "con partidos históricos no utilizados "
            "durante su entrenamiento."
        )

    st.divider()

    st.info(
        "Las probabilidades mostradas son "
        "estimaciones basadas en cuotas o spread. "
        "No garantizan resultados. "
        "Una probabilidad alta no implica "
        "rentabilidad en apuestas."
    )


# =========================================================
# INICIO DE LA APLICACIÓN
# =========================================================

try:
    user = ensure_auth()

except Exception:
    user = None


if not user:
    login_screen()

    st.stop()


# =========================================================
# SIDEBAR PRIVADA
# =========================================================

with st.sidebar:
    st.title("😈 DEMON")

    st.markdown(
        "**PREDICTIONS 4.0**"
    )

    st.caption(
        "🔴 PERFORMANCE EDITION"
    )

    st.divider()

    st.success(
        "🔐 SESIÓN ACTIVA"
    )

    st.caption(
        f"👤 {user['email']}"
    )

    if st.button(
        "🚪 CERRAR SESIÓN",
        use_container_width=True,
    ):
        try:
            get_supabase().auth.sign_out()

        except Exception:
            pass

        clear_auth()

        st.rerun()

    st.divider()

    st.subheader(
        "⚙️ CENTRO DE CONTROL"
    )

    day = st.date_input(
        "📅 Fecha",
        dt.datetime.now(TZ).date(),
    )

    selected = st.multiselect(
        "🏆 Ligas",
        list(LEAGUES),
        default=[
            "NBA",
            "NFL",
            "NHL",
            "MLB",
        ],
    )

    min_conf = st.slider(
        "🎯 Probabilidad mínima",
        50,
        90,
        50,
    )

    only_live = st.checkbox(
        "🔴 Solo partidos en vivo"
    )

    search = st.text_input(
        "🔎 Buscar equipo",
        placeholder="Ej: Lakers...",
    )

    st.divider()

    if st.button(
        "🔄 ACTUALIZAR",
        type="primary",
        use_container_width=True,
    ):
        st.cache_data.clear()

        st.rerun()

    st.caption(
        "📡 ESPN · Actualización cada 60 segundos"
    )

    st.caption(
        "🌎 Hora Colombia"
    )

    st.caption(
        "💾 Historial conectado a Supabase"
    )


# =========================================================
# DASHBOARD PRIVADO
# =========================================================

hero()


@st.fragment(run_every=60)
def live_dashboard():
    dashboard(
        day,
        selected,
        min_conf,
        only_live,
        search,
    )


live_dashboard()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    '😈 DEMON PREDICTIONS 4.0'
    '<br><br>'
    'PERFORMANCE EDITION · DEMON RED'
    '<br><br>'
    'SPORTS INTELLIGENCE & COMBO HISTORY'
    '<br><br>'
    '© 2026 DEMON PREDICTIONS'
    '</div>',
    unsafe_allow_html=True,
)
