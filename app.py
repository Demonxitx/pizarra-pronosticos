"""Pizarra de Pronósticos: partidos de hoy con probabilidades en tiempo real.

Fuente de datos: marcadores públicos de ESPN (sin clave de API).
Las probabilidades salen de las cuotas del mercado (moneyline) o, si no hay,
del spread (diferencia de puntos esperada). Se refrescan solas cada 60 segundos.

Ejecutar:  py -3.13 -m streamlit run app.py
"""
import math
import re
import datetime as dt

import requests
import pandas as pd
import streamlit as st

# nombre -> (deporte, liga, desviación típica para convertir spread en probabilidad)
LEAGUES = {
    "NBA": ("basketball", "nba", 12.0),
    "WNBA": ("basketball", "wnba", 11.0),
    "NCAA baloncesto": ("basketball", "mens-college-basketball", 11.0),
    "NFL": ("football", "nfl", 13.5),
    "NCAA fútbol americano": ("football", "college-football", 14.0),
    "NHL": ("hockey", "nhl", None),
    "MLB": ("baseball", "mlb", None),
    "Premier League": ("soccer", "eng.1", None),
    "La Liga": ("soccer", "esp.1", None),
    "Serie A": ("soccer", "ita.1", None),
    "Bundesliga": ("soccer", "ger.1", None),
    "Ligue 1": ("soccer", "fra.1", None),
    "Champions League": ("soccer", "uefa.champions", None),
    "MLS": ("soccer", "usa.1", None),
    "Liga BetPlay": ("soccer", "col.1", None),
    "Libertadores": ("soccer", "conmebol.libertadores", None),
}

BASE = "https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"


def ml_to_prob(ml):
    """Convierte una cuota americana (por ejemplo -150 o +130) en probabilidad."""
    try:
        ml = float(str(ml).replace("EVEN", "100").replace("+", ""))
    except (TypeError, ValueError):
        return None
    if ml == 0:
        return None
    return 100 / (ml + 100) if ml > 0 else -ml / (-ml + 100)


def pick_ml(odds, side):
    """Busca la cuota de un lado (home, away, draw) en los dos formatos de ESPN."""
    block = odds.get(side + "TeamOdds") if side != "draw" else odds.get("drawOdds")
    if isinstance(block, dict) and block.get("moneyLine") is not None:
        return ml_to_prob(block["moneyLine"])
    ml = odds.get("moneyline", {})
    side_block = ml.get(side, {}) if isinstance(ml, dict) else {}
    for key in ("close", "open"):
        val = side_block.get(key, {}).get("odds") if isinstance(side_block.get(key), dict) else None
        if val is not None:
            return ml_to_prob(val)
    return None


def spread_prob(odds, home_abbr, away_abbr, sd):
    """Probabilidad del local a partir del spread, con distribución normal."""
    details = str(odds.get("details", "")).strip()
    if not details or sd is None:
        return None
    if details.upper() == "EVEN":
        return 0.5
    m = re.match(r"([A-Za-z.]+)\s*([+-]?\d+(?:\.\d+)?)", details)
    if not m:
        return None
    abbr, line = m.group(1).upper(), abs(float(m.group(2)))
    p_fav = 0.5 * (1 + math.erf(line / sd / math.sqrt(2)))
    if abbr == home_abbr.upper():
        return p_fav
    if abbr == away_abbr.upper():
        return 1 - p_fav
    return None


def probabilities(comp, home, away, sd):
    """Devuelve (p_local, p_visitante, p_empate, fuente) en porcentaje, o None."""
    odds_list = comp.get("odds") or []
    if not odds_list:
        return None
    odds = odds_list[0]
    ph, pa, pd_ = pick_ml(odds, "home"), pick_ml(odds, "away"), pick_ml(odds, "draw")
    if ph is not None and pa is not None:
        total = ph + pa + (pd_ or 0)  # quita el margen de la casa
        return ph / total * 100, pa / total * 100, (pd_ / total * 100 if pd_ else None), "cuotas del mercado"
    p = spread_prob(odds, home["abbr"], away["abbr"], sd)
    if p is not None:
        return p * 100, (1 - p) * 100, None, "spread"
    return None


@st.cache_data(ttl=60, show_spinner=False)
def load_league(name, day):
    sport, league, sd = LEAGUES[name]
    url = BASE.format(sport=sport, league=league)
    r = requests.get(url, params={"dates": day.strftime("%Y%m%d")}, timeout=15,
                     headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    games = []
    for ev in r.json().get("events", []):
        comp = ev["competitions"][0]
        teams = {}
        for c in comp["competitors"]:
            t = c["team"]
            teams[c["homeAway"]] = {
                "name": t.get("displayName", "?"),
                "abbr": t.get("abbreviation", "?"),
                "score": c.get("score", "0"),
            }
        if "home" not in teams or "away" not in teams:
            continue
        start = dt.datetime.fromisoformat(ev["date"].replace("Z", "+00:00")).astimezone()
        st_type = ev["status"]["type"]
        probs = probabilities(comp, teams["home"], teams["away"], sd)
        games.append({
            "liga": name, "hora": start, "state": st_type.get("state", "pre"),
            "estado": st_type.get("shortDetail", ""),
            "home": teams["home"], "away": teams["away"], "probs": probs,
        })
    return games


def label(g):
    if g["probs"] is None:
        return None
    ph, pa, pdr, _ = g["probs"]
    best = max([(ph, g["home"]["name"]), (pa, g["away"]["name"])] + ([(pdr, "Empate")] if pdr else []))
    return best


def render(selected, day, min_conf):
    all_games, errors = [], []
    for name in selected:
        try:
            all_games += load_league(name, day)
        except Exception as e:  # una liga caída no tumba la app
            errors.append(f"{name}: {e}")
    for e in errors:
        st.warning("No se pudo cargar " + e)

    rows, cards = [], []
    for g in all_games:
        best = label(g)
        if best is None or best[0] < min_conf:
            if best is None:
                cards.append(g)
            continue
        rows.append({
            "Liga": g["liga"], "Hora": g["hora"].strftime("%H:%M"),
            "Partido": f'{g["away"]["name"]} @ {g["home"]["name"]}',
            "Pronóstico": best[1], "Probabilidad %": round(best[0], 1),
            "Estado": g["estado"],
        })
        cards.append(g)

    st.caption(f"Actualizado {dt.datetime.now().strftime('%H:%M:%S')} · se refresca cada 60 s")
    if not rows:
        st.info("No hay partidos con probabilidad para esta fecha y filtros. Prueba otra fecha o más ligas.")
        return

    df = pd.DataFrame(rows).sort_values("Probabilidad %", ascending=False).reset_index(drop=True)
    st.subheader("Los pronósticos más claros")
    st.dataframe(df, use_container_width=True, hide_index=True,
                 column_config={"Probabilidad %": st.column_config.ProgressColumn(
                     "Probabilidad %", min_value=0, max_value=100, format="%.1f")})

    st.subheader("Todos los partidos")
    for g in sorted(cards, key=lambda x: (x["liga"], x["hora"])):
        with st.container(border=True):
            top = st.columns([2, 3, 2])
            top[0].markdown(f'**{g["liga"]}**  \n{g["hora"].strftime("%H:%M")}')
            top[1].markdown(f'**{g["away"]["name"]}** @ **{g["home"]["name"]}**')
            if g["state"] != "pre":
                top[2].markdown(f'{g["away"]["score"]} - {g["home"]["score"]}  \n{g["estado"]}')
            else:
                top[2].markdown(g["estado"])
            if g["probs"] is None:
                st.caption("Sin cuotas disponibles todavía para este partido.")
                continue
            ph, pa, pdr, src = g["probs"]
            c = st.columns(3 if pdr else 2)
            c[0].metric(g["away"]["abbr"] + " (visitante)", f"{pa:.1f}%")
            c[-1].metric(g["home"]["abbr"] + " (local)", f"{ph:.1f}%")
            if pdr:
                c[1].metric("Empate", f"{pdr:.1f}%")
            st.progress(min(max(ph / 100, 0.0), 1.0))
            st.caption(f"Fuente: {src}")


st.set_page_config(page_title="Pizarra de Pronósticos", page_icon="📊", layout="wide")
st.title("Pizarra de Pronósticos")
st.write("Probabilidades de victoria calculadas con las cuotas del mercado, que es la base más precisa disponible gratis. "
         "Ningún pronóstico garantiza un resultado.")

with st.sidebar:
    st.header("Filtros")
    day = st.date_input("Fecha", dt.date.today())
    selected = st.multiselect("Deportes y ligas", list(LEAGUES), default=["NBA", "NFL", "NHL", "MLB"])
    min_conf = st.slider("Probabilidad mínima del favorito (%)", 50, 90, 50)
    st.caption("Fuente de datos: marcadores públicos de ESPN.")

if not selected:
    st.info("Elige al menos una liga en el panel izquierdo.")
else:
    @st.fragment(run_every=60)
    def live():
        render(selected, day, min_conf)

    live()
