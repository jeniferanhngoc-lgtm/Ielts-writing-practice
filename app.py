import streamlit as st
from core.content_validation import load_content
from ui.state import initialize, save_banner
from ui.practice import practice
from ui.screens import today, library, corrections, progress, settings_page

st.set_page_config(page_title='Task 1 · Mỗi ngày một bước tiến',page_icon='✍️',layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3 {letter-spacing:-.025em}
[data-testid="stMetric"] {background:white;border:1px solid #e0e8e8;border-radius:14px;padding:16px}
[data-testid="stSidebar"] {border-right:1px solid #dde5e5}
div.stButton>button {border-radius:9px}
</style>''',unsafe_allow_html=True)
initialize()
structures,exercises=load_content()
exercises+=st.session_state.get('extra_exercises',[])
with st.sidebar:
    st.title('✍️ Task 1 Studio')
    st.caption('HỌC HIỂU · NHỚ MẪU · TỰ VIẾT')
    page=st.radio('Không gian học',['Hôm nay','Thư viện cấu trúc','Luyện tập','Chữa bài & viết lại','Lịch sử & sổ lỗi','Cài đặt & dữ liệu'],label_visibility='collapsed')
    st.divider()
    st.caption('Một người học · Giờ Việt Nam\n\nKhông tích hợp AI. Điểm luyện tập không phải band IELTS.')
    if st.session_state.timer.get('running_since') is not None:
        st.info('Đồng hồ buổi học đang chạy. Về Hôm nay để tạm dừng.')
if page=='Hôm nay': today(exercises)
elif page=='Thư viện cấu trúc': library(structures)
elif page=='Luyện tập': practice(exercises,structures)
elif page=='Chữa bài & viết lại': corrections(exercises,structures)
elif page=='Lịch sử & sổ lỗi': progress(exercises)
else: settings_page(structures,exercises)
st.divider()
save_banner()
