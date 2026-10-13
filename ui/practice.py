import time
import uuid
import streamlit as st
from core.content_validation import CATEGORIES, ROOT, full_model
from core.grading import memory_grade, grade_quiz, word_count
from core.review_schedule import now
from ui.state import emit, records
from ui.core_framework import show_highlighted

LABELS={'introduction':'Introduction','overview':'Overview','body1':'Body 1','body2':'Body 2'}


def show_model(exercise, structures):
    st.caption('Màu cam + chữ đậm: cụm cấu trúc cần nhớ, không phải đánh dấu lỗi.')
    st.caption(f"Phiên bản nội dung: {exercise['content_version']} · Bài tham khảo biên soạn, không phải điểm giám khảo.")
    for part,text in exercise.get('paragraphs',{}).items():
        st.markdown(f'**{LABELS.get(part,part)}**')
        show_highlighted(text)
        st.caption(exercise.get('paragraph_notes',{}).get(part,''))
    st.caption(f"{word_count(full_model(exercise))} từ")
    with st.expander('Giải thích cách nối câu trong bài'):
        for item in exercise.get('sentence_notes',[]):
            show_highlighted(item['sentence'])
            st.caption(item['explanation_vi'])
    st.markdown('**Cấu trúc mục tiêu và cách dùng**')
    for item in structures:
        if item['structure_id'] in exercise['target_structure_ids']:
            st.info(item['template'])
            st.write(item['explanation_vi'])
            st.caption(item['usage_conditions'])


def practice(exercises,structures):
    st.title('Luyện tập')
    st.write('Hiểu mẫu → nhớ cấu trúc → đổi dữ liệu → tự viết.')
    purpose=st.radio('Chế độ học',['Ôn tập','Kiểm tra'],horizontal=True,key='study_mode')
    category=st.selectbox('Nhóm bài',['all']+list(CATEGORIES),format_func=lambda x:'Tất cả dạng bài' if x=='all' else CATEGORIES[x],key='practice_category')
    pool=[e for e in exercises if e['status']!='duplicate' and (category=='all' or e['category']==category)]
    search=st.text_input('Tìm đề theo tên hoặc mã')
    pool=[e for e in pool if search.casefold() in (e['title']+' '+e['exercise_id']).casefold()]
    if not pool:
        st.info('Không có đề phù hợp bộ lọc.'); return
    chosen=st.selectbox('Chọn đề',[e['exercise_id'] for e in pool],format_func=lambda x:next(f"{e['exercise_id']} · {e['title']} {'✓' if e['status']=='verified' else '— cần kiểm tra'}" for e in pool if e['exercise_id']==x),key='practice_exercise')
    e=next(x for x in pool if x['exercise_id']==chosen)
    st.subheader(e['title'])
    left,right=st.columns([1,1],gap='large')
    with left:
        with st.container(height=720,border=True):
            st.markdown('### Đề bài')
            asset=ROOT/e.get('asset_reference','missing')
            if asset.is_file():
                st.image(str(asset),width='stretch')
                st.download_button('Tải ảnh đề để phóng to / đính kèm',asset.read_bytes(),file_name=asset.name,key='img'+chosen)
            else:
                st.info('Ảnh chưa được đưa vào bản triển khai này.')
            st.write(e['prompt'])
            st.caption(e.get('source_note',''))
            if purpose=='Ôn tập':
                with st.expander('Gợi ý đọc đề và chia bài'):
                    st.write(e.get('analysis_vi','Đang kiểm tra dữ liệu.'))
                    st.write(e.get('outline_vi',''))
            if purpose=='Ôn tập' and e.get('data'):
                with st.expander('Dữ liệu của đề'):
                    show_data(e['data'])
    with right:
        with st.container(height=720,border=True):
            st.markdown('### Bài làm của bạn')
            if e['status']!='verified':
                st.warning(e.get('review_reason','Nội dung chưa được kiểm tra. Chưa mở bài học/chấm tự động.'))
                return
            if purpose=='Kiểm tra':
                from ui.journey import test_panel
                test_panel(e)
            else:
                from ui.learning_modes import learning_panel
                learning_panel(e,structures)


def answer_panel(e,structures,chosen):
    mode=st.radio('Cách luyện',['Học thuộc','Vận dụng','Quiz'],horizontal=True,key='practice-mode')
    task_id=''
    reference=''
    quiz=None
    part=None
    if mode=='Quiz':
        quiz=st.selectbox('Bài luyện',e['quizzes'],index=next((i for i,q in enumerate(e['quizzes']) if q['quiz_id']==st.session_state.get('review_task')),0),format_func=lambda q:q['prompt'])
        task_id=quiz['quiz_id']
        st.markdown(quiz['prompt'])
        if quiz['kind']=='order':
            for number,clause in enumerate(quiz['options'],1):
                st.write(f'{number}. {clause}')
    elif mode=='Học thuộc':
        choices={**e['paragraphs'],'full':full_model(e)}
        part=st.selectbox('Phần cần nhớ',list(choices),format_func=lambda x:LABELS.get(x,'Cả bài'),key='memory_part')
        reference=choices[part]
        sentences=[s.strip() for s in __import__('re').split(r'(?<=[.!?])\s+(?=[A-Z])',reference) if s.strip()]
        if part!='full' and st.checkbox('Luyện từng câu'):
            idx=st.selectbox('Câu',range(len(sentences)),format_func=lambda i:f'Câu {i+1}')
            reference=sentences[idx]
            part+=f'-sentence-{idx}'
        task_id='memory-'+part
        from ui.structure_hints import memory_hints
        memory_hints(e,structures,part)
        st.caption('Điểm nhớ mẫu: khoảng cách chỉnh sửa giữa các từ/dấu câu. Thiếu, thừa và thay từ đều trừ điểm. Bỏ qua khoảng trắng; mặc định phân biệt hoa/thường và dấu câu. Đây không phải band IELTS.')
        sensitive=st.checkbox('Phân biệt chữ hoa/thường',value=True)
        punctuation=st.checkbox('Tính dấu câu',value=True)
        if st.checkbox('Hiện mẫu để học',key='show'+chosen+task_id):
            show_highlighted(reference)
    else:
        part=st.selectbox('Phần tự viết',['sentence','overview','body1','body2','full','transfer'],format_func=lambda x:{'sentence':'Một câu','full':'Bài hoàn chỉnh','transfer':'Đổi dữ liệu (bài bổ sung tự tạo)'}.get(x,LABELS.get(x,x)))
        task_id='open-'+part
        if part=='transfer':
            st.info('Bài tự tạo: tỷ lệ hộ gia đình có internet là 20% năm 2000, 50% năm 2010 và 80% năm 2020. Viết 1–2 câu bằng rise from … to … / started at … .')
            reference='The percentage of households with internet access started at 20% in 2000, after which it rose to 50% in 2010, before reaching 80% in 2020.'
        else:
            reference=full_model(e) if part=='full' else e['paragraphs'].get(part,e['paragraphs']['body1'].split('. ')[0]+'.')
        st.caption('Không chấm đúng/sai bằng so chuỗi. Nộp để lưu, đối chiếu mẫu và tự đánh giá.')
    key=chosen+task_id
    if key not in st.session_state:
        st.session_state[key]={'attempt_id':str(uuid.uuid4()),'started':time.time(),'submitted':False,'retry_of':None}
    state=st.session_state[key]
    if not state['submitted']:
        with st.form('answer-'+key):
            if quiz and quiz['kind']=='single':
                answer=st.radio('Câu trả lời',quiz['options'],index=None)
            elif quiz and quiz['kind']=='multi':
                answer=st.multiselect('Chọn tất cả đáp án đúng (đúng toàn bộ mới được 1 điểm)',quiz['options'])
            else:
                answer=st.text_area('Bài của bạn',height=220 if mode!='Quiz' else 100,max_chars=20000)
            checks=[]
            if part=='full':
                st.markdown('**Checklist trước khi nộp cả bài**')
                for i,line in enumerate(e.get('checklist_vi') or ['Đã kiểm tra overview, số liệu, thì và ngữ pháp.']):
                    checks.append(st.checkbox(line,key=key+state['attempt_id']+'check'+str(i)))
            submitted=st.form_submit_button('Nộp bài',type='primary')
        if submitted:
            if part=='full' and not all(checks):
                st.warning('Tích đủ checklist trước khi nộp cả bài. Bài viết vẫn được giữ.'); return
            if not answer or (isinstance(answer,str) and not answer.strip()):
                st.warning('Bạn chưa nhập câu trả lời.'); return
            if mode=='Học thuộc':
                result=memory_grade(answer,reference,sensitive,punctuation)
            elif mode=='Quiz':
                result=grade_quiz(quiz,answer,e['status'])
            else:
                result=dict(score=None,max_score=None,grading_type='open',outcome='self_review')
            attempt=dict(learning_mode='study',assisted=True,attempt_id=state['attempt_id'],learner_id=st.session_state.settings['learner_id'],exercise_id=chosen,task_id=task_id,content_version=e['content_version'],submitted_at=now().isoformat(),answer=answer,duration_seconds=round(time.time()-state['started']),duration_basis='Thời gian từ lúc mở bài đến nộp, có thể gồm thời gian rời trang',retry_of=state['retry_of'],reference_snapshot=reference or quiz['accepted_answers'],**result)
            if mode=='Học thuộc':
                attempt['normalization_policy']={'case_sensitive':sensitive,'punctuation':punctuation}
            emit('attempt',attempt,event_id=attempt['attempt_id'])
            state['submitted']=True
            state['result']=attempt
            st.rerun()
    else:
        result=state['result']
        if result['score'] is not None:
            st.metric('Điểm khớp mẫu' if mode=='Học thuộc' else 'Điểm quiz',f"{result['score']}/{result['max_score']}")
        outcomes={'matched':'Đã khớp mẫu hoàn toàn.','not_matched':'Chưa khớp mẫu. Cách viết khác vẫn có thể đúng tiếng Anh.','correct':'Đúng đáp án.','incorrect':'Chưa đúng đáp án của bài đóng.','unconfirmed':'Chưa được xác nhận trong tập đáp án đã biên tập.','self_review':'Đã ghi nhận bài trong phiên; tự đối chiếu hoặc chuyển sang Chữa bài.'}
        st.info(outcomes.get(result['outcome'],result['outcome']))
        if result.get('changes'):
            st.dataframe(result['changes'],hide_index=True,width='stretch')
        if quiz:
            st.markdown('**Đáp án**')
            from ui.readable import show_answer
            show_answer(quiz['accepted_answers'],quiz.get('options') if quiz['kind']=='order' else None)
            st.write(quiz['explanation_vi'])
        else:
            st.markdown('**Mẫu để đối chiếu**'); show_highlighted(result['reference_snapshot'])
            st.caption('Hãy kiểm tra số liệu, đơn vị, thì, overview và cấu trúc mục tiêu.')
        if st.button('Thử lại',key='retry'+key):
            st.session_state[key]={'attempt_id':str(uuid.uuid4()),'started':time.time(),'submitted':False,'retry_of':result['attempt_id']}
            st.rerun()
    if st.checkbox('Xem bài mẫu đầy đủ và giải thích',key='model'+chosen):
        show_model(e,structures)



def show_data(data):
    labels={'years':'Năm','unit':'Đơn vị','stages':'Các giai đoạn','components':'Thành phần','sequence':'Trình tự','layers':'Các lớp','regions':'Khu vực','countries':'Quốc gia','groups':'Nhóm','months':'Số tháng','container_m3':'Dung tích thùng (m³)'}
    def label(key):
        return labels.get(key,str(key).replace('_',' ').replace('�','–'))
    def readable(value):
        if isinstance(value,dict):
            return '; '.join(f'{label(k)}: {readable(v)}' for k,v in value.items())
        if isinstance(value,list):
            return ' → '.join(readable(v) for v in value)
        if isinstance(value,bool):
            return 'Có' if value else 'Không'
        return str(value)
    if data.get('unit'):
        st.caption('Đơn vị: '+str(data['unit']))
    if data.get('approximate'):
        st.caption('Số liệu gần đúng, đọc từ hình.')
    years=data.get('years',[])
    series={k:v for k,v in data.items() if k!='years' and isinstance(v,list) and years and len(v)==len(years)}
    if series:
        st.dataframe([{'Nhóm':label(k),**{str(y):readable(v) for y,v in zip(years,values)}} for k,values in series.items()],hide_index=True,width='stretch')
    remaining=[{'Thông tin':label(k),'Nội dung':readable(v)} for k,v in data.items() if k not in series and k not in ['unit','approximate'] and not (k=='years' and series)]
    if remaining:
        st.dataframe(remaining,hide_index=True,width='stretch')
