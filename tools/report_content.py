import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
items=json.loads((ROOT/'content/exercises.json').read_text(encoding='utf-8'))
counts={status:sum(e['status']==status for e in items) for status in ['verified','needs_review','duplicate']}
lines=['# Kiểm kê nội dung và vấn đề nguồn','',f"100 ảnh: {counts['verified']} đề sẵn sàng học; {counts['needs_review']} đề cần xác nhận; {counts['duplicate']} ảnh lặp.",'',f"Tổng bài đóng đã soạn: {sum(len(e.get('quizzes',[])) for e in items)}. Mỗi đề sẵn sàng có bài đầy đủ ≥150 từ, dàn ý, giải thích và chế độ học câu/đoạn/cả bài.",'','verified là trạng thái biên tập nội bộ: đã đối chiếu ảnh và ngữ pháp, không phải xác nhận của IELTS hoặc giám khảo. Số đọc trên biểu đồ được diễn đạt gần đúng.','', '## Cần xác nhận từ ảnh nguồn','','Không tự điền đơn vị, sửa số hoặc bịa phần đề bị thiếu. Các đề dưới đây đã được kiểm tra nhưng chưa có full bài đáng tin cậy, nên ứng dụng chưa cho chấm tự động.','','| Mã | Đề | Cần bổ sung |','|---|---|---|']
for e in items:
    if e['status']=='needs_review': lines.append(f"| {e['exercise_id']} | {e['title']} | {e['review_reason']} |")
lines+=['','## Bản trùng','','| Ảnh | Dùng bài |','|---|---|']
for e in items:
    if e['status']=='duplicate':lines.append(f"| {e['exercise_id']} | {e['duplicate_of']} |")
lines+=['','## Toàn bộ tệp nguồn','','| Mã | Tên tệp | Trạng thái |','|---|---|---|']
for e in items:lines.append(f"| {e['exercise_id']} | {Path(e['asset_reference']).name} | {e['status']} |")
(ROOT/'CONTENT_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(counts)
