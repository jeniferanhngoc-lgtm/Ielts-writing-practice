from streamlit.testing.v1 import AppTest
from core.content_validation import ROOT
from ui.answer_diff import answer_diff_html

def test_inline_diff_safe_and_missing():
    markup=answer_diff_html('<script>fell</script>', 'rose sharply')
    assert '<script>' not in markup and '&lt;' in markup
    assert '#b91c1c' in markup
    assert 'Thiếu: sharply' in answer_diff_html('rose', 'rose sharply')
    assert '#9a3412' in answer_diff_html('fell', 'rose', True)

def test_independent_no_model_and_submit():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
    at.secrets['storage_mode']='demo'
    at.run()
    next(w for w in at.radio if w.label=='Cách học').set_value('Tự làm bài').run()
    assert not at.exception
    assert not any(w.label=='Hiện mẫu để kiểm tra' for w in at.checkbox)
    assert len(at.text_area)==1
    assert not any('Dàn ý' in w.label for w in at.expander)
    at.text_area[0].set_value('The chart shows waste. Overall, production fell.')
    next(w for w in at.button if w.label=='Nộp toàn bài').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['data']['score'] is None
    assert at.session_state.events[-1]['data']['study_mode']=='independent'
    assert any('#9a3412' in w.value for w in at.markdown)
