import base64
import logging
import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime
import mimetypes

# Set page configuration
st.set_page_config(
    page_title="Futsal De Toque",
    page_icon=":material/sports_soccer:",
    layout="wide"
)

st.sidebar.title("Futsal De Toque")
st.markdown("# PARTIDOS DE HOY")

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
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

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
    logos_data = load_json(f'{root_path}/data/logos.json')
except (json.JSONDecodeError, FileNotFoundError) as e:
    st.error(f"Error loading logos.json: {str(e)}")
    st.stop()

logo_dict, missing_logos = build_logo_dict(logos_data, root_path)
if missing_logos:
    st.warning(f"Missing or invalid logo files:\n" + "\n".join(missing_logos))

# Cache today's matches
@st.cache_data
def get_todays_matches(_json_files, current_date_str):
    all_matches = []
    for file_name, category in _json_files.items():
        file_path = f"{root_path}/data/{file_name}"
        try:
            data = load_json(file_path)
            for table in data:
                for match in table['Data']:
                    if match['Fecha'].startswith(current_date_str):
                        match['Category'] = category
                        match['Local_Logo'] = logo_dict.get(get_base_team_name(match['Local']), "")
                        match['Visitante_Logo'] = logo_dict.get(get_base_team_name(match['Visitante']), "")
                        all_matches.append(match)
        except FileNotFoundError:
            logging.warning(f"Error: {file_name} not found in the data directory.")
            continue
        except json.JSONDecodeError:
            logging.warning(f"Error: Invalid JSON format in {file_name}.")
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
        return df[['Date & Time', 'Home Team', 'Home Goals', 'Away Team', 'Away Goals', 'Venue', 'Category', 'Local_Logo', 'Visitante_Logo']]
    return pd.DataFrame()

# Load and display today's matches
current_date = datetime.now().strftime('%d/%m/%Y')
df_todays_matches = get_todays_matches(json_files, current_date)

if not df_todays_matches.empty:
    # Group by Category
    for category, group in df_todays_matches.groupby('Category', sort=False):
        st.subheader(category)
        # Limit to 10 matches per category to reduce rendering overhead
        display_group = group.head(10)
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
            column_order=['Date & Time', 'Local_Logo', 'Home Team', 'Visitante_Logo', 'Away Team', 'Venue']
        )
        if len(group) > 10:
            st.write(f"Showing first 10 matches for {category}. Total matches: {len(group)}")
else:
    st.write("No hay partidos programados para hoy.")