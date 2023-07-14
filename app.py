import streamlit as st
import pandas as pd
import os
import datetime

aclist = ['A521', 'A522', 'A523', 'A524', 'A526', 'A527', 'A528', 'A529', 'A531', 'A532', 'A533', 'A534', 'A535', 'A540', 'A542', 'A544', 'A600', 'A607', 'A629', 'A630', 'A631', 'A632', 'A633', 'A634', 'A635', 'A636', 'A637', 'A639', 'A640', 'A641', 'A642', 'A643', 'A644', 'A645', 'A646', 'A647', 'A648', 'A649', 'A650', 'A651', 'A652', 'A653', 'A654', 'A655', 'A656', 'A657', 'A658', 'A661', 'A662', 'A663', 'A666', 'A667', 'A668', 'A669', 'A670', 'A671', 'A672', 'A673', 'A674', 'A675', 'A676', 'A677', 'A683', 'A684', 'A685', 'A687', 'A689', 'A690', 'A691', 'A693', 'A694', 'A695', 'A697', 'A698', 'A699', 'A810', 'A811', 'A812', 'A814', 'A815', 'A816', 'A817']
mainbase = ["SGN", "HAN", "DAD", "HPH", "VII", "CXR", "VCA", "PQC"]
aclist_df = pd.DataFrame(aclist, columns=["REG"])

def calculate_ground_time(std, sta):

    std_datetime = datetime.datetime.strptime(std, '%H:%M')
    sta_datetime = datetime.datetime.strptime(sta, '%H:%M')

    if std_datetime < sta_datetime:
        std_datetime += datetime.timedelta(days=1)

        ground_time = std_datetime - sta_datetime

    else:
        ground_time = std_datetime - sta_datetime

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
                    'Night-Stop': last_row['STA']
                })
            else:
                last_row_data.append({
                    'REG': aircraft,
                    'DEP': last_row['ARR'],
                    'ARR': prev_row['ARR'] if prev_row is not None else None,
                    'STA': prev_row['STA'] if prev_row is not None else None,
                    'STD': last_row['STD'],
                    'Route': f"{last_row['DEP']} - {last_row['ARR']}"if prev_row is not None else None,
                    'Night-Stop': f"{prev_row['STA']} - {last_row['STD']}"if prev_row is not None else None,
                    'GRD-TIME': calculate_ground_time(last_row['STD'], prev_row['STA']) if prev_row is not None else None,
                })

    df_output = pd.DataFrame(last_row_data)
    return df_output



def upload_and_read_excel():
    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        try:
            file_contents = uploaded_file.read()
            file_path = f"./{uploaded_file.name}"
            with open(file_path, 'wb') as f:
                f.write(file_contents)
            df = pd.read_excel(file_path)
            st.write("Uploaded file & reading data! Done")
            return df
        except pd.errors.ParserError as e:
            st.error(f"Error reading file: {uploaded_file.name} - {e}")

if __name__ == "__main__":
    df = upload_and_read_excel()
    if df is not None:
        
        df_output = process_flight_data(df, aclist, mainbase)
        merged_df = aclist_df.merge(df_output, on='REG', how='left')

        df_final_ns = merged_df[['REG', 'ARR', 'STA', 'Route', 'Night-Stop', 'GRD-TIME']]
        st.dataframe(df_final_ns)

