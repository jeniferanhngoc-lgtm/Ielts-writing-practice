"""Compact study route, adapted to chart meaning rather than chart shape."""
import html
import re
import streamlit as st

CORE=[
 ('1 · Introduction', 'The chart illustrates how many [plural noun] [verb] … . / how much [uncountable noun] [verb] … .', 'Đếm được: how many cars were produced; không đếm được: how much electricity was generated. Chi tiêu: how much people spent. Với % giữ the percentage/proportion of … .'),
 ('2 · Overview', 'Overall, there was an increase/decline in [A], while [B] … . In addition, [C] had the highest/lowest figure.', 'Nêu xu hướng chung + điểm nổi bật. So sánh tĩnh bỏ xu hướng, viết Overall, A had the highest figure, while B had the lowest. Không dùng consistently nếu có ngoại lệ.'),
 ('3 · Body — khung chính', 'The figure for [A] started at [X], after which it experienced a rise/decline to [Y], before ending the period at [Z].', 'Dùng khi có đủ các mốc và diễn biến phù hợp. Chỉ hai mốc: The figure for A rose/fell from X to Y. Không tạo thêm mốc giữa.'),
 ('4 · Body — tránh lặp', '[Initial data], with a subsequent increase/decline to [Y] and a final rise/fall to [Z].', 'Sau with là cụm danh từ. Học một khung thay thế này trước; không cần học hết các biến thể.'),
 ('5 · So sánh và nối nhóm', 'Similarly, … . / Conversely, … . / …, while … . / …, compared with … . / The figures for A and B were X and Y respectively.', 'Conversely dùng khi ngược xu hướng; Similarly khi tương tự. While nối mệnh đề; compared with + đối tượng/số liệu tương ứng; respectively ghép đúng thứ tự. Dùng cho biểu đồ theo thời gian, tĩnh và kết hợp.'),
]
EXTRA={
 'mixed':('Mixed chart', 'The [first chart] illustrates …, while the [second chart] shows … . Overall, [main feature 1]. In addition, [main feature 2]. Body 1: [first chart]. Body 2: [second chart].', 'Dùng lại khung xu hướng hoặc so sánh trong từng body; giữ đúng đơn vị của từng biểu đồ.'),
 'maps':('Maps', 'The maps illustrate how [place] changed … . Overall, … . [A] was replaced by / converted into [B], while [C] remained unchanged.', 'Chia body theo khu vực. Quá khứ: was/were; kế hoạch: is planned to be … .'),
 'process':('Process', 'The diagram illustrates how [product] is produced. Overall, the process begins with … and ends with … . First, …, after which … . Finally, … .', 'Hiện tại đơn cho quy trình nói chung; bị động khi chủ ngữ nhận tác động: is/are + V3.'),
 'natural_process':('Natural process', 'The diagram illustrates how [organism] develops. Overall, … . First, …, after which … . The cycle then begins again.', 'Chỉ dùng cycle khi có vòng lặp. Ưu tiên chủ động cho phát triển tự nhiên, nhưng chọn thể theo từng hành động.'),
 'mechanism':('Cách hoạt động', 'The diagram illustrates how [device] works. Overall, it is used to … . [A] is connected to [B]. … flows through … .', 'Body 1 cấu tạo, body 2 vận hành nếu phù hợp hình; thường hiện tại đơn.'),
 'future':('Dự báo', '… is expected to rise/fall to … . / … is projected to reach … .', 'Giữ nguyên khung, thay động từ phần dự báo. Không trình bày dự báo như số liệu đã xác nhận.'),
 'odd':('Dạng đặc biệt', 'Overall, the main differences are … . A is larger/smaller/longer than B, while … .', 'Chọn đặc điểm thực sự có trong hình. Không ép so sánh hình dạng thành tăng/giảm số liệu.'),
}

# Identify literal scaffold phrases, not grammar correctness or complete sentence parsing.
PATTERN=re.compile(r"\b(?:the (?:chart|charts|graph|graphs|table|diagram|diagrams|maps?) (?:illustrates?|shows?|compares?)|how many|how much|the (?:number|amount|percentage|proportion) of|the figures? for|overall|there (?:was|were|is|are) an? (?:increase|decrease|rise|fall|decline)|in addition|started at|after which|before ending the period at|ending (?:the period )?at|with a subsequent|followed by|compared (?:with|to)|respectively|while|whereas|similarly|conversely|similar changes|to a (?:greater|lesser) extent|with respective figures (?:of|being)|twice as much|three times as much|exceeded those for|rose to a peak of|before falling to|in order to|so that|at which point|being turned into|being converted into|was constructed|was built|was demolished|were cut down|were cleared|were planted|was extended|was widened|was reopened|was accompanied by|by contrast|meanwhile|(?:is|are) (?:expected|projected|predicted) to|(?:was|were|is|are) (?:replaced by|converted into)|remained unchanged|(?:begins?|beginning) with|(?:ends?|ending) with|the process continues with|once|first|finally|rose|fell|increased|decreased|from|to)\b",re.I)


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
    if category in ('all','cot_4','cot_lt4','cot_5plus','two_years','future','mixed'):
        with st.expander('Overview — chọn 1 trong 3 tình huống theo ghi chú của bạn'):
            show_highlighted('Cùng xu hướng: Overall, there was an increase/decline in [measure] in all [groups] examined. In addition, [A] consistently had the highest figures, while [B] had the lowest.')
            show_highlighted('Khác xu hướng: Overall, there was a decline in [measure] in [group 1], while a rise was seen in [group 2]. In addition, [A] generally had the highest figures.')
            show_highlighted('Vượt lên dẫn đầu: Overall, the figure for [A] increased to surpass that of [B], making it the most [used/consumed] [category] from [year] onwards.')
            st.caption('Nếu cần nhấn mạnh mức tăng: with the most dramatic rise being seen in the figures for A. Despite this chỉ dùng nếu nhận xét tiếp theo thực sự tương phản. Chỉ nói dẫn đầu từ một năm khi hình xác nhận vị trí đó.')
        with st.expander('Body — biến thể bổ sung, chưa cần học hết'):
            show_highlighted('Similar changes, but to a lesser/greater extent, were seen in the figure for [B], which [verb] … .')
            show_highlighted('[A] rose to a peak of [X] in [year], before falling to [Y].')
            show_highlighted('[A] started at [X], after which it fluctuated until [year], before ending the period at [Y].')
            show_highlighted('[A] started at [X] and continued to rise, reaching [Y] in the final year.')
            show_highlighted('Conversely, the figure for [B] fell to [Y].')
            st.caption('Chuẩn hóa từ ghi chú Introduction: experienced (quá khứ); reach a peak of / peak at; a slight decrease (danh từ), decreased slightly (động từ). Mẫu số liệu phải kiểm tra lại ảnh trước khi học thuộc.')
    for key,(title,template,note) in EXTRA.items():
        if category in ('all',key):
            with st.expander('Khung riêng · '+title):
                show_highlighted(template);st.caption(note)
    st.caption('Đổi thì và chủ động/bị động theo đề: people spent / money was spent; cars were produced / electricity was generated. Các khung có thể rút ngắn, không cần dùng hết trong một bài.')
