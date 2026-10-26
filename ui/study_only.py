"""Two-pane copy/recall with paragraph fields and an optional stopwatch."""
import re
import time
import uuid
import streamlit as st
from core.content_validation import CATEGORIES, ROOT, full_model
from core.grading import memory_grade, word_count
from core.review_schedule import now
from ui.state import emit, flush

PARTS={'introduction':'Introduction','overview':'Overview',
       'body1':'Body 1','body2':'Body 2','full':'Toàn bài'}
PARAGRAPHS=list(PARTS)[:4]
MODES=['Chép theo mẫu','Học thuộc']


def plain_explanation(text):
    return re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]', '', str(text))


def go_to_exercise(ident):
    st.session_state['study-exercise-picker']=ident


def retain_draft(widget_key,draft_key):
    st.session_state.study_drafts[draft_key]=st.session_state[widget_key]


def clock_seconds(clock,stamp=None):
    stamp=time.monotonic() if stamp is None else stamp
    return max(0.0,clock.get('seconds',0.0)+
               (stamp-clock['running_since'] if clock.get('running_since') is not None else 0.0))


def clock_pause(clock,stamp=None):
    clock['seconds']=clock_seconds(clock,stamp)
    clock['running_since']=None


def clock_start(clock,stamp=None):
    if clock.get('running_since') is None:
        clock['running_since']=time.monotonic() if stamp is None else stamp
    clock['used']=True


def clock_label(seconds):
    seconds=int(seconds)
    return f'{seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02}'


@st.fragment(run_every='1s')
def stopwatch(clock,key,submitted):
    enabled=st.checkbox('Tính thời gian',key='clock-enabled:'+key)
    if not enabled:
        if clock.get('running_since') is not None:
            clock_pause(clock)
        return
    st.metric('Đồng hồ',clock_label(clock_seconds(clock)))
    st.caption('Bấm Bắt đầu khi muốn tính giờ. Tạm dừng khi nghỉ; nộp bài sẽ dừng đồng hồ.')
    running=clock.get('running_since') is not None
    if st.button('Tiếp tục' if clock.get('seconds',0)>0 else 'Bắt đầu',
                 disabled=submitted or running,key='clock-start:'+key):
        clock_start(clock)
        st.rerun()
    if st.button('Tạm dừng',disabled=submitted or not running,key='clock-pause:'+key):
        clock_pause(clock)
        st.rerun()
    if st.button('Đặt lại',disabled=submitted,key='clock-reset:'+key):
        clock.update(seconds=0.0,running_since=None,used=False)
        st.rerun()


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


def paragraph_inputs(exercise,part,reveal,draft_key):
    answers={}
    selected=PARAGRAPHS if part=='full' else [part]
    # Preserve a previous whole-essay draft if it has four clearly separated paragraphs.
    if part=='full':
        old=st.session_state.study_drafts.get(draft_key,'')
        chunks=re.split(r'\n\s*\n',old.strip()) if old.strip() else []
        if len(chunks)==4:
            for p,text in zip(PARAGRAPHS,chunks):
                st.session_state.study_drafts.setdefault(draft_key+':'+p,text)
        elif old.strip():
            with st.expander('Bản nháp toàn bài từ phiên bản trước'):
                st.write(old)
    for p in selected:
        st.markdown('### '+PARTS[p])
        if reveal:
            st.caption('Mẫu để chép / đối chiếu')
            st.write(exercise['paragraphs'][p])
        entry_key=draft_key+':'+p if part=='full' else draft_key
        widget_key='draft-widget:'+entry_key
        label='Ô viết · '+PARTS[p] if part=='full' else 'Ô viết'
        answers[p]=st.text_area(label,value=st.session_state.study_drafts.get(entry_key,''),
            height=250,
            key=widget_key,placeholder='Viết trọn đoạn '+PARTS[p]+' tại đây.',
            on_change=retain_draft,args=(widget_key,entry_key))
        st.caption(f"{word_count(answers[p])} từ · Mẫu: {word_count(exercise['paragraphs'][p])} từ")
        st.divider()
    return answers


def study(exercises):
    st.markdown('<style>\n.st-key-study-right [data-testid="stElementContainer"]:has([data-testid="stTextArea"]) {\n    flex:0 0 auto !important; height:auto !important; min-height:0 !important;\n}\n.st-key-study-right [data-testid="stTextArea"] {\n    height:auto !important; min-height:0 !important; width:100%;\n}\n.st-key-study-right [data-baseweb="textarea"] {\n    height:auto !important; min-height:0 !important;\n    border:1px solid #788b9b !important; border-radius:8px;\n}\n.st-key-study-right textarea {\n    resize:vertical !important; min-height:120px !important;\n    max-height:none !important; overflow:auto !important; box-sizing:border-box !important;\n}\n</style>',unsafe_allow_html=True)
    st.session_state.setdefault('study_drafts',{})
    with st.sidebar:
        st.title('✍️ Chép & học thuộc')
        category=st.selectbox('Dạng đề',['all']+list(CATEGORIES),
             format_func=lambda x:'Tất cả' if x=='all' else CATEGORIES[x])
        search=st.text_input('Tìm đề')
        pool=[e for e in exercises if e.get('status')=='verified'
              and e.get('model_origin') in ('user_pdf','user_revision')
              and (category=='all' or e['category']==category)
              and search.casefold() in (e['exercise_id']+' '+e['title']).casefold()]
        if not pool:
            st.info('Chưa có đề phù hợp.');return
        pool.sort(key=lambda e:(e.get('source_lesson_index',999),e['exercise_id']))
        byid={e['exercise_id']:e for e in pool}
        if st.session_state.get('study-exercise-picker') not in byid:
            st.session_state['study-exercise-picker']=next(iter(byid))
        ident=st.selectbox('Chọn đề',list(byid),key='study-exercise-picker',format_func=lambda x:x+' · '+byid[x]['title'])
        mode=st.radio('Cách học',MODES)
        part=st.selectbox('Phần cần chép / học',list(PARTS),format_func=PARTS.get)
        st.caption('Đề trái · Mẫu và ô viết phải')
        st.caption('Toàn bài: 4 ô viết riêng · Có đồng hồ tùy chọn')
        st.caption('Chỉ sử dụng 18 bài gốc trong PDF bạn cung cấp.')
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
    clock=state.setdefault('clock',{'seconds':0.0,'running_since':None,'used':False})
    # Switching to a different exercise/mode/part pauses the previous stopwatch.
    previous=st.session_state.get('study-clock-active')
    if previous and previous!=state_key and previous in st.session_state:
        old_clock=st.session_state[previous].get('clock',{})
        if old_clock.get('running_since') is not None:
            clock_pause(old_clock)
    st.session_state['study-clock-active']=state_key
    with st.sidebar:
        stopwatch(clock,draft_key,state['submitted'])
    st.title('Chép theo mẫu' if copy else 'Học thuộc')
    st.caption(f"{e['title']} · {PARTS[part]} · Hai khung cuộn riêng")
    st.caption('Mẫu nguyên văn: '+e['source_filename']+' · trang '+', '.join(str(p) for p in e['source_pages']))
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
                if not state['submitted']:
                    st.subheader('Bài của bạn · '+PARTS[part])
                    if part=='full':
                        st.caption('Cuộn trong khung này: mỗi đoạn có mẫu và ô viết ngay bên dưới. Nộp chung sau Body 2.')
                    answers=paragraph_inputs(e,part,reveal,draft_key)
                    answer='\n\n'.join(answers[p] for p in (PARAGRAPHS if part=='full' else [part]))
                    st.caption(f'Tổng: {word_count(answer)} từ')
                    label='Nộp toàn bài' if part=='full' else 'Nộp bài'
                    if st.button(label,type='primary',key='submit-'+state_key):
                        missing=[PARTS[p] for p,value in answers.items() if not value.strip()]
                        if missing:
                            st.warning('Chưa viết: '+', '.join(missing)+'.');return
                        for p,value in answers.items():
                            entry_key=draft_key+':'+p if part=='full' else draft_key
                            st.session_state.study_drafts[entry_key]=value
                        clock_pause(clock)
                        timed=round(clock_seconds(clock),1) if clock['used'] else None
                        result=memory_grade(answer,reference,case_sensitive=True,punctuation=True)
                        attempt=dict(attempt_id=state['attempt_id'],
                            learner_id=st.session_state.settings['learner_id'],
                            exercise_id=ident,task_id=task_id,content_version=e['content_version'],
                            submitted_at=now().isoformat(),answer=answer,reference_snapshot=reference,
                            paragraph_answers=dict(answers),timer_used=bool(clock['used']),
                            timed_seconds=timed,duration_seconds=timed if timed is not None else 0,
                            duration_basis='Đồng hồ bật thủ công, không gồm thời gian tạm dừng.' if timed is not None else 'Không sử dụng đồng hồ.',
                            wall_time_seconds=round(time.time()-state['started']),
                            retry_of=state['retry_of'],study_mode='copy' if copy else 'recall',
                            normalization_policy={'case_sensitive':True,'punctuation':True},**result)
                        emit('attempt',attempt,event_id=attempt['attempt_id'])
                        state.update(submitted=True,result=attempt)
                        st.rerun()
                else:
                    result=state['result']
                    st.metric('Mức khớp mẫu',f"{result['score']}/100")
                    st.caption('Đối chiếu từ và dấu câu với mẫu; không phải chấm ngữ pháp hay band IELTS.')
                    if result.get('timer_used'):
                        st.info('Thời gian đã bấm giờ: '+clock_label(result['timed_seconds']))
                    for p in (PARAGRAPHS if part=='full' else [part]):
                        st.markdown('**'+PARTS[p]+'**')
                        if reveal:
                            st.caption('Mẫu đối chiếu')
                            st.write(e['paragraphs'][p])
                        if e.get('paragraph_notes',{}).get(p):
                            with st.expander('Giải thích cấu trúc · '+PARTS[p]):
                                st.write(plain_explanation(e['paragraph_notes'][p]))
                        st.caption('Bạn viết')
                        st.write(result.get('paragraph_answers',{}).get(p,result['answer'] if part!='full' else ''))
                    if part=='full' and not result.get('paragraph_answers'):
                        st.write(result['answer'])
                    if result.get('changes'):
                        st.dataframe(result['changes'],hide_index=True,width='stretch')
                    else:
                        st.success('Đã khớp toàn bộ phần đã chọn.')
                    ordered_ids=list(byid)
                    current_index=ordered_ids.index(ident)
                    next_ident=ordered_ids[current_index+1] if current_index+1<len(ordered_ids) else None
                    st.button('Bài tiếp theo',type='primary',key='next-'+state_key,
                              disabled=next_ident is None,on_click=go_to_exercise,
                              args=(next_ident,))
                    if next_ident is None:
                        st.caption('Đã đến bài cuối trong danh sách đang lọc. Bạn có thể chọn đề khác ở thanh bên.')
                    if st.button('Viết lại',key='retry-'+state_key):
                        st.session_state[state_key]={
                            'attempt_id':str(uuid.uuid4()),'started':time.time(),
                            'submitted':False,'retry_of':result['attempt_id'],'round':state['round']+1,
                            'clock':{'seconds':0.0,'running_since':None,'used':False}}
                        st.rerun()
                if state['submitted'] and e.get('source_explanation_verbatim'):
                    with st.expander('Tóm tắt cấu trúc nguyên văn trong PDF'):
                        st.text(plain_explanation(e['source_explanation_verbatim']))
                if state['submitted'] and e.get('source_caveats'):
                    with st.expander('Ghi chú kiểm tra — không thay đổi câu mẫu'):
                        for note in e['source_caveats']:
                            st.write(plain_explanation(note))

