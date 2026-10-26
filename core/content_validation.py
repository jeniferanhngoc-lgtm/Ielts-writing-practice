import json
from pathlib import Path

CATEGORIES = {
 'cot_4':'Thay đổi theo thời gian · đúng 4 nhóm','cot_lt4':'Thay đổi theo thời gian · dưới 4 nhóm',
 'cot_5plus':'Thay đổi theo thời gian · từ 5 nhóm','two_years':'Hai mốc năm',
 'future':'Dự báo','static':'So sánh tĩnh','mixed':'Biểu đồ kết hợp','maps':'Bản đồ',
 'process':'Quy trình','natural_process':'Quá trình tự nhiên','mechanism':'Cách hoạt động','odd':'Dạng đặc biệt'}
ROOT = Path(__file__).resolve().parents[1]


def validate_exercise(item, structure_ids):
    required = ['exercise_id','title','category','prompt','status','content_version','target_structure_ids']
    for name in required:
        if name not in item:
            raise ValueError(f'Thiếu {name}')
    if item['category'] not in CATEGORIES or item['status'] not in ['draft','verified','needs_review','duplicate']:
        raise ValueError('Nhóm hoặc trạng thái không hợp lệ')
    if not set(item['target_structure_ids']).issubset(structure_ids):
        raise ValueError('ID cấu trúc không tồn tại')
    asset = item.get('asset_reference','')
    if asset and (not asset.startswith('assets/') or Path(asset).is_absolute() or '..' in Path(asset).parts or ':' in asset):
        raise ValueError('Đường dẫn ảnh phải nằm trong assets')
    if item['status'] == 'verified':
        paragraphs = item.get('paragraphs',{})
        if set(paragraphs) != {'introduction','overview','body1','body2'} or not all(paragraphs.values()):
            raise ValueError('Đề verified phải có đủ 4 đoạn mẫu')
        if not item.get('analysis_vi') or not item.get('outline_vi') or not item.get('quizzes'):
            raise ValueError('Đề verified thiếu phân tích, dàn ý hoặc quiz')
    for quiz in item.get('quizzes',[]):
        if quiz.get('kind') not in ['single','multi','fill','numeric','correction','order']:
            raise ValueError('Dạng quiz không hợp lệ')
        if not quiz.get('accepted_answers') or not quiz.get('explanation_vi') or not quiz.get('prompt'):
            raise ValueError('Quiz thiếu câu hỏi, đáp án hoặc giải thích')
        if quiz['kind'] in ['single','multi'] and not set(quiz['accepted_answers']).issubset(quiz.get('options',[])):
            raise ValueError('Đáp án không nằm trong lựa chọn')
        if quiz['kind'] == 'numeric' and quiz.get('tolerance',0) < 0:
            raise ValueError('Sai số phải không âm')
    return item


def load_content():
    structures = json.loads((ROOT/'content/structures.json').read_text(encoding='utf-8'))
    exercises = json.loads((ROOT/'content/exercises.json').read_text(encoding='utf-8'))
    # Only user-supplied answers are eligible; generated models cannot re-enter.
    source_path=ROOT/'content/user_answer_source_20261020.json'
    if source_path.is_file():
        source=json.loads(source_path.read_text(encoding='utf-8'))
        exercises=source['source_exercises']
    else:
        exercises=[e for e in exercises if e.get('model_origin') in ('user_pdf','user_revision')]
    ids = {s['structure_id'] for s in structures}
    seen = set()
    for item in exercises:
        validate_exercise(item,ids)
        if item['exercise_id'] in seen:
            raise ValueError('ID đề trùng')
        seen.add(item['exercise_id'])
    return structures, exercises


def full_model(exercise):
    return '\n\n'.join(exercise.get('paragraphs',{}).get(k,'') for k in ['introduction','overview','body1','body2'])
