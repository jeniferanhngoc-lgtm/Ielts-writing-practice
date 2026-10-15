"""Single-answer recall questions grounded in each existing example."""
import random
import re

# Phrase, distractors, and explanation for the intended source sentence.
BLANKS = {
 'intro-count': ('how many', ['how much', 'how little'], 'Cars là danh từ đếm được số nhiều nên dùng how many.'),
 'intro-amount': ('how much', ['how many', 'how few'], 'Electricity không đếm được nên dùng how much.'),
 'intro-percentage': ('the percentage of', ['the amount of', 'the number of'], 'Đại lượng cần mô tả là tỷ lệ %, không phải số lượng người.'),
 'overview-all': ('In addition', ['Because of', 'Despite of'], 'In addition bổ sung điểm nổi bật thứ hai; theo sau là một mệnh đề.'),
 'overview-trend': ('while', ['despite', 'because of'], 'While nối hai mệnh đề mô tả các xu hướng đối lập.'),
 'overview-overtake': ('surpass', ['surpassing', 'surpassed'], 'Sau increased to cần động từ nguyên mẫu surpass.'),
 'from-to': ('from', ['by', 'at'], 'Rose from X to Y: từ mốc đầu X đến mốc cuối Y. By chỉ mức chênh lệch.'),
 'sequence': ('after which', ['after that it', 'after'], 'After which nối mệnh đề sau với sự việc trước; after đơn lẻ không nối hai mệnh đề theo cách này.'),
 'with': ('with a subsequent', ['with subsequently', 'with increased'], 'Sau with dùng cụm danh từ: a subsequent rise.'),
 'similar': ('to a lesser extent', ['to a lesser extend', 'at a lesser extent'], 'Cụm đúng là to a lesser extent: cùng chiều nhưng mức thay đổi nhỏ hơn.'),
 'peak': ('a peak of', ['a peak at of', 'peak to'], 'Rose to a peak of + số liệu. Một cách khác là peaked at + số liệu.'),
 'conversely': ('Conversely', ['Similarly', 'Likewise'], 'A tăng còn B giảm nên dùng Conversely để nêu xu hướng ngược.'),
 'respectively': ('respectively', ['respective', 'respectful'], 'Respectively ghép theo thứ tự France → 75, Italy → 60.'),
 'forecast': ('is projected to', ['is projected for', 'is projecting to'], 'Dự báo dùng is projected to + động từ nguyên mẫu.'),
 'static-overview': ('while', ['despite', 'because of'], 'While nối hai mệnh đề đối chiếu nhóm cao nhất và thấp nhất.'),
 'compare': ('compared with', ['compared than', 'comparing than'], 'Compared with + số liệu/đối tượng tương ứng để so sánh.'),
 'mixed-intro': ('while', ['despite', 'because of'], 'While nối hai mệnh đề giới thiệu hai biểu đồ.'),
 'map-intro': ('illustrate', ['illustrates', 'illustrating'], 'The maps là chủ ngữ số nhiều nên dùng illustrate.'),
 'map-overview': ('remained unchanged', ['remained change', 'remained to unchanged'], 'Remained unchanged mô tả đặc điểm giữ nguyên.'),
 'location': ('above', ['aboves', 'aboving'], 'Above là giới từ: ở phía trên một bộ phận khác.'),
 'map-change': ('was replaced by', ['was replace by', 'was replaced into'], 'Was replaced by: A được thay bằng B; converted into là chuyển đổi thành.'),
 'map-build': ('was demolished', ['was demolish', 'was demolishing'], 'Công trình bị phá bỏ: was + V3 (demolished).'),
 'map-trees': ('to make way for', ['to making way for', 'to make way of'], 'To make way for + công trình: dọn chỗ để xây công trình đó.'),
 'map-roads': ('was widened', ['was widen', 'were widened'], 'Bị động quá khứ: đường được mở rộng, was + widened.'),
 'map-links': ('being turned into', ['be turned into', 'being turn into'], 'With + danh từ + being + V3 mô tả thay đổi bị động.'),
 'map-accompanied': ('was accompanied by', ['was accompany by', 'was accompanied into'], 'Was accompanied by + cụm danh từ nêu thay đổi đi kèm.'),
 'process-intro': ('is produced', ['is produce', 'is producing'], 'Coffee được sản xuất: hiện tại đơn bị động is + V3.'),
 'process-overview': ('beginning with', ['beginning to with', 'began with'], 'Beginning with + danh từ/V-ing nêu điểm đầu, song song với ending with.'),
 'process-order': ('at which point', ['at which', 'at that it point'], 'At which point nối thời điểm mà vật liệu đã sẵn sàng cho bước sau.'),
 'process-purpose': ('in order to', ['in order that to', 'in order for to'], 'In order to + động từ nguyên mẫu nêu mục đích; so that cần mệnh đề.'),
}


def choice_question(item):
    phrase, distractors, explanation = BLANKS[item['structure_id']]
    example = item['examples'][0]
    match = re.search(re.escape(phrase), example, flags=re.I)
    if not match:
        raise ValueError('Quiz phrase missing from source: '+item['structure_id'])
    answer = match[0]
    options = [answer]+distractors
    random.Random(item['structure_id']).shuffle(options)
    return dict(prompt=example[:match.start()]+' ______ '+example[match.end():],
                answer=answer, options=options, explanation=explanation, example=example)


def lesson_type(lesson):
    index = int(lesson['id'].split('.')[1])
    return {1:'Line chart', 2:'Bar chart', 3:'Table', 4:'Line chart', 5:'Bar chart',
            6:'Table', 7:'Pie chart', 8:'Pie chart', 9:'Line chart', 10:'Line chart',
            11:'Pie chart', 12:'Bar chart', 13:'Mixed chart', 14:'Maps', 15:'Maps',
            16:'Process', 17:'Process', 18:'Vòng đời tự nhiên'}[index]


def filter_lessons(bank, category):
    return [x for x in bank if category == 'Tất cả' or lesson_type(x) == category
            or (category == 'Process' and lesson_type(x) == 'Vòng đời tự nhiên')]


def random_lesson(ids, current):
    candidates = [ident for ident in ids if ident != current]
    return random.SystemRandom().choice(candidates or ids)
