import base64
import logging

import streamlit as st
import json
import pandas as pd
import os
import mimetypes

# Veteranos page content
st.set_page_config(
    page_title="Futsal San Rafael",
    page_icon=":material/sports_soccer:",
    layout="wide"
)
st.markdown(body="# Veteranos", width="content")
st.sidebar.markdown("# Futsal San Rafael")

tab1, tab2, tab3 = st.tabs(["Fixture", "Tabla", "Estadisticas"])

root_path = f"{os.getcwd()}"


# Function to convert local image to Base64 data URL
def image_to_base64(image_path):
    try:
        # Guess the MIME type based on file extension
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            return ""
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded}"
    except (FileNotFoundError, IOError):
        return ""


# Load logos.json with error handling
try:
    with open(f'{root_path}/data/logos.json', 'r') as jfile_logos:
        logos_data = json.load(jfile_logos)
except json.JSONDecodeError as e:
    st.error(f"Error parsing logos.json: {str(e)}")
    st.stop()
except FileNotFoundError:
    st.error("Error: logos.json not found in the data directory.")
    st.stop()

# Create a dictionary to map team base names to Base64 data URLs
logo_dict = {}
missing_logos = []
for item in logos_data:
    team = item['equipo']
    logo_path = f"{root_path}{item['logo']}"
    base64_url = image_to_base64(logo_path)
    if base64_url:
        logo_dict[team] = base64_url
    else:
        missing_logos.append(f"{team}: {logo_path}")
if missing_logos:
    st.warning(f"Missing or invalid logo files:\n" + "\n".join(missing_logos))

# Function to get base team name (e.g., "Tenis A" -> "Tenis")
def get_base_team_name(team):
    for base_name in logo_dict.keys():
        if team.startswith(base_name):
            return base_name
    return team  # Fallback to original name if no match


with tab1:
    try:
        with open(f'{root_path}/data/veteranos.json', 'r') as jfile:
            data = json.load(jfile)
            if not data:  # Check if data is empty
                st.header("El fixture será cargado en los próximos días")
                st.stop()  # Stop further execution of this tab if data is empty
    except json.JSONDecodeError as e:
        st.error(f"Error parsing veteranos.json: {str(e)}")
        st.stop()
    except FileNotFoundError:
        st.error("Error: veteranos.json not found in the data directory.")
        st.stop()

    # Flatten the nested JSON structure
    all_matches = []
    for fecha in data:
        for match in fecha['Data']:
            match['Fecha Numero'] = fecha['Fecha']
            all_matches.append(match)

    # Create DataFrame
    df = pd.DataFrame(all_matches)

    # Debug: Check for invalid date values
    invalid_dates = df[df['Fecha'].str.strip() == '']
    if not invalid_dates.empty:
        st.warning(f"Found {len(invalid_dates)} rows with empty or invalid dates: {invalid_dates['Fecha'].tolist()}")


    # Convert 'Fecha' to datetime with error handling
    def parse_date(date_str):
        try:
            return pd.to_datetime(date_str, format='%d/%m/%Y %H:%M')
        except (ValueError, TypeError) as e:
            st.error(f"Failed to parse date: {date_str}. Error: {str(e)}")
            return pd.NaT


    df['Fecha'] = df['Fecha'].apply(parse_date)

    # Check for rows where datetime conversion failed
    if df['Fecha'].isna().any():
        st.warning(
            f"Rows with invalid dates: {df[df['Fecha'].isna()][['Fecha Numero', 'Local', 'Visitante']].to_dict('records')}")

    # Add logo paths to the DataFrame
    df['Local_Logo'] = df['Local'].apply(lambda x: logo_dict.get(get_base_team_name(x), ""))
    df['Visitante_Logo'] = df['Visitante'].apply(lambda x: logo_dict.get(get_base_team_name(x), ""))

    # Select relevant columns for display
    columns = ['Fecha', 'Local_Logo', 'Local', 'GL', 'Visitante_Logo', 'Visitante', 'GV', 'Cancha', 'Arbitro 1',
               'Arbitro 2']

    # Group by Fecha Numero and display tables
    for fecha_num, group in df.groupby('Fecha Numero', sort=False):
        st.header(fecha_num)
        # Create a copy to avoid modifying the original DataFrame
        display_group = group[columns].copy()
        # Display the table with datetime column and logos
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
                "Cancha": st.column_config.TextColumn("Cancha"),
                "Arbitro 1": st.column_config.TextColumn("Referee 1"),
                "Arbitro 2": st.column_config.TextColumn("Referee 2")
            },
            hide_index=True
        )

with tab2:
    # Filter matches for regular season (Fecha 1 to Fecha 9)
    regular_season = [f for f in data if f['Fecha'].startswith('Fecha ')]
    all_matches = []
    for fecha in regular_season:
        for match in fecha['Data']:
            # Only include matches where goals are not empty AND 'Visitante' is not empty
            if match['GL'] != "" and match['GV'] != "" and match['Visitante'] != "":
                match['Fecha Numero'] = fecha['Fecha']
                all_matches.append(match)

    df_matches = pd.DataFrame(all_matches)

    # If no matches have been played yet, initialize an empty DataFrame
    if df_matches.empty:
        logging.warning("No played matches found to calculate standings.")
        # Get all unique teams from the *entire* data structure, including scheduled matches
        # and ensure 'Visitante' is not empty for team extraction
        all_teams_data = [match for fecha in data for match in fecha['Data'] if match['Local'] != "" and match['Visitante'] != ""]
        teams = pd.unique(pd.DataFrame(all_teams_data)[['Local', 'Visitante']].values.ravel('K'))
        standings = {team: {'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'Pts': 0, 'GF': 0, 'GA': 0, 'GD': 0} for team in teams}
    else:
        # Convert goals to numeric, handling empty strings (though filtered above, good for robustness)
        df_matches['GL'] = pd.to_numeric(df_matches['GL'], errors='coerce').fillna(0).astype(int)
        df_matches['GV'] = pd.to_numeric(df_matches['GV'], errors='coerce').fillna(0).astype(int)

        # Get unique teams from only the *played* matches
        teams = pd.unique(df_matches[['Local', 'Visitante']].values.ravel('K'))

        # Initialize standings dictionary
        standings = {team: {'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'Pts': 0, 'GF': 0, 'GA': 0, 'GD': 0} for team in teams}

        # Calculate standings for played matches
        for _, match in df_matches.iterrows():
            local = match['Local']
            visitante = match['Visitante']
            gl = match['GL']
            gv = match['GV']

            # Update matches played
            standings[local]['MP'] += 1
            standings[visitante]['MP'] += 1

            # Update goals for and against
            standings[local]['GF'] += gl
            standings[local]['GA'] += gv
            standings[visitante]['GF'] += gv
            standings[visitante]['GA'] += gl

            # Determine match outcome
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

        # Calculate goal difference
        for team in standings:
            standings[team]['GD'] = standings[team]['GF'] - standings[team]['GA']

    # Create standings DataFrame
    standings_data = []
    for team, stats in standings.items():
        standings_data.append({
            'Team': team,
            'Logo': logo_dict.get(get_base_team_name(team), ""),
            'MP': stats['MP'],
            'W': stats['W'],
            'D': stats['D'],
            'L': stats['L'],
            'Pts': stats['Pts'],
            'GD': stats['GD']
        })

    df_standings = pd.DataFrame(standings_data)

    # Sort by points (descending), then goal difference (descending), then team name (alphabetically)
    df_standings = df_standings.sort_values(by=['Pts', 'GD', 'Team'], ascending=[False, False, True])

    # Display the standings table
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

with tab3:
    # Load veteranos-statistics.csv
    try:
        csv_path = f'{root_path}/data/veteranos-statistics.csv'
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        logging.warning("Error: veteranos-statistics.csv not found in the data directory.")
        st.header("Tabla de goleadores aún no disponible.")
        st.stop()
    except pd.errors.EmptyDataError:
        st.error("Error: veteranos-statistics.csv is empty.")
        st.stop()
    except pd.errors.ParserError:
        st.error("Error: Invalid CSV format in veteranos-statistics.csv.")
        st.stop()

    # Clean and process the data
    df.columns = df.columns.str.strip()
    # Drop the column with empty header
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    df = df.rename(columns={
        'Goles': 'Goals',
        'Jugador': 'Player',
        'Club': 'Club'
    })

    # Sort by Goals in descending order, then by Player name for ties
    df = df.sort_values(by=['Goals', 'Player'], ascending=[False, True])

    # Reset index to reflect rank starting from 1
    df = df.reset_index(drop=True)
    df.index = df.index + 1

    # Display the table
    st.header("Goleadores")
    st.dataframe(
        df,
        column_config={
            "Goals": st.column_config.NumberColumn(
                "Goles",
                help="Numero de goles convertidos"
            ),
            "Player": st.column_config.TextColumn(
                "Jugador",
                help="Nombre Jugador"
            ),
            "Club": st.column_config.TextColumn(
                "Club",
                help="Club Jugador"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    st.markdown("---")