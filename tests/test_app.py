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
