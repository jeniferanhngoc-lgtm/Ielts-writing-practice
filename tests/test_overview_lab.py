from streamlit.testing.v1 import AppTest
from core.content_validation import ROOT,load_content
from ui.overview_lab import FIELDS,reference


def test_overview_sources_are_synchronized():
    for e in load_content()[1]:
        if e['status']!='verified':continue
        quiz=next(q for q in e['quizzes'] if q['quiz_id']=='overview-choice')
        assert quiz['accepted_answers']==[e['paragraphs']['overview']]
        assert e['paragraphs']['overview'] in quiz['options']
    e=next(e for e in load_content()[1] if e['exercise_id']=='q085')
    assert 'generally' in e['paragraphs']['overview']
    assert len(reference(e))==8


def test_overview_worksheet_requires_observations_then_reveals_model():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
    at.secrets['storage_mode']='demo';at.run()
    at.sidebar.radio[0].set_value('Luyện tập').run()
    next(w for w in at.selectbox if w.label=='Chọn đề').set_value('q085').run()
    next(w for w in at.selectbox if w.label=='Dạng luyện tập').set_value('Phân tích & viết overview').run()
    next(b for b in at.button if b.label=='Nộp phân tích và xem overview mẫu').click().run()
    assert at.warning and not at.session_state.events
    next(w for w in at.radio if w.label=='Thay đổi theo thời gian').set_value('Có')
    for field in FIELDS:next(w for w in at.text_input if w.label==field).set_value('Nhận xét của tôi')
    for w in at.text_area:w.set_value('My overview observations.')
    next(b for b in at.button if b.label=='Nộp phân tích và xem overview mẫu').click().run()
    assert not at.exception
    assert len(at.session_state.events)==1
    assert at.session_state.events[0]['data']['task_id']=='overview-analysis'
    assert any('generally' in w.value for w in at.markdown)
    at.run();assert len(at.session_state.events)==1
