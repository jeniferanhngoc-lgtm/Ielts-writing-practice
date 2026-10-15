"""Structure multiple choice and essay copying/recall, with sidebar controls."""
import uuid
import streamlit as st
from core.personal_bank import ROOT, PARTS, CAUTIONS, load_bank, reference
from core.structure_choice import choice_question, filter_lessons, random_lesson
from core.grading import memory_grade
from core.review_schedule import now
from ui.core_framework import show_highlighted
from ui.state import emit

GROUPS = {
    'Biểu đồ số liệu': ['intro-count', 'intro-amount', 'intro-percentage', 'overview-all',
                       'overview-trend', 'overview-overtake', 'from-to', 'sequence',
                       'with', 'similar', 'peak', 'conversely', 'respectively', 'forecast',
                       'static-overview', 'compare', 'mixed-intro'],
    'Maps': ['map-intro', 'map-overview', 'location', 'map-change', 'map-build',
             'map-trees', 'map-roads', 'map-links', 'map-accompanied'],
    'Process': ['process-intro', 'process-overview', 'process-order', 'process-purpose'],
}
ESSAY_MODES = ['Ôn tập · Chép theo mẫu', 'Luyện tập · Tự nhớ và viết']
TYPES = ['Tất cả', 'Line chart', 'Bar chart', 'Table', 'Pie chart', 'Mixed chart', 'Maps', 'Process', 'Vòng đời tự nhiên']
CHOICE_TITLES = {'intro-count':'Introduction · Số lượng đếm được',
                 'intro-amount':'Introduction · Lượng không đếm được',
                 'conversely':'Body · Hai xu hướng đối lập',
                 'respectively':'Ghép số liệu theo đúng thứ tự'}


def record(exercise_id, task, answer, target, result, assisted):
    ident = str(uuid.uuid4())
    emit('attempt', dict(attempt_id=ident, exercise_id=exercise_id, task_id=task,
                        answer=answer, reference_snapshot=target,
                        submitted_at=now().isoformat(), assisted=assisted,
                        learning_mode='study' if assisted else 'test', **result), ident)


def study_structures(structures, controls=None):
    controls = controls if controls is not None else st.sidebar
    byid = {x['structure_id']: x for x in structures}
    with controls:
        st.caption('CHỌN CẤU TRÚC')
        group = st.selectbox('Dạng cấu trúc', list(GROUPS), key='focus-structure-group')
        ids = GROUPS[group]
        if st.session_state.get('focus-structure') not in ids:
            st.session_state['focus-structure'] = ids[0]
        ident = st.selectbox('Cấu trúc cần nhớ', ids, format_func=lambda k: CHOICE_TITLES.get(k,byid[k]['title']), key='focus-structure')
    item = byid[ident]
    question = choice_question(item)
    st.title('Học cấu trúc bằng trắc nghiệm')
    st.caption('Chọn cụm đúng để hoàn thành câu. Sau khi nộp, xem khung và giải thích.')
    st.subheader(CHOICE_TITLES.get(ident,item['title']))
    show_highlighted(question['prompt'])
    base = 'focus-choice:'+ident
    round_no = st.session_state.get(base+':round', 0)
    prefix = base+':'+str(round_no)
    saved = st.session_state.get(prefix+':result')
    if saved is None:
        with st.form(prefix+':form'):
            selected = st.radio('Chọn đáp án', question['options'], index=None, key=prefix+':answer')
            sent = st.form_submit_button('Kiểm tra đáp án', type='primary')
        if sent:
            if selected is None:
                st.warning('Chọn một đáp án trước khi kiểm tra.')
            else:
                correct = selected == question['answer']
                record('structure:'+ident, 'structure-choice-'+ident, selected, item['template'],
                       dict(score=int(correct), max_score=1, grading_type='quiz'), round_no > 0)
                st.session_state[prefix+':result'] = dict(correct=correct, answer=selected)
                st.rerun()
    else:
        st.success('Đúng!') if saved['correct'] else st.info('Chưa đúng. Đáp án: '+question['answer'])
        st.write(question['explanation'])
        with st.container(border=True):
            st.markdown('**Khung cần thuộc**'); show_highlighted(item['template'])
            st.markdown('**Ví dụ hoàn chỉnh**'); show_highlighted(question['example'])
            st.caption(item['usage_conditions'])
        a, b = st.columns(2)
        if a.button('Làm lại câu này', key=prefix+':again'):
            st.session_state[base+':round'] = round_no+1
            st.rerun()
        def next_question():
            st.session_state['focus-structure'] = ids[(ids.index(ident)+1) % len(ids)]
        b.button('Cấu trúc tiếp theo →', on_click=next_question, key=prefix+':next', type='primary')


def essay_controls(bank, controls):
    with controls:
        st.caption('CHỌN BÀI HỌC')
        mode = st.selectbox('Chế độ học bài', ESSAY_MODES, key='focus-essay-mode')
        category = st.selectbox('Dạng đề', TYPES, key='focus-essay-type')
        pool = filter_lessons(bank, category)
        byid = {x['id']:x for x in pool}
        ids = list(byid)
        if st.session_state.get('focus-essay') not in ids:
            st.session_state['focus-essay'] = ids[0]
        ident = st.selectbox('Bài cần thuộc', ids, format_func=lambda k:k+' · '+byid[k]['title'], key='focus-essay')
        def randomize():
            st.session_state['focus-essay'] = random_lesson(ids, st.session_state.get('focus-essay'))
        st.button('🎲 Chọn bài ngẫu nhiên', on_click=randomize, key='focus-random', width='stretch', disabled=len(ids)<2)
        part = st.selectbox('Học theo đoạn / toàn bài', list(PARTS), format_func=PARTS.get, key='focus-essay-part')
        st.caption('Ngẫu nhiên chọn trong dạng đề đang lọc. Chọn Tất cả để lấy từ toàn bộ 18 bài.')
    return byid[ident], part, mode


def study_essays(controls=None):
    controls = controls if controls is not None else st.sidebar
    lesson, part, mode = essay_controls(load_bank(), controls)
    ident = lesson['id']
    copying = mode == ESSAY_MODES[0]
    st.title('Ôn tập · Chép theo mẫu' if copying else 'Luyện tập · Tự nhớ và viết')
    st.caption(ident+' · '+lesson['title']+' · '+PARTS[part])
    with st.expander('Ảnh đề & lưu ý bài gốc'):
        st.image(str(ROOT/lesson['image']), width=650)
        st.write(CAUTIONS.get(ident, 'Bài gốc chưa được xác minh toàn bộ. Đối chiếu đơn vị, nhãn và số liệu với ảnh đề.'))
    st.caption('Chép lại để quen câu chữ.' if copying else 'Mẫu được ẩn đến khi nộp. Tự nhớ rồi viết lại phần đã chọn.')
    target = reference(lesson, part)
    base = 'focused-essay:'+ident+':'+part+(':+copy' if copying else ':+recall')
    round_no = st.session_state.get(base+':round', 0)
    prefix = base+':'+str(round_no)
    saved = st.session_state.get(prefix+':result')
    if saved:
        st.success(f"Độ khớp với mẫu: {saved['score']}%")
        st.caption('Đo độ nhớ/chép đúng văn bản gốc; không phải band IELTS. Cách diễn đạt khác có thể vẫn đúng.')
        with st.expander('Chỗ thiếu, thừa hoặc khác mẫu', expanded=bool(saved['changes'])):
            if saved['changes']:
                st.dataframe(saved['changes'], hide_index=True, width='stretch')
            else:
                st.write('Đã khớp toàn bộ từ theo mẫu; không phân biệt hoa/thường và dấu câu.')
        left, right = st.columns(2)
        with left:
            st.markdown('**Bài bạn đã viết**'); st.write(saved['answer'])
        with right:
            st.markdown('**Bài mẫu đối chiếu**'); show_highlighted(target)
        if st.button('Viết lại lần nữa', key=prefix+':again', type='primary'):
            st.session_state[base+':round'] = round_no+1
            st.rerun()
        return
    if copying:
        with st.container(border=True):
            st.markdown('**Bài mẫu để chép**'); show_highlighted(target)
    with st.form(prefix+':form'):
        draft = st.text_area('Chép bài vào đây' if copying else 'Viết bài từ trí nhớ',
                             height=280, max_chars=20000, key=prefix+':draft')
        sent = st.form_submit_button('Chấm bài', type='primary')
    if sent:
        if not draft.strip():
            st.warning('Hãy viết bài trước khi chấm.'); return
        grade = memory_grade(draft, target, case_sensitive=False, punctuation=False)
        record('personal:'+ident, ('copy-' if copying else 'recall-')+part, draft, target, grade, copying or round_no > 0)
        st.session_state[prefix+':result'] = dict(score=grade['score'], changes=grade['changes'], answer=draft)
        st.rerun()
    if copying:
        with st.expander('Giải thích trong tài liệu'):
            st.write('\n\n'.join(lesson['source_notes']))
