import uuid
import streamlit as st
from core.review_schedule import now
from storage.store import LocalStore, merge_events
from core.content_validation import ROOT


def records(kind):
    return [e['data'] for e in st.session_state.events if e['kind']==kind]


def emit(kind,data,event_id=None):
    event = {'id':event_id or str(uuid.uuid4()),'kind':kind,'data':data}
    st.session_state.events = merge_events(st.session_state.events,[event])
    if event['id'] not in st.session_state.persisted:
        st.session_state.pending[event['id']] = event
    flush()
    return event['id']


def flush():
    store = st.session_state.get('store')
    if not store:
        return
    for ident,event in list(st.session_state.pending.items()):
        try:
            store.save(event)
        except Exception:
            st.session_state.save_error = 'Chưa lưu được. Bài vẫn còn trong phiên; thử lưu lại hoặc xuất bản sao JSON.'
            break
        else:
            st.session_state.persisted.add(ident)
            del st.session_state.pending[ident]
            st.session_state.save_error = ''


def initialize():
    defaults = dict(events=[],pending={},persisted=set(),save_error='',store=None,
                    timer={'seconds':0,'running_since':None}, settings={'learner_id':'learner-1','start_date':now().date().isoformat(),'daily_minutes':45,'sundays':True,'target_date':'','target_meaning':'Chưa xác định'})
    for key,value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    try:
        mode = st.secrets.get('storage_mode','demo')
    except Exception:
        mode = 'demo'
    st.session_state.storage_mode = mode
    if not st.session_state.get('loaded'):
        try:
            if mode == 'local':
                st.session_state.store = LocalStore(ROOT/'private_data/progress.sqlite3')
            elif mode == 'sheets':
                from storage.sheets_store import SheetsStore
                st.session_state.store = SheetsStore(st.secrets['gcp_service_account'],st.secrets['spreadsheet_id'])
            elif mode != 'demo':
                raise ValueError('Chế độ lưu không hợp lệ')
            if st.session_state.store:
                loaded = st.session_state.store.load()
                st.session_state.events = merge_events(st.session_state.events,loaded)
                st.session_state.persisted.update(e['id'] for e in loaded)
                for ident in list(st.session_state.pending):
                    if ident in st.session_state.persisted:
                        del st.session_state.pending[ident]
            settings = records('settings')
            if settings:
                st.session_state.settings = settings[-1]
            st.session_state.loaded = True
            st.session_state.load_error = ''
        except Exception:
            st.session_state.store = None
            st.session_state.load_error = 'Chưa đọc được kho lưu trữ. Kiểm tra cấu hình/kết nối; chưa xác nhận đồng bộ.'


def save_banner():
    if st.session_state.get('load_error'):
        st.warning(st.session_state.load_error)
    if st.session_state.storage_mode == 'demo':
        st.info('Chế độ demo: tiến độ chỉ nằm trong phiên. Xuất JSON trước khi đóng trang, hoặc cấu hình lưu local/Google Sheets.')
    elif st.session_state.storage_mode == 'local':
        st.caption('Lưu SQLite trên máy này. Khi đưa lên Streamlit Cloud, chuyển sang Google Sheets để lưu qua redeploy.')
    if st.session_state.pending:
        st.warning(f"{len(st.session_state.pending)} bản ghi chưa lưu lâu dài. {st.session_state.save_error}")
    elif st.session_state.persisted:
        st.caption('Các thay đổi hiện tại đã được kho lưu trữ xác nhận.')
    if st.session_state.pending and st.session_state.store and st.button('Thử lưu lại'):
        flush()
        st.rerun()
    if st.session_state.get('load_error') and st.button('Kết nối lại kho lưu trữ'):
        st.session_state.loaded = False
        st.rerun()
