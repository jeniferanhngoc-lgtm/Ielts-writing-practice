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

# Illustrative practice data, independent of whichever chart is currently open.
CORE_EXAMPLES=[
 [
  ('Đếm được', 'The table illustrates how many cars were produced in three countries between 2000 and 2010.', 'cars là danh từ đếm được số nhiều; were produced là bị động quá khứ.'),
  ('Không đếm được', 'The chart illustrates how much electricity was generated in France between 2000 and 2010.', 'electricity không đếm được; was generated là bị động quá khứ.'),
  ('Chi tiêu', 'The chart illustrates how much people spent on food in 2010.', 'how much nói về số tiền; people là chủ ngữ của spent.'),
  ('Tỷ lệ phần trăm', 'The graph illustrates the percentage of people who used public transport between 2000 and 2010.', 'Giữ percentage khi đề cho %, thay vì chuyển thành số người.'),
 ],
 [
  ('Xu hướng đối lập', 'Overall, spending on online games increased, while spending on console games declined. In addition, handheld games had the highest sales throughout the period.', 'Câu 1 nêu xu hướng; câu 2 nêu nhóm dẫn đầu. Chỉ dùng throughout nếu đúng ở mọi mốc.'),
  ('So sánh tĩnh', 'Overall, cars were the most popular means of transport, while bicycles were the least popular.', 'Không có thay đổi theo thời gian thì so sánh cao/thấp, không tự thêm tăng/giảm.'),
 ],
 [
  ('Ba mốc', 'The figure for company A started at 12 tonnes in 2000, after which it experienced a decline to 11 tonnes in 2005, before ending the period at 8 tonnes in 2015.', 'A = company A; X = 12; Y = 11; Z = 8. Nhớ ba nhịp: bắt đầu → chuyển biến → kết thúc.'),
  ('Chỉ hai mốc', 'The figure for company A fell from 12 tonnes in 2000 to 8 tonnes in 2015.', 'Chỉ có hai mốc thì dùng from … to …; không thêm diễn biến ở giữa.'),
 ],
 [
  ('with + cụm danh từ', 'Sales stood at 10 million dollars in 2000, with a subsequent increase to 15 million in 2005 and a final rise to 20 million in 2010.', 'Sau with: a subsequent increase và a final rise là các cụm danh từ; không viết with increased.'),
 ],
 [
  ('Similarly / Conversely', 'Spending on online games rose from 1 to 9 billion dollars. Similarly, spending on mobile phone games increased. Conversely, spending on console games fell.', 'Similarly nối hai nhóm cùng tăng; Conversely chuyển sang nhóm giảm.'),
  ('while / compared with', 'The figure for A was 40%, while that for B was 25%. The figure for A was 40%, compared with 25% for B.', 'while + mệnh đề đầy đủ; compared with + số liệu/đối tượng tương ứng.'),
  ('respectively', 'The figures for A and B were 40% and 25% respectively.', 'Ghép theo thứ tự: A = 40%; B = 25%.'),
 ],
]

EXTRA_EXAMPLES={
 'mixed': [('Hai biểu đồ, hai đơn vị', 'The bar chart illustrates the number of visitors to a museum, while the pie chart shows the proportion of visitors in each age group. Overall, visitor numbers increased, and adults made up the largest age group.', 'Body 1 mô tả số khách trong bar chart; Body 2 mô tả tỷ lệ các nhóm tuổi trong pie chart.')],
 'maps': [('Thay đổi và giữ nguyên', 'The maps illustrate how a town centre changed between 2000 and 2020. Overall, the area became more commercial. The old factory was replaced by a supermarket, while the park remained unchanged.', 'A = old factory; B = supermarket; C = park. Dùng was vì thay đổi đã xảy ra.')],
 'process': [('Quy trình sản xuất', 'The diagram illustrates how orange juice is produced. Overall, the process begins with harvesting oranges and ends with packaging the juice. First, the oranges are washed, after which they are pressed. Finally, the juice is packaged.', 'Vật liệu nhận tác động: are washed, are pressed, is packaged. Sau begins with / ends with dùng V-ing hoặc danh từ.')],
 'natural_process': [('Vòng đời', 'The diagram illustrates how a butterfly develops. Overall, its life cycle consists of four main stages. First, eggs hatch into caterpillars, after which pupae are formed. Adult butterflies then emerge and lay eggs, and the cycle begins again.', 'Các giai đoạn: egg → caterpillar → pupa → adult. Chọn chủ động/bị động theo hành động, không áp dụng một thể cho cả bài.')],
 'mechanism': [('Cấu tạo và vận hành', 'The diagram illustrates how a water filter works. Overall, it removes impurities from water. The inlet pipe is connected to a tank containing a filter. Water flows through the filter before leaving through the outlet pipe.', 'is connected to mô tả cấu tạo; flows through mô tả hướng chuyển động.')],
 'future': [('Quá khứ và dự báo', 'The figure rose from 20% in 2000 to 35% in 2020 and is projected to reach 50% in 2050.', 'rose cho dữ liệu quá khứ; is projected to reach đánh dấu số liệu dự báo.')],
 'odd': [('So sánh kích thước', 'Overall, the main differences are in the size and shape of the two containers. Container A is taller than container B, while container B is wider.', 'So sánh đúng chiều: taller là cao hơn; wider là rộng hơn. Không dùng increased khi hình không thể hiện sự thay đổi.')],
}


def show_examples(examples):
    st.markdown('**Ví dụ áp dụng**')
    for label, example, explanation in examples:
        st.markdown('**'+label+'**')
        show_highlighted(example)
        st.caption('Cách áp dụng: '+explanation)

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
    st.caption('Ví dụ bên dưới dùng dữ liệu minh họa để học cấu trúc; khi viết bài thật hãy thay bằng đúng thông tin trên đề.')
    for index,(title,template,note) in enumerate(CORE):
        with st.expander(title,expanded=title.startswith('1')):
            show_highlighted(template);st.caption(note)
            show_examples(CORE_EXAMPLES[index])
    if category in ('all','cot_4','cot_lt4','cot_5plus','two_years','future','mixed'):
        with st.expander('Overview — chọn 1 trong 3 tình huống theo ghi chú của bạn'):
            show_highlighted('Cùng xu hướng: Overall, there was an increase/decline in [measure] in all [groups] examined. In addition, [A] consistently had the highest figures, while [B] had the lowest.')
            show_examples([('Cùng tăng', 'Overall, the proportion of internet users increased in all four countries examined. In addition, country A consistently had the highest figures, while country B had the lowest.', 'Nhóm nào cũng tăng; chỉ dùng consistently khi A cao nhất và B thấp nhất ở mọi mốc.')])
            show_highlighted('Khác xu hướng: Overall, there was a decline in [measure] in [group 1], while a rise was seen in [group 2]. In addition, [A] generally had the highest figures.')
            show_examples([('Nhóm giảm và nhóm tăng', 'Overall, there was a decline in the amount of waste produced by companies A and B, while a rise was seen in company C.', 'Nhóm 1 = A và B giảm; nhóm 2 = C tăng. Không dùng opposite trend nếu hai nhóm cùng tăng.')])
            show_highlighted('Vượt lên dẫn đầu: Overall, the figure for [A] increased to surpass that of [B], making it the most [used/consumed] [category] from [year] onwards.')
            show_examples([('Đổi vị trí dẫn đầu', 'Overall, the proportion of bus users increased to surpass that of car users, making buses the most popular means of transport in 2009.', 'Chỉ biết hai năm 2004 và 2009 thì nêu in 2009; không tự khẳng định thời điểm vượt lên ở giữa.')])
            st.caption('Nếu cần nhấn mạnh mức tăng: with the most dramatic rise being seen in the figures for A. Despite this chỉ dùng nếu nhận xét tiếp theo thực sự tương phản. Chỉ nói dẫn đầu từ một năm khi hình xác nhận vị trí đó.')
        with st.expander('Body — biến thể bổ sung, chưa cần học hết'):
            show_highlighted('Similar changes, but to a lesser/greater extent, were seen in the figure for [B], which [verb] … .')
            show_examples([('Cùng chiều, mức tăng nhỏ hơn', 'The figure for A rose from 20 to 40 tonnes. Similar changes, but to a lesser extent, were seen in the figure for B, which increased from 10 to 15 tonnes.', 'A tăng 20 tonnes, B tăng 5 tonnes nên dùng to a lesser extent.')])
            show_highlighted('[A] rose to a peak of [X] in [year], before falling to [Y].')
            show_examples([('Tăng đến đỉnh rồi giảm', 'The figure for A rose to a peak of 50% in 2010, before falling to 35% in 2020.', 'Đỉnh = 50% năm 2010; mốc cuối = 35% năm 2020.')])
            show_highlighted('[A] started at [X], after which it fluctuated until [year], before ending the period at [Y].')
            show_examples([('Có biến động ở giữa', 'The figure for A started at 20% in 2000, after which it fluctuated between 18% and 25% until 2015, before ending the period at 30% in 2020.', 'Chỉ dùng fluctuated khi có nhiều mốc lên xuống; không suy ra biến động từ hai mốc.')])
            show_highlighted('[A] started at [X] and continued to rise, reaching [Y] in the final year.')
            show_examples([('Tăng xuyên suốt', 'The figure for A started at 20% in 2000 and continued to rise, reaching 50% in the final year.', 'continued to rise cần được xác nhận bởi các mốc ở giữa; reaching nối mốc kết thúc.')])
            show_highlighted('Conversely, the figure for [B] fell to [Y].')
            show_examples([('Xu hướng ngược lại', 'The figure for A increased to 50%. Conversely, the figure for B fell to 15%.', 'A tăng nhưng B giảm, nên Conversely phù hợp.')])
            st.caption('Chuẩn hóa từ ghi chú Introduction: experienced (quá khứ); reach a peak of / peak at; a slight decrease (danh từ), decreased slightly (động từ). Mẫu số liệu phải kiểm tra lại ảnh trước khi học thuộc.')
    for key,(title,template,note) in EXTRA.items():
        if category in ('all',key):
            with st.expander('Khung riêng · '+title):
                show_highlighted(template);st.caption(note)
                show_examples(EXTRA_EXAMPLES[key])
    st.caption('Đổi thì và chủ động/bị động theo đề: people spent / money was spent; cars were produced / electricity was generated. Các khung có thể rút ngắn, không cần dùng hết trong một bài.')
