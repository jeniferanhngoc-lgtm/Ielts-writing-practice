import streamlit as st
from core.content_validation import load_content
from ui.state import initialize
from ui.study_only import study

st.set_page_config(page_title='Task 1 · Chép & học thuộc',page_icon='✍️',
                   layout='wide',initial_sidebar_state='expanded')
st.markdown("""<style>
.block-container {max-width:1600px;padding-top:1rem;padding-bottom:.5rem}
h1 {font-size:1.7rem; margin-bottom:.3rem}
.st-key-study-panes [data-testid="stHorizontalBlock"] {
    flex-direction:row !important; flex-wrap:nowrap !important; align-items:flex-start !important;
}
.st-key-study-panes [data-testid="stColumn"] {
    min-width:0 !important; width:calc(50% - 1rem) !important; flex:1 1 0% !important;
}
.st-key-study-left, .st-key-study-right {overscroll-behavior:contain}
[data-testid="stSidebar"] {border-right:1px solid #dde5e5}
</style>""",unsafe_allow_html=True)
initialize()
_, exercises=load_content()
study(exercises)

