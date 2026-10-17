"""Two-pane study only. No quiz, drag board, flashcards or tools navigation."""
import time
import uuid
import streamlit as st
from core.content_validation import CATEGORIES, ROOT, full_model
from core.grading import memory_grade, word_count
from core.review_schedule import now
from ui.state import emit, flush

PARTS={'introduction':'Introduction','overview':'Overview',
       'body1':'Body 1','body2':'Body 2','full':'Toàn bài'}
MODES=['Chép theo mẫu','Học thuộc']


def retain_draft(widget_key,draft_key):
    st.session_state.study_drafts[draft_key]=st.session_state[widget_key]


def storage_status():
    if st.session_state.get('load_error'):
        st.warning(st.session_state.load_error)
    elif st.session_state.get('storage_mode')=='demo':
        st.caption('Chưa bật lưu lâu dài; bài làm chỉ được giữ trong phiên hiện tại.')
    elif st.session_state.get('storage_mode')=='local':
        st.caption('Lưu trên máy chủ hiện tại. Trên Streamlit Cloud cần cấu hình Sheets để giữ qua triển khai.')
    pending=st.session_state.get('pending',{})
    if pending:
        st.caption(f'{len(pending)} bản ghi chưa lưu lâu dài.')
        if st.session_state.get('store') and st.button('Thử lưu lại'):
            flush();st.rerun()
    elif st.session_state.get('persisted'):
        st.caption('Bài đã nộp được kho lưu trữ xác nhận.')


def study(exercises):
    st.session_state.setdefault('study_drafts',{})
    with st.sidebar:
        st.title('✍️ Chép & học thuộc')
        category=st.selectbox('Dạng đề',['all']+list(CATEGORIES),
             format_func=lambda x:'Tất cả' if x=='all' else CATEGORIES[x])
        search=st.text_input('Tìm đề')
        pool=[e for e in exercises if e.get('status')=='verified'
              and (category=='all' or e['category']==category)
              and search.casefold() in (e['exercise_id']+' '+e['title']).casefold()]
        if not pool:
            st.info('Chưa có đề phù hợp.');return
        byid={e['exercise_id']:e for e in pool}
        ident=st.selectbox('Chọn đề',list(byid),format_func=lambda x:x+' · '+byid[x]['title'])
        mode=st.radio('Cách học',MODES)
        part=st.selectbox('Phần cần chép / học',list(PARTS),format_func=PARTS.get)
        st.caption('Chọn cả đoạn hoặc toàn bài. Không chia từng câu.')
        st.caption('Đề trái · Mẫu và ô viết phải')
        storage_status()
    e=byid[ident]
    copy=mode==MODES[0]
    reference=full_model(e) if part=='full' else e['paragraphs'][part]
    task_id=('copy-' if copy else 'memory-')+part
    draft_key=f"{ident}:{e['content_version']}:{task_id}"
    state_key='study-only:'+draft_key
    if state_key not in st.session_state:
        st.session_state[state_key]={'attempt_id':str(uuid.uuid4()),'started':time.time(),
                                    'submitted':False,'retry_of':None,'round':0}
    state=st.session_state[state_key]
    st.title('Chép theo mẫu' if copy else 'Học thuộc')
    st.caption(f"{e['title']} · {PARTS[part]} · Hai khung cuộn riêng")
    # All controls live in the sidebar, keeping the two panes at the top of the page.
    # Force horizontal columns at narrow widths as well; no stacked source/answer layout.
    with st.container(key='study-panes'):
        left,right=st.columns(2,gap='medium')
        with left:
            with st.container(height=660,border=True,key='study-left'):
                st.subheader('Đề bài')
                asset=ROOT/e.get('asset_reference','missing')
                if asset.is_file():
                    st.image(str(asset),width='stretch')
                else:
                    st.caption('Chưa có ảnh đề trong bản triển khai.')
                st.write(e['prompt'])
                if e.get('source_note'):
                    st.caption(e['source_note'])
        with right:
            with st.container(height=660,border=True,key='study-right'):
                reveal=copy
                if not copy:
                    reveal=st.checkbox('Hiện mẫu để kiểm tra',key='reveal-'+draft_key)
                if reveal:
                    st.divider()
                    st.markdown('### '+('Mẫu để chép' if copy else 'Mẫu đối chiếu'))
                    for p in (list(PARTS)[:4] if part=='full' else [part]):
                        st.markdown('**'+PARTS[p]+'**')
                        st.write(e['paragraphs'][p])
                st.divider()
                st.subheader('Bài của bạn · '+PARTS[part])
                if not state['submitted']:
                    widget_key='draft-widget:'+draft_key
                    answer=st.text_area('Ô viết',value=st.session_state.study_drafts.get(draft_key,''),
                        height=410 if part=='full' else 340,max_chars=20000,
                        placeholder='Viết đủ phần đã chọn. Nếu viết toàn bài, xuống dòng giữa bốn đoạn.',
                        key=widget_key,on_change=retain_draft,args=(widget_key,draft_key))
                    st.caption(f'{word_count(answer)} từ · Mẫu: {word_count(reference)} từ')
                    if st.button('Nộp bài',type='primary',key='submit-'+state_key):
                        if not answer.strip():
                            st.warning('Bạn chưa viết bài.');return
                        st.session_state.study_drafts[draft_key]=answer
                        result=memory_grade(answer,reference,case_sensitive=True,punctuation=True)
                        attempt=dict(attempt_id=state['attempt_id'],
                            learner_id=st.session_state.settings['learner_id'],
                            exercise_id=ident,task_id=task_id,content_version=e['content_version'],
                            submitted_at=now().isoformat(),answer=answer,reference_snapshot=reference,
                            duration_seconds=round(time.time()-state['started']),
                            duration_basis='Thời gian mở bài đến nộp; có thể gồm thời gian rời trang.',
                            retry_of=state['retry_of'],study_mode='copy' if copy else 'recall',
                            normalization_policy={'case_sensitive':True,'punctuation':True},**result)
                        emit('attempt',attempt,event_id=attempt['attempt_id'])
                        state.update(submitted=True,result=attempt)
                        st.rerun()
                else:
                    result=state['result']
                    st.metric('Mức khớp mẫu',f"{result['score']}/100")
                    st.caption('Đối chiếu từ và dấu câu với mẫu; không phải chấm ngữ pháp hay band IELTS.')
                    st.write(result['answer'])
                    if result.get('changes'):
                        st.dataframe(result['changes'],hide_index=True,width='stretch')
                    else:
                        st.success('Đã khớp toàn bộ phần đã chọn.')
                    if st.button('Viết lại',key='retry-'+state_key):
                        st.session_state[state_key]={
                            'attempt_id':str(uuid.uuid4()),'started':time.time(),
                            'submitted':False,'retry_of':result['attempt_id'],'round':state['round']+1}
                        st.rerun()

