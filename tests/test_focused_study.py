import html
import re
from streamlit.testing.v1 import AppTest
from core.content_validation import ROOT, load_content
from core.personal_bank import load_bank, reference
from core.structure_choice import choice_question, filter_lessons, random_lesson
from ui.focused_study import GROUPS, ESSAY_MODES, TYPES


def app():
    at = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30)
    at.secrets['storage_mode'] = 'demo'
    return at.run()


def item(at, kind, label):
    return next(x for x in getattr(at, kind) if x.label == label)


def prose(at):
    return '\n'.join(html.unescape(re.sub('<[^>]+>', '', x.value)) for x in at.markdown)


def test_default_copy_mode_has_sidebar_controls_and_model():
    at = app()
    assert not at.exception
    assert at.title[0].value == 'Ôn tập · Chép theo mẫu'
    assert item(at.sidebar, 'selectbox', 'Chế độ học bài').value == ESSAY_MODES[0]
    assert len(at.sidebar.selectbox) == 4
    assert not at.metric
    assert 'The graph illustrates how much waste' in prose(at)
    assert 'From 2005 to 2015, the figure' not in prose(at)
    assert item(at, 'text_area', 'Chép bài vào đây').value == ''


def test_copy_and_recall_grading_are_distinct_and_idempotent():
    at = app()
    target = reference(load_bank()[0], 'introduction')
    item(at, 'text_area', 'Chép bài vào đây').set_value(target)
    item(at, 'button', 'Chấm bài').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] == 100
    assert at.session_state.events[-1]['data']['assisted']
    item(at.sidebar, 'selectbox', 'Chế độ học bài').set_value(ESSAY_MODES[1]).run()
    assert 'The graph illustrates how much waste' not in prose(at)
    assert not any(x.label=='Giải thích trong tài liệu' for x in at.expander)
    item(at, 'button', 'Chấm bài').click().run()
    assert len(at.session_state.events) == 1
    item(at, 'text_area', 'Viết bài từ trí nhớ').set_value(target)
    item(at, 'button', 'Chấm bài').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] == 100
    assert not at.session_state.events[-1]['data']['assisted']
    assert 'The graph illustrates how much waste' in prose(at)
    count = len(at.session_state.events)
    at.run()
    assert len(at.session_state.events) == count
    item(at, 'button', 'Viết lại lần nữa').click().run()
    assert item(at, 'text_area', 'Viết bài từ trí nhớ').value == ''


def test_filter_random_full_essay_and_stable_selection_on_rerun():
    at = app()
    item(at.sidebar, 'selectbox', 'Dạng đề').set_value('Maps').run()
    assert item(at.sidebar, 'selectbox', 'Bài cần thuộc').value == '1.14'
    item(at.sidebar, 'button', '🎲 Chọn bài ngẫu nhiên').click().run()
    assert item(at.sidebar, 'selectbox', 'Bài cần thuộc').value == '1.15'
    at.run()
    assert item(at.sidebar, 'selectbox', 'Bài cần thuộc').value == '1.15'
    item(at.sidebar, 'selectbox', 'Học theo đoạn / toàn bài').set_value('full').run()
    assert reference(load_bank()[14], 'full') in prose(at)
    item(at.sidebar, 'selectbox', 'Dạng đề').set_value('Mixed chart').run()
    assert item(at.sidebar, 'selectbox', 'Bài cần thuộc').value == '1.13'
    assert item(at.sidebar, 'button', '🎲 Chọn bài ngẫu nhiên').disabled
    item(at.sidebar, 'selectbox', 'Chế độ học bài').set_value(ESSAY_MODES[1]).run()
    target = reference(load_bank()[12], 'full')
    item(at, 'text_area', 'Viết bài từ trí nhớ').set_value(target)
    item(at, 'button', 'Chấm bài').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] == 100
    assert at.session_state.events[-1]['data']['task_id'] == 'recall-full'


def test_multiple_choice_answer_feedback_next_and_no_implicit_answer():
    at = app()
    item(at.sidebar, 'button', 'Học cấu trúc').click().run()
    assert not at.exception
    assert at.title[0].value == 'Học cấu trúc bằng trắc nghiệm'
    assert len(item(at, 'radio', 'Chọn đáp án').options) == 3
    assert item(at, 'radio', 'Chọn đáp án').value is None
    item(at, 'button', 'Kiểm tra đáp án').click().run()
    assert not at.session_state.events
    item(at, 'radio', 'Chọn đáp án').set_value('how much')
    item(at, 'button', 'Kiểm tra đáp án').click().run()
    assert at.session_state.events[-1]['data']['score'] == 0
    assert '**Khung cần thuộc**' in prose(at)
    count = len(at.session_state.events)
    at.run()
    assert len(at.session_state.events) == count
    item(at, 'button', 'Làm lại câu này').click().run()
    item(at, 'radio', 'Chọn đáp án').set_value('how many')
    item(at, 'button', 'Kiểm tra đáp án').click().run()
    assert at.session_state.events[-1]['data']['score'] == 1
    assert at.session_state.events[-1]['data']['assisted']
    item(at, 'button', 'Cấu trúc tiếp theo →').click().run()
    assert item(at.sidebar, 'selectbox', 'Cấu trúc cần nhớ').value == 'intro-amount'
    assert not at.exception


def test_every_offered_structure_has_source_backed_choices():
    structures, _ = load_content()
    byid = {x['structure_id']:x for x in structures}
    for ids in GROUPS.values():
        for ident in ids:
            q = choice_question(byid[ident])
            assert len(q['options']) == len(set(q['options'])) == 3
            assert q['answer'] in q['options']
            assert q['prompt'].replace(' ______ ', q['answer']) == q['example']
            assert q['example'] == byid[ident]['examples'][0]
            assert q['explanation']
    bank = load_bank()
    for category in TYPES:
        assert filter_lessons(bank, category)
    assert [x['id'] for x in filter_lessons(bank, 'Maps')] == ['1.14','1.15']
    assert [x['id'] for x in filter_lessons(bank, 'Process')] == ['1.16','1.17','1.18']
    assert random_lesson(['1.14','1.15'], '1.14') == '1.15'


def test_all_structure_groups_render_and_switch_back_to_essays():
    at = app()
    item(at.sidebar, 'button', 'Học cấu trúc').click().run()
    for group in GROUPS:
        item(at.sidebar, 'selectbox', 'Dạng cấu trúc').set_value(group).run()
        assert not at.exception
        assert item(at, 'radio', 'Chọn đáp án')
    item(at.sidebar, 'button', 'Học thuộc bài').click().run()
    assert at.title[0].value == 'Ôn tập · Chép theo mẫu'
