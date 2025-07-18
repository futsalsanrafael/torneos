import base64

import streamlit as st
import json
import pandas as pd
import os
# Elite page content

# Inject custom CSS to style tabs
st.markdown(body="# Veteranos", width="content")
st.sidebar.markdown("# AFUSSAR")

tab1, tab2, tab3 = st.tabs(["Fixture", "Posiciones", "Estadisticas"])

root_path = f"{os.getcwd()}"