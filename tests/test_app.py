from pathlib import Path
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'


def app():
    at=AppTest.from_file(str(APP),default_timeout=30)
    at.secrets['storage_mode']='demo'
    return at.run()


def test_pages_render():
    at=app()
    assert not at.exception
    for label in ['Thư viện cấu trúc','Luyện tập','Chữa bài & viết lại','Lịch sử & sổ lỗi','Cài đặt & dữ liệu']:
        at.sidebar.radio[0].set_value(label).run()
        assert not at.exception,label


def test_submit_rerun_retry_and_correction():
    at=app()
    at.sidebar.radio[0].set_value('Luyện tập').run()
    at.text_area[0].set_value('The diagrams show the landfill.')
    next(b for b in at.button if b.label=='Nộp bài').click().run()
    assert not at.exception
    assert len(at.session_state.events)==1
    at.run(); assert len(at.session_state.events)==1
    next(b for b in at.button if b.label=='Thử lại').click().run()
    at.text_area[0].set_value('The diagrams show how a landfill works.')
    next(b for b in at.button if b.label=='Nộp bài').click().run()
    assert len(at.session_state.events)==2
    assert at.session_state.events[1]['data']['retry_of']==at.session_state.events[0]['id']
    at.sidebar.radio[0].set_value('Chữa bài & viết lại').run()
    next(t for t in at.text_area if t.label=='Nhận xét từ bên ngoài').set_value('Kiểm tra bị động.')
    next(t for t in at.text_area if t.label=='Bản viết lại').set_value('The hole is dug in natural rock.')
    next(b for b in at.button if b.label=='Lưu nhận xét và bản viết lại').click().run()
    assert not at.exception
    assert at.session_state.events[-1]['kind']=='correction'


def test_settings_exam_date_survives_navigation():
    from datetime import date, timedelta
    at=app()
    at.sidebar.radio[0].set_value('Cài đặt & dữ liệu').run()
    next(w for w in at.date_input if w.label=='Ngày thi nếu đã biết').set_value(date(2027,6,1))
    next(w for w in at.selectbox if w.label=='Mốc 30 ngày là gì?').set_value('Đến ngày thi')
    next(b for b in at.button if b.label=='Lưu cài đặt').click().run()
    assert not at.exception
    assert at.session_state.settings['target_date']=='2027-06-01'
    assert at.session_state.events[-1]['kind']=='settings'
    at.sidebar.radio[0].set_value('Hôm nay').run()
    at.sidebar.radio[0].set_value('Cài đặt & dữ liệu').run()
    assert next(w for w in at.date_input if w.label=='Ngày thi nếu đã biết').value==date(2027,6,1)
    assert next(w for w in at.selectbox if w.label=='Mốc 30 ngày là gì?').value=='Đến ngày thi'
    next(w for w in at.date_input if w.label=='Ngày thi nếu đã biết').set_value(date.fromisoformat(at.session_state.settings['start_date'])-timedelta(days=1))
    next(b for b in at.button if b.label=='Lưu cài đặt').click().run()
    assert not at.exception
    assert at.error
    assert at.session_state.settings['target_date']=='2027-06-01'


def test_practice_data_is_table_and_all_modes_render():
    at=app()
    at.sidebar.radio[0].set_value('Luyện tập').run()
    next(w for w in at.selectbox if w.label=='Chọn đề').set_value('q004').run()
    assert len(at.dataframe)>0
    assert not at.get('json')
    for mode in ['Vận dụng','Quiz','Học thuộc']:
        next(w for w in at.radio if w.label=='Cách luyện').set_value(mode).run()
        assert not at.exception



def test_memory_structure_hints_follow_selected_part():
    at=app()
    at.sidebar.radio[0].set_value('Luyện tập').run()
    assert any(x.label=='Gợi ý cấu trúc áp dụng' for x in at.expander)
    next(w for w in at.selectbox if w.label=='Chọn đề').set_value('q014').run()
    assert any('how many' in x.value for x in at.markdown)
    next(w for w in at.selectbox if w.label=='Phần cần nhớ').set_value('overview').run()
    assert not at.exception
    assert any('most dramatic rise' in x.value for x in at.markdown)
    assert not any('The chart/table illustrates how many' in x.value for x in at.markdown)
