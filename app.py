import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import math

# 1. Supabase 연결 설정 (기존과 동일)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 웹사이트 기본 설정
st.set_page_config(page_title="한국초 북극항로 탐험대", page_icon="🧊", layout="wide")

# ==========================================
# 🎨 1. 고급 디자인 업데이트 (CSS 스타일링)
# ==========================================
st.markdown("""
<style>
    /* 1. 웹사이트 전체 배경: 웅장한 빙하 사진 (외부 무료 이미지 주소) */
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), 
                          url("https://images.unsplash.com/photo-1599394142106-f6487e4f8d4e?q=80&w=2560");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* 2. 탭(Tab) 스타일: 더 귀엽고 눈에 띄게 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f8ff;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        color: #004085;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #cfe2f3;
        border: 1px solid #004085;
    }

    /* 3. 입력폼(Form) 배경: 하얗고 테두리는 둥글게 */
    .stForm {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* 4. 제목 글자 색상 변경 */
    h1 { color: #0a4d8c; }
    h2, h3, h4 { color: #004085; }
    
</style>
""", unsafe_allow_html=True)


# --- 제목과 선생님의 그림 나란히 배치 ---
title_col1, title_col2 = st.columns([1, 8])

with title_col1:
    # 🚨 여기에 선생님이 깃허브에 올리신 그림 파일 이름을 정확히 적어주세요! (예: logo.png)
    # 만약 아직 그림이 없다면, 아래 줄을 주석(#) 처리하거나 기본 아이콘을 쓰셔도 됩니다.
    # st.image("내가만든그림.png", width=80) 
    st.markdown("<h1 style='font-size: 60px;'>🧊</h1>", unsafe_allow_html=True) # 임시 아이콘

with title_col2:
    st.title("한국초 북극항로 탐험대, 우리의 의견은?")
# --------------------------------

# 2. 데이터 불러오기 함수 (기존과 동일)
def load_data():
    response = supabase.table("opinions").select("*").execute()
    return response.data

data = load_data()
df = pd.DataFrame(data) if data else pd.DataFrame(columns=["id", "school_name", "nickname", "choice", "comment", "likes", "created_at"])

# --- 세션 상태 초기화 (기존과 동일) ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'liked_posts' not in st.session_state:
    st.session_state.liked_posts = []

# 3. 탭 3개로 생성하기 (영상 탭 포함)
tab1, tab2, tab3 = st.tabs(["🏠 우리들의 투표소", "💬 친구들의 의견 모음", "📺 북극항로가 뭐예요?"])

# ==========================================
# 탭 1: 우리들의 투표소 (메인 화면)
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("✏️ 내 의견 남기기")
        # CSS로 디자인된 Form
        with st.form("opinion_form", clear_on_submit=True):
            school_name = st.text_input("학교 이름 (예: 한국초등학교)")
            nickname = st.text_input("닉네임 (예: 북극곰)")
            choice = st.selectbox("나의 선택", ["🌊 찬성", "⛔ 반대"])
            comment = st.text_area("이유를 자유롭게 적어주세요.")
            submit_btn = st.form_submit_button("탐험대에 의견 제출하기")
            
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
                    st.success("등록 완료! '친구들의 의견 모음' 탭에서 내 의견을 확인해보세요.")
                    st.rerun() 
                else:
                    st.warning("학교 이름, 닉네임, 이유를 모두 입력해주세요.")
                    
        # 🎨 중간에 귀여운 그림 삽입: 손 흔드는 북극곰
        # (웹상의 무료 일러스트 주소를 가져왔습니다.)
        st.divider()
        st.image("https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX29mZmljaWFsX3BsYW50cy8xL2xyL2ZyZnJpZW5kX3BvbGFyX2JlYXJfY3V0ZV9pbGx1c3RyYXRpb25fMS5qcGc.jpg", width=250)
        st.write("<i style='color:grey;'>“친구들의 따뜻한 의견을 기다려!”</i>", unsafe_allow_html=True)


    with col2:
        st.subheader("🔥 공감 Top 10 게시판")
        if not df.empty:
            top10_df = df.sort_values(by="likes", ascending=False).head(10)
            for index, row in top10_df.iterrows():
                with st.container(border=True): 
                    # 이모지를 넣어 더 초등학생 눈높이에 맞게
                    choice_icon = "🌊" if "찬성" in row['choice'] else "⛔"
                    st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 대원 ➡️ {choice_icon} **[{row['choice']}]**")
                    st.write(row['comment'])
                    
                    post_id = row['id']
                    has_liked = post_id in st.session_state.liked_posts 
                    
                    if st.button(f"❤️ 공감 ({row['likes']})", key=f"top_like_{post_id}", disabled=has_liked):
                        new_likes = row['likes'] + 1
                        supabase.table("opinions").update({"likes": new_likes}).eq("id", post_id).execute()
                        st.session_state.liked_posts.append(post_id)
                        st.rerun()
        else:
            st.info("아직 등록된 의견이 없습니다.")

        # 🎨 중간에 멋진 그림 삽입: 빙하 사이를 가는 배
        st.divider()
        st.image("https://images.rawpixel.com/image_800/czNmcy1wcml2YXRlL3Jhd3BpeGVsX2ltYWdlcy93ZWJzaXRlX29mZmljaWFsX3BsYW50cy8xL2xyL3NoaXBfaW5fYXJjdGljX29jZWFuX2lsbHVzdHJhdGlvbi5qcGc.jpg", width=350)
        st.write("<i style='color:grey;'>“우리들의 의견이 북극으로 가는 길을 열 거야!”</i>", unsafe_allow_html=True)

# ==========================================
# 탭 2: 친구들의 의견 모음 (기존과 동일)
# ==========================================
with tab2:
    st.subheader("💬 모든 대원들의 의견")
    
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
                choice_icon = "🌊" if "찬성" in row['choice'] else "⛔"
                st.markdown(f"🏫 **{row['school_name']}** | **{row['nickname']}** 대원 ➡️ {choice_icon} **[{row['choice']}]**")
                st.write(row['comment'])
                
                post_id = row['id']
                has_liked = post_id in st.session_state.liked_posts
                
                if st.button(f"❤️ 공감 ({row['likes']})", key=f"all_like_{post_id}", disabled=has_liked):
                    new_likes = row['likes'] + 1
                    supabase.table("opinions").update({"likes": new_likes}).eq("id", post_id).execute()
                    st.session_state.liked_posts.append(post_id)
                    st.rerun()
        
        st.divider()
        
        # 하단 통계 그래프 (메인화면에서 게시판 하단으로 이동 - 디자인 깔끔하게)
        st.subheader("📊 지금 우리들의 생각은?")
        pie_data = df['choice'].value_counts().reset_index()
        pie_data.columns = ['choice', 'count']
        fig = px.pie(pie_data, values='count', names='choice', color='choice',
                     color_discrete_map={'🌊 찬성':'#36A2EB', '⛔ 반대':'#FF6384'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

        # 페이지 버튼
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

# ==========================================
# 탭 3: 유튜브 영상 시청 (기존과 동일)
# ==========================================
with tab3:
    st.subheader("📺 북극항로 탐험, 영상으로 먼저 만나요!")
    
    # 틀고 싶은 유튜브 영상 주소 (선생님께서 원하시는 영상 주소로 수정 가능)
    youtube_url = "https://www.youtube.com/watch?v=o-tgQzqlwkQ&list=RDo-tgQzqlwkQ&start_radio=1" 
    
    # 유튜브 영상 띄우기
    st.video(youtube_url)
