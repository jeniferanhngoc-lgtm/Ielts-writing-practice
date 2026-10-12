"""Google Sheets setup without exposing credentials in the learner UI."""
import streamlit as st
from core.content_validation import ROOT


def sheets_panel():
    st.subheader('Kết nối Google Sheets')
    mode=st.session_state.storage_mode
    if mode=='sheets' and st.session_state.get('loaded') and st.session_state.get('store'):
        st.success('Đã kết nối và đọc lịch sử từ Google Sheets.')
        st.caption('Bài nộp, cài đặt, bản sửa và buổi học đã kết thúc được lưu tự động. Trạng thái ghi hiển thị cuối trang.')
    elif mode=='sheets':
        st.warning('Đã chọn Google Sheets nhưng chưa kết nối được. Kiểm tra API, quyền chia sẻ và Secrets.')
    else:
        st.info('Chưa bật Google Sheets. Hiện đang lưu '+('trên máy này.' if mode=='local' else 'trong phiên trình duyệt.'))
    with st.expander('Hướng dẫn kết nối qua Google Cloud Console',expanded=mode!='sheets'):
        st.markdown("""1. Mở **Google Cloud Console**, tạo/chọn project. Trong **APIs & Services → Library**, bật **Google Sheets API** và **Google Drive API**.
2. Vào **IAM & Admin → Service Accounts**, tạo service account. Mở tài khoản đó → **Keys → Add key → Create new key → JSON**.
3. Tạo một Google Sheet riêng. Bấm **Share**, thêm địa chỉ `client_email` trong JSON với quyền **Editor**.
4. Trên ứng dụng Streamlit Cloud, mở **Manage app → Settings → Secrets**. Điền cấu hình theo mẫu bên dưới, lấy giá trị từ JSON. Không đưa khóa lên GitHub hoặc gửi vào chat.
5. Lưu Secrets và khởi động lại ứng dụng. Trang này sẽ báo khi đọc được lịch sử.
6. Nộp thử một bài, mở phiên trình duyệt mới và kiểm tra **Lịch sử** để xác nhận đọc lại được bài vừa lưu.

`spreadsheet_id` là phần nằm giữa `/d/` và `/edit` trong link Google Sheet. Tab **Events** được ứng dụng tạo tự động; giữ nguyên tab này để bảo toàn lịch sử.

Nếu đã có tiến độ cũ, **xuất JSON trước khi đổi cấu hình**, rồi nhập lại sau khi kết nối Sheets.""")
        st.link_button('Mở Google Cloud Console','https://console.cloud.google.com/')
        st.link_button('Tạo Google Sheet','https://sheets.google.com/create')
        st.code((ROOT/'.streamlit/secrets.example.toml').read_text(encoding='utf-8'),language='toml')
        st.caption('Chỉ điền thông tin thật trong Secrets của Streamlit. Máy cá nhân dùng .streamlit/secrets.toml.')
