from streamlit.testing.v1 import AppTest
from core.content_validation import ROOT
from core.review_schedule import reviews_from_attempts


def app():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
    at.secrets['storage_mode']='demo'
    at.run()
    at.sidebar.radio[0].set_value('Hôm nay').run()
    return at


def test_dashboard_test_route_hides_answers_until_submit():
    at=app()
    next(b for b in at.button if b.label=='Bắt đầu kiểm tra').click().run()
    assert not at.exception
    assert next(w for w in at.radio if w.label=='Chế độ học').value=='Kiểm tra'
    assert not any('Gợi ý đọc đề' in x.label for x in at.expander)
    assert not any('Gợi ý cấu trúc' in x.label for x in at.expander)
    assert not any('Xem bài mẫu' in x.label for x in at.checkbox)
    next(b for b in at.button if b.label=='Bắt đầu làm bài').click().run()
    next(w for w in at.text_area if w.label=='Bài kiểm tra của bạn').set_value('A remembered introduction.')
    next(b for b in at.button if b.label=='Nộp bài kiểm tra').click().run()
    assert not at.exception
    a=at.session_state.events[-1]['data']
    assert a['learning_mode']=='test' and not a['assisted']
    assert reviews_from_attempts([a])
    count=len(at.session_state.events);at.run();assert len(at.session_state.events)==count


def test_structure_test_is_separate_page_without_model():
    at=app()
    next(b for b in at.button if b.label=='Học bộ khung cốt lõi').click().run()
    next(b for b in at.button if b.key=='test-intro').click().run()
    assert not at.exception
    assert not any('Thư viện cấu trúc'==x.value for x in at.title)
    assert not any('The table illustrates how many' in x.value for x in at.markdown)
    next(w for w in at.text_area if w.label=='Gõ lại câu ví dụ từ trí nhớ').set_value('The table illustrates how many cars were produced.')
    next(b for b in at.button if b.label=='Nộp câu').click().run()
    assert at.session_state.events[-1]['data']['learning_mode']=='test'


def test_assisted_work_does_not_advance_mastery():
    a=dict(exercise_id='q001',task_id='memory-introduction',grading_type='memory',score=100,max_score=100,submitted_at='2026-10-13T10:00:00+07:00',assisted=True)
    assert not reviews_from_attempts([a])
    assert reviews_from_attempts([dict(a,assisted=False)])
