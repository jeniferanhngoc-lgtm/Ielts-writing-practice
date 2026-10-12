"""Study scaffolding, separate from the answer and exact-match grading."""
import streamlit as st


def memory_hints(exercise, structures, part):
    role=part.split('-sentence-')[0]
    category=exercise['category']
    with st.expander('Gợi ý cấu trúc áp dụng',expanded=True):
        st.caption('Khung có chỗ trống để tự điền. Bật “Hiện mẫu để học” khi muốn xem câu mẫu chính xác; điểm học thuộc vẫn so với mẫu đó.')
        if role in ('introduction','full'):
            st.markdown('**Introduction — chọn theo thông tin trong đề**')
            if category=='maps':
                st.write('The maps illustrate how [place] changed between [year] and [year].')
                st.caption('Bản đồ quá khứ dùng changed; hiện trạng dùng is arranged; quy hoạch dùng proposed changes / is planned to change.')
            elif category in ('process','natural_process','mechanism'):
                st.write('The diagram illustrates how [subject] [verb].')
                st.caption('Sản xuất: how [product] is produced. Tự nhiên: how [organism] develops. Máy móc: how [device] works. Chọn theo đúng đề.')
            else:
                st.write('The chart/table illustrates how many [plural noun] [verb] [place/time].')
                st.write('The chart/table illustrates how much [uncountable noun] [verb] [place/time].')
                st.write('Chi tiêu: … how much [people/governments] spent on [item] … .')
                st.caption('Nếu đơn vị là %: dùng the percentage/proportion of … để giữ nghĩa tỷ lệ. How many không tự thể hiện phần trăm. Biểu đồ kết hợp cần giới thiệu cả hai biểu đồ.')
        if role in ('overview','full'):
            st.markdown('**Overview — chỉ chọn nhận xét đúng với hình**')
            if category=='maps':
                st.write('Overall, the area saw several changes, including [main change] and [main change].')
            elif category=='natural_process':
                st.write('Overall, the cycle involves [main stages], before the cycle begins again.')
                st.caption('Chỉ dùng cycle nếu hình thực sự là chu kỳ; không bắt mọi quá trình tự nhiên có vòng lặp.')
            elif category=='process':
                st.write('Overall, the process comprises several stages, beginning with [noun/V-ing] and ending with [noun/V-ing].')
            elif category=='mechanism':
                st.write('Overall, the system is designed to [purpose], using [main components].')
            elif category in ('static','odd'):
                st.write('Overall, [A] had the highest [measure], while [B] had the lowest. / The main differences were [features].')
            else:
                st.write('Overall, there was an increase/decline in [measure], while [opposite trend] was seen in [group].')
                st.write('…, with the most dramatic rise being seen in [group].')
                st.caption('Tất cả cùng xu hướng: dùng in all … examined. Consistently = đúng suốt kỳ; generally = có ngoại lệ. Despite this chỉ dùng khi hai nhận xét có sự tương phản.')
        if role in ('body1','body2','full'):
            st.markdown('**Khung body gắn với đề này**')
            selected=[s for s in structures if s['structure_id'] in exercise['target_structure_ids'] and s['paragraph_role']=='body' and category in s['categories']]
            for item in selected:
                st.write(item['template'])
                st.caption(item['usage_conditions'])
            if not selected:
                st.caption('Dựa vào thứ tự bước hoặc đặc điểm trong hình; không ép đề vào khung tăng/giảm.')
        st.markdown('**Chọn thì và chủ động / bị động**')
        st.write('“The chart illustrates …” dùng hiện tại để giới thiệu hình. Động từ ở phần sau theo thời gian dữ liệu, không nhất thiết cùng thì với illustrates.')
        if category=='future':
            st.info('Đề có dự báo: tách phần đã xảy ra và phần dự kiến. Dùng rose/was produced cho quá khứ; is expected to rise / is projected to be produced cho dự báo. Không đổi dự báo thành sự thật chỉ vì năm đó đã qua ngoài đời.')
        elif category in ('process','natural_process','mechanism'):
            st.info('Quy trình hoặc cơ chế nói chung: thường dùng hiện tại đơn. Nếu đề mô tả quy trình trong quá khứ hoặc kế hoạch thì đổi theo đề.')
        else:
            st.info('Dữ liệu trong giai đoạn đã kết thúc: quá khứ đơn (rose, spent, was/were produced). Hiện trạng: hiện tại đơn (rises, spends, is/are produced). Quy hoạch/dự kiến: is planned/expected to … . Đề không ghi năm: đọc ngữ cảnh, không tự thêm năm.')
        st.write('Chủ động khi chủ ngữ thực hiện hành động: people spent money; water evaporates. Bị động khi chủ ngữ nhận tác động: money was spent; cars were produced.')
        st.write('Bị động: hiện tại is/are + V3; quá khứ was/were + V3; tương lai will be + V3. Dự báo: is/are expected to be + V3.')
        st.caption('How much không bắt buộc bị động. Money/energy + was/is; cars + were/are. Tự nhiên có thể dùng cả chủ động và bị động theo từng hành động.')
        st.caption('Nguồn: Introduction.docx của bạn và PDF thầy Kiên; phần phân biệt thì, điều kiện áp dụng và sửa ngữ pháp là bổ sung biên tập. Khung không phải đáp án duy nhất đúng tiếng Anh.')
