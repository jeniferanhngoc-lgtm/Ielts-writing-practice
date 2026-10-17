"""Five offline learning modes with append-only progress."""
import json
import time
import uuid
import streamlit as st
from core.content_validation import ROOT, full_model
from core.grading import normalize, word_count
from core.learning import (ROLES, sentence_cards, shuffled, grade_order, grade_categories,
                          cloze_model, grade_cloze, overview_task, grouping_task,
                          grouping_grade, reverse_task, flashcards)
from core.review_schedule import now, reviews_from_attempts
from ui.state import emit, records
from ui.readable import show_answer
from ui.drag_component import drag_board

MODES = ['Ghép khung & kéo-thả','Điền khung cấu trúc','Dịch ngược — 3 cách',
         'Quy trình 4 bước','Flashcard & ôn lại']


def task_state(e, task_id):
    key=f"learn:{e['exercise_id']}:{e['content_version']}:{task_id}"
    if key not in st.session_state:
        st.session_state[key]={'attempt_id':str(uuid.uuid4()),'started':time.time(),
                               'submitted':False,'retry_of':None,'round':0}
    return key,st.session_state[key]


def submit(e, task_id, state, answer, reference, score=None, maximum=None,
           grading_type='open', **extra):
    ident=state['attempt_id']
    result=dict(attempt_id=ident,learner_id=st.session_state.settings['learner_id'],
                exercise_id=e['exercise_id'],task_id=task_id,
                content_version=e['content_version'],submitted_at=now().isoformat(),
                answer=answer,reference_snapshot=reference,
                duration_seconds=round(time.time()-state['started']),
                duration_basis='Thời gian mở bài đến nộp; có thể gồm thời gian rời trang.',
                retry_of=state['retry_of'],score=score,max_score=maximum,
                grading_type=grading_type,**extra)
    emit('attempt',result,event_id=ident)
    state.update(submitted=True,result=result)
    st.rerun()


def result_header(state, objective=False):
    if objective:
        r=state['result']
        st.metric('Điểm luyện tập',f"{r['score']}/{r['max_score']}")
    else:
        st.info('Đã ghi nhận. Đối chiếu mẫu; cách diễn đạt khác vẫn có thể đúng.')
    st.caption('Trạng thái lưu lâu dài ở cuối trang. Điểm luyện tập không phải band IELTS.')


def retry(key,state,label='Làm lại bài này'):
    if st.button(label,key=key+'retry'):
        st.session_state[key]={'attempt_id':str(uuid.uuid4()),'started':time.time(),
                              'submitted':False,'retry_of':state['attempt_id'],
                              'round':state['round']+1}
        st.rerun()


def learning_panel(e, structures, mode):
    # Supplemental editorial metadata is separate from the original corpus.
    metadata=json.loads((ROOT/'content/learning_tasks.json').read_text(encoding='utf-8'))
    e=dict(e,learning_tasks=e.get('learning_tasks',metadata.get(e['exercise_id'],{})),
           content_version=str(e['content_version'])+'+learning-v1')
    if mode==MODES[0]: outline_panel(e)
    elif mode==MODES[1]: cloze_panel(e)
    elif mode==MODES[2]: reverse_panel(e)
    elif mode==MODES[3]: micro_panel(e)
    else: flash_panel(structures)


def outline_panel(e):
    choice=st.radio('Bài ghép khung',['Sắp xếp câu','Phân loại câu'],horizontal=True,key=e['exercise_id']+'outline-kind')
    task='outline-order' if choice=='Sắp xếp câu' else 'outline-category'
    cards=sentence_cards(e)
    functions=False
    annotations=None
    if choice=='Phân loại câu':
        subtype=st.radio('Cách phân loại',['Vị trí đoạn','Chức năng câu'],key=e['exercise_id']+'category-subtype')
        if subtype=='Chức năng câu':
            annotations=e['learning_tasks'].get('sentence_functions')
            if not annotations:
                st.info('Phân loại theo chức năng: tự đối chiếu ở đề này. Không tự chấm vì một câu có thể vừa tả xu hướng vừa so sánh. Đề q014 có nhãn chức năng đã biên tập để chấm.')
            functions=True;task+='-function'
            if annotations:
                for card in cards:
                    card['accepted_functions']=annotations[card['id']]
    key,state=task_state(e,task)
    labels=dict(ROLES)
    if functions:
        labels={'introduction':ROLES['introduction'],'overview':ROLES['overview'],
                'trend':'Thân bài — miêu tả xu hướng','comparison':'Thân bài — so sánh cao/thấp, mức độ',
                'both':'Thân bài — vừa xu hướng vừa so sánh',
                'other':'Thân bài — vị trí / bước / đặc điểm khác'}
        st.caption('Một câu có thể làm hai việc. Đáp án chấp nhận các chức năng đã biên tập.')
    if state['submitted']:
        result_header(state,state['result']['score'] is not None)
        if choice=='Sắp xếp câu':
            st.caption('Thứ tự mẫu để học liên kết câu, không phải thứ tự duy nhất đúng cho mọi bài.')
            for card in cards:
                st.write(f"{ROLES[card['role']]}: {card['text']}")
        else:
            rows=[]
            for card in cards:
                given=state['result']['answer'][card['id']]
                if functions and not annotations:
                    rows.append({'Câu':card['text'],'Bạn chọn':labels.get(given,given),
                                 'Vị trí trong mẫu':ROLES[card['role']],
                                 'Gợi ý tự kiểm tra':'Xu hướng: biến động theo thời gian; so sánh: mức cao/thấp/chênh lệch; câu có thể có cả hai.'})
                    continue
                targets=card.get('accepted_functions',[card['role']]) if functions else [card['role']]
                rows.append({'Câu':card['text'],'Bạn chọn':labels.get(given,given),
                             'Đáp án': ' / '.join(labels[x] for x in targets),'Khớp':given in targets})
            st.dataframe(rows,hide_index=True,width='stretch')
        retry(key,state);return
    items=shuffled(cards,e['exercise_id']+task+str(state['round']))
    interface=st.radio('Cách thao tác',['Kéo-thả','Chọn bằng ô nhập'],horizontal=True,key=key+'interface')
    widget_key=key+str(state['round'])
    if choice=='Sắp xếp câu':
        st.caption('Xếp lại đúng thứ tự bài mẫu đã biên tập. Câu cùng chức năng có thể có thứ tự hợp lý khác; điểm ở đây chỉ đo khớp mẫu.')
        initial=state.get('board',[c['id'] for c in items])
        if interface=='Kéo-thả':
            answer=drag_board(items,[],initial,widget_key,'order')
            state['board']=answer
        else:
            selected=st.multiselect('Chọn các câu theo thứ tự từ đầu đến cuối',
                                    initial,format_func=lambda ident:next(c['text'] for c in cards if c['id']==ident),
                                    key=widget_key+'fallback')
            answer=selected
        reference=[c['text'] for c in cards]
    else:
        initial=state.get('board',{c['id']:'unassigned' for c in items})
        boxes=[{'id':'unassigned','label':'Chưa phân loại'}]+[{'id':k,'label':v} for k,v in labels.items()]
        if interface=='Kéo-thả':
            answer=drag_board(items,boxes,initial,widget_key,'category')
            state['board']=answer
        else:
            answer={c['id']:st.selectbox(c['text'],['unassigned']+list(labels),
                        format_func=lambda x:'Chưa phân loại' if x=='unassigned' else labels[x],
                        key=widget_key+c['id']) for c in items}
        reference={c['text']: (ROLES[c['role']] if functions and not annotations else
                   ' / '.join(labels[x] for x in (c.get('accepted_functions',[c['role']]) if functions else [c['role']]))) for c in cards}
    if st.button('Chấm bài ghép khung',type='primary',key=widget_key+'submit'):
        if not isinstance(answer,(list,dict)) or (isinstance(answer,dict) and 'unassigned' in answer.values()):
            st.warning('Hãy phân loại đủ tất cả câu.');return
        if functions and not annotations:
            submit(e,task,state,answer,reference)
            return
        try:
            score,maximum=grade_order(cards,answer) if choice=='Sắp xếp câu' else grade_categories(cards,answer,functions)
        except ValueError as exc:
            st.warning(str(exc));return
        submit(e,task,state,answer,reference,score,maximum,'quiz')


def cloze_panel(e):
    style=st.radio('Cách điền',['Chọn cụm từ','Gõ cụm từ'],horizontal=True,key=e['exercise_id']+'cloze-style')
    paragraphs,blanks=cloze_model(e)
    key,state=task_state(e,'cloze-'+('dropdown' if style=='Chọn cụm từ' else 'input'))
    st.caption('Điền cụm từ đúng theo bài mẫu. Đây là bài nhớ mẫu, không đánh giá mọi cách viết tương đương. Không phân biệt hoa/thường; giữ đúng từ và dấu câu trong cụm.')
    for role,text in paragraphs.items():
        st.markdown('**'+ROLES[role]+'**');st.write(text)
    if state['submitted']:
        result_header(state,True)
        for blank in blanks:
            given=state['result']['answer'].get(blank['id'],'')
            matched=normalize(given)==normalize(blank['answer'])
            st.write(f"Ô {blank['id']}: {'✓' if matched else 'Cần ôn'} — Bạn điền: {given} → Mẫu: {blank['answer']}")
            st.caption(blank['hint'])
        retry(key,state);return
    answers={}
    with st.form(key+str(state['round'])):
        for blank in blanks:
            label=f"Ô {blank['id']} — {blank['hint']}"
            if style=='Chọn cụm từ':
                answers[blank['id']]=st.selectbox(label,blank['options'],index=None,key=key+str(state['round'])+blank['id'])
            else:
                answers[blank['id']]=st.text_input(label,key=key+str(state['round'])+blank['id'])
        send=st.form_submit_button('Chấm bài điền khung',type='primary')
    if send:
        if not all(answers.values()):
            st.warning('Điền đủ các ô trước khi nộp.');return
        score,maximum=grade_cloze(blanks,answers)
        submit(e,'cloze-'+('dropdown' if style=='Chọn cụm từ' else 'input'),state,answers,
               {b['id']:b['answer'] for b in blanks},score,maximum,'memory')


def fallback_reverse(e):
    # Transparent supplementary exercises, not inferred facts from the chosen image.
    if e['category']=='maps':
        return dict(source='Bài bổ sung tự tạo; sơ đồ dưới đây độc lập với ảnh đề bên trái.',
          prompt_vi='Đất nông nghiệp đã được thay bằng một sân chơi.',
          mini=[{'Trước':'Farmland','Sau':'Playground'}],
          forms=['A + was replaced by + B','A + was converted into + B','B + was built, replacing + A'],
          answers=['The farmland was replaced by a playground.','The farmland was converted into a playground.',
                   'A playground was built, replacing the farmland.'])
    if e['category']=='natural_process':
        return dict(source='Bài bổ sung tự tạo; quá trình dưới đây độc lập với ảnh đề bên trái.',
          prompt_vi='Nước bốc hơi trước khi ngưng tụ thành những giọt nước.',
          mini=[{'Bước 1':'Water evaporates','Bước 2':'Water vapour condenses into droplets'}],
          forms=['S + V, after which …','After + S + V, …','S + V + before V-ing'],
          answers=['Water evaporates, after which the water vapour condenses into droplets.',
                   'After water evaporates, the water vapour condenses into droplets.',
                   'Water evaporates before condensing into droplets.'])
    if e['category']=='process':
        return dict(source='Bài bổ sung tự tạo; quy trình dưới đây độc lập với ảnh đề bên trái.',
          prompt_vi='Hạt được sấy khô trước khi được rang.',
          mini=[{'Bước 1':'Drying the beans','Bước 2':'Roasting the beans'}],
          forms=['S + passive, after which …','After + S + passive, …','S + passive + before V-ing'],
          answers=['The beans are dried, after which they are roasted.',
                   'After the beans are dried, they are roasted.',
                   'The beans are dried before being roasted.'])
    if e['category']=='future':
        return dict(source='Bài bổ sung tự tạo; dự báo dưới đây độc lập với ảnh đề bên trái.',
          prompt_vi='Tỷ lệ người sống ở đô thị được dự báo sẽ đạt 60% vào năm 2030.',
          mini=[{'Năm':'2030','Tỷ lệ':'60%','Tình trạng':'Dự báo'}],
          forms=['S + is projected to …','S + is expected to …','There is a projection that …'],
          answers=['The proportion of people living in cities is projected to reach 60% in 2030.',
                   'The proportion of people living in cities is expected to reach 60% in 2030.',
                   'There is a projection that 60% of people will live in cities in 2030.'])
    if e['category']=='static':
        return dict(source='Bài bổ sung tự tạo; bảng dưới đây độc lập với ảnh đề bên trái.',
          prompt_vi='Mức tiêu thụ dầu ở A là 70 triệu tấn, gấp đôi mức ở B (35 triệu tấn).',
          mini=[{'Quốc gia':'A','Triệu tấn':70},{'Quốc gia':'B','Triệu tấn':35}],
          forms=['S + was double that of …','S + consumed twice as much … as …','Data …, compared with …'],
          answers=['Oil consumption in A was double that of B, at 70 and 35 million tonnes respectively.',
                   'A consumed twice as much oil as B, at 70 and 35 million tonnes respectively.',
                   'A consumed 70 million tonnes of oil, compared with 35 million tonnes in B.'])
    if e['category']=='mechanism':
        return dict(source='Bài bổ sung tự tạo; vị trí dưới đây độc lập với ảnh đề bên trái.',
          prompt_vi='Đầu đốt nằm phía trên giỏ của khí cầu.',
          mini=[{'Trên':'Burner','Dưới':'Basket'}],
          forms=['S + is located above …','S + is positioned above …','Below + A + is + B'],
          answers=['The burner is located above the basket of the balloon.',
                   'The burner is positioned above the basket of the balloon.',
                   'Below the burner is the basket of the balloon.'])
    return dict(source='Bài bổ sung tự tạo; số liệu dưới đây độc lập với ảnh đề bên trái.',
      prompt_vi='Số khách du lịch giảm mạnh từ 100,000 năm 2019 xuống 40,000 năm 2020.',
      chart=[{'Năm':'2019','Khách du lịch':100000},{'Năm':'2020','Khách du lịch':40000}],
      forms=['S + V + Adv + from … to …','There was + a + Adj + N + in …','S + saw + a + Adj + N'],
      answers=['The number of tourists fell sharply from 100,000 in 2019 to 40,000 in 2020.',
               'There was a sharp fall in the number of tourists, from 100,000 in 2019 to 40,000 in 2020.',
               'The number of tourists saw a sharp fall from 100,000 in 2019 to 40,000 in 2020.'])


def reverse_panel(e):
    task=reverse_task(e) or fallback_reverse(e)
    st.caption(task['source'])
    if task.get('mini'): st.table(task['mini'])
    if task.get('chart'): st.line_chart(task['chart'],x='Năm',y='Khách du lịch')
    st.info(task['prompt_vi'])
    key,state=task_state(e,'reverse-3-forms')
    st.caption('Viết cùng một ý bằng ba khung. Không tự chấm ngữ pháp; mẫu chỉ hiện sau khi bạn nộp.')
    if state['submitted']:
        result_header(state)
        for i,(form,reference) in enumerate(zip(task['forms'],task['answers'])):
            st.markdown(f'**Cách {i+1} — {form}**')
            st.write('Bạn viết: '+state['result']['answer'][str(i+1)])
            st.success(reference)
        retry(key,state);return
    with st.form(key+str(state['round'])):
        answers={str(i+1):st.text_area(f'Cách {i+1}: {form}',height=80,max_chars=2000,
                    key=key+str(state['round'])+str(i)) for i,form in enumerate(task['forms'])}
        send=st.form_submit_button('Nộp 3 câu và đối chiếu mẫu',type='primary')
    if send:
        if not all(x.strip() for x in answers.values()):
            st.warning('Viết đủ ba câu trước khi xem mẫu.');return
        submit(e,'reverse-3-forms',state,answers,
               {f'Cách {i+1}':answer for i,answer in enumerate(task['answers'])},
               task_context={'prompt_vi':task['prompt_vi'],'source':task['source'],
                             'forms':task['forms'],'mini':task.get('mini',task.get('chart',[]))})


def micro_panel(e):
    flow_key=f"micro-flow:{e['exercise_id']}:{e['content_version']}"
    flow=st.session_state.setdefault(flow_key,{'step':1})
    titles={1:'Paraphrase mở bài · 2 phút',2:'Chọn 2 ý overview · 3 phút',
            3:'Gom nhóm dữ liệu · 3 phút',4:'Viết đoạn · 10 phút'}
    step=flow['step']
    st.progress((step-1)/4,text=f'Bước {step}/4 — {titles[step]}')
    st.caption('Thời gian là mục tiêu gợi ý. Chỉ chuyển bước sau khi nộp; dùng nút về bước trước để xem hoặc làm lại.')
    key,state=task_state(e,'micro-'+str(step))
    if state['submitted']:
        result_header(state,state['result']['score'] is not None)
        st.markdown('**Mẫu / dàn ý để đối chiếu**')
        show_answer(state['result']['reference_snapshot'])
        if step==3: st.caption('Gom nhóm có thể có cách khác hợp lý; không ép mọi đề vào cùng một cách chia.')
        retry(key,state,'Làm lại bước này')
        if step<4 and st.button('Sang bước tiếp theo',type='primary',key=key+'next'):
            flow['step']+=1;st.rerun()
        elif step==4:
            st.success('Đã hoàn thành 4 bước của đề này.')
            if st.button('Bắt đầu lượt 4 bước mới',key=key+'restart'):
                # Preserve attempts; new widgets and new attempts for every step.
                for n in range(1,5):
                    sk,old=task_state(e,'micro-'+str(n))
                    st.session_state[sk]={'attempt_id':str(uuid.uuid4()),'started':time.time(),
                      'submitted':False,'retry_of':old['attempt_id'],'round':old['round']+1}
                flow['step']=1;st.rerun()
    else:
        with st.form(key+str(state['round'])):
            if step==1:
                st.write(e['prompt'])
                answer=st.text_area('Câu mở bài của bạn',max_chars=3000)
                reference=e['paragraphs']['introduction']
            elif step==2:
                overview=overview_task(e)
                if overview:
                    answer=st.multiselect('Chọn đúng 2 nhận xét nổi bật',overview['options'])
                    reference=overview['accepted_answers']
                else:
                    st.caption('Đề chưa có bộ lựa chọn hai ý; viết hai nhận xét để tự đối chiếu.')
                    answer=st.text_area('Hai ý overview của bạn',max_chars=3000)
                    reference=e['paragraphs']['overview']
            elif step==3:
                grouping=grouping_task(e)
                if grouping:
                    st.caption(grouping.get('instruction','Chọn Body 1 hoặc Body 2 cho từng mục.'))
                    answer={item:st.selectbox(item,['Chưa chọn','body1','body2'],
                              format_func=lambda x:ROLES.get(x,x),key=key+str(state['round'])+item)
                            for item in grouping['items']}
                else:
                    # All memberships are open until an editor approves alternatives.
                    data=e.get('data',{});years=data.get('years',[])
                    items=[k for k,v in data.items() if isinstance(v,list) and k!='years'
                           and years and len(v)==len(years)]
                    st.caption('Chưa có đáp án gom nhóm đóng đã biên tập cho đề này. Tự chia nhóm rồi đối chiếu dàn ý; không tính điểm.')
                    if items:
                        answer={item:st.selectbox(item,['Chưa chọn','body1','body2','both'],
                                  format_func=lambda x:{**ROLES,'both':'Cả hai body (chia theo thời gian)'}.get(x,x),
                                  key=key+str(state['round'])+item) for item in items}
                    else:
                        answer=st.text_area('Nhóm thông tin / giai đoạn cho Body 1 và Body 2',max_chars=4000)
                reference=e['outline_vi']
            else:
                intro=task_state(e,'micro-1')[1].get('result',{}).get('answer','')
                st.caption('Mở bài bạn đã viết: '+str(intro))
                answer={part:st.text_area(ROLES[part],height=130,max_chars=10000,
                             key=key+str(state['round'])+part) for part in ['overview','body1','body2']}
                reference={ROLES[part]:e['paragraphs'][part] for part in answer}
            send=st.form_submit_button('Nộp bước '+str(step),type='primary')
        if send:
            valid=all(x and str(x).strip() and x!='Chưa chọn' for x in answer.values()) if isinstance(answer,dict) else bool(answer and (not isinstance(answer,str) or answer.strip()))
            if not valid:
                st.warning('Hoàn thành phần này trước khi nộp.');return
            score=maximum=None;kind='open'
            if step==2 and overview:
                if len(answer)!=2:
                    st.warning('Chọn đúng hai ý.');return
                score=int(set(answer)==set(reference));maximum=1;kind='quiz'
            elif step==3 and grouping:
                score,maximum=grouping_grade(grouping,answer);kind='quiz'
                reference=[{ROLES[role]:', '.join(item for item,value in variant.items() if value==role)
                            for role in ('body1','body2')} for variant in grouping['accepted_assignments']]
            submit(e,'micro-'+str(step),state,answer,reference,score,maximum,kind)
    if step>1 and st.button('Về bước trước',key=key+'back'):
        flow['step']-=1;st.rerun()


def flash_panel(structures):
    cards=flashcards(structures)
    reviews=reviews_from_attempts(records('attempt'))
    only_due=st.checkbox('Chỉ thẻ đến hạn hoặc chưa học',key='flash-only-due')
    today=now().date().isoformat()
    pool=[c for c in cards if not only_due or reviews.get('flashcards:flash-'+c['id'],{}).get('next_review_date',today)<=today]
    if not pool:
        st.success('Bạn đã ôn hết thẻ đến hạn. Tắt bộ lọc nếu muốn học thêm.');return
    ident=st.selectbox('Chọn flashcard',[c['id'] for c in pool],
                      format_func=lambda x:next(c['front'] for c in pool if c['id']==x),key='flash-card-select')
    card=next(c for c in cards if c['id']==ident)
    pseudo={'exercise_id':'flashcards','content_version':'flash-v1'}
    key,state=task_state(pseudo,'flash-'+ident)
    review=reviews.get('flashcards:flash-'+ident)
    if review: st.caption('Lần ôn tiếp: '+review['next_review_date']+' · Lịch dựa trên tự đánh giá.')
    st.markdown('**Mặt trước**');st.info(card['front'])
    if state['submitted']:
        st.success('Đã lưu tự đánh giá và cập nhật lịch ôn.')
        st.write(card['back']);st.caption(card['note'])
        retry(key,state,'Ôn lại thẻ này');return
    shown=st.session_state.get(key+'shown-'+str(state['round']),False)
    if not shown:
        st.caption('Nhẩm hoặc viết ra giấy trước khi lật thẻ.')
        if st.button('Lật thẻ — xem mặt sau',key=key+'flip'+str(state['round'])):
            st.session_state[key+'shown-'+str(state['round'])]=True;st.rerun()
    else:
        st.markdown('**Mặt sau**');st.success(card['back'])
        st.write(card['example']);st.caption(card['note'])
        a,b=st.columns(2)
        for column,label,passed in [(a,'Cần ôn lại',False),(b,'Đã nhớ',True)]:
            if column.button(label,key=key+label+str(state['round'])):
                submit(pseudo,'flash-'+ident,state,label,card['back'],
                       grading_type='flashcard',self_assessed_passed=passed)

