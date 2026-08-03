import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Supabase 연결 설정 (secrets.toml에서 가져옴)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 웹사이트 기본 설정
st.set_page_config(page_title="북극항로 찬반 투표", page_icon="🚢", layout="wide")
st.title("🚢 북극항로 개척, 학생들의 의견은?")

# 2. 데이터 불러오기 함수
def load_data():
    response = supabase.table("opinions").select("*").execute()
    return response.data

# 데이터 불러와서 표(DataFrame) 형태로 변환
data = load_data()
df = pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "school_name", "nickname", "choice", "comment", "likes", "created_at"])

# 3. 화면 레이아웃을 왼쪽, 오른쪽 2단으로 나누기
col1, col2 = st.columns([1, 1])

# --- 왼쪽 영역: 의견 제출 및 통계 ---
with col1:
    st.subheader("✏️ 내 의견 남기기")
    
    # 폼 생성
    with st.form("opinion_form", clear_on_submit=True):
        # 이름 대신 학교 이름과 닉네임을 따로 받습니다.
        school_name = st.text_input("학교 이름 (예: 한국고등학교)")
        nickname = st.text_input("닉네임 (예: 북극곰)")
        
        choice = st.selectbox("의견 선택", ["찬성", "반대"])
        comment = st.text_area("의견을 자유롭게 적어주세요.")
        submit_btn = st.form_submit_button("제출하기")
        
        # 제출 버튼을 눌렀을 때의 동작
        if submit_btn:
            if school_name and nickname and comment:
                # Supabase에 데이터 저장
                supabase.table("opinions").insert({
                    "school_name": school_name,
                    "nickname": nickname,
                    "choice": choice,
                    "comment": comment,
                    "likes": 0
                }).execute()
                st.success("의견이 성공적으로 등록되었습니다!")
                st.rerun() # 화면 즉시 새로고침
            else:
                st.warning("학교 이름, 닉네임, 의견을 모두 입력해주세요.")
                
    st.divider()
    
    # 원 그래프 시각화
    st.subheader("📊 실시간 찬반 비율")
    if not df.empty:
        # 찬성/반대 갯수 세기
        pie_data = df['choice'].value_counts().reset_index()
        pie_data.columns = ['choice', 'count']
        
        # Plotly 라이브러리로 원 그래프 그리기
        fig = px.pie(pie_data, values='count', names='choice', color='choice',
                     color_discrete_map={'찬성':'#36A2EB', '반대':'#FF6384'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("아직 등록된 의견이 없어 통계를 낼 수 없습니다.")

# --- 오른쪽 영역: Top 10 게시판 ---
with col2:
    st.subheader("🔥 공감 Top 10 게시판")
    
    if not df.empty:
        # 좋아요 수 기준으로 내림차순 정렬 후 상위 10개만 추출
        top10_df = df.sort_values(by="likes", ascending=False).head(10)
        
        # 추출한 10개의 데이터를 순서대로 화면에 그리기
        for index, row in top10_df.iterrows():
            with st.container(border=True): # 테두리가 있는 박스 생성
                # 학교 이름과 닉네임을 함께 출력합니다.
                st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 님 ➡️ **[{row['choice']}]**")
                st.write(row['comment'])
                
                # 공감(좋아요) 버튼
                if st.button(f"❤️ 공감 ({row['likes']})", key=f"like_{row['id']}"):
                    # 클릭 시 데이터베이스의 좋아요 숫자를 1 올림
                    new_likes = row['likes'] + 1
                    supabase.table("opinions").update({"likes": new_likes}).eq("id", row['id']).execute()
                    st.rerun() # 화면 즉시 새로고침
    else:
        st.info("아직 등록된 의견이 없습니다. 첫 번째 의견을 남겨주세요!")
