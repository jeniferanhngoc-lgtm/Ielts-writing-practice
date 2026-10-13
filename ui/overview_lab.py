"""Overview observation worksheet; free observations use self-review, not exact matching."""
import streamlit as st
from ui.learning_modes import task_state, submit, result_header, retry
from ui.core_framework import show_highlighted

FIELDS=['Xu hướng chung: tăng / giảm / hỗn hợp','Highest figures — cao nhất','Lowest figures — thấp nhất','Most drastic changes — thay đổi mạnh nhất','Stability — ổn định','Similar patterns — xu hướng giống nhau','Opposite patterns — xu hướng ngược nhau']


def reference(e):
    if e['exercise_id']=='q085':
        return {
        'Thay đổi theo thời gian':'Có: 1990–2005.',
        FIELDS[0]:'Italy, Portugal và UK giảm đầu–cuối; USA tăng đầu–cuối.',
        FIELDS[1]:'Portugal nhìn chung cao nhất; Italy vượt lên vào năm 2000. Dùng generally, không dùng consistently cho Portugal.',
        FIELDS[2]:'UK thấp nhất ở tất cả các mốc → consistently.',
        FIELDS[3]:'Portugal giảm mạnh nhất xét chênh lệch điểm phần trăm đầu–cuối trong các số liệu xấp xỉ đã đọc.',
        FIELDS[4]:'Không có nhóm giữ nguyên suốt kỳ. Không gọi một biến động nhỏ là hoàn toàn không đổi.',
        FIELDS[5]:'Italy, Portugal và UK cùng giảm nếu so đầu–cuối; diễn biến ở giữa không hoàn toàn giống nhau.',
        FIELDS[6]:'USA tăng đầu–cuối, ngược với ba nước còn lại.'}
    return None


def overview_lab(e):
    st.subheader('Đọc biểu đồ → chọn ý → viết overview')
    st.caption('Điền các mục để quan sát, rồi chỉ chọn 2–3 đặc điểm nổi bật để viết. Không cần đưa đủ 8 mục vào overview.')
    key,state=task_state(e,'overview-analysis')
    if state['submitted']:
        result_header(state)
        st.markdown('**Nhận xét bạn đã ghi**')
        from ui.readable import show_answer
        show_answer(state['result']['answer'])
        notes=reference(e)
        if notes:
            st.markdown('**Đối chiếu 8 mục**');show_answer(notes)
        else:
            st.markdown('**Phân tích đề để đối chiếu**');st.write(e['analysis_vi'])
            st.caption('Đề này chưa có đáp án đóng cho từng mục. Tự đối chiếu với ảnh, phân tích và hai body; không tự động kết luận nhận xét khác mẫu là sai.')
            with st.expander('Chi tiết bằng chứng trong hai body'):
                show_highlighted(e['paragraphs']['body1']);show_highlighted(e['paragraphs']['body2'])
        st.markdown('**Overview mẫu đã chọn lọc**')
        show_highlighted(e['paragraphs']['overview'])
        st.info('there was an increase/decline in … → while [opposite trend] … → In addition, [highest/lowest or strongest change] … . Không dùng khung xu hướng cho so sánh tĩnh.')
        st.caption('Consistently: đúng ở mọi mốc. Generally: nhìn chung, có ngoại lệ. Nối hai mệnh đề bằng “A …; meanwhile, B … .” hoặc tách thành hai câu. Với while: “A …, while B … .”')
        retry(key,state);return
    if e['category'] in ('maps','process','natural_process','mechanism','odd'):
        st.info('Các mục số liệu có thể không áp dụng. Với Maps chọn thay đổi lớn; Process chọn đầu–cuối/giai đoạn; chu kỳ chọn vòng lặp. Ghi “Không áp dụng” ở mục không phù hợp.')
    with st.form(key+str(state['round'])):
        answers={'Thay đổi theo thời gian':st.radio('Thay đổi theo thời gian',['Có','Không','Không áp dụng / cần phân biệt các biểu đồ'],index=None)}
        for field in FIELDS:
            answers[field]=st.text_input(field,placeholder='Ghi nhận xét; hoặc Không có / Không áp dụng / Chưa xác định')
        answers['Hai hoặc ba ý nổi bật nhất']=st.text_area('Chọn 2–3 ý đưa vào overview',max_chars=5000)
        answers['Overview tự viết']=st.text_area('Viết overview từ những ý đã chọn',max_chars=5000)
        sent=st.form_submit_button('Nộp phân tích và xem overview mẫu',type='primary')
    if sent:
        if not all(v and v.strip() for v in answers.values()):st.warning('Điền đủ mục; mục không phù hợp ghi Không áp dụng.');return
        submit(e,'overview-analysis',state,answers,{'Phân tích':reference(e) or e['analysis_vi'],'Overview':e['paragraphs']['overview']},task_context={'purpose':'Phân tích 8 mục trước khi chọn ý overview; tự đối chiếu, không chấm so chuỗi.'})
