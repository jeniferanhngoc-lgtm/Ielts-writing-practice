import random
import re

ROLES={'introduction':'Mở bài','overview':'Overview','body1':'Body 1','body2':'Body 2'}


def sentences(text):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z])',text) if x.strip()]


def sentence_cards(e):
    cards=[]
    for role in ROLES:
        for sentence in sentences(e['paragraphs'][role]):
            cards.append({'id':f'S{len(cards)+1:02}', 'text':sentence,'role':role})
    ids=list(range(1,len(cards)+1))
    random.Random(e['exercise_id']+'labels').shuffle(ids)
    for card,ident in zip(cards,ids):card['id']=f'S{ident:02}'
    return cards


def shuffled(items,seed):
    result=list(items)
    random.Random(seed).shuffle(result)
    if len(result)>1 and result==list(items):
        result=result[1:]+result[:1]
    return result


PHRASES={
 'Overall':'Nhìn chung; báo hiệu overview',
 'after which':'sau đó; nối một mệnh đề có chủ ngữ và động từ',
 'followed by':'tiếp theo là; theo sau bằng danh từ/cụm danh từ',
 'compared with':'so với', 'compared to':'so với',
 'while':'trong khi; nối hai mệnh đề', 'whereas':'trong khi; đối chiếu',
 'respectively':'lần lượt theo thứ tự đã nêu',
 'increased':'đã tăng', 'decreased':'đã giảm',
 'rose':'đã tăng', 'fell':'đã giảm',
 'was replaced by':'đã được thay thế bằng',
 'is placed':'được đặt; bị động hiện tại',
 'is expected to':'được dự kiến sẽ',
 'accounted for':'chiếm; quá khứ',
 'remained':'đã duy trì', 'before':'trước khi',
}


def cloze(e):
    blanks=[]; paragraphs=[]
    pattern=re.compile(r'\b('+ '|'.join(re.escape(x) for x in sorted(PHRASES,key=len,reverse=True))+r')\b',re.I)
    for role in ROLES:
        def replace(m):
            answer=m.group(0)
            source=next(k for k in PHRASES if k.lower()==answer.lower())
            blanks.append({'answer':answer,'hint':PHRASES[source]})
            return f"【{len(blanks)}】"
        paragraphs.append((ROLES[role],pattern.sub(replace,e['paragraphs'][role],count=3)))
    return paragraphs,blanks


def overview_choices(e):
    text=e['paragraphs']['overview']
    parts=sentences(text)
    if len(parts)<2:
        parts=re.split(r',? (?:while|with|and) ',text,maxsplit=1)
    # A one-feature overview cannot be honestly labelled as two independent features.
    correct=parts[:2]
    wrong=['Giải thích nguyên nhân bằng suy đoán ngoài biểu đồ.', 'Nêu ý kiến cá nhân thay cho đặc điểm của hình.']
    return correct, shuffled(correct+wrong,e['exercise_id'])


REVERSE={
 'trend':{
 'vi':'Số lượng khách du lịch giảm mạnh vào năm 2020.',
 'forms':['S + V + Adv','There + was + a + Adj + N + in …','S + saw + a + Adj + N'],
 'answers':['The number of tourists fell sharply in 2020.','There was a sharp fall in the number of tourists in 2020.','The number of tourists saw a sharp fall in 2020.'],
 'note':'Quá khứ: fell / was / saw. Sau fall (danh từ) dùng sharp; sau fell dùng sharply. Ví dụ bổ sung, không lấy số liệu từ hình đang chọn.'},
 'maps':{'vi':'Một công viên đã thay thế nhà máy vào năm 2010.',
 'forms':['A + replaced + B','B + was replaced by + A','B + was removed to make way for + A'],
 'answers':['A park replaced the factory in 2010.','The factory was replaced by a park in 2010.','The factory was removed to make way for a park in 2010.'],
 'note':'Câu đầu chủ động; hai câu sau bị động quá khứ. Ví dụ bổ sung, không phải dữ kiện của hình đang chọn.'},
 'process':{'vi':'Sau khi công nhân rửa trái cây, họ cắt chúng.',
 'forms':['After + S + V, S + V','S + V, after which + S + V','Bị động: Once + S + be + V3, S + be + V3'],
 'answers':['After workers wash the fruit, they cut it.','Workers wash the fruit, after which they cut it.','Once the fruit is washed, it is cut.'],
 'note':'Hiện tại đơn cho quy trình nói chung. Hai câu đầu chủ động, câu cuối bị động. Ví dụ bổ sung.'},
 'static':{'vi':'Tỷ lệ của A là 40%, gấp đôi tỷ lệ của B (20%).',
 'forms':['twice as high as','double that of','with respective figures of'],
 'answers':['The percentage for A was twice as high as that for B, at 40% and 20% respectively.','The percentage for A was 40%, double that of B at 20%.','A had a higher percentage than B, with respective figures of 40% and 20%.'],
 'note':'Ví dụ bổ sung với thời điểm quá khứ; không diễn giải chênh lệch này là xu hướng tăng theo thời gian.'},
 'future':{'vi':'Số lượng khách được dự báo sẽ tăng lên 500 vào năm 2030.',
 'forms':['is expected to + V','is projected to + V','A rise … is predicted'],
 'answers':['The number of visitors is expected to rise to 500 in 2030.','The number of visitors is projected to increase to 500 in 2030.','A rise in the number of visitors to 500 is predicted for 2030.'],
 'note':'Ví dụ bổ sung. Dùng rise to vì 500 là mốc đạt tới; dự báo không phải sự thật đã xảy ra.'},
}


def reverse_task(e):
    c=e['category']
    key=c if c in REVERSE else ('process' if c in ('natural_process','mechanism') else 'static' if c=='odd' else 'trend')
    return REVERSE[key]
