import html
import re
from streamlit.testing.v1 import AppTest
from core.content_validation import ROOT
from core.personal_bank import load_bank, reference
from ui.focused_study import STEPS


def app():
    at = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30)
    at.secrets['storage_mode'] = 'demo'
    return at.run()


def item(at, kind, label):
    return next(x for x in getattr(at, kind) if x.label == label)


def prose(at):
    return '\n'.join(html.unescape(re.sub('<[^>]+>', '', x.value)) for x in at.markdown)


def test_default_is_one_essay_section_with_three_steps():
    at = app()
    assert not at.exception
    assert at.title[0].value == 'Học bài mẫu'
    assert item(at, 'radio', 'Cách học').options == STEPS
    assert len(at.selectbox) == 2
    assert not at.metric
    assert not any(x.label == 'Dạng học thuộc' for x in at.selectbox)
    assert 'The graph illustrates how much waste' in prose(at)
    assert 'From 2005 to 2015, the figure' not in prose(at)


def test_recall_hidden_model_submission_and_no_duplicate():
    at = app()
    item(at, 'radio', 'Cách học').set_value(STEPS[2]).run()
    assert not at.exception
    assert 'The graph illustrates how much waste' not in prose(at)
    item(at, 'button', 'Kiểm tra').click().run()
    assert not at.session_state.events
    target = reference(load_bank()[0], 'introduction')
    item(at, 'text_area', 'Bài viết từ trí nhớ').set_value(target)
    item(at, 'button', 'Kiểm tra').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] == 100
    assert not at.session_state.events[-1]['data']['assisted']
    count = len(at.session_state.events)
    at.run()
    assert len(at.session_state.events) == count
    item(at, 'button', 'Luyện lại').click().run()
    assert item(at, 'text_area', 'Bài viết từ trí nhớ').value == ''


def test_two_primary_buttons_and_maps_process_examples():
    at = app()
    item(at.sidebar, 'button', 'Học cấu trúc').click().run()
    assert at.title[0].value == 'Học cấu trúc'
    assert not at.exception
    for group in ['Maps', 'Process', 'Biểu đồ số liệu']:
        item(at, 'selectbox', 'Dạng bài').set_value(group).run()
        assert not at.exception
        assert any(x.value == '**Ví dụ**' for x in at.markdown)
    item(at, 'button', 'Tiếp theo → Điền khuyết').click().run()
    assert item(at, 'radio', 'Cách học').value == STEPS[1]
    assert at.text_input
    item(at.sidebar, 'button', 'Học bài mẫu').click().run()
    assert at.title[0].value == 'Học bài mẫu'


def test_hint_remains_assisted_when_hidden_again():
    at = app()
    item(at, 'radio', 'Cách học').set_value(STEPS[2]).run()
    item(at, 'checkbox', 'Cần gợi ý chữ cái đầu').check().run()
    item(at, 'checkbox', 'Cần gợi ý chữ cái đầu').uncheck().run()
    item(at, 'text_area', 'Bài viết từ trí nhớ').set_value(reference(load_bank()[0], 'introduction'))
    item(at, 'button', 'Kiểm tra').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['assisted']
