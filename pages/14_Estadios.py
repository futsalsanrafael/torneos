import folium
import streamlit as st

from streamlit_folium import st_folium


# Canchas page content
st.set_page_config(
    page_title="Futsal San Rafael",
    page_icon=":material/sports_soccer:",
    layout="wide"
)
st.markdown(body="# Estadios", width="content")
st.sidebar.markdown("# Futsal San Rafael")

st.header("Sportivo Pedal Club")
m = folium.Map(location=[-34.628520, -68.336973], zoom_start=16)
folium.Marker(
    [-34.628520, -68.336973], popup="Sportivo Pedal Club", tooltip="Sportivo Pedal Club"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("Tenis Club")
m = folium.Map(location=[-34.62106, -68.37281], zoom_start=16)
folium.Marker(
    [-34.62106, -68.37281], popup="Tenis Club", tooltip="Tenis Club"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("CIU UTN")
m = folium.Map(location=[-34.603497, -68.327794], zoom_start=16)
folium.Marker(
    [-34.603497, -68.327794], popup="CIU UTN", tooltip="CIU UTN"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("Banco Mendoza")
m = folium.Map(location=[-34.602058, -68.348941], zoom_start=16)
folium.Marker(
    [-34.602058, -68.348941], popup="Banco Mendoza", tooltip="Banco Mendoza"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("Polideportivo Nro2")
m = folium.Map(location=[-34.634303, -68.324028], zoom_start=16)
folium.Marker(
    [-34.634303, -68.324028], popup="Banco Mendoza", tooltip="Banco Mendoza"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("Club Pescadores")
m = folium.Map(location=[-34.602605, -68.354466], zoom_start=16)
folium.Marker(
    [-34.602605, -68.354466], popup="Banco Mendoza", tooltip="Banco Mendoza"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("HURACAN")
m = folium.Map(location=[-34.628061, -68.294438], zoom_start=16)
folium.Marker(
    [-34.628061, -68.294438], popup="HURACAN", tooltip="HURACAN"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("CIC SOSNEADO FUTSAL")
m = folium.Map(location=[-34.636386, -68.374009], zoom_start=16)
folium.Marker(
    [-34.636386, -68.374009], popup="CIC SOSNEADO FUTSAL", tooltip="CIC SOSNEADO FUTSAL"
).add_to(m)

st_folium(m, width=725, returned_objects=[])

st.header("CDA")
m = folium.Map(location=[-34.608495, -68.341752], zoom_start=16)
folium.Marker(
    [-34.608495, -68.341752], popup="CDA", tooltip="CDA"
).add_to(m)

st_folium(m, width=725, returned_objects=[])