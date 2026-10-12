import time
import uuid
import streamlit as st
from core.learning_tasks import ROLES, sentence_cards, shuffled, cloze, overview_choices, reverse_task
from core.review_schedule import now, reviews_from_attempts
from ui.state import emit, records

MODES=['Ghép nối khung bài','Điền từ nối & cấu trúc','Dịch ngược · 3 cách viết','Luyện từng bước','Flashcard · Ôn ngắt quãng','Viết & học thuộc']


def readable_answer(value):
    if isinstance(value,dict):
        for k,v in value.items():
            st.markdown('**'+str(k)+'**'); readable_answer(v)
    elif isinstance(value,(list,tuple)):
        for x in value: readable_answer(x)
    else: st.write(str(value))


def state_for(e,task):
    key='learn:'+e['exercise_id']+':'+task
    if key not in st.session_state:
        st.session_state[key]={'id':str(uuid.uuid4()),'started':time.time(),'result':None,'retry_of':None}
    return key,st.session_state[key]


def save(e,task,state,answer,reference,score=None,maximum=None,kind='open'):
    event=dict(attempt_id=state['id'],learner_id=st.session_state.settings['learner_id'],exercise_id=e['exercise_id'],task_id=task,content_version=e['content_version'],submitted_at=now().isoformat(),answer=answer,reference_snapshot=reference,score=score,max_score=maximum,grading_type=kind,outcome='self_review' if score is None else ('correct' if score==maximum else 'incorrect'),duration_seconds=round(time.time()-state['started']),retry_of=state['retry_of'])
    emit('attempt',event,event_id=state['id']);state['result']=event


def result_panel(key,state,explanation=''):
    result=state['result']
    if not result:return False
    if result['score'] is not None:st.metric('Điểm luyện tập',f"{result['score']}/{result['max_score']}")
    st.markdown('**Bài đã nộp**');readable_answer(result['answer'])
    st.markdown('**Đáp án / bài tham khảo**');readable_answer(result['reference_snapshot'])
    if explanation:st.info(explanation)
    if st.button('Làm lại',key=key+'retry'):
        st.session_state[key]={'id':str(uuid.uuid4()),'started':time.time(),'result':None,'retry_of':result['attempt_id']};st.rerun()
    return True


def learning_panel(e,structures):
    mode=st.selectbox('Dạng luyện tập',MODES,key='learning_mode')
    if mode==MODES[0]:outline(e)
    elif mode==MODES[1]:fill(e)
    elif mode==MODES[2]:reverse(e)
    elif mode==MODES[3]:micro(e,structures)
    elif mode==MODES[4]:flashcards(e,structures)
    else:
        from ui.practice import answer_panel
        answer_panel(e,structures,e['exercise_id'])


def outline(e):
    from streamlit_sortables import sort_items
    kind=st.radio('Bài ghép nối',['Sắp xếp câu','Phân loại câu'])
    task='outline-'+('order' if kind=='Sắp xếp câu' else 'category')
    key,state=state_for(e,task)
    cards=sentence_cards(e)
    labels={c['id']:c['id']+' · '+c['text'] for c in cards}
    expected=[labels[c['id']] for c in cards]
    st.caption('Kéo thẻ hoặc chọn cách nhập bằng bàn phím. Chấm theo thứ tự/vị trí trong bài mẫu; một cách sắp xếp khác vẫn có thể hợp lý.')
    if result_panel(key,state,e['outline_vi']):return
    accessible=st.checkbox('Dùng bàn phím thay kéo-thả',key=key+'access')
    mixed=shuffled(expected,e['exercise_id'])
    style='.sortable-item {white-space:normal; height:auto; padding:12px; font-size:15px;} .sortable-container {background:#f1f7f7;}'
    if kind=='Sắp xếp câu':
        if accessible:
            for item in mixed:st.write(item)
            typed=st.text_input('Nhập mã câu theo thứ tự, cách nhau bằng dấu phẩy',key=key+'typed')
            answer=[labels.get(x.strip(),x.strip()) for x in typed.split(',') if x.strip()]
        else:answer=sort_items(mixed,direction='vertical',custom_style=style,key=state['id'])
        if st.button('Kiểm tra thứ tự',key=key+'submit'):
            if sorted(answer)!=sorted(expected):st.warning('Cần dùng mỗi câu đúng một lần.');return
            save(e,task,state,answer,expected,sum(a==b for a,b in zip(answer,expected)),len(expected),'quiz');st.rerun()
    else:
        headers=list(ROLES.values())
        if accessible:
            answer={h:[] for h in headers}
            for item in mixed:
                dest=st.selectbox(item,['Chưa xếp']+headers,key=key+item[:3])
                if dest!='Chưa xếp':answer[dest].append(item)
        else:
            bins=sort_items([{'header':'Chưa xếp','items':mixed}]+[{'header':h,'items':[]} for h in headers],multi_containers=True,direction='vertical',custom_style=style,key=state['id'])
            answer={b['header']:b['items'] for b in bins if b['header']!='Chưa xếp'}
        reference={h:[labels[c['id']] for c in cards if ROLES[c['role']]==h] for h in headers}
        if st.button('Kiểm tra phân loại',key=key+'submit'):
            if sorted(x for v in answer.values() for x in v)!=sorted(expected):st.warning('Xếp đủ các câu vào bốn nhóm.');return
            score=sum(x in reference[h] for h,items in answer.items() for x in items)
            save(e,task,state,answer,reference,score,len(cards),'quiz');st.rerun()
    st.caption('Body 1/2 theo dàn ý của đề; một câu có thể vừa nêu xu hướng vừa so sánh, nên không ép vào hai chức năng loại trừ nhau.')


def fill(e):
    kind=st.radio('Cách điền',['Chọn cụm từ','Gõ chính xác'])
    task='cloze-'+kind;key,state=state_for(e,task)
    paragraphs,blanks=cloze(e)
    if result_panel(key,state,'Chấm khớp cụm từ của mẫu, bỏ qua hoa/thường và khoảng trắng. Cụm khác có thể đúng tiếng Anh nhưng không phải mẫu đang học.'):return
    for role,text in paragraphs:st.markdown('**'+role+'**');st.write(text)
    answers=[]
    with st.form(key+state['id']):
        for i,b in enumerate(blanks,1):
            st.caption(f"{i}. {b['hint']}")
            if kind=='Chọn cụm từ':
                options=shuffled(list(dict.fromkeys([b['answer'],'because of','in contrast','as a result'])),str(i)+e['exercise_id'])
                answers.append(st.selectbox(f'Ô {i}',['— Chọn —']+options))
            else:answers.append(st.text_input(f'Ô {i}'))
        submit=st.form_submit_button('Kiểm tra điền từ')
    if submit:
        if any(not a.strip() or a=='— Chọn —' for a in answers):st.warning('Điền đủ các ô trước khi kiểm tra.');return
        score=sum(' '.join(a.casefold().split())==' '.join(b['answer'].casefold().split()) for a,b in zip(answers,blanks))
        ref=[f"Ô {i}: {b['answer']} — {b['hint']}" for i,b in enumerate(blanks,1)]
        save(e,task,state,answers,ref,score,len(blanks),'quiz');st.rerun()


def reverse(e):
    task='reverse-three';key,state=state_for(e,task);item=reverse_task(e)
    st.info(item['vi']);st.caption(item['note'])
    if result_panel(key,state,'Đối chiếu cấu trúc, nghĩa, thì và thể. Không chấm câu mở bằng so chuỗi hoặc quy đổi band.'):return
    with st.form(key+state['id']):
        answers=[st.text_area(f'Cách {i}: {form}',max_chars=3000) for i,form in enumerate(item['forms'],1)]
        submit=st.form_submit_button('Lưu và đối chiếu 3 cách viết')
    if submit:
        if not all(a.strip() for a in answers):st.warning('Viết đủ ba cách.');return
        save(e,task,state,answers,item['answers']);st.rerun()


def micro(e,structures):
    progress_key='micro-step:'+e['exercise_id']
    step=st.session_state.get(progress_key,0)
    titles=['1. Paraphrase mở bài · 2 phút','2. Chọn ý overview · 3 phút','3. Gom nhóm thông tin · 3 phút','4. Viết đoạn · 10 phút']
    st.subheader(titles[step]);st.progress(step/4)
    st.caption('Thời lượng gợi ý; không khóa bài khi hết giờ. Mỗi bước được lưu riêng.')
    task='micro-'+str(step);key,state=state_for(e,task)
    if not result_panel(key,state,e['outline_vi'] if step==2 else ''):
        if step in (0,3):
            from ui.structure_hints import memory_hints
            memory_hints(e,structures,'introduction' if step==0 else 'body1')
            with st.form(key+state['id']):
                if step==0:answer=st.text_area('Viết introduction',max_chars=5000)
                else:answer={p:st.text_area(ROLES[p],max_chars=10000) for p in ('overview','body1','body2')}
                submit=st.form_submit_button('Lưu bước này')
            if submit:
                if not (answer.strip() if isinstance(answer,str) else all(v.strip() for v in answer.values())):st.warning('Điền đủ nội dung.');return
                ref=e['paragraphs']['introduction'] if step==0 else {ROLES[p]:e['paragraphs'][p] for p in answer}
                save(e,task,state,answer,ref);st.rerun()
        elif step==1:
            correct,options=overview_choices(e)
            st.write(f'Chọn {len(correct)} ý nổi bật được nêu trong overview của bài mẫu.')
            answer=st.multiselect('Ý chính',options,key=key+'selection')
            if st.button('Kiểm tra ý chính',key=key+'submit'):
                if len(answer)!=len(correct):st.warning(f'Chọn đúng {len(correct)} ý.');return
                save(e,task,state,answer,correct,int(set(answer)==set(correct)),1,'quiz');st.rerun()
        else:
            cards=[c for c in sentence_cards(e) if c['role'].startswith('body')]
            st.caption('Chia các thẻ thông tin vào hai body theo dàn ý mẫu. Có thể có cách chia khác hợp lý.')
            answer={}
            for c in shuffled(cards,e['exercise_id']):
                answer[c['text']]=st.radio(c['text'],['Chưa xếp','Body 1','Body 2'],horizontal=True,key=key+c['id'])
            if st.button('Kiểm tra gom nhóm',key=key+'submit'):
                if 'Chưa xếp' in answer.values():st.warning('Gom đủ thông tin trước khi kiểm tra.');return
                ref={c['text']:ROLES[c['role']] for c in cards}
                save(e,task,state,answer,ref,sum(answer[t]==v for t,v in ref.items()),len(ref),'quiz');st.rerun()
    a,b=st.columns(2)
    if a.button('Bước trước',disabled=step==0,key=key+'back'):
        st.session_state[progress_key]=step-1;st.rerun()
    if b.button('Bước tiếp theo',disabled=not state['result'] or step==3,key=key+'next'):
        st.session_state[progress_key]=step+1;st.rerun()
    if step==3 and state['result']:st.success('Đã hoàn thành 4 bước. Có thể chuyển sang Viết & học thuộc để viết cả bài.')


def flashcards(e,structures):
    cards=[s for s in structures if e['category'] in s['categories']]
    reviews=reviews_from_attempts(records('attempt'))
    only_due=st.checkbox('Chỉ thẻ mới hoặc đến hạn',value=True)
    def review(s):return reviews.get(e['exercise_id']+':flash-'+s['structure_id'])
    if only_due:cards=[s for s in cards if not review(s) or review(s)['next_review_date']<=now().date().isoformat()]
    if not cards:st.success('Chưa có thẻ đến hạn. Bỏ lọc để ôn thêm.');return
    card=st.selectbox('Thẻ cấu trúc',cards,format_func=lambda s:s['title'])
    task='flash-'+card['structure_id'];key,state=state_for(e,task)
    old=review(card)
    if old:st.caption('Lần ôn tiếp theo: '+old['next_review_date'])
    st.info(card['explanation_vi']);st.caption(card['usage_conditions'])
    if state['result']:
        result_panel(key,state,'Lịch 1–3–7–14 ngày dựa trên tự đánh giá, không phải điểm chấm tự động.');return
    if st.button('Lật thẻ',key=key+'flip'):st.session_state[key+'flipped'+state['id']]=True
    if st.session_state.get(key+'flipped'+state['id']):
        st.write(card['template']);readable_answer(card['examples'])
        st.caption('Ví dụ của cấu trúc; không mặc định là dữ kiện của ảnh bên trái.')
        for label,passed in [('Cần ôn lại',False),('Đã nhớ',True)]:
            if st.button(label,key=key+label):
                save(e,task,state,label,card['template'],int(passed),1,'flashcard');st.rerun()
