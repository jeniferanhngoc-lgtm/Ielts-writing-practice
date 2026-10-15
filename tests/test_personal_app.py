from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from core.personal_bank import load_bank, reference, cloze
from ui.personal_memory import MODES

APP = Path(__file__).resolve().parents[1]/'app.py'


def app():
    at = AppTest.from_file(str(APP), default_timeout=45)
    at.secrets['storage_mode'] = 'demo'
    at.run()
    at.sidebar.radio[0].set_value('Học thuộc bài của tôi').run()
    assert not at.exception
    return at


def widget(at, kind, label):
    return next(x for x in getattr(at, kind) if x.label == label)


def test_all_modes_and_lessons_render():
    at = app()
    for lesson in load_bank():
        widget(at, 'selectbox', 'Chọn bài từ Word').set_value(lesson['id']).run()
        assert not at.exception, lesson['id']
    for mode in MODES:
        widget(at, 'selectbox', 'Dạng học thuộc').set_value(mode).run()
        assert not at.exception, mode


def test_memory_score_save_rerun_and_hints():
    at = app()
    widget(at, 'selectbox', 'Dạng học thuộc').set_value('Viết lại từ trí nhớ').run()
    target = reference(load_bank()[0], 'introduction')
    widget(at, 'text_area', 'Viết lại từ trí nhớ').set_value(target)
    widget(at, 'button', 'Nộp bài học thuộc').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] == 100
    assert not at.session_state.events[-1]['data']['assisted']
    count = len(at.session_state.events)
    at.run()
    assert len(at.session_state.events) == count
    widget(at, 'button', 'Nộp bài học thuộc').click().run()
    assert at.session_state.events[-1]['data']['assisted']
    widget(at, 'button', 'Bắt đầu lượt kiểm tra mới').click().run()
    assert not at.exception
    widget(at, 'checkbox', 'Hiện gợi ý chữ cái đầu').check().run()
    widget(at, 'checkbox', 'Hiện gợi ý chữ cái đầu').uncheck().run()
    widget(at, 'text_area', 'Viết lại từ trí nhớ').set_value(target)
    widget(at, 'button', 'Nộp bài học thuộc').click().run()
    assert at.session_state.events[-1]['data']['assisted']


def test_cloze_and_quiz_validation():
    at = app()
    widget(at, 'selectbox', 'Dạng học thuộc').set_value('Điền khuyết').run()
    _, answers = cloze(reference(load_bank()[0], 'introduction'))
    for i, answer in enumerate(answers):
        widget(at, 'text_input', f'Ô {i+1}').set_value(answer)
    widget(at, 'button', 'Kiểm tra điền khuyết').click().run()
    assert not at.exception
    event = at.session_state.events[-1]['data']
    assert event['score'] == event['max_score']
    widget(at, 'selectbox', 'Dạng học thuộc').set_value('Quiz & giải thích').run()
    count = len(at.session_state.events)
    widget(at, 'button', 'Nộp quiz').click().run()
    assert len(at.session_state.events) == count
    widget(at, 'radio', 'Câu nào là Overview của bài này?').set_value(reference(load_bank()[0], 'overview'))
    widget(at, 'button', 'Nộp quiz').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] == 1


def test_ai_requires_key_and_mocked_request_keeps_key_out_of_events():
    at = app()
    widget(at, 'selectbox', 'Dạng học thuộc').set_value('Hỏi ChatGPT').run()
    with patch.dict('os.environ', {'OPENAI_API_KEY': ''}):
        widget(at, 'button', 'Gửi câu hỏi, bài viết và ảnh đề tới OpenAI').click().run()
    assert not at.exception
    with patch('openai.OpenAI') as client:
        client.return_value.responses.create.return_value.output_text = 'Giải thích mẫu thử nghiệm.'
        widget(at, 'text_input', 'OpenAI API key (tùy chọn nếu đã cấu hình secrets)').set_value('test-key-never-persist')
        widget(at, 'button', 'Gửi câu hỏi, bài viết và ảnh đề tới OpenAI').click().run()
        assert not at.exception
        payload = client.return_value.responses.create.call_args.kwargs
        assert payload['store'] is False
        assert payload['input'][0]['content'][1]['type'] == 'input_image'
        assert 'test-key-never-persist' not in str(at.session_state.events)
