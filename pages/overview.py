import streamlit as st
import pandas as pd
import os
import datetime
from st_aggrid import AgGrid,GridOptionsBuilder

st.set_page_config(
    page_title='Maintenance Operation Control',
    layout = 'wide',
    initial_sidebar_state = 'collapsed')
