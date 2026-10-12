"""Offline learning tasks derived from the existing, verified model bank."""
import hashlib
import random
import re

ROLES = {'introduction':'Mở bài (Introduction)', 'overview':'Tổng quan (Overview)',
         'body1':'Thân bài 1 (Body 1)', 'body2':'Thân bài 2 (Body 2)'}


def sentences(text):
    # A decimal or an abbreviation without a following capital is not a boundary.
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+(?=[A-Z])', text) if x.strip()]


def sentence_cards(exercise):
    result = []
    for role in ROLES:
        for i, text in enumerate(sentences(exercise['paragraphs'].get(role, ''))):
            result.append({'id':f'{role}-{i}', 'text':text, 'role':role})
    return result


def shuffled(items, seed):
    result = list(items)
    rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest(), 16))
    rng.shuffle(result)
    if len(result)>1 and result==list(items):
        result = result[1:]+result[:1]
    return result


def grade_order(cards, answer):
    expected = [c['id'] for c in cards]
    if len(answer)!=len(expected) or set(answer)!=set(expected):
        raise ValueError('Mỗi câu phải xuất hiện đúng một lần.')
    return sum(a==b for a,b in zip(answer,expected)), len(expected)


def grade_categories(cards, answer, functions=False):
    if set(answer)!=set(c['id'] for c in cards):
        raise ValueError('Phân loại đủ tất cả câu.')
    def accepted(c):
        return c.get('accepted_functions',[c['role']]) if functions else [c['role']]
    return sum(answer[c['id']] in accepted(c) for c in cards), len(cards)


CLOZE = [
 ('Overall', 'Mở đầu tổng quan', ['Overall','Finally','For example']),
 ('after which', 'Sau đó (nối mệnh đề)', ['after which','compared with','respectively']),
 ('followed by', 'Tiếp theo là', ['followed by','because of','as opposed to']),
 ('compared with', 'So với', ['compared with','after which','ending at']),
 ('compared to', 'So với', ['compared to','before ending','with a subsequent']),
 ('in contrast', 'Ngược lại', ['in contrast','similarly','respectively']),
 ('meanwhile', 'Trong khi đó', ['meanwhile','therefore','respectively']),
 ('respectively', 'Lần lượt theo thứ tự', ['respectively','gradually','overall']),
 ('reaching a peak of', 'Đạt đỉnh ở mức', ['reaching a peak of','starting at','compared with']),
 ('reach a peak of', 'Đạt đỉnh ở mức', ['reach a peak of','end the period at','compare with']),
 ('rose sharply', 'Tăng mạnh (quá khứ)', ['rose sharply','fell sharply','remained stable']),
 ('increased significantly', 'Tăng đáng kể', ['increased significantly','decreased slightly','remained unchanged']),
 ('remained unchanged', 'Giữ nguyên', ['remained unchanged','rose dramatically','fell sharply']),
 ('before', 'Trước khi', ['before','despite','compared']),
 ('while', 'Trong khi / đối chiếu', ['while','therefore','respectively']),
 ('whereas', 'Trong khi / tương phản', ['whereas','therefore','respectively']),
 ('was replaced by', 'Đã được thay thế bằng', ['was replaced by','remained unchanged','was located in']),
 ('was converted into', 'Đã được chuyển thành', ['was converted into','remained unchanged','was located in']),
 ('was built', 'Đã được xây dựng', ['was built','was demolished','remained unchanged']),
 ('is followed by', 'Được tiếp nối bởi', ['is followed by','is compared with','is located above']),
 ('are then', 'Sau đó … (chủ ngữ số nhiều)', ['are then','was then','is then']),
 ('is then', 'Sau đó … (chủ ngữ số ít)', ['is then','were then','are then']),
 ('Once', 'Một khi / khi điều kiện đã đạt', ['Once','Despite','Respectively']),
 ('First', 'Bước đầu tiên', ['First','Finally','Overall']),
 ('Finally', 'Bước cuối', ['Finally','First','Overall']),
 ('from', 'Từ mốc khởi đầu', ['from','by','at']),
 ('to', 'Đến mốc đạt tới', ['to','by','from']),
]


def cloze_model(exercise):
    blanks = []
    paragraphs = {}
    pattern = re.compile(r'\b(?:'+ '|'.join(re.escape(x[0]) for x in CLOZE) + r')\b', re.I)
    lookup={x[0].casefold():x for x in CLOZE}
    for role in ROLES:
        role_count = 0
        def replace(match):
            nonlocal role_count
            if role_count>=4:
                return match.group()
            role_count+=1
            phrase=match.group()
            _,hint,options=lookup[phrase.casefold()]
            idx=len(blanks)+1
            blanks.append({'id':str(idx),'answer':phrase,'hint':hint,
                           'options':shuffled([phrase]+[x for x in options if x.casefold()!=phrase.casefold()],exercise['exercise_id']+str(idx))})
            return f'［{idx}］'
        paragraphs[role]=pattern.sub(replace,exercise['paragraphs'].get(role,''))
    return paragraphs, blanks


def grade_cloze(blanks, answers):
    from core.grading import normalize
    score=sum(normalize(answers.get(b['id'],''))==normalize(b['answer']) for b in blanks)
    return score,len(blanks)


def overview_task(exercise):
    """Select exactly two model-derived features, never fabricate chart facts."""
    features = sentences(exercise['paragraphs']['overview'])
    if features:
        features[0]=re.sub(r'^Overall,?\s*','',features[0])
    if len(features)<2:
        # One sentence can carry multiple features; do not guess how to split it.
        return None
    correct=features[:2]
    wrong=['Đề cho biết nguyên nhân kinh tế dẫn đến mọi thay đổi.',
           'Có thể kết luận xu hướng tương lai dù đề không có dự báo.']
    return {'options':shuffled(correct+wrong,exercise['exercise_id']+'overview-features'),
            'accepted_answers':correct}


def grouping_task(exercise):
    """Only editor-approved membership can be auto-graded."""
    return exercise.get('learning_tasks',{}).get('grouping')


def grouping_grade(task, answer):
    expected=task['accepted_assignments']
    if set(answer)!=set(task['items']):
        raise ValueError('Chọn nhóm cho đủ tất cả mục.')
    return int(any(answer==x for x in expected)),1


def reverse_task(exercise):
    data=exercise.get('data',{})
    years=data.get('years',[])
    if exercise['category'] in ('cot_4','cot_lt4','cot_5plus','two_years') and len(years)>=2:
        for name,values in data.items():
            if name=='years' or not isinstance(values,list) or len(values)!=len(years):
                continue
            a,b=values[0],values[-1]
            if not all(isinstance(v,(int,float)) and not isinstance(v,bool) for v in (a,b)) or a==b:
                continue
            start,end=str(years[0]),str(years[-1])
            rise=b>a
            verb,noun,vi=('increased','increase','tăng') if rise else ('decreased','decrease','giảm')
            n1,n2=f'{a:,}',f'{b:,}'
            subject=name.replace('_',' ')
            if re.fullmatch(r'\d+[–-]\d+|\d+\+',subject):
                subject='the '+subject+' age group'
            raw_unit=str(data.get('unit',''))
            unit={'percent':'%','cars':' cars','NZD':' NZD',
                  'million kg':' million kg','million tons':' million tons',
                  'million tonnes as labelled':' million tonnes',
                  'subscriptions per 100 inhabitants':' subscriptions per 100 inhabitants',
                  'AUD/month':' AUD per month'}.get(raw_unit,'')
            n1+=unit
            n2+=unit
            direction='lên' if rise else 'xuống'
            return {'source':'Dữ liệu của đề đang chọn; mô tả đầu–cuối, không hàm ý tăng/giảm liên tục.',
                    'prompt_vi':f'Số liệu của {subject} {vi} từ {n1} năm {start} {direction} {n2} năm {end}. Giữ đúng đơn vị theo hình.',
                    'forms':['S + V + from … to …','There was + a/an + N + in …','S + started at …, followed by …'],
                    'answers':[f'The figure for {subject} {verb} from {n1} in {start} to {n2} in {end}.',
                               f'There was {"an" if rise else "a"} {noun} in the figure for {subject}, from {n1} in {start} to {n2} in {end}.',
                               f'The figure for {subject} started at {n1} in {start}, followed by {"an" if rise else "a"} {noun} to {n2} in {end}.']}
    return None


def flashcards(structures):
    result=[{'id':s['structure_id'],'front':s['title']+' — Hãy nhớ khung câu và một ví dụ.',
             'back':s['template'],'example':s['examples'][0],
             'note':s['usage_conditions'],'categories':s['categories']} for s in structures]
    result += [
      {'id':'syn-show','front':"Thay thế cho show khi giới thiệu hình?",
       'back':'illustrate / provide information about / compare',
       'example':'The chart compares car production in three countries.',
       'note':'Compare dùng khi có so sánh; không phải mọi hình đều dùng được.','categories':[]},
      {'id':'syn-peak','front':'Hai cách viết “đạt đỉnh ở mức X”?',
       'back':'reach a peak of X / peak at X','example':'Sales peaked at 50 million.',
       'note':'Không viết reach at a peak. Chọn thì theo đề.','categories':[]},
      {'id':'syn-number','front':'Chọn number, amount hay proportion?',
       'back':'the number of + danh từ đếm được số nhiều; the amount of + không đếm được; the proportion/percentage of + tỷ lệ',
       'example':'The number of tourists rose. The amount of water fell.',
       'note':'Không đổi tỷ lệ phần trăm thành số người.','categories':[]},
      {'id':'syn-to-by','front':'Rise to và rise by khác nhau thế nào?',
       'back':'to = mốc đạt tới; by = mức tăng',
       'example':'20 → 35: rose to 35; rose by 15.',
       'note':'20% → 35% là tăng 15 điểm phần trăm, không phải tăng tương đối 15%.','categories':[]},
    ]
    return result

