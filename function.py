import streamlit as st
import pandas as pd
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from st_aggrid import AgGrid,GridOptionsBuilder
import streamlit_authenticator as stauth
import pandas as pd


def calculate_ground_time(std, sta):
    if pd.isnull(std) or pd.isnull(sta):
        return np.nan

    std_time = datetime.datetime.strptime(std, '%H:%M')
    sta_time = datetime.datetime.strptime(sta, '%H:%M')

    if std_time < sta_time:
        std_time += datetime.timedelta(days=1)

    ground_time = std_time - sta_time

    return str(ground_time)[:-3]



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
    
    uploaded_file = st.sidebar.file_uploader("Upload Flight Plan - NightStop", type=["xlsx"])
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
    uploaded_file = st.sidebar.file_uploader("Upload Flight Plan - Preflight", type=["xlsx"], key=key)

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
                if len(flights) >= 2:  # Add this check
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

def classify_color(value):
    if value < pd.Timedelta(hours=3):
        return 'red'
    elif value <= pd.Timedelta(hours=7):
        return 'orange'
    else:
        return 'blue'
    
# Định dạng thời gian

def format_timedelta(td):
    hours = td.total_seconds() // 3600
    minutes = (td.total_seconds() % 3600) // 60

    if pd.isnull(hours) or pd.isnull(minutes):
        return "NaN"

    return f"{int(hours):02d}:{int(minutes):02d}"


# Biểu đồ hiển thị

def plot_ground_time(df, city, title):
    filtered_df = df[df['ARR_x'] == city]
    filtered_df['GroundTime'] = pd.to_timedelta(filtered_df['GroundTime'] + ':00')
    filtered_df = filtered_df.sort_values('GroundTime')
    filtered_df['Color'] = filtered_df['GroundTime'].apply(classify_color)

    plt.figure(figsize=(10, 8))
    plt.bar(filtered_df['REG'], filtered_df['GroundTime'].dt.total_seconds() / 3600, color=filtered_df['Color'])

    plt.xlabel(f'Danh sách các tàu ở {city}')
    plt.ylabel('Tổng Ground Time (hours)')
    plt.title(f'Biểu đồ thời gian Ground Time các tàu ở {city}')
    plt.xticks(rotation=80)
    plt.ylim(bottom=0)  # Set the Y-axis lower limit to 0

    for i, value in enumerate(filtered_df['GroundTime']):
        plt.text(i, value.total_seconds() / 3600, format_timedelta(value), ha='center', va='bottom', rotation=90, fontsize=8)

    st.pyplot(plt)

def plot_ground_time_v1(df, city, title):
    filtered_df = df[df['ARR_x'] == city]
    # Convert 'GroundTime' to timedelta, handle conversion errors
    filtered_df['GroundTime'] = pd.to_timedelta(filtered_df['GroundTime'] + ':00', errors='coerce')
    # Fill NaN values with 0 hours
    filtered_df['GroundTime'] = filtered_df['GroundTime'].fillna(pd.Timedelta(hours=0))
    filtered_df = filtered_df.sort_values('GroundTime')
    filtered_df['Color'] = filtered_df['GroundTime'].apply(classify_color)

    # Ensure 'To Go' column exists
    if 'To Go' in filtered_df.columns:
        to_go_data = filtered_df['To Go']

    plt.figure(figsize=(12, 10))
    # Create a horizontal bar chart
    bars = plt.barh(filtered_df['REG'], filtered_df['GroundTime'].dt.total_seconds() / 3600, color=filtered_df['Color'])

    plt.ylabel(f'Danh sách các tàu ở {city}')
    plt.xlabel('Tổng Ground Time (hours)')
    plt.title(f'Biểu đồ thời gian Ground Time các tàu ở {city}')
    plt.yticks(fontsize=8)  # Reduce font size to fit more labels
    plt.xlim(left=0)  # Set the X-axis lower limit to 0

    for i, bar in enumerate(bars):
        xval = bar.get_width()
        plt.text(xval + 0.05, bar.get_y() + bar.get_height()/2, to_go_data.iloc[i], ha='left', va='center', rotation=0, fontsize=9)
        plt.text(xval - 0.05, bar.get_y() + bar.get_height()/2, format_timedelta(filtered_df['GroundTime'].iloc[i]), ha='right', va='center', rotation=0, fontsize=11, color='white')

    st.pyplot(plt)
def upload_and_read_excel_daily_check():
    key = "daily_check"
    uploaded_file = st.sidebar.file_uploader("Upload File DailyCheck From AMOS", type=["csv"], key=key)

    if uploaded_file is not None:
        try:
            file_contents = uploaded_file.read()
            folder_path = "./FPL"
            os.makedirs(folder_path, exist_ok=True)  # Create the folder if it doesn't exist
            file_path = os.path.join(folder_path, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(file_contents)
            df = pd.read_csv(file_path)
            df.reset_index(inplace=True)
            df.rename(columns={'A/C': 'REG'}, inplace=True)  # Modify df in place
            st.write("Uploaded file & reading data! Done")
            return df[['REG', 'To Go']]  # Access 'REG' instead of 'A/C'
        except pd.errors.ParserError as e:
            st.error(f"Error reading file: {uploaded_file.name} - {e}")

