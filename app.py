import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import math

# 1. Supabase 연결 설정
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="북극항로 찬반 투표", page_icon="🚢", layout="wide")
st.title("🚢 북극항로 개척, 학생들의 의견은?")

# 2. 데이터 불러오기 함수
def load_data():
    response = supabase.table("opinions").select("*").execute()
    return response.data

data = load_data()
df = pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "school_name", "nickname", "choice", "comment", "likes", "created_at"])

# --- ⭐️ 세션 상태(Session State) 초기화 ---
# 현재 페이지 번호 기억하기
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# 내가 공감을 누른 글들의 ID를 기억할 리스트 만들기
if 'liked_posts' not in st.session_state:
    st.session_state.liked_posts = []
# ------------------------------------------

# 3. 탭 생성하기
tab1, tab2 = st.tabs(["🏠 메인 대시보드", "💬 전체 의견 게시판"])

# ==========================================
# 탭 1: 메인 대시보드
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
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
                    st.session_state.current_page = 1 
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

    with col2:
        st.subheader("🔥 공감 Top 10")
        if not df.empty:
            top10_df = df.sort_values(by="likes", ascending=False).head(10)
            for index, row in top10_df.iterrows():
                with st.container(border=True): 
                    st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 님 ➡️ **[{row['choice']}]**")
                    st.write(row['comment'])
                    
                    # ⭐️ 중복 공감 방지 로직 (메인 화면)
                    post_id = row['id']
                    # 이 글의 ID가 내 메모장(liked_posts)에 있다면 True, 없으면 False
                    has_liked = post_id in st.session_state.liked_posts 
                    
                    # disabled=has_liked 를 추가하면, 이미 누른 글은 버튼이 회색으로 변하며 안 눌러집니다.
                    if st.button(f"❤️ 공감 ({row['likes']})", key=f"top_like_{post_id}", disabled=has_liked):
                        new_likes = row['likes'] + 1
                        supabase.table("opinions").update({"likes": new_likes}).eq("id", post_id).execute()
                        st.session_state.liked_posts.append(post_id) # 메모장에 눌렀다고 기록
                        st.rerun()
        else:
            st.info("아직 등록된 의견이 없습니다.")

# ==========================================
# 탭 2: 전체 의견 게시판 
# ==========================================
with tab2:
    st.subheader("💬 모든 학생들의 의견")
    
    if not df.empty:
        all_df = df.sort_values(by="id", ascending=False)
        
        POSTS_PER_PAGE = 5 
        total_posts = len(all_df)
        total_pages = math.ceil(total_posts / POSTS_PER_PAGE)
        
        start_idx = (st.session_state.current_page - 1) * POSTS_PER_PAGE
        end_idx = start_idx + POSTS_PER_PAGE
        page_df = all_df.iloc[start_idx:end_idx]
        
        for index, row in page_df.iterrows():
            with st.container(border=True):
                st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 님 ➡️ **[{row['choice']}]**")
                st.write(row['comment'])
                
                # ⭐️ 중복 공감 방지 로직 (전체 게시판 화면)
                post_id = row['id']
                has_liked = post_id in st.session_state.liked_posts
                
                if st.button(f"❤️ 공감 ({row['likes']})", key=f"all_like_{post_id}", disabled=has_liked):
                    new_likes = row['likes'] + 1
                    supabase.table("opinions").update({"likes": new_likes}).eq("id", post_id).execute()
                    st.session_state.liked_posts.append(post_id) # 메모장에 눌렀다고 기록
                    st.rerun()
        
        st.divider()
        
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ 이전 페이지", disabled=(st.session_state.current_page == 1)):
                st.session_state.current_page -= 1
                st.rerun()
        with col_page:
            st.markdown(f"<h4 style='text-align: center;'>{st.session_state.current_page} / {total_pages}</h4>", unsafe_allow_html=True)
        with col_next:
            if st.button("다음 페이지 ➡️", disabled=(st.session_state.current_page == total_pages)):
                st.session_state.current_page += 1
                st.rerun()
    else:
        st.info("아직 등록된 의견이 없습니다.")
