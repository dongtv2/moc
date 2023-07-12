import streamlit as st
import pandas as pd

import datetime
import os

from st_aggrid import AgGrid, GridOptionsBuilder  #add import for GridOptionsBuilder


st.set_page_config(
    page_title= 'VJC-Maintenance Operation Center',
    page_icon= 'VJC',
    layout="wide"
)

st.title("Mainpage")
aclist = ['A521', 'A522', 'A523', 'A524', 'A526', 'A527', 'A528', 'A529', 'A531', 'A532', 'A533', 'A534', 'A535', 'A540', 'A542', 'A544', 'A600', 'A607', 'A629', 'A630', 'A631', 'A632', 'A633', 'A634', 'A635', 'A636', 'A637', 'A639', 'A640', 'A641', 'A642', 'A643', 'A644', 'A645', 'A646', 'A647', 'A648', 'A649', 'A650', 'A651', 'A652', 'A653', 'A654', 'A655', 'A656', 'A657', 'A658', 'A661', 'A662', 'A663', 'A666', 'A667', 'A668', 'A669', 'A670', 'A671', 'A672', 'A673', 'A674', 'A675', 'A676', 'A677', 'A683', 'A684', 'A685', 'A687', 'A689', 'A690', 'A691', 'A693', 'A694', 'A695', 'A697', 'A698', 'A699', 'A810', 'A811', 'A812', 'A814', 'A815', 'A816', 'A817']
mainbase = ["SGN", "HAN", "DAD", "HPH", "VII", "CXR", "VCA", "PQC"]

ac_df = pd.DataFrame(aclist, columns=["REG"])
df_output = []

def calculate_ground_time(std, sta):
    std_datetime = datetime.datetime.strptime(std, '%H:%M')
    sta_datetime = datetime.datetime.strptime(sta, '%H:%M')

    if std_datetime < sta_datetime:
        std_datetime += datetime.timedelta(days=1)

        ground_time = std_datetime - sta_datetime

    else:   
        ground_time = std_datetime - sta_datetime

    return str(ground_time)[:-3] 
def process_data(file_name, mainbase, aclist):
    ac_df = pd.DataFrame(aclist, columns=["REG"])
    df_output = []

    df = pd.read_excel(file_name)
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
                    'STA': last_row['STA']
                })
            else:
                last_row_data.append({
                    'REG': aircraft,
                    'DEP': last_row['ARR'],
                    'ARR': prev_row['ARR'],
                    'STA': prev_row['STA'],
                    'STD': last_row['STD'],
                    'Ground Time': calculate_ground_time(last_row['STD'], prev_row['STA'])
                })

    df_output = pd.DataFrame(last_row_data)
    return df_output


uploaded_file = st.file_uploader("Upload a file", type='xlsx')
folder_path = "/Users/dongthan/Desktop/moc/moc/FPL"

if uploaded_file is not None:
    # Create the folder if it doesn't exist
   
    os.makedirs(folder_path, exist_ok=True)

    # Save the uploaded file to the specified folder
    file_path = os.path.join(folder_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("File uploaded successfully!")


# Get the list of uploaded files in the folder
uploaded_files = os.listdir(folder_path)
uploaded_files.sort(key=lambda file: os.path.getmtime(os.path.join(folder_path, file)), reverse=True)
recent_files = uploaded_files[:10]
# Create a dropdown list of the uploaded files
selected_file = st.selectbox("Select an uploaded file", recent_files)


# Display the selected file
if selected_file:
    st.write(f"You selected: {selected_file}")
    df_selected = process_data(selected_file, mainbase, aclist)

    aclist_df = pd.DataFrame(aclist, columns=["REG"])
    merged_df = aclist_df.merge(df_selected, on='REG', how='left')

    # Display the merged DataFrame
    # AgGrid(merged_df, allow_unsafe=True, fit_columns_on_grid_load=True)

    # Tìm các dòng có giá trị null trong cột "DEP" hoặc "ARR"
    null_rows = merged_df[merged_df['DEP'].isnull() | merged_df['ARR'].isnull()]

    # Tạo bảng danh sách các giá trị "REG" có DEP hoặc ARR = null
    null_reg_table = null_rows[['REG']].reset_index(drop=True)


    col2, col1 = st.columns([3, 1])

    # Display the null_reg_table in the first column
    with col1:
        st.subheader("AIRCRAFT ON GROUND")
        AgGrid(null_reg_table)

    # Display the merged_df table in the second column
    with col2:
        AgGrid(merged_df, allow_unsafe=True, columns_auto_size_mode = True) 
