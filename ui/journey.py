"""Learner-facing navigation, task cards and independent recall checks."""
import time
import uuid
from datetime import date, timedelta
import streamlit as st
from core.review_schedule import now, reviews_from_attempts
from core.content_validation import CATEGORIES, full_model
from core.grading import memory_grade
from ui.state import records, emit
from ui.core_framework import framework_panel, show_highlighted
from ui.readable import show_answer

PARTS={'introduction':'Introduction','overview':'Overview','body1':'Body 1','body2':'Body 2','full':'Cả bài'}


def navigate(page,**kwargs):
    st.session_state.route={'page':page,**kwargs}
    st.rerun()


def apply_route():
    route=st.session_state.pop('route',None)
    if not route:return
    st.session_state.page=route.pop('page')
    for k,v in route.items():st.session_state[k]=v


def task_name(task):
    if task=='overview-analysis':return 'Phân tích và viết overview'
    if task.startswith('flash-'):return 'Ôn flashcard'
    if task.startswith('structure-'):return 'Nhớ cấu trúc'
    if task.startswith('micro-'):return 'Luyện từng bước'
    for part,label in PARTS.items():
        if part in task:return 'Viết '+label
    if 'cloze' in task or 'fill' in task:return 'Điền cấu trúc'
    if 'outline' in task or 'order' in task:return 'Ghép khung bài'
    if 'reverse' in task:return 'Viết câu theo ba cách'
    return 'Ôn bài đã học'


def today(exercises,structures):
    st.title('Hôm nay bạn muốn học gì?')
    st.write('Học khung → tự nhớ → kiểm tra → ôn lại đúng lúc.')
    attempts=records('attempt'); day=now().date()
    days={date.fromisoformat(a['submitted_at'][:10]) for a in attempts}
    cursor=day if day in days else day-timedelta(days=1); streak=0
    while cursor in days:streak+=1;cursor-=timedelta(days=1)
    done=sum(a['submitted_at'][:10]==day.isoformat() for a in attempts)
    a,b,c=st.columns(3)
    a.metric('Chuỗi ngày có bài hoàn thành',f'{streak} ngày')
    b.metric('Lần hoàn thành hôm nay',done)
    c.metric('Kiểm tra độc lập hôm nay',sum(a.get('learning_mode')=='test' and a['submitted_at'][:10]==day.isoformat() for a in attempts))
    st.progress(min(done/5,1),text=f'{min(done,5)}/5 lượt · mục tiêu gợi ý hôm nay')
    a,b=st.columns(2)
    if a.button('Học bộ khung cốt lõi',type='primary',width='stretch'):navigate('Thư viện cấu trúc')
    if b.button('Bắt đầu kiểm tra',width='stretch'):navigate('Luyện tập',study_mode='Kiểm tra')
    st.subheader('Nhiệm vụ đến hạn ôn')
    byid={e['exercise_id']:e for e in exercises}
    due=[r for r in reviews_from_attempts(attempts).values() if r['next_review_date']<=day.isoformat()]
    if not due:st.info('Chưa có bài đến hạn. Học một khung mới hoặc làm kiểm tra đầu tiên bên trên.')
    for i,r in enumerate(due):
        e=byid.get(r['exercise_id'])
        with st.container(border=True):
            st.markdown('### '+(e['title'] if e else 'Thẻ cấu trúc'))
            st.write(task_name(r['task_id'])+' · '+('Cần ôn lại' if r['mastery_state']=='learning' else 'Đến hạn củng cố'))
            st.caption('Lịch ôn: '+r['next_review_date'])
            a,b=st.columns(2)
            part=next((p for p in PARTS if p in r['task_id']),'introduction')
            if a.button('Ôn tập có gợi ý',key=f'due-study-{i}'):
                if e:
                    from ui.learning_modes import MODES
                    task=r['task_id']
                    mode=MODES[0] if 'outline' in task else MODES[1] if 'cloze' in task else MODES[2] if 'reverse' in task else MODES[3] if 'micro' in task else 'Viết & học thuộc'
                    navigate('Luyện tập',study_mode='Ôn tập',practice_category='all',practice_exercise=e['exercise_id'],learning_mode=mode,memory_part=part,review_task=task,**{'practice-mode':'Quiz' if any(q['quiz_id']==task for q in e['quizzes']) else 'Học thuộc'})
                else:navigate('Thư viện cấu trúc',structure_lesson=(r['exercise_id'].split(':',1)[1],'study')) if r['exercise_id'].startswith('structure:') else navigate('Thư viện cấu trúc')
            if b.button('Kiểm tra ngay',key=f'due-test-{i}'):
                if e:navigate('Luyện tập',study_mode='Kiểm tra',practice_category='all',practice_exercise=e['exercise_id'],test_part=part)
                else:navigate('Thư viện cấu trúc',structure_lesson=(r['exercise_id'].split(':',1)[1],'test')) if r['exercise_id'].startswith('structure:') else navigate('Thư viện cấu trúc')
    st.subheader('Lộ trình ngắn để bắt đầu')
    for title,description in [('1 · Nắm khung','Introduction → Overview → hai body. Học ít cấu trúc, dùng lại nhiều lần.'),('2 · Luyện từng phần','Ghép câu, điền khung, dịch ngược hoặc quy trình bốn bước.'),('3 · Kiểm tra không gợi ý','Tự viết từ trí nhớ, đối chiếu mẫu màu cam rồi ôn lại.')]:
        with st.container(border=True):st.markdown('**'+title+'**');st.write(description)
    with st.expander('Đồng hồ buổi học'):
        from ui.screens import timer_panel
        timer_panel()
    st.caption('Ôn có gợi ý được lưu riêng và không dùng để tăng mức thành thạo. Flashcard dùng lịch tự đánh giá; kết quả cũ vẫn được giữ.')


def library(structures,exercises):
    st.title('Học cấu trúc · hiểu rồi tự nhớ')
    active=st.session_state.get('structure_lesson')
    if active:
        item=next((s for s in structures if s['structure_id']==active[0]),None)
        if item:
            if st.button('← Về thư viện'):
                del st.session_state.structure_lesson;st.rerun()
            st.subheader(item['title'])
            structure_lesson(item,active[1])
            return
    category=st.selectbox('Lọc dạng bài',['all']+list(CATEGORIES),format_func=lambda x:'Tất cả' if x=='all' else CATEGORIES[x])
    framework_panel(category)
    st.divider()
    st.subheader('Chọn cấu trúc để luyện')
    role=st.selectbox('Chức năng',['all','introduction','overview','body'])
    pool=[s for s in structures if (category=='all' or category in s['categories']) and (role=='all' or role==s['paragraph_role'])]
    pool.sort(key=lambda s:0 if s.get('curriculum') else 1)
    for s in pool:
        with st.container(border=True):
            st.markdown('### '+s['title'])
            show_highlighted(s['template'])
            st.write(s['explanation_vi']);st.caption(s['usage_conditions'])
            st.caption('Khung chuẩn đã chốt' if s.get('curriculum') else 'Khung nền / tham khảo bổ sung')
            st.markdown('**Ví dụ luyện**')
            for example in s['examples']:show_highlighted(example)
            a,b=st.columns(2)
            if a.button('Luyện cấu trúc này',key='study-'+s['structure_id']):
                st.session_state.structure_lesson=(s['structure_id'],'study');st.rerun()
            if b.button('Kiểm tra cấu trúc này',key='test-'+s['structure_id']):
                st.session_state.structure_lesson=(s['structure_id'],'test');st.rerun()
    lesson=st.session_state.get('structure_lesson')
    if lesson:
        s=next((s for s in structures if s['structure_id']==lesson[0]),None)
        if s:
            st.divider();st.subheader('Bài luyện · '+s['title'])
            structure_lesson(s,lesson[1])


def structure_lesson(s,mode):
    st.caption('Ôn có gợi ý' if mode=='study' else 'Kiểm tra nhớ mẫu · hãy tự nhớ câu ví dụ vừa học')
    if mode=='study':
        st.write(s['explanation_vi']);show_highlighted(s['template']);show_highlighted(s['examples'][0])
    else:
        st.write('Viết lại câu ví dụ đã học của cấu trúc này. Không mở tài liệu trong lúc làm.')
    key='structure:'+s['structure_id']+':'+mode
    state=st.session_state.setdefault(key,{'id':str(uuid.uuid4()),'start':time.time()})
    if 'result' not in state:
        with st.form(key+state['id']):
            answer=st.text_area('Gõ lại câu ví dụ từ trí nhớ',max_chars=5000)
            sent=st.form_submit_button('Nộp câu')
        if sent:
            if not answer.strip():st.warning('Hãy viết câu trước khi nộp.');return
            grade=memory_grade(answer,s['examples'][0],True,True)
            event=dict(attempt_id=state['id'],exercise_id='structure:'+s['structure_id'],task_id='structure-'+s['structure_id'],learner_id=st.session_state.settings['learner_id'],content_version='structure-v2',submitted_at=now().isoformat(),answer=answer,reference_snapshot=s['examples'][0],duration_seconds=round(time.time()-state['start']),learning_mode=mode,assisted=mode=='study',**grade)
            emit('attempt',event,event_id=state['id']);state['result']=event;st.rerun()
    else:
        st.metric('Điểm khớp mẫu',str(state['result']['score'])+'/100')
        show_answer(state['result']['answer']);show_answer(state['result']['reference_snapshot'])
        st.caption('Khác mẫu không đồng nghĩa sai ngữ pháp. Màu cam đánh dấu cụm cấu trúc.')
        if st.button('Luyện lại',key=key+'retry'):del st.session_state[key];st.rerun()


@st.fragment(run_every='1s')
def countdown(deadline):
    remaining=max(0,int(deadline-time.time()))
    st.metric('Thời gian còn lại',f'{remaining//60:02}:{remaining%60:02}')
    if not remaining:st.warning('Hết thời gian mục tiêu. Bản nháp được giữ; bạn vẫn có thể nộp và kết quả sẽ ghi quá giờ.')


def test_panel(e):
    st.subheader('Kiểm tra · tự viết từ trí nhớ')
    st.caption('Không hiện khung, dàn ý hoặc mẫu trước khi nộp. Điểm đo khớp mẫu đã học, không phải band hay điểm ngữ pháp.')
    part=st.selectbox('Phần kiểm tra',list(PARTS),format_func=PARTS.get,key='test_part')
    timed=st.checkbox('Giới hạn thời gian mục tiêu',key='timed-test')
    minutes=st.number_input('Số phút',1,60,20 if part=='full' else 3) if timed else None
    key='test:'+e['exercise_id']+':'+e['content_version']+':'+part
    state=st.session_state.get(key)
    if state is None:
        if st.button('Bắt đầu làm bài',type='primary'):
            st.session_state[key]={'id':str(uuid.uuid4()),'start':time.time(),'limit':minutes*60 if minutes else None};st.rerun()
        return
    if 'result' not in state:
        if state['limit']:countdown(state['start']+state['limit'])
        with st.form(key+state['id']):
            answer=st.text_area('Bài kiểm tra của bạn',height=280,max_chars=20000)
            checks=[]
            if part=='full':
                st.markdown('**Checklist trước khi nộp cả bài**')
                checks=[st.checkbox(line,key=state['id']+str(i)) for i,line in enumerate(e.get('checklist_vi') or ['Đã kiểm tra số liệu, overview và ngữ pháp.'])]
            sent=st.form_submit_button('Nộp bài kiểm tra',type='primary')
        if sent:
            if not answer.strip() or not all(checks):st.warning('Viết bài và tích đủ checklist (nếu làm cả bài) trước khi nộp.');return
            reference=full_model(e) if part=='full' else e['paragraphs'][part]
            grade=memory_grade(answer,reference,True,True);duration=round(time.time()-state['start'])
            event=dict(attempt_id=state['id'],learner_id=st.session_state.settings['learner_id'],exercise_id=e['exercise_id'],task_id='test-'+part,content_version=e['content_version'],submitted_at=now().isoformat(),answer=answer,reference_snapshot=reference,duration_seconds=duration,learning_mode='test',assisted=False,overtime=bool(state['limit'] and duration>state['limit']),**grade)
            emit('attempt',event,event_id=state['id']);state['result']=event;st.rerun()
    else:
        r=state['result'];st.metric('Điểm nhớ mẫu',str(r['score'])+'/100')
        a,b=st.columns(2)
        with a:st.markdown('**Bạn viết**');show_answer(r['answer'])
        with b:st.markdown('**Mẫu đối chiếu**');show_answer(r['reference_snapshot'])
        if r.get('changes'):st.dataframe(r['changes'],hide_index=True,width='stretch')
        st.info('Đã lưu kiểm tra và cập nhật lịch ôn. Khác mẫu chưa đủ để kết luận sai tiếng Anh.')
        if r.get('overtime'):st.caption('Bài nộp quá thời gian mục tiêu.')
        if st.button('Kiểm tra lại'):del st.session_state[key];st.rerun()
