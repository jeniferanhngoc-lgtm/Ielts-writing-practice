import random

CONNECTORS={
 'while':'while nối hai mệnh đề tương phản hoặc hai đặc điểm cần đối chiếu.',
 'whereas':'whereas nối hai mệnh đề có đặc điểm tương phản.',
 'from':'from đánh dấu số/mốc khởi đầu; đi với to để nêu mốc cuối.',
 'to':'to chỉ mốc đạt tới; by chỉ mức chênh lệch.',
 'before':'before diễn tả trước bước/mốc tiếp theo; trước V-ing khi cùng chủ ngữ.',
 'after':'after nối thứ tự thời gian; after which + mệnh đề có chủ ngữ và động từ.',
 'with':'with + cụm danh từ để bổ sung thông tin hoặc số liệu.',
 'at':'at dùng trước mức số liệu hoặc vị trí phù hợp với câu.',
 'in':'in dùng trước năm, giai đoạn hoặc địa điểm trong câu này.',
 'by':'by chỉ tác nhân trong bị động hoặc mốc hoàn thành/mức chênh lệch tùy câu.',
 'is':'is là động từ be số ít, hiện tại; có thể kết hợp quá khứ phân từ trong bị động.',
 'was':'was là động từ be số ít, quá khứ; không dùng were với chủ ngữ số ít.',
 'are':'are là be số nhiều, hiện tại; dùng cho các vật/bộ phận trong quy trình.',
 'were':'were là be số nhiều, quá khứ; dùng với số liệu hoặc đối tượng số nhiều.',
}
for e in exercises.values():
    if e['status']!='verified': continue
    sentences=[]
    for part in ['body1','body2']:
        sentences+=re.split(r'(?<=[.!?])\s+(?=[A-Z])',e['paragraphs'][part])
    made=0
    e['sentence_notes']=[]
    for sentence in sentences:
        words=[w for w in CONNECTORS if re.search(r'\b'+w+r'\b',sentence)]
        if words:
            word=words[0]
            e['sentence_notes'].append({'sentence':sentence,'explanation_vi':CONNECTORS[word]})
            if made<2:
                e['quizzes'].append(dict(quiz_id=f'fill-body-{made+1}',kind='fill',prompt='Điền MỘT từ còn thiếu trong câu mẫu: '+re.sub(r'\b'+word+r'\b','____',sentence,count=1),accepted_answers=[word],explanation_vi=CONNECTORS[word]+' Câu hoàn chỉnh: '+sentence))
                made+=1
    e['quizzes'].append(dict(quiz_id='outline',kind='single',prompt='Cách chia hai body phù hợp với bài mẫu này là gì?',options=[e['outline_vi'],'Chép toàn bộ lời đề vào body 1, chỉ đưa ý kiến cá nhân ở body 2.','Body 1 giải thích nguyên nhân ngoài đề; body 2 dự đoán thêm tương lai.'],accepted_answers=[e['outline_vi']],explanation_vi=e['outline_vi']+' Cách chia này gom thông tin để so sánh hoặc theo dõi quy trình; không phải cách chia duy nhất hợp lệ.'))
    # An explicitly constrained order exercise, preserving the original sentence.
    candidate=next((s for s in sentences if ', ' in s),None)
    if candidate:
        clauses=candidate.split(', ',1)
        e['quizzes'].append(dict(quiz_id='order',kind='order',prompt='Sắp xếp hai phần theo câu mẫu. Nhập mã theo thứ tự, ví dụ 2,1.',options=[clauses[1],clauses[0]+','],accepted_answers=[['2','1']],explanation_vi='Câu mẫu: '+candidate+' Giữ phần mở đầu trước phần bổ sung; đây là bài nhớ câu đã cho.'))
    for q in e['quizzes']:
        if q['kind']=='single': random.Random(e['exercise_id']+q['quiz_id']).shuffle(q['options'])
    e['checklist_vi']=['Đúng đối tượng, năm và đơn vị của ảnh.','Overview nêu đặc điểm nổi bật, không suy đoán nguyên nhân.','Body chia nhóm hợp lý và có số liệu/chi tiết hỗ trợ.','Đã kiểm tra thì, số ít/số nhiều và giới từ.','Dùng từ quen thuộc đúng nghĩa; không ép từ đồng nghĩa.','Nếu viết cả bài: ít nhất 150 từ; không có trần chính thức 220 từ.']

NUMERIC={
 4:('Giá trị kiwi xuất sang Nhật năm 2012 là bao nhiêu triệu NZ$?',325.3,'Đọc Japan/2012: NZ$325,300,000 = 325.3 triệu. Đơn vị không phải số quả.'),
 10:('Khoảng bao nhiêu phần trăm nhóm 15–24 đi xem phim năm 2000? Nhập số, chấp nhận sai số 2 điểm phần trăm.',58,'Đường đỏ kết thúc ngay dưới60%, khoảng58%; dùng about khi viết.'),
 14:('Australia sản xuất bao nhiêu ô tô năm 2009?',245624,'Hàng Australia, cột2009 là245,624. Viết: Australia produced 245,624 cars in 2009.'),
 17:('Africa chiếm bao nhiêu phần trăm timber?',9,'Pie timber: Africa9%, khác forest27%. Cấu trúc: Africa accounted for 9% of timber.'),
 25:('Teachers’ salaries chiếm bao nhiêu phần trăm năm 1991?',50,'Đọc pie1991:50%. Exactly half, không phải majority lớn hơn50%.'),
 26:('Northern Ireland giảm bao nhiêu điểm phần trăm từ2013 đến2014?',1,'5.6−4.6=1 điểm phần trăm. fell by one percentage point; fell to4.6%.'),
 29:('Chênh lệch lương tuần nam/nữ trong technicians là bao nhiêu dollars?',500,'1400−900=500. Men earned $500 more per week than women in this group.'),
 31:('Tokyo có bao nhiêu triệu hành khách/năm?',1927,'Cột passengers/year (millions):1927, không phải chiều dài155km.'),
 33:('Bao nhiêu phần trăm Chinese residents sống ở city?',99,'Bảng:99% Chinese residents ởcity; không phải99% dân Australia là Chinese.'),
 38:('Sole parent có tỷ lệ nghèo bao nhiêu phần trăm?',21,'21% là cao nhất, nhưng số người232,000 thấp hơn couple with children933,000.'),
 42:('Australia có bao nhiêu motorcycles đăng ký năm2014?',709000,'Hàng motorcycles/cột2014 là709,000; không nhập30.8 vì đó là% change.'),
 44:('Phụ nữ40–44 có hai con chiếm bao nhiêu phần trăm năm2006?',38.3,'Đọc hàng2006, cộtTwo children:38.3%.'),
 45:('Nhóm75+ không có bằng cấp chiếm bao nhiêu phần trăm?',72,'Phần xám nhóm75+:72%. Đây là majority vì lớn hơn50%.'),
 46:('Canada dự báo65+ năm2030 là bao nhiêu phần trăm trong bản làm tròn?',26,'Bản q046:26%. Dùng is projected to reach26%, không dùng số26.35 của q048.'),
 48:('Canada dự báo65+ năm2030 là bao nhiêu phần trăm trong bản chi tiết?',26.35,'Bản q048:26.35%, giữ số thập phân theo bảng.'),
 52:('UK dành bao nhiêu phần trăm thu nhập cho housing?',37,'UK/housing:37%. Đây là tỷ lệ thu nhập, không phải37% tất cả người Anh.'),
 57:('Immigration vì formal study chiếm bao nhiêu phần trăm?',26,'Immigration26%, emigration4%; xác định đúng hướng di cư.'),
 60:('Food/clothes chiếm bao nhiêu phần trăm income năm2013?',60,'15000/25000×100=60%. Đây là phép tính từ bảng; khác các tỷ lệ trong pie.'),
 61:('Food/beverages tăng bao nhiêu điểm phần trăm?',10,'32−22=10 điểm phần trăm. Không viết tăng10% tương đối.'),
 66:('Korea sản xuất bao nhiêu triệu tons waste năm2000?',19,'Korea2000:19; năm1980 thiếu dữ liệu, không xem là0.'),
 67:('China dự báo có bao nhiêu km high-speed rail năm2020?',13126,'2020:13,126km; đây là projection theo đề.'),
 72:('Science PhD chiếm bao nhiêu phần trăm năm2008?',30,'Pie2008:30%. Là nhóm lớn nhất nhưng không phải majority.'),
 74:('Black coal đưa bao nhiêu units tới consumers từ100 units đầu vào?',29,'100−68−3=29. Không dừng ở32 vì còn mất3 ởtransmission/distribution.'),
 75:('Tổng chi tiêu gia đình năm2001 là bao nhiêu AUD/tháng?',715,'Bảng total2001:A$715; giữ đơn vị mỗi tháng.'),
 83:('Bus chiếm bao nhiêu phần trăm năm2009?',46,'Bus46% lớn nhất nhưng dưới50%, không viết majority.'),
 86:('Dân số Malaysia năm2002 là bao nhiêu triệu?',24.3,'Malaysia2002:24.3 triệu. Phân biệt với Australia19.6 triệu.'),
 87:('Suitable degree courses năm2007 chiếm bao nhiêu phần trăm?',37,'37% cao nhất trong5 lý do, nhưng không phải majority.'),
 90:('Argentina có bao nhiêu xe năm2009?',466089,'Đọc đúng466,089 trên ảnh; không lấy466,085 từ ghi chép.'),
 91:('Macquarie Island có bao nhiêu visitors năm2000?',330,'330 lượt, không phải330,000. Đọc đúng số hàng cuối.'),
 94:('Women làm part-time ởNetherlands trung bình bao nhiêu giờ?',29.2,'29.2 giờ, cao hơn men28.3 giờ. Ảnh không nêu per week.'),
 95:('Sinh viên từ gia đình middle income năm1991 chiếm bao nhiêu phần trăm?',62,'Pie middle income62%; đây là majority. Không nhầm với high income30%.'),
 96:('Hiện tại có bao nhiêu private studying tables ở giữa thư viện?',6,'Đếm2 hàng×3 bàn=6, trước đây4 bàn. The number of tables increased from four to six.')}
for n,(question,answer,explanation) in NUMERIC.items():
    exercises[f'q{n:03}']['quizzes'].append(dict(quiz_id='read-data',kind='numeric',prompt=question,accepted_answers=[answer],tolerance=2 if n==10 else 0,explanation_vi=explanation))
