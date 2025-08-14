import folium
import streamlit as st
import pandas as pd
import logging
from streamlit_folium import st_folium
from streamlit.components.v1 import html

# Set page configuration
st.set_page_config(
    page_title="Futsal De Toque",
    page_icon="images/favicon.jpg",
    layout="wide"
)

st.logo("images/round.png")
st.markdown("# Estadios")
st.sidebar.markdown("# Futsal De Toque")

# Define stadium data
stadiums = [
    {
        "name": "Sportivo Pedal Club",
        "lat": -34.628520,
        "lon": -68.336973,
        "google_maps": "https://maps.google.com/?q=-34.628520,-68.336973"
    },
    {
        "name": "Tenis Club",
        "lat": -34.62106,
        "lon": -68.37281,
        "google_maps": "https://maps.google.com/?q=-34.62106,-68.37281"
    },
    {
        "name": "CIU UTN",
        "lat": -34.603497,
        "lon": -68.327794,
        "google_maps": "https://maps.google.com/?q=-34.603497,-68.327794"
    },
    {
        "name": "Banco Mendoza",
        "lat": -34.602058,
        "lon": -68.348941,
        "google_maps": "https://maps.google.com/?q=-34.602058,-68.348941"
    },
    {
        "name": "Polideportivo Nro2",
        "lat": -34.634303,
        "lon": -68.324028,
        "google_maps": "https://maps.google.com/?q=-34.634303,-68.324028"
    },
    {
        "name": "Club Pescadores",
        "lat": -34.602605,
        "lon": -68.354466,
        "google_maps": "https://maps.google.com/?q=-34.602605,-68.354466"
    },
    {
        "name": "Huracan",
        "lat": -34.628061,
        "lon": -68.294438,
        "google_maps": "https://maps.google.com/?q=-34.628061,-68.294438"
    },
    {
        "name": "CIC Sosnneado Futsal",
        "lat": -34.636386,
        "lon": -68.374009,
        "google_maps": "https://maps.google.com/?q=-34.636386,-68.374009"
    },
    {
        "name": "CDA",
        "lat": -34.608495,
        "lon": -68.341752,
        "google_maps": "https://maps.google.com/?q=-34.608495,-68.341752"
    },
]

# Cache map creation
@st.cache_data
def create_all_stadiums_map(_stadiums):
    lats = [s["lat"] for s in _stadiums]
    lons = [s["lon"] for s in _stadiums]
    center = [(min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2]
    m = folium.Map(location=center, zoom_start=13, tiles="CartoDB Positron")
    for stadium in _stadiums:
        folium.Marker(
            [stadium["lat"], stadium["lon"]],
            tooltip=stadium["name"],
            icon=folium.Icon(color="blue", icon="futbol")
        ).add_to(m)
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    logging.info("Created all stadiums map")
    return m

@st.cache_data
def create_single_stadium_map(lat, lon, name, _key):
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="CartoDB Positron")
    folium.Marker(
        [lat, lon],
        tooltip=name,
        icon=folium.Icon(color="blue", icon="futbol")
    ).add_to(m)
    logging.info(f"Created single stadium map for {name}")
    return m

# JavaScript to detect mobile device
mobile_detection_js = """
<script>
function isMobile() {
    return /Mobi|Android/i.test(navigator.userAgent);
}
window.addEventListener('load', function() {
    const isMobileDevice = isMobile();
    const channel = new BroadcastChannel('streamlit-mobile');
    channel.postMessage({isMobile: isMobileDevice});
});
</script>
"""

# Inject JavaScript to detect mobile device
html(mobile_detection_js, height=0)

# Check session state for mobile detection
if "is_mobile" not in st.session_state:
    st.session_state["is_mobile"] = st.query_params.get("mobile", ["false"])[0].lower() == "true"

# Display summary table
st.subheader("Lista de Estadios")
df_stadiums = pd.DataFrame(stadiums)
st.dataframe(
    df_stadiums[["name", "google_maps"]],
    column_config={
        "name": st.column_config.TextColumn("Estadio"),
        "google_maps": st.column_config.LinkColumn(
            "Navegar",
            display_text="Ver en Google Maps",
            help="Abrir ubicación en Google Maps"
        )
    },
    hide_index=True,
    use_container_width=True
)

# Mobile-friendly layout
st.markdown("### Ver Mapas")
view_option = st.radio(
    "Selecciona una vista:",
    ["Todos los estadios", "Estadio individual"],
    key="view_option",
    horizontal=True
)

if view_option == "Todos los estadios":
    # st.subheader("Todos los Estadios")
    all_map = create_all_stadiums_map(stadiums)
    st_folium(
        all_map,
        use_container_width=True,
        height=400 if st.session_state.get("is_mobile", False) else 600,
        returned_objects=[],
        key="all_stadiums_map"
    )
else:
    selected_stadium = st.selectbox(
        "Selecciona un estadio",
        [s["name"] for s in stadiums],
        key="selected_stadium"
    )
    stadium = next(s for s in stadiums if s["name"] == selected_stadium)
    st.subheader(selected_stadium)
    single_map = create_single_stadium_map(
        stadium["lat"], stadium["lon"], stadium["name"], selected_stadium
    )
    st_folium(
        single_map,
        use_container_width=True,
        height=300 if st.session_state.get("is_mobile", False) else 400,
        returned_objects=[],
        key=f"map_{selected_stadium}"
    )