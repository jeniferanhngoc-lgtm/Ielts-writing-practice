from streamlit.testing.v1 import AppTest
from core.content_validation import ROOT,load_content
from core.personal_bank import load_bank

def test_revised_lessons_reach_active_bank():
    es=load_content()[1]
    assert len(es)==18
    a=next(e for e in es if e['source_lesson_index']==3)
    b=next(e for e in es if e['source_lesson_index']==8)
    assert a['category']=='two_years'
    assert b['category']=='cot_lt4'
    assert a['data']['School B · Handwriting']==[7,7]
    assert b['data']['paper and packaging']==[230,250,350]
    for e in (a,b):
        assert (ROOT/e['asset_reference']).exists()
        lesson=next(l for l in load_bank() if l['id']==f"1.{e['source_lesson_index']}")
        assert lesson['sections']==e['paragraphs']
        assert len(' '.join(e['paragraphs'].values()).split())>=150
        assert e['quizzes'][0]['accepted_answers']==[e['paragraphs']['overview']]

def test_current_app_renders_revisions():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
    at.secrets['storage_mode']='demo'
    at.run()
    assert not at.exception
    for ident in ('q101','q041'):
        at.selectbox(key='study-exercise-picker').set_value(ident).run()
        assert not at.exception
        assert any('Mẫu đã cập nhật' in c.value for c in at.caption)
        target=next(e for e in load_content()[1] if e['exercise_id']==ident)['paragraphs']['introduction']
        next(w for w in at.text_area if w.label=='Ô viết').set_value(target)
        next(w for w in at.button if w.label=='Nộp bài').click().run()
        assert not at.exception
        assert at.session_state.events[-1]['data']['score']==100
        assert at.session_state.events[-1]['data']['reference_snapshot']==target
