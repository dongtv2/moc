from st_on_hover_tabs import on_hover_tabs
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd

from IPython.display import display

st.set_page_config(layout="wide")

st.header("Allocation the aircraft")
st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)
# Tao danh sach
aclist = ['A521', 'A522', 'A523', 'A524', 'A526', 'A527', 'A528', 'A529', 'A531', 'A532', 'A533', 'A534', 'A535', 'A540', 'A542', 'A544', 'A600', 'A607', 'A629', 'A630', 'A631', 'A632', 'A633', 'A634', 'A635', 'A636', 'A637', 'A639', 'A640', 'A641', 'A642', 'A643', 'A644', 'A645', 'A646', 'A647', 'A648', 'A649', 'A650', 'A651', 'A652', 'A653', 'A654', 'A655', 'A656', 'A657', 'A658', 'A661', 'A662', 'A663', 'A666', 'A667', 'A668', 'A669', 'A670', 'A671', 'A672', 'A673', 'A674', 'A675', 'A676', 'A677', 'A683', 'A684', 'A685', 'A687', 'A689', 'A690', 'A691', 'A693', 'A694', 'A695', 'A697', 'A698', 'A699', 'A810', 'A811', 'A812', 'A814', 'A815', 'A816', 'A817']
mainbase = ["SGN", "HAN", "DAD", "HPH", "VII", "CXR", "VCA", "PQC"]

ac_df = pd.DataFrame(aclist, columns=["REG"])
# st.table(ac_df)
with st.sidebar:
    tabs = on_hover_tabs(tabName=['Dashboard', 'Allocation', 'OWP'], 
                         iconName=['dashboard', 'allocation', 'owp'], default_choice=0)

if tabs == 'Allocation':
    st.write('Name of option is {}'.format(tabs))
    file = st.file_uploader("Import xlsx file", type="xlsx")
    if file is not None:
        file_name = file.name
        with open(file_name, "wb") as f:
            f.write(file.getbuffer())
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

        def combine_sta_std(row):
            if row['ARR'] not in mainbase:
                return f"{row['STD']}-{row['STA']}"
            return row['STA']

        for aircraft in aclist:
            if aircraft in df['REG'].values:
                flights = df.loc[df['REG'] == aircraft]
                last_row = flights.iloc[-1]
                arr_value = last_row['ARR']

                if arr_value in mainbase:
                    last_row_data.append({
                        'REG': aircraft,
                         'DEP': last_row['DEP'],
                        'ARR': arr_value,
                        'STA': last_row['STA'],
                        'STD': last_row['STD']
                       
                    })
                else:
                    prev_row = flights.iloc[-2]  # Lấy dữ liệu từ dòng phía trên
                    last_row_data.append({
                        'REG': aircraft,
                        'DEP': last_row['DEP'],
                        'ARR': prev_row['ARR'],  # Sử dụng giá trị "ARR" từ dòng phía trên
                        'STA': combine_sta_std(prev_row),  # Sử dụng hàm combine_sta_std để nối giá trị "STA" và "STD" từ dòng phía trên
                        'STD': last_row['STD'] # Giữ nguyên giá trị "STD" từ dòng cuối cùng
                    
                    })
        df_output = pd.DataFrame(last_row_data)









        st.write(df_output)  # Display the cleaned data frame

