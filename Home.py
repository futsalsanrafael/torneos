import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime
#
# Main page content
st.set_page_config(page_title="AFUSAR")
st.sidebar.title("AFUSSAR")

st.markdown("# PARTIDOS DE HOY")
# st.sidebar.markdown("# HOY")

# Define root path and JSON file paths
root_path = f"{os.getcwd()}/data"
json_files = {
    "elite.json": "Elite",
    "a2z1.json": "A2 ZONA 1",
    "a1.json": "A 1"
}


# Function to load and filter matches for today
def get_todays_matches():
    all_matches = []
    current_date = datetime.now().strftime('%d/%m/%Y')  # e.g., "18/07/2025"

    for file_name, category in json_files.items():
        file_path = f"{root_path}/{file_name}"
        try:
            with open(file_path, 'r') as jfile:
                data = json.load(jfile)
            for table in data:
                for match in table['Data']:
                    if match['Fecha'].startswith(current_date):
                        match['Category'] = category
                        all_matches.append(match)
        except FileNotFoundError:
            st.error(f"Error: {file_name} not found in the data directory.")
            continue
        except json.JSONDecodeError:
            st.error(f"Error: Invalid JSON format in {file_name}.")
            continue

    # Create DataFrame
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
        # Convert Date & Time to datetime
        df['Date & Time'] = pd.to_datetime(df['Date & Time'], format='%d/%m/%Y %H:%M', errors='coerce')
        # Sort by Date & Time
        df = df.sort_values(by='Date & Time')
        # Select relevant columns
        return df[['Date & Time', 'Home Team', 'Away Team', 'Venue', 'Category']]
    return pd.DataFrame()  # Return empty DataFrame if no matches


# Load and display today's matches
df_todays_matches = get_todays_matches()

if not df_todays_matches.empty:
    st.dataframe(
        df_todays_matches,
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
            ),
            "Category": st.column_config.TextColumn(
                "Categoria",
                help="League category"
            )
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.write("No hay partidos programados para hoy.")

st.markdown("---")