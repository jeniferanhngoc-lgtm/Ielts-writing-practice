"""Two focused learning routes, one item and one recall exercise at a time."""
import uuid
import streamlit as st
from core.personal_bank import ROOT, PARTS, CAUTIONS, load_bank, reference, cloze, initials
from core.grading import memory_grade, normalize
from core.review_schedule import now
from ui.core_framework import show_highlighted
from ui.state import emit

STEPS = ['1 · Xem mẫu', '2 · Điền khuyết', '3 · Tự viết lại']
GROUPS = {
    'Biểu đồ số liệu': ['intro-count', 'intro-amount', 'intro-percentage', 'overview-all',
                       'overview-trend', 'overview-overtake', 'from-to', 'sequence',
                       'with', 'similar', 'peak', 'conversely', 'respectively', 'forecast',
                       'static-overview', 'compare', 'mixed-intro'],
    'Maps': ['map-intro', 'map-overview', 'location', 'map-change', 'map-build',
             'map-trees', 'map-roads', 'map-links', 'map-accompanied'],
    'Process': ['process-intro', 'process-overview', 'process-order', 'process-purpose'],
}


def record(exercise_id, task, answer, target, result, assisted):
    ident = str(uuid.uuid4())
    emit('attempt', dict(attempt_id=ident, exercise_id=exercise_id, task_id=task,
                        answer=answer, reference_snapshot=target,
                        submitted_at=now().isoformat(), assisted=assisted,
                        learning_mode='study' if assisted else 'test', **result), ident)


def recall(exercise_id, task, target, key, step):
    """Keep answers hidden until submission; never count a revealed retry as independent."""
    key += ':'+str(step)
    round_no = st.session_state.get(key+':round', 0)
    prefix = key+':'+str(round_no)
    saved = st.session_state.get(prefix+':result')
    if saved is not None:
        st.success(f"Đã nhớ {saved['percent']}% theo mẫu.")
        show_highlighted(target)
        if saved.get('changes'):
            with st.expander('Xem chỗ thiếu hoặc khác mẫu'):
                st.dataframe(saved['changes'], hide_index=True, width='stretch')
        st.caption('Khác mẫu vẫn có thể đúng cách diễn đạt. Điểm này chỉ đo trí nhớ.')
        if st.button('Luyện lại', key=prefix+':again', type='primary'):
            st.session_state[key+':round'] = round_no+1
            st.rerun()
        return
    if step == STEPS[1]:
        prompt, answers = cloze(target)
        show_highlighted(prompt)
        with st.form(prefix+':form'):
            supplied = [st.text_input(f'Ô {i+1}', key=prefix+':blank-'+str(i)) for i in range(len(answers))]
            sent = st.form_submit_button('Kiểm tra', type='primary')
        if sent:
            if not any(x.strip() for x in supplied):
                st.warning('Điền câu trả lời trước khi kiểm tra.'); return
            score = sum(normalize(a)==normalize(b) for a,b in zip(supplied, answers))
            result = dict(score=score, max_score=len(answers), grading_type='quiz')
            record(exercise_id, task+'-cloze', supplied, target, result, False)
            st.session_state[prefix+':result'] = dict(percent=round(100*score/len(answers)), changes=[
                {'Ô':i+1, 'Bạn điền':a, 'Mẫu':b} for i,(a,b) in enumerate(zip(supplied,answers)) if normalize(a)!=normalize(b)])
            st.rerun()
    else:
        st.write('Ẩn mẫu rồi tự gõ lại phần vừa học.')
        hint = st.checkbox('Cần gợi ý chữ cái đầu', key=prefix+':hint')
        if hint:
            st.info(initials(target))
            st.session_state[prefix+':assisted'] = True
        with st.form(prefix+':form'):
            draft = st.text_area('Bài viết từ trí nhớ', height=220, max_chars=20000, key=prefix+':draft')
            sent = st.form_submit_button('Kiểm tra', type='primary')
        if sent:
            if not draft.strip():
                st.warning('Viết câu trả lời trước khi kiểm tra.'); return
            result = memory_grade(draft, target, case_sensitive=False, punctuation=False)
            record(exercise_id, task+'-memory', draft, target, result, st.session_state.get(prefix+':assisted', False))
            st.session_state[prefix+':result'] = dict(percent=result['score'], changes=result['changes'])
            st.rerun()


def step_picker(key):
    return st.radio('Cách học', STEPS, horizontal=True, key=key)


def next_step(key, step):
    index = STEPS.index(step)
    if index < len(STEPS)-1:
        def advance():
            st.session_state[key] = STEPS[index+1]
        st.button('Tiếp theo → '+STEPS[index+1].split(' · ')[1], on_click=advance,
                  key=key+':next', type='primary' if index==0 else 'secondary')


def study_structures(structures):
    st.title('Học cấu trúc')
    st.caption('Chọn một khung. Xem ví dụ, điền chỗ trống rồi tự gõ lại.')
    group = st.selectbox('Dạng bài', list(GROUPS), key='focus-structure-group')
    byid = {x['structure_id']: x for x in structures}
    options = GROUPS[group]
    ident = st.selectbox('Cấu trúc cần nhớ', options, format_func=lambda k: byid[k]['title'], key='focus-structure')
    item = byid[ident]
    step_key = 'focus-structure-step:'+ident
    step = step_picker(step_key)
    if step == STEPS[0]:
        with st.container(border=True):
            st.markdown('**Khung cần thuộc**')
            show_highlighted(item['template'])
            st.markdown('**Ví dụ**')
            show_highlighted(item['examples'][0])
            st.write(item['explanation_vi'])
        with st.expander('Cách dùng và ví dụ khác'):
            st.write(item['usage_conditions'])
            for example in item['examples'][1:]:
                show_highlighted(example)
            st.caption(item['common_errors'])
    else:
        target_kind = st.selectbox('Nội dung cần nhớ', ['Khung cấu trúc', 'Câu ví dụ'], key='focus-target:'+ident)
        target = item['template'] if target_kind == 'Khung cấu trúc' else item['examples'][0]
        if target_kind == 'Khung cấu trúc':
            st.caption('Giữ các ô [đối tượng], [số liệu] như trong khung đã học.')
        suffix = 'template' if target_kind == 'Khung cấu trúc' else 'example'
        recall('structure:'+ident, 'structure-'+ident+'-'+suffix, target,
               'focus-structure:'+ident+':'+suffix, step)
    next_step(step_key, step)


def study_essays():
    st.title('Học bài mẫu')
    st.caption('Học từng đoạn trước, sau đó chọn Cả bài để nhớ toàn bộ.')
    bank = load_bank()
    byid = {x['id']: x for x in bank}
    ident = st.selectbox('Bài cần thuộc', list(byid), format_func=lambda k: k+' · '+byid[k]['title'], key='focus-essay')
    lesson = byid[ident]
    part = st.selectbox('Phần cần thuộc', list(PARTS), format_func=PARTS.get, key='focus-essay-part')
    with st.expander('Ảnh đề'):
        st.image(str(ROOT/lesson['image']), width=650)
    if ident in CAUTIONS:
        st.caption('Lưu ý bài gốc: '+CAUTIONS[ident])
    else:
        st.caption('Bài gốc từ Word; hãy đối chiếu số liệu với ảnh đề.')
    step_key = 'focus-essay-step:'+ident+':'+part
    step = step_picker(step_key)
    target = reference(lesson, part)
    if step == STEPS[0]:
        with st.container(border=True):
            st.markdown('**'+PARTS[part]+'**')
            show_highlighted(target)
        with st.expander('Giải thích trong tài liệu'):
            st.write('\n\n'.join(lesson['source_notes']))
    else:
        recall('personal:'+ident, 'focused-'+part, target, 'focus-essay:'+ident+':'+part, step)
    next_step(step_key, step)
