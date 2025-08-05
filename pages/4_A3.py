import base64
import logging
import streamlit as st
import json
import pandas as pd
import os
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Futsal De Toque - A3",
    page_icon=":material/sports_soccer:",
    layout="wide"
)
st.markdown("# A3")
st.sidebar.markdown("# Futsal De Toque")

# Detect mobile device
is_mobile = st.query_params.get("mobile", ["false"])[0].lower() == "true" or (
    "Mobi" in st._get_user_agent() if hasattr(st, "_get_user_agent") else False
)

# Define tabs
tab1, tab2, tab3 = st.tabs(["Fixture", "Tabla", "Estadisticas"])

# Root path
root_path = os.getcwd()

# Cache file loading with category-specific key
@st.cache_data
def load_json_a3(file_path, category="a3"):
    logger.info(f"Loading JSON: {file_path}")
    with open(file_path, 'r') as file:
        return json.load(file)

@st.cache_data
def load_csv_a3(file_path, category="a3"):
    logger.info(f"Loading CSV: {file_path}")
    return pd.read_csv(file_path)

# Cache image to Base64 conversion
@st.cache_data
def image_to_base64(image_path, _category="a3"):
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            return ""
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded}"
    except (FileNotFoundError, IOError):
        logger.warning(f"Failed to load image: {image_path}")
        return ""

# Cache logo dictionary creation
@st.cache_data
def build_logo_dict(_logos_data, root_path, _category="a3"):
    logo_dict = {}
    missing_logos = []
    for item in _logos_data:
        team = item['equipo']
        logo_path = f"{root_path}{item['logo']}"
        base64_url = image_to_base64(logo_path, _category="a3")
        if base64_url:
            logo_dict[team] = base64_url
        else:
            missing_logos.append(f"{team}: {logo_path}")
    logger.info(f"Built logo dict with {len(logo_dict)} logos")
    return logo_dict, missing_logos

# Function to get base team name
def get_base_team_name(team):
    for base_name in logo_dict.keys():
        if team.startswith(base_name):
            return base_name
    return team

# Load logos.json
try:
    logos_data = load_json_a3(f'{root_path}/data/logos.json', category="a3")
except (json.JSONDecodeError, FileNotFoundError) as e:
    logger.error(f"Error loading logos.json: {str(e)}")
    st.error(f"Error loading logos.json: {str(e)}")
    st.stop()

logo_dict, missing_logos = build_logo_dict(logos_data, root_path, _category="a3")
if missing_logos:
    st.warning(f"Missing or invalid logo files:\n" + "\n".join(missing_logos))

# Tab 1: Fixture
with tab1:
    try:
        data = load_json_a3(f'{root_path}/data/a3.json', category="a3")
        if not data:
            st.header("El fixture será cargado en los próximos días")
            st.stop()
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading a3.json: {str(e)}")
        st.error(f"Error loading a3.json: {str(e)}")
        st.stop()

    @st.cache_data
    def process_fixtures_a3(_data, category="a3"):
        logger.info("Processing fixtures for a3")
        all_matches = []
        for fecha in _data:
            for match in fecha['Data']:
                match['Fecha Numero'] = fecha['Fecha']
                all_matches.append(match)
        df = pd.DataFrame(all_matches)
        def parse_date(date_str):
            if not date_str or date_str.strip() == '':
                return pd.NaT
            try:
                return pd.to_datetime(date_str, format='%d/%m/%Y %H:%M')
            except (ValueError, TypeError):
                return pd.NaT
        df['Fecha'] = df['Fecha'].apply(parse_date)
        df['Local_Logo'] = df['Local'].apply(lambda x: logo_dict.get(get_base_team_name(x), ""))
        df['Visitante_Logo'] = df['Visitante'].apply(lambda x: logo_dict.get(get_base_team_name(x), ""))
        return df

    df = process_fixtures_a3(data, category="a3")
    if df['Fecha'].isna().any():
        st.warning(f"Rows with invalid dates: {df[df['Fecha'].isna()][['Fecha Numero', 'Local', 'Visitante']].to_dict('records')}")

    columns = ['Fecha', 'Local_Logo', 'Local', 'GL', 'Visitante_Logo', 'Visitante', 'GV', 'Cancha']
    # Pagination for mobile
    page_size = 5 if is_mobile else 10
    for fecha_num, group in df.groupby('Fecha Numero', sort=False):
        with st.expander(fecha_num, expanded=False):
            try:
                with st.spinner(f"Cargando tabla para {fecha_num}"):
                    display_group = group[columns].copy()
                    if is_mobile:
                        # Simplify for mobile: smaller images, no sorting
                        st.dataframe(
                            display_group,
                            use_container_width=True,
                            height=300,
                            column_config={
                                "Fecha": st.column_config.DatetimeColumn("Dia/Hora", format="DD/MM/YYYY HH:mm"),
                                "Local_Logo": st.column_config.ImageColumn(" ", width=30),
                                "Local": st.column_config.TextColumn("Local"),
                                "GL": st.column_config.TextColumn("Goles", width=40),
                                "Visitante_Logo": st.column_config.ImageColumn(" ", width=30),
                                "Visitante": st.column_config.TextColumn("Visitante"),
                                "GV": st.column_config.TextColumn("Goles", width=40),
                                "Cancha": st.column_config.TextColumn("Cancha")
                            },
                            hide_index=True,
                            key=f"fixture_{fecha_num.replace(' ', '_')}"
                        )
                    else:
                        st.dataframe(
                            display_group,
                            use_container_width=True,
                            column_config={
                                "Fecha": st.column_config.DatetimeColumn("Dia/Hora", format="DD/MM/YYYY HH:mm"),
                                "Local_Logo": st.column_config.ImageColumn(" ", width=40),
                                "Local": st.column_config.TextColumn("Local"),
                                "GL": st.column_config.TextColumn("Goles", width=40),
                                "Visitante_Logo": st.column_config.ImageColumn(" ", width=40),
                                "Visitante": st.column_config.TextColumn("Visitante"),
                                "GV": st.column_config.TextColumn("Goles", width=40),
                                "Cancha": st.column_config.TextColumn("Cancha")
                            },
                            hide_index=True,
                            key=f"fixture_{fecha_num.replace(' ', '_')}"
                        )
                    st.markdown("---")
            except Exception as e:
                logger.error(f"Error rendering fixture table for {fecha_num}: {str(e)}")
                st.error(f"Error al mostrar la tabla para {fecha_num}. Por favor, intenta de nuevo.")

# Tab 2: Tabla (Standings)
with tab2:
    try:
        data = load_json_a3(f'{root_path}/data/a3.json', category="a3")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading a3.json: {str(e)}")
        st.error(f"Error loading a3.json: {str(e)}")
        st.stop()

    regular_season = [f for f in data if f['Fecha'].startswith('Fecha ')]
    @st.cache_data
    def calculate_standings_a3(_regular_season, category="a3"):
        logger.info("Calculating standings for a3")
        all_matches = []
        for fecha in _regular_season:
            for match in fecha['Data']:
                if match['Visitante'].strip() == '':
                    continue
                match['Fecha Numero'] = fecha['Fecha']
                match['Zona'] = match.get('Zona', '')
                all_matches.append(match)
        df_matches = pd.DataFrame(all_matches)
        df_matches['GL'] = pd.to_numeric(df_matches['GL'], errors='coerce').fillna(0).astype(int)
        df_matches['GV'] = pd.to_numeric(df_matches['GV'], errors='coerce').fillna(0).astype(int)
        zonas = df_matches['Zona'].unique()
        all_standings = []
        if len(zonas) == 1 and zonas[0] == '':
            # Single standings table if no zones
            teams = pd.unique(df_matches[['Local', 'Visitante']].values.ravel('K'))
            standings = {team: {'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'Pts': 0, 'GF': 0, 'GA': 0, 'GD': 0} for team in teams}
            for _, match in df_matches.iterrows():
                local = match['Local']
                visitante = match['Visitante']
                gl = match['GL']
                gv = match['GV']
                standings[local]['MP'] += 1
                standings[visitante]['MP'] += 1
                standings[local]['GF'] += gl
                standings[local]['GA'] += gv
                standings[visitante]['GF'] += gv
                standings[visitante]['GA'] += gl
                if gl > gv:
                    standings[local]['W'] += 1
                    standings[local]['Pts'] += 2
                    standings[visitante]['L'] += 1
                elif gl < gv:
                    standings[local]['L'] += 1
                    standings[visitante]['W'] += 1
                    standings[visitante]['Pts'] += 2
                else:
                    standings[local]['D'] += 1
                    standings[local]['Pts'] += 1
                    standings[visitante]['D'] += 1
                    standings[visitante]['Pts'] += 1
            for team in standings:
                standings[team]['GD'] = standings[team]['GF'] - standings[team]['GA']
            standings_data = [
                {'Team': team, 'Logo': logo_dict.get(get_base_team_name(team), ""), **stats}
                for team, stats in standings.items()
            ]
            df_standings = pd.DataFrame(standings_data)
            df_standings = df_standings.sort_values(by=['Pts', 'GD', 'Team'], ascending=[False, False, True])
            all_standings.append(df_standings)
        else:
            # Zone-based standings
            for zona in sorted(zonas):
                df_zona = df_matches[df_matches['Zona'] == zona]
                teams = pd.unique(df_zona[['Local', 'Visitante']].values.ravel('K'))
                standings = {team: {'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'Pts': 0, 'GF': 0, 'GA': 0, 'GD': 0} for team in teams}
                for _, match in df_zona.iterrows():
                    local = match['Local']
                    visitante = match['Visitante']
                    gl = match['GL']
                    gv = match['GV']
                    standings[local]['MP'] += 1
                    standings[visitante]['MP'] += 1
                    standings[local]['GF'] += gl
                    standings[local]['GA'] += gv
                    standings[visitante]['GF'] += gv
                    standings[visitante]['GA'] += gl
                    if gl > gv:
                        standings[local]['W'] += 1
                        standings[local]['Pts'] += 2
                        standings[visitante]['L'] += 1
                    elif gl < gv:
                        standings[local]['L'] += 1
                        standings[visitante]['W'] += 1
                        standings[visitante]['Pts'] += 2
                    else:
                        standings[local]['D'] += 1
                        standings[local]['Pts'] += 1
                        standings[visitante]['D'] += 1
                        standings[visitante]['Pts'] += 1
                for team in standings:
                    standings[team]['GD'] = standings[team]['GF'] - standings[team]['GA']
                standings_data = [
                    {'Zona': zona, 'Team': team, 'Logo': logo_dict.get(get_base_team_name(team), ""), **stats}
                    for team, stats in standings.items()
                ]
                df_standings = pd.DataFrame(standings_data)
                df_standings = df_standings.sort_values(by=['Pts', 'GD', 'Team'], ascending=[False, False, True])
                all_standings.append(df_standings)
        return all_standings

    all_standings = calculate_standings_a3(regular_season, category="a3")
    for df_standings in all_standings:
        zona = df_standings.get('Zona', 'General').iloc[0]
        with st.expander(zona, expanded=True):
            try:
                with st.spinner(f"Cargando tabla para {zona}"):
                    if is_mobile:
                        # Simplify for mobile: smaller images, no sorting
                        st.dataframe(
                            df_standings,
                            use_container_width=True,
                            height=300,
                            column_config={
                                "Team": st.column_config.TextColumn("Equipo"),
                                "Logo": st.column_config.ImageColumn(" ", width=30),
                                "MP": st.column_config.NumberColumn("Partidos Jugados", width=80),
                                "W": st.column_config.NumberColumn("Ganados", width=60),
                                "D": st.column_config.NumberColumn("Empates", width=60),
                                "L": st.column_config.NumberColumn("Perdidos", width=60),
                                "Pts": st.column_config.NumberColumn("Puntos", width=60),
                                "GF": st.column_config.NumberColumn("Goles a Favor", width=80),
                                "GA": st.column_config.NumberColumn("Goles en Contra", width=80),
                                "GD": st.column_config.NumberColumn("Goles Diferencia", width=80)
                            },
                            hide_index=True,
                            column_order=['Logo', 'Team', 'Pts', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD'],
                            key=f"standings_{zona.replace(' ', '_')}"
                        )
                    else:
                        st.dataframe(
                            df_standings,
                            use_container_width=True,
                            column_config={
                                "Team": st.column_config.TextColumn("Equipo"),
                                "Logo": st.column_config.ImageColumn(" ", width=40),
                                "MP": st.column_config.NumberColumn("Partidos Jugados", width=80),
                                "W": st.column_config.NumberColumn("Ganados", width=60),
                                "D": st.column_config.NumberColumn("Empates", width=60),
                                "L": st.column_config.NumberColumn("Perdidos", width=60),
                                "Pts": st.column_config.NumberColumn("Puntos", width=60),
                                "GF": st.column_config.NumberColumn("Goles a Favor", width=80),
                                "GA": st.column_config.NumberColumn("Goles en Contra", width=80),
                                "GD": st.column_config.NumberColumn("Goles Diferencia", width=80)
                            },
                            hide_index=True,
                            column_order=['Logo', 'Team', 'Pts', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'GD'],
                            key=f"standings_{zona.replace(' ', '_')}"
                        )
                    st.markdown("---")
            except Exception as e:
                logger.error(f"Error rendering standings table for {zona}: {str(e)}")
                st.error(f"Error al mostrar la tabla para {zona}. Por favor, intenta de nuevo.")

# Tab 3: Estadisticas (Statistics)
with tab3:
    try:
        df_stats = load_csv_a3(f'{root_path}/data/a3-statistics.csv', category="a3")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        logger.warning(f"Error loading a3-statistics.csv: {str(e)}")
        st.header("Tabla de goleadores aún no disponible.")
        st.stop()

    @st.cache_data
    def process_statistics_a3(_df, category="a3"):
        logger.info("Processing statistics for a3")
        _df.columns = _df.columns.str.strip()
        if 'Unnamed: 0' in _df.columns:
            _df = _df.drop(columns=['Unnamed: 0'])
        _df = _df.rename(columns={'Goles': 'Goals', 'Jugador': 'Player', 'Club': 'Club'})
        _df = _df.sort_values(by=['Goals', 'Player'], ascending=[False, True])
        _df = _df.reset_index(drop=True)
        _df.index = _df.index + 1
        return _df

    df_stats = process_statistics_a3(df_stats, category="a3")
    st.header("Goleadores")
    try:
        with st.spinner("Cargando tabla de goleadores"):
            if is_mobile:
                # Limit rows and simplify for mobile
                st.dataframe(
                    df_stats.head(10),  # Show top 10 scorers
                    column_config={
                        "Goals": st.column_config.NumberColumn("Goles", help="Numero de goles convertidos"),
                        "Player": st.column_config.TextColumn("Jugador", help="Nombre Jugador"),
                        "Club": st.column_config.TextColumn("Club", help="Club Jugador")
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=300,
                    key="statistics_table"
                )
            else:
                st.dataframe(
                    df_stats,
                    column_config={
                        "Goals": st.column_config.NumberColumn("Goles", help="Numero de goles convertidos"),
                        "Player": st.column_config.TextColumn("Jugador", help="Nombre Jugador"),
                        "Club": st.column_config.TextColumn("Club", help="Club Jugador")
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="statistics_table"
                )
    except Exception as e:
        logger.error(f"Error rendering statistics table: {str(e)}")
        st.error("Error al mostrar la tabla de goleadores. Por favor, intenta de nuevo.")
    st.markdown("---")