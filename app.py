import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="우리 동네 댕냥이 보호소", page_icon="🐾", layout="wide")

@st.cache_data
def load_clean_data():
    file_path = "유기동물보호+현황_20260119191718.csv"
    if not os.path.exists(file_path):
        return None
        
    df = pd.read_csv(file_path, header=[2, 3])
    new_columns = []
    for col in df.columns:
        if col[0] == col[1]: new_columns.append(col[0])
        elif "Unnamed" in col[0]: new_columns.append(col[1])
        else: new_columns.append(f"{col[0]}_{col[1]}")
    df.columns = new_columns
    
    for col in df.columns:
        if "자치구별" not in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    df = df[df["자치구별(2)"] != "소계"]
    return df

try:
    df = load_clean_data()
    if df is not None:
        # 사진 표시
        all_files = os.listdir('.')
        dog_images = sorted([f for f in all_files if f.lower().startswith('dog') and f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if dog_images:
            cols = st.columns(len(dog_images))
            for i, img in enumerate(dog_images):
                cols[i].image(img, use_container_width=True, caption=f"귀요미 {i+1}호")

        st.title("🐾 우리 동네 댕냥이들은 어디에 있을까?")
        all_gus = df["자치구별(2)"].unique()
        selected_gu = st.sidebar.multiselect("📍 동네 선택", all_gus, default=all_gus)
        display_df = df[df["자치구별(2)"].isin(selected_gu)]

        # 요약 및 그래프
        st.write("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("🏠 전체 친구들", f"{display_df['소계'].sum()} 마리")
        c2.metric("🐕 멍멍이", f"{display_df['개_소계'].sum()} 마리")
        c3.metric("🐈 야옹이", f"{display_df['고양이_소계'].sum()} 마리")
        
        tab1, tab2 = st.tabs(["📊 지역별", "🍕 비중"])
        with tab1: st.plotly_chart(px.bar(display_df, x="자치구별(2)", y="소계", color="자치구별(2)", color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        with tab2: st.plotly_chart(px.pie(values=[display_df['개_소계'].sum(), display_df['고양이_소계'].sum()], names=["강아지 🐶", "고양이 🐈"], hole=0.5, color_discrete_sequence=["#FFCC00", "#FF6666"]), use_container_width=True)

        # 상세 표 (하이라이트)
        def highlight_max_row(s):
            return ['background-color: #FFECB3' if v == s.max() else '' for v in s]

        st.dataframe(display_df[["자치구별(2)", "소계", "개_소계", "고양이_소계"]].style.apply(highlight_max_row, subset=['소계', '개_소계', '고양이_소계'], axis=0), use_container_width=True)
        st.balloons()
except Exception as e:
    st.error(f"⚠️ 에러 발생: {e}")