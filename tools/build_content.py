"""Offline content assembly only. No network or AI calls. Source facts are hand reviewed."""
import json
import shutil
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
(ROOT/'content').mkdir(exist_ok=True)
(ROOT/'assets/questions').mkdir(parents=True,exist_ok=True)
inventory_path=ROOT/'content/inventory.json'
if not inventory_path.exists(): inventory_path=ROOT/'tmp/inventory.json'
inventory=json.loads(inventory_path.read_text(encoding='utf-8'))
structures=[]


def structure(ident,title,role,template,explanation,conditions,example,errors,pages,categories,note='Đã chuẩn hóa ngữ pháp; ví dụ luyện bổ sung tự tạo.'):
    structures.append(dict(structure_id=ident,title=title,paragraph_role=role,template=template,explanation_vi=explanation,usage_conditions=conditions,examples=[example],common_errors=errors,source_reference=f'PDF thầy Kiên, trang PDF {pages}',categories=categories,status='verified',editorial_note=note))


trend=['cot_4','cot_lt4','cot_5plus','two_years','future','mixed']
all_categories=trend+['static','maps','process','natural_process','mechanism','odd']
structure('intro','Giới thiệu đúng nội dung','introduction','The chart/table shows the number/percentage/amount of … in … .','Nêu đối tượng, đơn vị và thời gian. Có thể dùng shows; không cần thay mọi từ bằng từ khó.','number + danh từ đếm được số nhiều; amount + không đếm được; percentage phải giữ nghĩa tỷ lệ.','The table shows the number of cars made in three countries in 2003, 2006 and 2009.','Không đổi percentage thành number; không dùng how much people cho số người.','11–14',all_categories)
structure('overview-trend','Tổng quan xu hướng','overview','Overall, … increased, while … decreased. In addition, … had the highest figure(s).','Chọn xu hướng chính và một điểm so sánh nổi bật.','Chỉ dùng increased/decreased nếu có thay đổi theo thời gian. Dùng consistently khi đúng ở mọi mốc.','Overall, car production increased in Argentina, while it decreased in Australia.','Không viết consistently nếu có ngoại lệ; không đưa nguyên nhân không có trong đề.','4–7',trend)
structure('from-to','Từ mốc đầu đến mốc cuối','body','The figure for … rose/fell from … in … to … in … .','from là mốc đầu, to là mốc cuối. by dùng cho lượng chênh lệch.','Hai mốc: chỉ mô tả chênh lệch, không suy diễn tăng đều ở giữa.','The figure rose from 20% to 35%, an increase of 15 percentage points.','Tăng từ 20% lên 35% là 15 điểm phần trăm, không phải tăng 15%.','8',trend)
structure('sequence','Mở đầu, chuyển biến, kết thúc','body','The … started at …, after which it experienced …, before ending the period at … .','Ghép mốc đầu, diễn biến tiếp theo và mốc cuối trong một câu.','Cần ít nhất ba mốc để mô tả hai nhịp; chủ ngữ của ending phải cùng đối tượng.','The proportion started at 20%, after which it rose to 35%, before ending the period at 30%.','experienced cho quá khứ; started at, không bỏ at.','7–10',trend)
structure('with','Đưa số liệu lên đầu','body','… in …, with a subsequent increase/decrease to … and a final … .','Sau with dùng cụm danh từ, chẳng hạn a rise hoặc a fall.','Dùng cho chuỗi thay đổi đã thể hiện trong dữ liệu.','Twenty per cent of households owned a car in 2000, with a subsequent rise to 35% and a final fall to 30%.','Không dùng with increased; không dùng cấu trúc này để bịa mốc giữa.','7–10',trend)
structure('followed','Biến động tiếp theo','body','The figure was …, followed by an increase/decrease to … .','followed by + danh từ chỉ diễn biến tiếp theo.','Mốc sau phải thực sự nằm sau mốc trước.','The figure was 20%, followed by an increase to 35%.','a slow increase, không phải an slow increase.','7–10',trend)
structure('similar','Xu hướng tương tự','body','A similar change was seen in …, which rose/fell from … to … .','Nối nhóm có cùng hướng thay đổi; vẫn ghi rõ số liệu riêng.','Cùng hướng không có nghĩa cùng mức độ. Có thể thêm to a lesser extent khi phù hợp.','A similar change was seen in France, where the figure rose from 30% to 40%.','Không ghép nhóm tăng với nhóm giảm bằng similarly.','7, 22–24',trend)
structure('peak','Nhấn mạnh đỉnh hoặc kết thúc','body','… increased/decreased, reaching … / ending at … .','Dùng V-ing bổ sung kết quả cho biến động đã nêu.','reaching a peak of chỉ dùng khi thật sự là điểm cao nhất trong phạm vi đề.','Sales increased, reaching a peak of 50 million in 2010.','Không viết reaching at; viết reaching 50 hoặc reaching a peak of 50.','9–11',trend)
structure('respectively','Ghép số liệu theo thứ tự','body','The figures for A and B were … and … respectively.','Số thứ nhất thuộc A, số thứ hai thuộc B.','Dùng khi thứ tự hai nhóm và hai số rõ ràng.','The figures for France and Italy were 75 and 60 million respectively.','Không đảo thứ tự đối tượng so với số liệu.','22, 35',['static']+trend)
structure('static-overview','Tổng quan so sánh tĩnh','overview','Overall, … had the highest figure, while … had the lowest.','Nêu chênh lệch nổi bật khi không có diễn biến theo thời gian.','Đề tĩnh không dùng rose/fell chỉ vì cột này cao hơn cột khác.','Overall, professionals earned the most, while manual workers earned the least.','Nhóm lớn nhất dưới 50% không phải majority.','35–36',['static','mixed'])
structure('compare','So sánh trực tiếp','body','… was …, compared with … for … .','Đặt hai số liệu cùng đơn vị cạnh nhau để so sánh.','So sánh cùng loại số liệu, tránh number với percentage.','The figure for men was $1,400, compared with $900 for women.','Không suy ra nguyên nhân từ chênh lệch.','35–36',['static','mixed','two_years','odd'])
structure('forecast','Dữ liệu dự báo','body','… is expected/projected to rise/fall to … in … .','Tách số thực tế và số dự báo của đề.','Theo nhãn dự báo của nguồn, kể cả khi năm ấy đã qua ở thời điểm học.','The proportion is projected to reach 30% in 2030.','Không trình bày dự báo như số liệu đã quan sát.','34',['future'])
structure('map-change','Thay đổi trên bản đồ','body','… was replaced by … / was converted into … .','Bị động để tập trung vào công trình; replaced by là thay thế, converted into là chuyển đổi.','Quá khứ cho bản đồ đã thay đổi; will be cho phương án tương lai.','The farmland was replaced by a playground.','Không tự đoán hướng Bắc nếu ảnh không có ký hiệu hướng.','38–39',['maps'])
structure('map-overview','Tổng quan bản đồ','overview','Overall, the area became more …, with the addition of … .','Tóm tắt 2–3 thay đổi lớn nhất, không liệt kê mọi chi tiết.','Dựa vào đặc điểm hiện trên bản đồ; không suy đoán nguyên nhân kinh tế.','Overall, the area gained more facilities, while the main road remained unchanged.','Không nói mọi thứ thay đổi nếu có công trình giữ nguyên.','38–39',['maps'])
structure('process-overview','Tổng quan quy trình','overview','Overall, the process begins with … and ends with … .','Dùng danh từ/V-ing sau with. Nêu đầu–cuối hoặc chu kỳ nếu có.','Quá trình tự nhiên không mặc định là chu kỳ. Cách hoạt động có thể tóm tắt chức năng.','Overall, the process begins with collecting waste glass and ends with producing new bottles.','Không tự đếm bước khi sơ đồ có nhánh chưa rõ.','42–46',['process','natural_process','mechanism'])
structure('process-order','Nối các bước','body','Once …, … . / …, after which … .','Once + mệnh đề; after which + mệnh đề để nối thứ tự.','Dùng bị động khi nguyên liệu chịu tác động, chủ động khi vật tự chuyển động/phát triển.','The beans are dried, after which they are roasted.','Không ép mọi câu quy trình thành bị động; chú ý thứ tự mũi tên.','42–46',['process','natural_process','mechanism'])
structure('location','Vị trí và bộ phận','body','… is located above/below/next to … .','Dùng từ vị trí quen thuộc để mô tả thiết bị hoặc bản đồ.','Chỉ nói vị trí thể hiện trên hình; không thêm bộ phận ngoài nguồn.','The burner is located above the basket.','Không tự thêm cơ chế không được minh họa.','38–39, 46',['maps','mechanism','odd'])

# Keep the learner-approved curriculum when rebuilding the original corpus.
patches=json.loads((ROOT/'content/structure_curriculum.json').read_text(encoding='utf-8'))
byid={s['structure_id']:s for s in structures}
byid.update({s['structure_id']:s for s in patches})
structures=list(byid.values())

exercises={}
titles='''Landfill for household waste|Renewable energy use|Central heating system|New Zealand kiwi fruit exports|Making compost|Steel production and employment|Felixstone maps|Road safety plans|Leisure time|Cinema attendance|Spending on books|Living in London|Households with cars|Car production|Age at first birth|Rainwater for drinking|World forests and timber|Office redevelopment|Rice export prices|Oil consumption|New Zealand population|Meat and fish consumption|Women in parliament|Telephone calls|School spending|Female unemployment|Making ceramic pots|Coffee exports|Weekly salaries|Darwin waterfront|Underground railways|Renewable power|Australian population|Mismatched prompt: household spending|Telephone subscriptions|Carbonated drinks|Happy Valley shopping centre|Poverty in Australia|Poverty in Australia (duplicate)|Science qualifications|Forest industry production|Vehicles registered in Australia|Forton Valley maps|Children born to women aged 40–44|Education in Glasgow|Population aged 65+ (rounded)|US household spending|Population aged 65+ (detailed)|City population: actual and predicted|Higher education|Hot air balloon|Household budgets in Europe|Water cycle|Employment categories|Urban and rural populations|UK visitor spending|Reasons for migration|British emigration|Smoking in Someland|UK food and clothing budgets|Online sales in Canada|World water and water use|Rainwater reuse|Carbonated drinks (duplicate)|International travel|Waste production|High-speed rail|Glass recycling|Coffee production|Smoked fish|Urban populations|Engineering graduate qualifications|Crime in a US city|Energy loss from coal|Australian household spending|Renewable energy supply|School leavers|Food and other goods|UK population age groups|US research spending|Ireland emigration and unemployment|Age at marriage|Travel to university|Film production|Government transport spending|Australia and Malaysia population|Reasons for choosing university|Communication services|City population (duplicate)|Car production (different middle year)|World Heritage visitors|Study abroad expenses|UK graduates and employment|Working hours|UK university students|School library|Opinions of urban life|Australia trade|Crime in England and Wales|Waste disposal'''.split('|')
categories='''process cot_5plus mechanism cot_5plus process mixed maps maps static cot_4 cot_4 mixed cot_lt4 cot_lt4 cot_5plus process static maps cot_4 future future cot_4 cot_5plus cot_lt4 cot_5plus two_years process cot_lt4 static maps static cot_5plus mixed two_years cot_lt4 process maps static static static cot_lt4 cot_5plus maps cot_5plus static future two_years future odd cot_4 mechanism static natural_process two_years future mixed static cot_5plus cot_lt4 mixed two_years mixed process process cot_5plus cot_5plus future process process process future two_years cot_lt4 odd two_years cot_4 cot_lt4 mixed mixed cot_5plus mixed two_years two_years cot_5plus cot_4 mixed two_years cot_5plus odd cot_lt4 cot_5plus mixed mixed static mixed maps two_years mixed cot_lt4 cot_lt4'''.split()
for i,entry in enumerate(inventory):
    target=ROOT/'assets/questions'/entry['filename']
    if not target.exists(): shutil.copy2(ROOT.parent/'4.Task1- Question Bank'/entry['filename'],target)
    exercises[entry['id']]=dict(exercise_id=entry['id'],title=titles[i],category=categories[i],asset_reference='assets/questions/'+entry['filename'],prompt='Summarise the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words. See the original question image.',source_label='Ngân hàng đề người dùng cung cấp',source_note='Đọc từ ảnh gốc. Số ước lượng được ghi about/approximately trong bài.',status='draft',content_version='2026-10-12.1',target_structure_ids=[],data={},review_reason='Đang biên tập bài mẫu và kiểm tra dữ liệu.',source_sha256=entry['sha256'])


def add(n,intro,overview,b1,b2,analysis,outline,ids,data=None,note=''):
    e=exercises[f'q{n:03}']
    e.update(status='verified',paragraphs=dict(introduction=intro,overview=overview,body1=b1,body2=b2),analysis_vi=analysis,outline_vi=outline,target_structure_ids=ids,data=data or {},review_reason='',paragraph_notes={'introduction':'Nêu đúng nội dung, thời gian và đơn vị; dùng shows/compares để diễn đạt đơn giản.','overview':'Tóm tắt điểm nổi bật từ đề; không thêm nguyên nhân. '+analysis,'body1':'Triển khai nhóm thứ nhất bằng số liệu/chi tiết cụ thể. '+outline,'body2':'Hoàn thành nhóm còn lại; giữ đơn vị và thứ tự thông tin.'})
    e['prompt']=intro+' Summarise the information by selecting and reporting the main features, and make comparisons where relevant. Write at least 150 words.'
    if note: e['source_note']=note
    # Fixed authored answer for a constrained missing-word question.
    keyword=next((w for w in ['while','from','compared','after','which','with','Overall','The'] if re.search(r'\b'+w+r'\b',overview)), 'Overall')
    blank=re.sub(r'\b'+keyword+r'\b','____',overview,count=1)
    e['quizzes']=[dict(quiz_id='overview-choice',kind='single',prompt='Chọn overview phù hợp với đề.',options=[overview,'Overall, all the figures were the same and there were no important differences.','Overall, the diagram explains why people preferred these changes.'],accepted_answers=[overview],explanation_vi=analysis+' Overview cần tổng hợp đặc điểm chính; không nói mọi số giống nhau hoặc tự giải thích nguyên nhân.'),dict(quiz_id='fill-overview',kind='fill',prompt='Điền đúng MỘT từ theo mẫu đang học: '+blank,accepted_answers=[keyword],explanation_vi=f'Từ trong mẫu là {keyword}. '+next((s['explanation_vi'] for s in structures if s['structure_id'] in ids and s['paragraph_role']=='overview'),'Đọc cả câu để giữ liên kết và ý nghĩa.'))]


def hold(n,reason):
    exercises[f'q{n:03}'].update(status='needs_review',review_reason=reason)


def duplicate(n,original):
    exercises[f'q{n:03}'].update(status='duplicate',duplicate_of=f'q{original:03}',review_reason=f'Cùng đề với q{original:03}; dùng bản đó để tránh học lặp.')


# Individual essays and source checks are kept separately for readable editing.
for source in sorted((ROOT/'tools/corpus').glob('*.py')):
    exec(compile(source.read_text(encoding='utf-8'),str(source),'exec'))

for name,data in [('structures',structures),('exercises',list(exercises.values())),('inventory',inventory)]:
    (ROOT/f'content/{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
focus=[('Nền tảng, đơn vị và xu hướng','Đọc đề, phân biệt number/amount/percentage; quiz đầu vào và viết 1 câu.')]*3+[('Introduction, overview, đúng 4 nhóm','Học một khung; viết overview và kiểm tra đặc điểm chính.')]*4+[('Dưới 4 nhóm, từ 5 nhóm, hai năm, dự báo','Luyện chia nhóm và body; ôn lại câu cũ.')]*7+[('So sánh tĩnh, mixed, maps và process','Mỗi ngày một dạng; nhận diện đơn vị, vị trí hoặc thứ tự.')]*7+[('Trộn dạng và giảm gợi ý','Viết overview/body không xem mẫu; đổi dữ liệu rồi đối chiếu.')]*5+[('Bài hoàn chỉnh khoảng 20 phút','Tự viết, kiểm tra, chữa và viết lại; ôn lỗi lặp.')]*4
(ROOT/'content/plan_30_days.json').write_text(json.dumps([dict(day=i+1,focus=a,task=b) for i,(a,b) in enumerate(focus)],ensure_ascii=False,indent=2),encoding='utf-8')
print({status:sum(e['status']==status for e in exercises.values()) for status in ['verified','draft','needs_review','duplicate']})
