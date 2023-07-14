import streamlit as st
import pandas as pd
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from st_aggrid import AgGrid,GridOptionsBuilder

import streamlit_authenticator as stauth


st.set_page_config(
    page_title='Maintenance Operation Control',
    layout = 'wide')


aclist = ['A521', 'A522', 'A523', 'A524', 'A526', 'A527', 'A528', 'A529', 'A531', 'A532', 'A533', 'A534', 'A535', 'A540', 'A542', 'A544', 'A600', 'A607', 'A629', 'A630', 'A631', 'A632', 'A633', 'A634', 'A635', 'A636', 'A637', 'A639', 'A640', 'A641', 'A642', 'A643', 'A644', 'A645', 'A646', 'A647', 'A648', 'A649', 'A650', 'A651', 'A652', 'A653', 'A654', 'A655', 'A656', 'A657', 'A658', 'A661', 'A662', 'A663', 'A666', 'A667', 'A668', 'A669', 'A670', 'A671', 'A672', 'A673', 'A674', 'A675', 'A676', 'A677', 'A683', 'A684', 'A685', 'A687', 'A689', 'A690', 'A691', 'A693', 'A694', 'A695', 'A697', 'A698', 'A699', 'A810', 'A811', 'A812', 'A814', 'A815', 'A816', 'A817']
mainbase = ["SGN", "HAN", "DAD", "HPH", "VII", "CXR", "VCA", "PQC"]
aclist_df = pd.DataFrame(aclist, columns=["REG"])

def calculate_ground_time(std, sta):
    if pd.notnull(std) and pd.notnull(sta):
        std_datetime = datetime.datetime.strptime(str(std), '%H:%M')
        sta_datetime = datetime.datetime.strptime(str(sta), '%H:%M')

        if std_datetime < sta_datetime:
            std_datetime += datetime.timedelta(days=1)

        ground_time = std_datetime - sta_datetime

        return str(ground_time)[:-3]
    else:
        return np.nan
def process_flight_data(df, aclist, mainbase):
    index = df[df['Unnamed: 0'] == 'DATE'].index[0]
    df = df.iloc[index:]
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.dropna(axis=0, how='all')
    df = df.reset_index(drop=True)
    df = df.drop(df.columns[[10, 11]], axis=1)
    df['REG'] = df['REG'].str.replace('VN-', '')

    last_row_data = []

    for aircraft in aclist:
        if aircraft in df['REG'].values:
            flights = df.loc[df['REG'] == aircraft]
            last_row = flights.iloc[-1]
            prev_row = None
            if len(flights) >= 2:
                prev_row = flights.iloc[-2] 
            arr_value = last_row['ARR']

            if arr_value in mainbase:
                last_row_data.append({
                    'REG': aircraft,
                    'DEP': last_row['DEP'],
                    'ARR': arr_value,
                    'STD': last_row['STD'],
                    'STA': last_row['STA'],
                    'Route': f"{last_row['DEP']} - {last_row['ARR']}",
                    'NightStop': last_row['STA']
                })
            else:
                last_row_data.append({
                    'REG': aircraft,
                    'DEP': last_row['ARR'],
                    'ARR': prev_row['ARR'] if prev_row is not None else None,
                    'STA': prev_row['STA'] if prev_row is not None else None,
                    'STD': last_row['STD'],
                    'Route': f"{last_row['DEP']} - {last_row['ARR']}"if prev_row is not None else None,
                    'NightStop': f"{prev_row['STA']} - {last_row['STD']}"if prev_row is not None else None,
                    'GroundTime': calculate_ground_time(last_row['STD'], prev_row['STA']) if prev_row is not None else None,
                })

    df_output = pd.DataFrame(last_row_data)
    return df_output



def upload_and_read_excel():
    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        try:
            file_contents = uploaded_file.read()
            folder_path = "./FPL"
            os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(file_contents)
            df = pd.read_excel(file_path)
            st.write("Uploaded file & reading data! Done")
            return df
        except pd.errors.ParserError as e:
            st.error(f"Error reading file: {uploaded_file.name} - {e}")

def upload_and_read_excel_preflt():
    key = "excel_file_upload"
    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"], key=key)

    if uploaded_file is not None:
        try:
            file_contents = uploaded_file.read()
            folder_path = "./FPL"
            os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(file_contents)
            df = pd.read_excel(file_path)
            st.write("Uploaded file & reading data! Done")
            return df
        except pd.errors.ParserError as e:
            st.error(f"Error reading file: {uploaded_file.name} - {e}")

 
def process_preflight_data(df,aclist,mainbase):
    index = df[df['Unnamed: 0'] == 'DATE'].index[0]
    df = df.iloc[index:]
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.dropna(axis=0, how='all')
    df = df.reset_index(drop=True)
    df = df.drop(df.columns[[10, 11]], axis=1)
    df['REG'] = df['REG'].str.replace('VN-', '')

    first_row_data = []
    
    for aircraft in aclist:
            if aircraft in df['REG'].values:
                flights = df.loc[df['REG'] == aircraft]
                first_row = flights.iloc[0]
                second_row = flights.iloc[1]
                dep_value = first_row['DEP']
                if dep_value in mainbase:
                    first_row_data.append({
                        'REG': aircraft,
                        'DEP': first_row['DEP'],
                        'ARR': first_row['ARR'],
                        'STD': first_row['STD'],
                        'STA': first_row['STA'],
                        'Route': f"{first_row['DEP']} - {first_row['ARR']}"
                    })
                else:
                    first_row_data.append({
                        'REG': aircraft,
                        'DEP': first_row['DEP'],
                        'ARR': first_row['ARR'],
                        'STD': first_row['STD'],
                        'STA': first_row['STA'],
                        'Route': f"{first_row['DEP']} - {first_row['ARR']}"
                    })
    df_output = pd.DataFrame(first_row_data)
    return df_output

tab1, tab2, tab3, tab4= st.tabs(["Night Stop", "Preflight", "Overviews","Charts"])

df_final_ns = None
df_final_preflight = None
merged_df = None

with tab1:
    st.header("NightStop")
    df_ns = upload_and_read_excel()

    if df_ns is not None:

        df_output = process_flight_data(df_ns, aclist, mainbase)

        merged_df_ns = aclist_df.merge(df_output, on='REG', how='left')

        df_final_ns = merged_df_ns[['REG', 'ARR', 'STA', 'Route', 'NightStop', 'GroundTime']]
       
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

        merged_df = df_final_ns.merge(df_final_preflight, on='REG', how='inner')

        merged_df['NS_TotalGround'] = merged_df.apply(lambda row: calculate_ground_time(row['STA_x'], row['STD']), axis=1)
        
        merged_df['TYPE'] = merged_df.apply(lambda row: '' if pd.isnull(row['GroundTime']) else 'TS_NS', axis=1)

        overview_df = merged_df[['TYPE','REG', 'ARR_x', 'NightStop','GroundTime','NS_TotalGround', 'STD']]

        AgGrid(overview_df)

with tab4:
    if merged_df is not None:

        # Create the chart
        classification_counts = merged_df['ARR_x'].value_counts()
        width = 8  # You can adjust this value based on your preference
        height = width * (3/5)

        fig, ax = plt.subplots(figsize=(width, height))  # Set the figsize with width=10 and height=4
        ax.bar(classification_counts.index, classification_counts.values)
        ax.set_xlabel('ARR_x')
        ax.set_ylabel('Count')

        # Add count labels on top of each bar
        for i, count in enumerate(classification_counts):
            ax.text(i, count, str(count), ha='center', va='bottom')

        # Display the chart using Streamlit
        st.pyplot(fig)