import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정
st.set_page_config(page_title="우리 동네 댕냥이 보호소", page_icon="🐾", layout="wide")

# 2. 데이터 불러오기 함수
@st.cache_data
def load_clean_data():
    df = pd.read_csv("유기동물보호+현황_20260119191718.csv", header=[2, 3])
    new_columns = []
    for col in df.columns:
        if col[0] == col[1]: new_columns.append(col[0])
        elif "Unnamed" in col[0]: new_columns.append(col[1])
        else: new_columns.append(f"{col[0]}_{col[1]}")
    df.columns = new_columns
    
    # 💡 숫자로 강제 변환 (글자 비교로 인한 중랑구 오류 방지)
    for col in df.columns:
        if "자치구별" not in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
    df = df[df["자치구별(2)"] != "소계"]
    return df

try:
    df = load_clean_data()

    # 3. 📸 사진 병렬 배치
    current_dir = os.path.dirname(os.path.abspath(__file__))
    all_files = os.listdir(current_dir)
    dog_images = sorted([f for f in all_files if f.lower().startswith('dog') and f.lower().endswith(('.jpg', '.jpeg', '.png'))])

    if dog_images:
        cols = st.columns(len(dog_images))
        for i, img in enumerate(dog_images):
            img_path = os.path.join(current_dir, img)
            cols[i].image(img_path, use_container_width=True, caption=f"귀요미 {i+1}호")

    # 4. 제목 및 UI
    st.title("🐾 우리 동네 댕냥이들은 어디에서 주인을 찾고 있을까?")
    
    all_gus = df["자치구별(2)"].unique()
    selected_gu = st.sidebar.multiselect("📍 궁금한 동네 선택", all_gus, default=all_gus)
    display_df = df[df["자치구별(2)"].isin(selected_gu)]

    # 5. 요약 전광판
    st.write("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("🏠 전체 친구들", f"{display_df['소계'].sum()} 마리")
    c2.metric("🐕 멍멍이", f"{display_df['개_소계'].sum()} 마리")
    c3.metric("🐈 야옹이", f"{display_df['고양이_소계'].sum()} 마리")
    st.write("---")

    # 6. 그래프 탭
    tab1, tab2 = st.tabs(["📊 지역별 현황", "🍕 동물별 비중"])
    with tab1:
        st.plotly_chart(px.bar(display_df, x="자치구별(2)", y="소계", color="자치구별(2)", 
                               color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    with tab2:
        fig_pie = px.pie(values=[display_df['개_소계'].sum(), display_df['고양이_소계'].sum()], 
                         names=["강아지 🐶", "고양이 🐈"], hole=0.5,
                         color_discrete_sequence=["#FFCC00", "#FF6666"])
        st.plotly_chart(fig_pie, use_container_width=True)

    # 7. 📋 상세 통계표 (소계, 개_소계, 고양이_소계 모두 강조!)
    st.subheader("📋 상세 통계표")
    view_cols = ["자치구별(2)", "소계", "개_소계", "고양이_소계"]

    # 각 기둥에서 최댓값을 찾아 노란색을 칠하는 함수
    def highlight_max_row(s):
        is_max = (s == s.max())
        return ['background-color: #FFECB3' if v else '' for v in is_max]

    # 💡 subset 부분에 강조하고 싶은 기둥들을 모두 적어줬어!
    st.dataframe(
        display_df[view_cols].style.apply(highlight_max_row, subset=['소계', '개_소계', '고양이_소계'], axis=0), 
        use_container_width=True
    )
    
    st.balloons()

except Exception as e:
    st.error(f"⚠️ 에러 발생: {e}")