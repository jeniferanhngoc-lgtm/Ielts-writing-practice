"""Personal DOCX and quiz-bank learning space, integrated with existing storage."""
import base64
import os
import uuid
import streamlit as st
from core.personal_bank import (ROOT, PARTS, STRUCTURES, CAUTIONS, load_bank,
                               reference, sentences, initials, cloze,
                               shuffled_indices, quizzes, tutor_prompt)
from core.grading import memory_grade, normalize
from core.review_schedule import now, reviews_from_attempts
from ui.state import emit, records

MODES = ['Đọc & hiểu bài', 'Thẻ cấu trúc', 'Điền khuyết', 'Nhớ từng câu',
         'Sắp xếp câu', 'Viết lại từ trí nhớ', 'Quiz & giải thích', 'Hỏi ChatGPT']


def save_attempt(lesson, task, answer, result, model='', assisted=False):
    ident = str(uuid.uuid4())
    emit('attempt', dict(attempt_id=ident, exercise_id='personal:'+lesson['id'],
         task_id=task, answer=answer, submitted_at=now().isoformat(),
         reference_snapshot=model, source_status='original_unverified',
         learning_mode='study' if assisted else 'test', assisted=assisted, **result), ident)


def secret(name, default=''):
    value = os.environ.get(name, '')
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, KeyError):
        return default


def feedback(result, model):
    st.metric('Độ khớp với mẫu gốc', f"{result['score']}%")
    st.caption('Chỉ đo trí nhớ theo văn bản nguồn; cách diễn đạt khác vẫn có thể đúng. Không phải điểm IELTS.')
    if result.get('changes'):
        st.dataframe(result['changes'], hide_index=True, width='stretch')
    with st.expander('Đối chiếu đáp án gốc', expanded=True):
        st.write(model)


def tutor(lesson):
    st.subheader('Gia sư giải thích và luyện nhớ')
    question = st.text_area('Bạn muốn hỏi gì?', 'Giải thích cách chia body và cho tôi bài tập nhớ cấu trúc trong bài này.', key='personal-question', max_chars=4000)
    draft = st.text_area('Bài bạn muốn được nhận xét (tùy chọn)', key='personal-ai-draft', max_chars=20000)
    prompt = tutor_prompt(lesson, draft, question)
    with st.expander('Dùng ChatGPT bằng cách sao chép'):
        st.code(prompt, language=None)
        st.download_button('Tải câu hỏi TXT', prompt, file_name=lesson['id']+'-chatgpt.txt')
        st.link_button('Mở ChatGPT', 'https://chatgpt.com/')
        st.caption('Dán câu hỏi và đính kèm ảnh đề khi cần kiểm tra số liệu.')
    st.caption('Kết nối trực tiếp dùng OpenAI API; cần API key riêng và có thể phát sinh phí API. Key nhập chỉ dùng trong phiên, không lưu vào tiến độ.')
    key = st.text_input('OpenAI API key (tùy chọn nếu đã cấu hình secrets)', type='password', key='personal-api-key')
    model = st.text_input('Model API', value=secret('OPENAI_MODEL', 'gpt-4.1-mini'), key='personal-api-model')
    if st.button('Gửi câu hỏi, bài viết và ảnh đề tới OpenAI', type='primary'):
        actual_key = key.strip() or secret('OPENAI_API_KEY')
        if not actual_key:
            st.info('Nhập API key hoặc dùng cách sao chép sang ChatGPT bên trên.')
        elif not question.strip() or not model.strip():
            st.warning('Cần câu hỏi và tên model trước khi gửi.')
        else:
            try:
                from openai import OpenAI
                path = ROOT/lesson['image']
                mime = 'image/jpeg' if path.suffix.lower() in ('.jpg', '.jpeg') else 'image/png'
                url = 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')
                with st.spinner('Gia sư đang đọc bài và ảnh đề…'):
                    response = OpenAI(api_key=actual_key, timeout=60, max_retries=1).responses.create(
                        model=model.strip(), store=False, max_output_tokens=2500,
                        input=[{'role': 'user', 'content': [
                            {'type': 'input_text', 'text': prompt},
                            {'type': 'input_image', 'image_url': url}]}])
                st.session_state['personal-ai-'+lesson['id']] = response.output_text
            except Exception:
                st.error('Chưa nhận được phản hồi. Kiểm tra key, quyền dùng model, hạn mức và kết nối. Bạn vẫn có thể tải câu hỏi để dùng ChatGPT.')
    answer = st.session_state.get('personal-ai-'+lesson['id'])
    if answer:
        st.markdown(answer)
        st.download_button('Lưu giải thích TXT', answer, file_name=lesson['id']+'-giai-thich.txt')


def personal_memory():
    st.title('Học thuộc bài của tôi')
    st.write('18 đề từ tài liệu của bạn · nhớ khung, nhớ câu, rồi tự viết cả bài.')
    lessons = load_bank()
    category = st.selectbox('Lọc bộ đề của tôi', ['Tất cả', 'Biểu đồ theo thời gian', 'Biểu đồ tĩnh & hỗn hợp', 'Maps', 'Process'])
    def group(lesson):
        n = int(lesson['id'].split('.')[1])
        return 'Biểu đồ theo thời gian' if n <= 10 else 'Biểu đồ tĩnh & hỗn hợp' if n <= 13 else 'Maps' if n <= 15 else 'Process'
    filtered = [x for x in lessons if category == 'Tất cả' or group(x) == category]
    byid = {x['id']: x for x in filtered}
    ident = st.selectbox('Chọn bài từ Word', list(byid), format_func=lambda k: k+' · '+byid[k]['title'], key='personal-lesson')
    lesson = byid[ident]
    attempts = [a for a in records('attempt') if a['exercise_id'].startswith('personal:')]
    reviews = list(reviews_from_attempts(attempts).values())
    due = [x for x in reviews if x['next_review_date'] <= now().date().isoformat()]
    a, b, c = st.columns(3)
    a.metric('Bài đã luyện', len({x['exercise_id'] for x in attempts}))
    b.metric('Lượt đã nộp', len(attempts))
    c.metric('Mục đến hạn ôn', len(due))
    with st.expander('Lộ trình học và lịch ôn'):
        st.markdown('1. Đọc đề và hiểu bốn đoạn.\n2. Nhớ thẻ cấu trúc và điều kiện sử dụng.\n3. Điền khuyết, nhớ từng câu, sắp xếp câu.\n4. Tự viết từng đoạn rồi cả bài khi không nhìn mẫu.\n5. Ôn lại theo lịch 1–3–7–14 ngày; nếu chưa khớp mẫu, ôn lại ngày sau.')
        st.caption('Lượt dùng gợi ý được lưu riêng và không tính là kiểm tra độc lập. Luyện nhớ giúp ghi nhớ; khi gặp đề mới cần đổi số liệu và chọn cấu trúc phù hợp.')
        if reviews:
            st.dataframe([{'Bài': x['exercise_id'].removeprefix('personal:'), 'Dạng': x['task_id'], 'Ngày ôn': x['next_review_date']} for x in reviews], hide_index=True)
    mode = st.selectbox('Dạng học thuộc', MODES, key='personal-mode')
    with st.expander('Xem ảnh đề', expanded=mode == MODES[0]):
        st.image(str(ROOT/lesson['image']), caption='Quiz bank · '+ident, width=700)
    st.warning(CAUTIONS.get(ident, 'Bản gốc chưa được xác minh toàn bộ. Đối chiếu số liệu, đơn vị và nhãn với ảnh đề trước khi học thuộc.'))
    prefix = 'personal-'+ident+'-'+str(MODES.index(mode))
    if mode == MODES[0]:
        for part, text in lesson['sections'].items():
            with st.container(border=True):
                st.subheader(lesson['section_labels'][part])
                st.write(text)
                st.caption({'introduction': 'Nêu loại biểu đồ, đối tượng, nơi chốn và thời gian.', 'overview': 'Tóm tắt đặc điểm nổi bật, xu hướng hoặc toàn bộ quy trình.', 'body1': 'Nhóm chi tiết thứ nhất; kiểm tra cách chia nhóm trong lời giải nguồn.', 'body2': 'Nhóm chi tiết thứ hai; so sánh hoặc tiếp nối nhóm trước.'}[part])
        with st.expander('Giải thích và dàn ý nguyên văn trong tài liệu'):
            st.write('\n\n'.join(lesson['original_paragraphs']))
        st.download_button('Tải bài và giải thích TXT', '\n\n'.join(lesson['original_paragraphs']), file_name=ident+'-bai-goc.txt')
    elif mode == MODES[1]:
        index = st.selectbox('Chọn thẻ cấu trúc', range(len(STRUCTURES)), format_func=lambda i: STRUCTURES[i][0])
        title, template, explanation = STRUCTURES[index]
        st.subheader(title)
        st.write('Tự đọc lại công thức rồi bấm lật thẻ.')
        if st.checkbox('Lật thẻ và xem điều kiện dùng', key=prefix+'-flip'):
            st.info(template); st.write(explanation)
        left, right = st.columns(2)
        for passed, column, label in [(False, left, 'Cần ôn thẻ này'), (True, right, 'Tự đánh giá đã nhớ thẻ')]:
            if column.button(label, key=prefix+'-card-'+str(index)+'-'+str(passed)):
                save_attempt(lesson, 'personal-flash-'+str(index), label,
                             dict(score=None, max_score=None, grading_type='flashcard', self_assessed_passed=passed),
                             template, assisted=True)
                st.success('Đã ghi tự đánh giá và cập nhật lịch ôn.')
        st.caption('Các khung này là gợi ý biên tập để vận dụng; bài gốc vẫn giữ nguyên ở mục Đọc & hiểu bài.')
    elif mode == MODES[7]:
        tutor(lesson)
    else:
        part = st.selectbox('Phần học thuộc', list(PARTS), format_func=PARTS.get, key=prefix+'-part')
        target = reference(lesson, part)
        prefix += '-'+part
        if mode == MODES[2]:
            hard = st.radio('Nội dung cần nhớ', ['Cụm cấu trúc', 'Số liệu'], horizontal=True, key=prefix+'-hard') == 'Số liệu'
            prefix += '-data' if hard else '-structure'
            prompt, answers = cloze(target, hard)
            st.info(prompt)
            with st.form(prefix+'-form'):
                supplied = [st.text_input(f'Ô {i+1}', key=prefix+f'-blank-{i}') for i in range(len(answers))]
                submit = st.form_submit_button('Kiểm tra điền khuyết')
            if submit:
                correct = sum(normalize(x) == normalize(y) for x, y in zip(supplied, answers))
                result = dict(score=correct, max_score=len(answers), grading_type='quiz')
                save_attempt(lesson, 'personal-cloze-'+part+('-data' if hard else ''), supplied, result, target, assisted=st.session_state.get(prefix+'-seen', False))
                st.session_state[prefix+'-result'] = supplied
                st.session_state[prefix+'-seen'] = True
            if prefix+'-result' in st.session_state:
                supplied = st.session_state[prefix+'-result']
                st.write(f"Đúng {sum(normalize(x)==normalize(y) for x,y in zip(supplied,answers))}/{len(answers)} ô theo mẫu.")
                st.dataframe([{'Ô': i+1, 'Bạn điền': x, 'Đáp án gốc': y, 'Kết quả': 'Đúng' if normalize(x)==normalize(y) else 'Khác mẫu'} for i,(x,y) in enumerate(zip(supplied,answers))], hide_index=True)
                st.caption('Cụm cấu trúc giúp nối ý và mô tả quan hệ; số liệu phải đối chiếu ảnh. Đáp án khác mẫu chưa chắc sai ngữ pháp.')
        elif mode in (MODES[3], MODES[5]):
            if mode == MODES[3]:
                items = sentences(target)
                idx = st.selectbox('Câu cần nhớ', range(len(items)), format_func=lambda n: 'Câu '+str(n+1), key=prefix+'-sentence')
                target = items[idx]
                prefix += '-sentence-'+str(idx)
            hints = st.checkbox('Hiện gợi ý chữ cái đầu', key=prefix+'-hints')
            if hints:
                st.info(initials(target))
            show = st.checkbox('Xem mẫu trước khi viết', key=prefix+'-show')
            if show:
                st.write(target)
            with st.form(prefix+'-form'):
                draft = st.text_area('Viết lại từ trí nhớ', height=220, key=prefix+'-draft', max_chars=20000)
                submitted = st.form_submit_button('Nộp bài học thuộc')
            if submitted:
                if not draft.strip():
                    st.warning('Hãy viết câu hoặc đoạn trước khi nộp.')
                else:
                    result = memory_grade(draft, target, case_sensitive=False, punctuation=False)
                    assisted = hints or show or st.session_state.get(prefix+'-seen', False)
                    save_attempt(lesson, prefix.removeprefix('personal-'+ident+'-'), draft, result, target, assisted)
                    st.session_state[prefix+'-result'] = result
                    st.session_state[prefix+'-seen'] = True
            if hints or show:
                st.session_state[prefix+'-seen'] = True
            if prefix+'-result' in st.session_state:
                feedback(st.session_state[prefix+'-result'], target)
                st.caption('Đã xem gợi ý/đáp án trong lượt này: lần nộp tiếp theo được tính là luyện có hỗ trợ.')
                if st.button('Bắt đầu lượt kiểm tra mới', key=prefix+'-reset'):
                    for suffix in ['-result', '-seen', '-draft', '-show', '-hints']:
                        st.session_state.pop(prefix+suffix, None)
                    st.rerun()
        elif mode == MODES[4]:
            items = sentences(target)
            if len(items) < 2:
                st.info('Phần này chỉ có một câu. Chọn Body, Overview hoặc Cả bài để sắp xếp.'); return
            order = shuffled_indices(len(items), ident+part)
            for label, idx in enumerate(order, 1):
                st.write(f'{label}. {items[idx]}')
            expected = [order.index(i)+1 for i in range(len(items))]
            with st.form(prefix+'-form'):
                value = st.text_input('Nhập thứ tự đúng, ngăn cách bằng dấu phẩy (ví dụ 3,1,2)', key=prefix+'-order')
                submit = st.form_submit_button('Kiểm tra thứ tự')
            if submit:
                try:
                    entered = [int(x.strip()) for x in value.split(',')]
                    if sorted(entered) != list(range(1, len(items)+1)):
                        raise ValueError()
                except ValueError:
                    st.warning('Cần nhập đủ mỗi số một lần, phân cách bằng dấu phẩy.')
                else:
                    correct = entered == expected
                    save_attempt(lesson, 'personal-order-'+part, value, dict(score=int(correct), max_score=1, grading_type='quiz'), target, assisted=st.session_state.get(prefix+'-seen', False))
                    st.session_state[prefix+'-result'] = correct
                    st.session_state[prefix+'-seen'] = True
            if prefix+'-result' in st.session_state:
                st.success('Đúng thứ tự mẫu!') if st.session_state[prefix+'-result'] else st.info('Thứ tự khác mẫu gốc.')
                st.write('Thứ tự gốc: '+', '.join(map(str, expected)))
                st.caption('Đối chiếu mạch ý: giới thiệu → tổng quan → chi tiết. Trong từng body, theo mốc thời gian hoặc trình tự quy trình; một số câu có thể đổi chỗ mà vẫn hợp lý.')
        elif mode == MODES[6]:
            questions = quizzes(lesson)
            qidx = st.selectbox('Câu hỏi quiz', range(len(questions)), format_func=lambda i: 'Câu '+str(i+1), key=prefix+'-quiz')
            q = questions[qidx]
            prefix += '-q'+str(qidx)
            order = shuffled_indices(len(q['options']), ident+str(qidx))
            options = [q['options'][i] for i in order]
            with st.form(prefix+'-form'):
                value = st.radio(q['question'], options, index=None, key=prefix+'-answer')
                submit = st.form_submit_button('Nộp quiz')
            if submit:
                if value is None:
                    st.warning('Chọn một đáp án trước khi nộp.')
                else:
                    correct = value == q['answer']
                    save_attempt(lesson, 'personal-quiz-'+str(qidx), value, dict(score=int(correct), max_score=1, grading_type='quiz'), q['answer'], assisted=st.session_state.get(prefix+'-seen', False))
                    st.session_state[prefix+'-result'] = correct
                    st.session_state[prefix+'-seen'] = True
            if prefix+'-result' in st.session_state:
                st.success('Đúng!') if st.session_state[prefix+'-result'] else st.info('Chưa đúng.')
                st.write('Đáp án: '+q['answer']); st.write(q['why'])
