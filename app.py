import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Supabase 연결 설정
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

data = load_data()
df = pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "school_name", "nickname", "choice", "comment", "likes", "created_at"])

# 3. 탭(Tab) 생성하기
tab1, tab2 = st.tabs(["🏠 메인 대시보드", "💬 전체 의견 게시판"])

# ==========================================
# 탭 1: 메인 대시보드 (투표, 통계, Top 10)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    # --- 왼쪽 영역: 의견 제출 및 통계 ---
    with col1:
        st.subheader("✏️ 내 의견 남기기")
        
        with st.form("opinion_form", clear_on_submit=True):
            school_name = st.text_input("학교 이름 (예: 한국초등학교)")
            nickname = st.text_input("닉네임 (예: 북극곰)")
            choice = st.selectbox("의견 선택", ["찬성", "반대"])
            comment = st.text_area("의견을 자유롭게 적어주세요.")
            submit_btn = st.form_submit_button("제출하기")
            
            if submit_btn:
                if school_name and nickname and comment:
                    supabase.table("opinions").insert({
                        "school_name": school_name,
                        "nickname": nickname,
                        "choice": choice,
                        "comment": comment,
                        "likes": 0
                    }).execute()
                    # 탭 기능을 안내하는 성공 메시지
                    st.success("등록 완료! '전체 의견 게시판' 탭에서 내 의견을 확인해보세요.")
                    st.rerun() 
                else:
                    st.warning("학교 이름, 닉네임, 의견을 모두 입력해주세요.")
                    
        st.divider()
        
        st.subheader("📊 실시간 찬반 비율")
        if not df.empty:
            pie_data = df['choice'].value_counts().reset_index()
            pie_data.columns = ['choice', 'count']
            fig = px.pie(pie_data, values='count', names='choice', color='choice',
                         color_discrete_map={'찬성':'#36A2EB', '반대':'#FF6384'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("아직 등록된 의견이 없어 통계를 낼 수 없습니다.")

    # --- 오른쪽 영역: Top 10 ---
    with col2:
        st.subheader("🔥 공감 Top 10")
        
        if not df.empty:
            top10_df = df.sort_values(by="likes", ascending=False).head(10)
            
            for index, row in top10_df.iterrows():
                with st.container(border=True): 
                    st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 님 ➡️ **[{row['choice']}]**")
                    st.write(row['comment'])
                    # 메인 화면에서도 공감을 누를 수 있도록 기능 유지
                    if st.button(f"❤️ 공감 ({row['likes']})", key=f"top_like_{row['id']}"):
                        new_likes = row['likes'] + 1
                        supabase.table("opinions").update({"likes": new_likes}).eq("id", row['id']).execute()
                        st.rerun()
        else:
            st.info("아직 등록된 의견이 없습니다.")

# ==========================================
# 탭 2: 전체 의견 게시판 (모든 글 보기 및 공감)
# ==========================================
with tab2:
    st.subheader("💬 모든 학생들의 의견")
    st.write("다른 학생들의 의견을 읽고 공감(❤️)을 눌러주세요! 많은 공감을 받으면 메인 화면 Top 10에 올라갑니다.")
    
    if not df.empty:
        # 전체 게시판은 새 글이 가장 위로 오도록 최신순(id 내림차순) 정렬
        all_df = df.sort_values(by="id", ascending=False)
        
        for index, row in all_df.iterrows():
            with st.container(border=True):
                st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 님 ➡️ **[{row['choice']}]**")
                st.write(row['comment'])
                
                # 전체 게시판용 공감 버튼
                if st.button(f"❤️ 공감 ({row['likes']})", key=f"all_like_{row['id']}"):
                    new_likes = row['likes'] + 1
                    supabase.table("opinions").update({"likes": new_likes}).eq("id", row['id']).execute()
                    st.rerun()
    else:
        st.info("아직 등록된 의견이 없습니다.")
