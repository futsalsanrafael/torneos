import base64

import streamlit as st
import json
import pandas as pd
import os
# Elite page content

# Inject custom CSS to style tabs
st.markdown(body="# ELITE", width="content")
st.sidebar.markdown("# AFUSSAR")

tab1, tab2, tab3 = st.tabs(["Fixture", "Posiciones", "Estadisticas"])

root_path = f"{os.getcwd()}"

with tab1:
    jfile = open(f'{root_path}/data/elite.json', 'r')
    data = json.load(jfile)

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
        st.warning(f"Rows with invalid dates: {df[df['Fecha'].isna()][['Fecha Numero', 'Local', 'Visitante']].to_dict('records')}")

    # Sort by Fecha within each Fecha Numero, handling NaT values
    df = df.sort_values(by=['Fecha'], na_position='last')

    # Select relevant columns for display
    columns = ['Fecha', 'Local', 'GL', 'Visitante', 'GV', 'Cancha', 'Arbitro 1', 'Arbitro 2']

    # Group by Fecha Numero and display tables
    for fecha_num, group in df.groupby('Fecha Numero'):
        st.header(fecha_num)
        # Create a copy to avoid modifying the original DataFrame
        display_group = group[columns].copy()
        # Display the table with datetime column intact
        st.dataframe(
            display_group,
            use_container_width=True,
            column_config={
                "Fecha": st.column_config.DatetimeColumn("Dia/Hora", format="DD/MM/YYYY HH:mm"),
                "Local": st.column_config.TextColumn("Local"),
                "GL": st.column_config.TextColumn("Goles", width=40),
                "Visitante": st.column_config.TextColumn("Visitante"),
                "GV": st.column_config.TextColumn("Goles", width=40),
                "Cancha": st.column_config.TextColumn("Cancha"),
                "Arbitro 1": st.column_config.TextColumn("Referee 1"),
                "Arbitro 2": st.column_config.TextColumn("Referee 2")
            },
            hide_index=True
        )
        st.markdown("---")

with tab2:
    # Load elite-pos.json
    try:
        with open(f'{root_path}/data/elite-pos.json', 'r') as jfile:
            data = json.load(jfile)
    except FileNotFoundError:
        st.error("Error: elite-pos.json not found in the data directory.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error: Invalid JSON format in elite-pos.json.")
        st.stop()

    # Convert JSON data to DataFrame
    df = pd.DataFrame(data)

    # Sort by puntos in descending order
    df = df.sort_values(by='puntos', ascending=False)

    # Rename columns for better readability
    df = df.rename(columns={
        'equipo': 'Equipo',
        'puntos': 'Puntos',
        'pj': 'PJ',
        'pg': 'G',
        'pe': 'E',
        'pp': 'P',
        'gf': 'GF',
        'gc': 'GC',
        'dg': 'Dif'
    })

    # Function to encode image to base64 for local files
    def get_image_base64(image_path):
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode()
        except FileNotFoundError:
            return None

    # Combine logo and team name into a single column with HTML
    def format_team_with_logo(row):
        logo_path = f"{root_path}{row['logo']}"
        image_base64 = get_image_base64(logo_path)
        if image_base64:
            return f'<div style="display: flex; align-items: center;"><img src="data:image/png;base64,{image_base64}" width=20" height="20" style="margin-right: 5px;">{row["Equipo"]}</div>'
        return row["Equipo"]

    df['Equipo'] = df.apply(format_team_with_logo, axis=1)

    # Convert DataFrame to HTML table
    html_table = df.to_html(escape=False, index=False, columns=['Equipo', 'Puntos', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'Dif'])
    st.markdown(html_table, unsafe_allow_html=True)

    st.markdown("---")

with tab3:
    # Load elite-statistics.csv
    try:
        csv_path = f'{root_path}/data/elite-statistics.csv'
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error("Error: elite-statistics.csv not found in the data directory.")
        st.stop()
    except pd.errors.EmptyDataError:
        st.error("Error: elite-statistics.csv is empty.")
        st.stop()
    except pd.errors.ParserError:
        st.error("Error: Invalid CSV format in elite-statistics.csv.")
        st.stop()

    # Clean and process the data
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespace from column names
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