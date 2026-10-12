import json


def make_prompt(exercise, attempt, structures):
    templates = '\n'.join(s['template'] for s in structures if s['structure_id'] in exercise['target_structure_ids'])
    return f'''Tôi đang luyện IELTS Academic Writing Task 1.
Đề: {exercise['prompt']}
Dữ liệu đã nhập: {json.dumps(exercise.get('data',{}),ensure_ascii=False)}
Lưu ý nguồn: {exercise.get('source_note','')}
Cấu trúc mục tiêu:
{templates}
Bài tôi viết:
{attempt['answer']}
Hãy kiểm tra mô tả dữ liệu, ngữ pháp và cách dùng cấu trúc. Giải thích bằng tiếng Việt, sửa tối thiểu và giữ ý của tôi. Dùng từ thông dụng, không ép paraphrase bằng từ khó. Chấp nhận cách diễn đạt đúng khác mẫu. Phân biệt câu đúng và câu đã dùng cấu trúc mục tiêu. Nếu thiếu ảnh hoặc dữ liệu, nói rõ thay vì đoán. Tôi sẽ đính kèm ảnh đề khi cần.'''
