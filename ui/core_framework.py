"""Compact study route, adapted to chart meaning rather than chart shape."""
import html
import re
import streamlit as st

CORE=[
 ('1 · Introduction', 'The chart illustrates how many [plural noun] [verb] … . / how much [uncountable noun] [verb] … .', 'Đếm được: how many cars were produced; không đếm được: how much electricity was generated. Chi tiêu: how much people spent. Với % giữ the percentage/proportion of … .'),
 ('2 · Overview', 'Overall, there was an increase/decline in [A], while [B] … . In addition, [C] had the highest/lowest figure.', 'Nêu xu hướng chung + điểm nổi bật. So sánh tĩnh bỏ xu hướng, viết Overall, A had the highest figure, while B had the lowest. Không dùng consistently nếu có ngoại lệ.'),
 ('3 · Body — khung chính', 'The figure for [A] started at [X], after which it rose/fell to [Y], before ending the period at [Z].', 'Dùng khi có đủ các mốc và diễn biến phù hợp. Chỉ hai mốc: The figure for A rose/fell from X to Y. Không tạo thêm mốc giữa.'),
 ('4 · Body — tránh lặp', '[Initial data], with a subsequent increase/decline to [Y] and a final rise/fall to [Z].', 'Sau with là cụm danh từ. Học một khung thay thế này trước; không cần học hết các biến thể.'),
 ('5 · So sánh và nối nhóm', '…, while … . / …, compared with … . / The figures for A and B were X and Y respectively.', 'While nối mệnh đề; compared with + đối tượng/số liệu tương ứng; respectively ghép đúng thứ tự. Dùng cho biểu đồ theo thời gian, tĩnh và kết hợp.'),
]
EXTRA={
 'maps':('Maps', 'The maps illustrate how [place] changed … . Overall, … . [A] was replaced by / converted into [B], while [C] remained unchanged.', 'Chia body theo khu vực. Quá khứ: was/were; kế hoạch: is planned to be … .'),
 'process':('Process', 'The diagram illustrates how [product] is produced. Overall, the process begins with … and ends with … . First, …, after which … . Finally, … .', 'Hiện tại đơn cho quy trình nói chung; bị động khi chủ ngữ nhận tác động: is/are + V3.'),
 'natural_process':('Natural process', 'The diagram illustrates how [organism] develops. Overall, … . First, …, after which … . The cycle then begins again.', 'Chỉ dùng cycle khi có vòng lặp. Ưu tiên chủ động cho phát triển tự nhiên, nhưng chọn thể theo từng hành động.'),
 'mechanism':('Cách hoạt động', 'The diagram illustrates how [device] works. Overall, it is used to … . [A] is connected to [B]. … flows through … .', 'Body 1 cấu tạo, body 2 vận hành nếu phù hợp hình; thường hiện tại đơn.'),
 'future':('Dự báo', '… is expected to rise/fall to … . / … is projected to reach … .', 'Giữ nguyên khung, thay động từ phần dự báo. Không trình bày dự báo như số liệu đã xác nhận.'),
 'odd':('Dạng đặc biệt', 'Overall, the main differences are … . A is larger/smaller/longer than B, while … .', 'Chọn đặc điểm thực sự có trong hình. Không ép so sánh hình dạng thành tăng/giảm số liệu.'),
}

# Identify literal scaffold phrases, not grammar correctness or complete sentence parsing.
PATTERN=re.compile(r"\b(?:the (?:chart|charts|graph|graphs|table|diagram|diagrams|maps?) (?:illustrates?|shows?|compares?)|how many|how much|the (?:number|amount|percentage|proportion) of|the figures? for|overall|there (?:was|were|is|are) an? (?:increase|decrease|rise|fall|decline)|in addition|started at|after which|before ending the period at|ending (?:the period )?at|with a subsequent|followed by|compared (?:with|to)|respectively|while|whereas|similarly|by contrast|meanwhile|(?:is|are) (?:expected|projected|predicted) to|(?:was|were|is|are) (?:replaced by|converted into)|remained unchanged|(?:begins?|beginning) with|(?:ends?|ending) with|the process continues with|once|first|finally|rose|fell|increased|decreased|from|to)\b",re.I)


def highlighted_html(text):
    text=str(text); chunks=[];last=0
    for match in PATTERN.finditer(text):
        chunks.append(html.escape(text[last:match.start()]))
        chunks.append('<strong style="color:#9a3412;background:#ffedd5;padding:0 2px;border-radius:3px">'+html.escape(match.group())+'</strong>')
        last=match.end()
    chunks.append(html.escape(text[last:]))
    return '<div style="white-space:pre-wrap;line-height:1.85;margin-bottom:0.75rem">'+''.join(chunks)+'</div>'


def show_highlighted(text):
    st.markdown(highlighted_html(text),unsafe_allow_html=True)


def framework_panel(category='all'):
    st.subheader('Khung cốt lõi · học ít, dùng nhiều')
    st.write('Giữ bố cục Introduction → Overview → Body 1 → Body 2. Ưu tiên 5 khung dưới đây cho biểu đồ số liệu; chỉ bổ sung khung riêng theo dạng.')
    for title,template,note in CORE:
        with st.expander(title,expanded=title.startswith('1')):
            show_highlighted(template);st.caption(note)
    for key,(title,template,note) in EXTRA.items():
        if category in ('all',key):
            with st.expander('Khung riêng · '+title):
                show_highlighted(template);st.caption(note)
    st.caption('Đổi thì và chủ động/bị động theo đề: people spent / money was spent; cars were produced / electricity was generated. Các khung có thể rút ngắn, không cần dùng hết trong một bài.')
