import streamlit as st
from core.content_validation import load_content
from ui.state import initialize, save_banner
from ui.practice import practice
from ui.screens import corrections, progress, settings_page
from ui.journey import today, library, apply_route
from ui.personal_memory import personal_memory
from ui.focused_study import study_structures, study_essays

st.set_page_config(page_title='Task 1 · Học thuộc cấu trúc và bài mẫu',page_icon='✍️',layout='wide')
st.markdown('''<style>
.block-container {max-width:960px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3 {letter-spacing:-.025em}
[data-testid="stMetric"] {background:white;border:1px solid #e0e8e8;border-radius:14px;padding:16px}
[data-testid="stSidebar"] {border-right:1px solid #dde5e5}
div.stButton>button {border-radius:9px}
</style>''',unsafe_allow_html=True)
initialize()
structures,exercises=load_content()
exercises+=st.session_state.get('extra_exercises',[])
if not st.session_state.get('focused_ui_v2'):
    st.session_state.page='Học bài mẫu'
    st.session_state.focused_ui_v2=True
apply_route()
with st.sidebar:
    st.title('✍️ Học thuộc Task 1')
    st.caption('MỖI LẦN MỘT KHUNG · MỖI LẦN MỘT ĐOẠN')
    def open_focus(destination):
        st.session_state.page=destination
    st.button('Học cấu trúc',on_click=open_focus,args=('Học cấu trúc',),width='stretch',type='primary' if st.session_state.get('page')=='Học cấu trúc' else 'secondary')
    st.button('Học thuộc bài',on_click=open_focus,args=('Học bài mẫu',),width='stretch',type='primary' if st.session_state.get('page','Học bài mẫu')=='Học bài mẫu' else 'secondary')
    study_controls=st.container()
    with st.expander('Công cụ khác'):
        page=st.radio('Không gian học',['Học bài mẫu','Học cấu trúc','Hôm nay','Học thuộc bài của tôi','Thư viện cấu trúc','Luyện tập','Chữa bài & viết lại','Lịch sử & sổ lỗi','Cài đặt & dữ liệu'],label_visibility='collapsed',key='page')
        st.caption('Quiz, ChatGPT, lịch ôn, thư viện đầy đủ và sao lưu tiến độ.')
    st.divider()
    st.caption('Cấu trúc: chọn đáp án. Bài mẫu: chép theo hoặc tự nhớ và viết.')
    if st.session_state.timer.get('running_since') is not None:
        st.info('Đồng hồ buổi học đang chạy. Về Hôm nay để tạm dừng.')
if page=='Học cấu trúc': study_structures(structures,study_controls)
elif page=='Học bài mẫu': study_essays(study_controls)
elif page=='Hôm nay': today(exercises,structures)
elif page=='Học thuộc bài của tôi': personal_memory()
elif page=='Thư viện cấu trúc': library(structures,exercises)
elif page=='Luyện tập': practice(exercises,structures)
elif page=='Chữa bài & viết lại': corrections(exercises,structures)
elif page=='Lịch sử & sổ lỗi': progress(exercises)
else: settings_page(structures,exercises)
st.divider()
save_banner(compact=page in ('Học cấu trúc','Học bài mẫu'))
