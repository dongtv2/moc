import streamlit as st
import pandas as pd
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from st_aggrid import AgGrid,GridOptionsBuilder
from function import *
import streamlit_authenticator as stauth


st.set_page_config(
    page_title='Maintenance Operation Control',
    layout = 'wide')


aclist = ['A521', 'A522', 'A523', 'A524', 'A526', 'A527', 'A528', 'A529', 'A531', 'A532', 'A533', 'A534', 'A535', 'A540', 'A542', 'A544', 'A600', 'A607', 'A629', 'A630', 'A631', 'A632', 'A633', 'A634', 'A635', 'A636', 'A637', 'A639', 'A640', 'A641', 'A642', 'A643', 'A644', 'A645', 'A646', 'A647', 'A648', 'A649', 'A650', 'A651', 'A652', 'A653', 'A654', 'A655', 'A656', 'A657', 'A658', 'A661', 'A662', 'A663', 'A666', 'A667', 'A668', 'A669', 'A670', 'A671', 'A672', 'A673', 'A674', 'A675', 'A676', 'A677', 'A683', 'A684', 'A685', 'A687', 'A689', 'A690', 'A691', 'A693', 'A694', 'A695', 'A697', 'A698', 'A699', 'A810', 'A811', 'A812', 'A814', 'A815', 'A816', 'A817']
mainbase = ["SGN", "HAN", "DAD", "HPH", "VII", "CXR", "VCA", "PQC"]
aclist_df = pd.DataFrame(aclist, columns=["REG"])




tab1, tab2, tab3, tab4, tab5= st.tabs(["Night Stop", "Preflight", "Overviews","Charts","Demo"])

df_final_ns = None
df_final_preflight = None
merged_df = None
overview_df = None

with tab1:
    st.header("NightStop")
    df_ns = upload_and_read_excel()
    with st.expander("Summary", expanded=True):
        
        st.write("ABC") 

    if df_ns is not None:

        df_output = process_flight_data(df_ns, aclist, mainbase)

        merged_df_ns = aclist_df.merge(df_output, on='REG', how='left')

        df_final_ns = merged_df_ns[['REG', 'ARR','STD','STA', 'Route', 'NightStop', 'GroundTime']]
       
        AgGrid(df_final_ns, fit_columns_on_grid_load=True)

with tab2:
    st.header("Preflight")
    df_preflight = upload_and_read_excel_preflt()

    if df_preflight is not None:

        df_output_preflight = process_preflight_data(df_preflight, aclist, mainbase)

        merged_df_preflight = aclist_df.merge(df_output_preflight, on='REG', how='left')

        df_final_preflight = merged_df_preflight[['REG','DEP' ,'ARR', 'STD','STA', 'Route']]

        AgGrid(df_final_preflight, fit_columns_on_grid_load=True)

with tab3:
    st.header("Overview allocation")

    if df_final_ns is not None and df_final_preflight is not None:

        overview_df = df_final_ns.merge(df_final_preflight, on='REG', how='inner')

        overview_df['NS_TotalGround'] = overview_df.apply(lambda row: calculate_ground_time(row['STD_y'], row['STA_x']), axis=1)

        overview_df['GroundTime'] = overview_df['GroundTime'].fillna(overview_df['NS_TotalGround'])



        overview_df = overview_df[['REG', 'ARR_x', 'NightStop','GroundTime', 'STD_y']]

        AgGrid(overview_df, fit_columns_on_grid_load=True)

with tab4:

    if df_final_ns is not None:
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("Biểu đồ phân bố NS ở các station", expanded=True):
                # Create the chart
                classification_counts = df_final_ns['ARR'].value_counts()

                fig, ax = plt.subplots()  # Set the figsize with width=10 and height=4
                ax.bar(classification_counts.index, classification_counts.values)
                ax.set_xlabel('ARR')
                ax.set_ylabel('Total Aircrafts')

                # Add count labels on top of each bar
                for i, count in enumerate(classification_counts):
                    ax.text(i, count, str(count), ha='center', va='bottom')

                # Display the chart using Streamlit
                st.pyplot(fig)

            if overview_df is not None:
                with st.expander("Biểu đồ ground time SGN - HAN", expanded=True):

                  # Call the function for SGN
                    plot_ground_time(overview_df, 'SGN', 'Biểu đồ ground time SGN')

                    # Call the function for HAN
                    plot_ground_time(overview_df, 'HAN', 'Biểu đồ ground time HAN')
        with c2:
            if overview_df is not None:
                
                with st.expander("Biểu đồ ground time DAD - CXR", expanded=True):

                    # Call the function for DAD
                    plot_ground_time(overview_df, 'DAD', 'Biểu đồ ground time DAD')

                    # Call the function for CXR
                    plot_ground_time(overview_df, 'CXR', 'Biểu đồ ground time CXR')
                


with tab5:
    st.header("Input AOG")
    