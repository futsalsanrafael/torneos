import base64
import logging
import streamlit as st
import json
import pandas as pd
import os
import mimetypes

# Set page configuration
st.set_page_config(
    page_title="Futsal De Toque - C20A1",
    page_icon=":material/sports_soccer:",
    layout="wide"
)
st.markdown("# C20 A1")
st.sidebar.markdown("# Futsal De Toque")

# Define tabs
tab1, tab2, tab3 = st.tabs(["Fixture", "Tabla", "Estadisticas"])

# Root path
root_path = os.getcwd()

# Cache file loading with category-specific key
@st.cache_data
def load_json_c20a1(file_path, category="c20a1"):
    with open(file_path, 'r') as file:
        return json.load(file)

@st.cache_data
def load_csv_c20a1(file_path, category="c20a1"):
    return pd.read_csv(file_path)

# Cache image to Base64 conversion
@st.cache_data
def image_to_base64(image_path):
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            return ""
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded}"
    except (FileNotFoundError, IOError):
        return ""

# Cache logo dictionary creation
@st.cache_data
def build_logo_dict(_logos_data, root_path):
    logo_dict = {}
    missing_logos = []
    for item in _logos_data:
        team = item['equipo']
        logo_path = f"{root_path}{item['logo']}"
        base64_url = image_to_base64(logo_path)
        if base64_url:
            logo_dict[team] = base64_url
        else:
            missing_logos.append(f"{team}: {logo_path}")
    return logo_dict, missing_logos

# Function to get base team name
def get_base_team_name(team):
    for base_name in logo_dict.keys():
        if team.startswith(base_name):
            return base_name
    return team

# Load logos.json
try:
    logos_data = load_json_c20a1(f'{root_path}/data/logos.json', category="c20a1")
except (json.JSONDecodeError, FileNotFoundError) as e:
    st.error(f"Error loading logos.json: {str(e)}")
    st.stop()

logo_dict, missing_logos = build_logo_dict(logos_data, root_path)
if missing_logos:
    st.warning(f"Missing or invalid logo files:\n" + "\n".join(missing_logos))

# Tab 1: Fixture
with tab1:
    try:
        data = load_json_c20a1(f'{root_path}/data/c20a1.json', category="c20a1")
        if not data:
            st.header("El fixture será cargado en los próximos días")
            st.stop()
    except (json.JSONDecodeError, FileNotFoundError) as e:
        st.error(f"Error loading c20a1.json: {str(e)}")
        st.stop()

    @st.cache_data
    def process_fixtures_c20a1(_data, category="c20a1"):
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

    df = process_fixtures_c20a1(data, category="c20a1")
    if df['Fecha'].isna().any():
        st.warning(f"Rows with invalid dates: {df[df['Fecha'].isna()][['Fecha Numero', 'Local', 'Visitante']].to_dict('records')}")

    columns = ['Fecha', 'Local_Logo', 'Local', 'GL', 'Visitante_Logo', 'Visitante', 'GV', 'Cancha']
    for fecha_num, group in df.groupby('Fecha Numero', sort=False):
        st.header(fecha_num)
        display_group = group[columns].copy()
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
            hide_index=True
        )

# Tab 2: Tabla (Standings)
with tab2:
    try:
        data = load_json_c20a1(f'{root_path}/data/c20a1.json', category="c20a1")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        st.error(f"Error loading c20a1.json: {str(e)}")
        st.stop()

    regular_season = [f for f in data if f['Fecha'].startswith('Fecha ')]
    @st.cache_data
    def calculate_standings_c20a1(_regular_season, category="c20a1"):
        all_matches = []
        for fecha in _regular_season:
            for match in fecha['Data']:
                if match['GL'] != "" and match['GV'] != "" and match['Visitante'] != "":
                    match['Fecha Numero'] = fecha['Fecha']
                    all_matches.append(match)
        df_matches = pd.DataFrame(all_matches)
        if df_matches.empty:
            all_teams_data = [match for fecha in data for match in fecha['Data'] if match['Local'] != "" and match['Visitante'] != ""]
            teams = pd.unique(pd.DataFrame(all_teams_data)[['Local', 'Visitante']].values.ravel('K'))
            standings = {team: {'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'Pts': 0, 'GF': 0, 'GA': 0, 'GD': 0} for team in teams}
        else:
            df_matches['GL'] = pd.to_numeric(df_matches['GL'], errors='coerce').fillna(0).astype(int)
            df_matches['GV'] = pd.to_numeric(df_matches['GV'], errors='coerce').fillna(0).astype(int)
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
        return standings

    standings = calculate_standings_c20a1(regular_season, category="c20a1")
    standings_data = [
        {'Team': team, 'Logo': logo_dict.get(get_base_team_name(team), ""), **stats}
        for team, stats in standings.items()
    ]
    df_standings = pd.DataFrame(standings_data)
    df_standings = df_standings.sort_values(by=['Pts', 'GD', 'Team'], ascending=[False, False, True])
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
            "GD": st.column_config.NumberColumn("Goles Diferencia", width=80)
        },
        hide_index=True,
        column_order=['Logo', 'Team', 'Pts', 'MP', 'W', 'D', 'L', 'GD']
    )

# Tab 3: Estadisticas (Statistics)
with tab3:
    try:
        df_stats = load_csv_c20a1(f'{root_path}/data/c20a1-statistics.csv', category="c20a1")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        logging.warning(f"Error loading c20a1-statistics.csv: {str(e)}")
        st.header("Tabla de goleadores aún no disponible.")
        st.stop()

    @st.cache_data
    def process_statistics_c20a1(_df, category="c20a1"):
        _df.columns = _df.columns.str.strip()
        if 'Unnamed: 0' in _df.columns:
            _df = _df.drop(columns=['Unnamed: 0'])
        _df = _df.rename(columns={'Goles': 'Goals', 'Jugador': 'Player', 'Club': 'Club'})
        _df = _df.sort_values(by=['Goals', 'Player'], ascending=[False, True])
        _df = _df.reset_index(drop=True)
        _df.index = _df.index + 1
        return _df

    df_stats = process_statistics_c20a1(df_stats, category="c20a1")
    st.header("Goleadores")
    st.dataframe(
        df_stats,
        column_config={
            "Goals": st.column_config.NumberColumn("Goles", help="Numero de goles convertidos"),
            "Player": st.column_config.TextColumn("Jugador", help="Nombre Jugador"),
            "Club": st.column_config.TextColumn("Club", help="Club Jugador")
        },
        hide_index=True,
        use_container_width=True
    )
    st.markdown("---")