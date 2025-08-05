import base64
import logging
import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime
import mimetypes
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Futsal De Toque",
    page_icon=":material/sports_soccer:",
    layout="wide"
)

st.sidebar.title("Futsal De Toque")
st.markdown("# PARTIDOS DE HOY")

# Detect mobile device
is_mobile = st.query_params.get("mobile", ["false"])[0].lower() == "true" or (
    "Mobi" in st._get_user_agent() if hasattr(st, "_get_user_agent") else False
)

# Define root path and JSON file paths
root_path = f"{os.getcwd()}/"
json_files = {
    "elite.json": "Elite",
    "a1.json": "A1",
    "a2.json": "A2",
    "a3.json": "A3",
    "senior.json": "Senior",
    "veteranos.json": "Veteranos",
    "femenino.json": "Femenino",
    "c13.json": "C13",
    "c15.json": "C15",
    "c17.json": "C17",
    "c20a1.json": "C20 A1",
    "c20a2.json": "C20 A2",
    "copa2025.json": "COPA 2025"
}

# Cache file loading
@st.cache_data
def load_json(file_path, _category="All"):
    logger.info(f"Loading JSON: {file_path}")
    start = time.time()
    with open(file_path, 'r') as file:
        data = json.load(file)
    logger.info(f"Loaded JSON in {time.time() - start:.2f} seconds")
    return data

# Cache image to Base64 conversion
@st.cache_data
def image_to_base64(image_path, _category="All"):
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            return ""
        start = time.time()
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode('utf-8')
        logger.info(f"Encoded image {image_path} in {time.time() - start:.2f} seconds")
        return f"data:{mime_type};base64,{encoded}"
    except (FileNotFoundError, IOError):
        logger.warning(f"Failed to load image: {image_path}")
        return ""

# Cache logo dictionary creation
@st.cache_data
def build_logo_dict(_logos_data, root_path, _category="All"):
    logo_dict = {}
    missing_logos = []
    start = time.time()
    for item in _logos_data:
        team = item['equipo']
        logo_path = f"{root_path}{item['logo']}"
        base64_url = image_to_base64(logo_path, _category="All")
        if base64_url:
            logo_dict[team] = base64_url
        else:
            missing_logos.append(f"{team}: {logo_path}")
    logger.info(f"Built logo dict with {len(logo_dict)} logos in {time.time() - start:.2f} seconds")
    return logo_dict, missing_logos

# Function to get base team name
def get_base_team_name(team):
    for base_name in logo_dict.keys():
        if team.startswith(base_name):
            return base_name
    return team

# Load logos.json
try:
    with st.spinner("Cargando logos"):
        logos_data = load_json(f'{root_path}/data/logos.json', _category="All")
except (json.JSONDecodeError, FileNotFoundError) as e:
    logger.error(f"Error loading logos.json: {str(e)}")
    st.error(f"Error loading logos.json: {str(e)}")
    st.stop()

logo_dict, missing_logos = build_logo_dict(logos_data, root_path, _category="All")
if missing_logos:
    st.warning(f"Missing or invalid logo files:\n" + "\n".join(missing_logos))

# Cache today's matches
@st.cache_data
def get_todays_matches(_json_files, current_date_str, _category="All"):
    logger.info(f"Fetching today's matches for {current_date_str}")
    start = time.time()
    all_matches = []
    for file_name, category in _json_files.items():
        file_path = f"{root_path}/data/{file_name}"
        try:
            data = load_json(file_path, _category=category)
            for table in data:
                for match in table['Data']:
                    if match['Fecha'].startswith(current_date_str):
                        match['Category'] = category
                        match['Local_Logo'] = logo_dict.get(get_base_team_name(match['Local']), "")
                        match['Visitante_Logo'] = logo_dict.get(get_base_team_name(match['Visitante']), "")
                        all_matches.append(match)
        except FileNotFoundError:
            logger.warning(f"Error: {file_name} not found in the data directory.")
            continue
        except json.JSONDecodeError:
            logger.warning(f"Error: Invalid JSON format in {file_name}.")
            continue

    if all_matches:
        df = pd.DataFrame(all_matches)
        df = df.rename(columns={
            'Fecha': 'Date & Time',
            'Local': 'Home Team',
            'GL': 'Home Goals',
            'Visitante': 'Away Team',
            'GV': 'Away Goals',
            'Cancha': 'Venue',
            'Arbitro 1': 'Referee 1',
            'Arbitro 2': 'Referee 2'
        })
        df['Date & Time'] = pd.to_datetime(df['Date & Time'], format='%d/%m/%Y %H:%M', errors='coerce')
        df = df.sort_values(by='Date & Time')
        logger.info(f"Fetched and processed today's matches in {time.time() - start:.2f} seconds")
        return df[['Date & Time', 'Home Team', 'Home Goals', 'Away Team', 'Away Goals', 'Venue', 'Category', 'Local_Logo', 'Visitante_Logo']]
    logger.info(f"No matches found for {current_date_str}")
    return pd.DataFrame()

# Load and display today's matches
current_date = datetime.now().strftime('%d/%m/%Y')
with st.spinner("Cargando partidos de hoy"):
    df_todays_matches = get_todays_matches(json_files, current_date, _category="All")

if not df_todays_matches.empty:
    # Group by Category
    with st.container():
        for category, group in df_todays_matches.groupby('Category', sort=False):
            if f"matches_rendered_{category}" not in st.session_state:
                st.subheader(category)
                # Limit to 10 matches per category to reduce rendering overhead
                display_group = group.head(10)
                try:
                    with st.spinner(f"Cargando tabla para {category}"):
                        if len(display_group) < 5 and is_mobile:
                            st.table(display_group[['Date & Time', 'Home Team', 'Away Team', 'Venue']])
                        else:
                            if is_mobile:
                                st.dataframe(
                                    display_group,
                                    column_config={
                                        "Date & Time": st.column_config.DatetimeColumn(
                                            "Fecha - Hora",
                                            format="DD/MM/YYYY HH:mm",
                                            help="Match date and time"
                                        ),
                                        "Home Team": st.column_config.TextColumn(
                                            "Local",
                                            help="Home team name"
                                        ),
                                        "Away Team": st.column_config.TextColumn(
                                            "Visitante",
                                            help="Away team name"
                                        ),
                                        "Venue": st.column_config.TextColumn(
                                            "Cancha",
                                            help="Match venue"
                                        )
                                    },
                                    hide_index=True,
                                    use_container_width=True,
                                    column_order=['Date & Time', 'Home Team', 'Away Team', 'Venue'],
                                    key=f"matches_{category.replace(' ', '_')}"
                                )
                            else:
                                st.dataframe(
                                    display_group,
                                    column_config={
                                        "Date & Time": st.column_config.DatetimeColumn(
                                            "Fecha - Hora",
                                            format="DD/MM/YYYY HH:mm",
                                            help="Match date and time"
                                        ),
                                        "Local_Logo": st.column_config.ImageColumn(
                                            " ",
                                            width=40,
                                            help="Home team logo"
                                        ),
                                        "Home Team": st.column_config.TextColumn(
                                            "Local",
                                            help="Home team name"
                                        ),
                                        "Visitante_Logo": st.column_config.ImageColumn(
                                            " ",
                                            width=40,
                                            help="Away team logo"
                                        ),
                                        "Away Team": st.column_config.TextColumn(
                                            "Visitante",
                                            help="Away team name"
                                        ),
                                        "Venue": st.column_config.TextColumn(
                                            "Cancha",
                                            help="Match venue"
                                        )
                                    },
                                    hide_index=True,
                                    use_container_width=True,
                                    column_order=['Date & Time', 'Local_Logo', 'Home Team', 'Visitante_Logo', 'Away Team', 'Venue'],
                                    key=f"matches_{category.replace(' ', '_')}"
                                )
                        st.session_state[f"matches_rendered_{category}"] = True
                        if len(group) > 10:
                            st.write(f"Showing first 10 matches for {category}. Total matches: {len(group)}")
                        st.markdown("---")
                except Exception as e:
                    logger.error(f"Error rendering matches table for {category}: {str(e)}")
                    st.error(f"Error al mostrar la tabla para {category}. Por favor, intenta de nuevo.")
else:
    st.write("No hay partidos programados para hoy.")